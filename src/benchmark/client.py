import argparse
import asyncio
import csv
import json
import time
from pathlib import Path

import httpx

from src.benchmark.metrics import summarize


def parse_sse_line(line):
    if not line.startswith("data:"):
        return None
    payload = line[5:].strip()
    if not payload or payload == "[DONE]":
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


async def run_one(client, args, semaphore):
    row = {
        "status_code": 0,
        "latency_s": 0.0,
        "ttft_s": None,
        "mean_itl_ms": None,
        "generated_tokens": 0,
        "output_chars": 0,
        "error": "",
    }
    headers = {}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"

    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
        "max_tokens": args.max_tokens,
        "stream": args.stream,
    }

    async with semaphore:
        started = time.perf_counter()
        first_chunk = None
        chunk_times = []
        output_parts = []

        try:
            if args.stream:
                async with client.stream(
                    "POST", args.url, json=payload, headers=headers
                ) as response:
                    row["status_code"] = response.status_code
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        event = parse_sse_line(line)
                        if event is None:
                            continue
                        choices = event.get("choices", [])
                        if choices:
                            content = choices[0].get("delta", {}).get("content")
                            if content:
                                now = time.perf_counter()
                                if first_chunk is None:
                                    first_chunk = now
                                    row["ttft_s"] = first_chunk - started
                                chunk_times.append(now)
                                output_parts.append(content)
                        usage = event.get("usage")
                        if usage and usage.get("completion_tokens") is not None:
                            row["generated_tokens"] = usage["completion_tokens"]
            else:
                response = await client.post(
                    args.url, json=payload, headers=headers
                )
                row["status_code"] = response.status_code
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    output = choices[0].get("message", {}).get("content", "")
                    output_parts.append(output or "")
                usage = data.get("usage", {})
                row["generated_tokens"] = usage.get("completion_tokens", 0)

            row["latency_s"] = time.perf_counter() - started
            row["output_chars"] = sum(len(part) for part in output_parts)
            if args.stream and len(chunk_times) > 1:
                intervals = [
                    (b - a) * 1000 for a, b in zip(chunk_times, chunk_times[1:])
                ]
                row["mean_itl_ms"] = sum(intervals) / len(intervals)
            if row["generated_tokens"] == 0 and output_parts:
                row["generated_tokens"] = len("".join(output_parts).split())

        except Exception as exc:
            row["latency_s"] = time.perf_counter() - started
            row["error"] = f"{type(exc).__name__}: {exc}"

        return row


async def main(args):
    semaphore = asyncio.Semaphore(args.concurrency)
    timeout = httpx.Timeout(args.timeout)
    limits = httpx.Limits(
        max_connections=args.concurrency,
        max_keepalive_connections=args.concurrency,
    )

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        started = time.perf_counter()
        rows = await asyncio.gather(*[
            run_one(client, args, semaphore) for _ in range(args.requests)
        ])
        wall_time = time.perf_counter() - started

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report = summarize(rows, wall_time)
    print(json.dumps(report, indent=2))
    print(f"CSV saved to: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAI-compatible LLM benchmark client")
    parser.add_argument("--url", default="http://127.0.0.1:8000/v1/chat/completions")
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", default="Explain how a hash table works.")
    parser.add_argument("--requests", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--output", default="results/raw/benchmark.csv")
    args = parser.parse_args()

    if args.requests < 1 or args.concurrency < 1 or args.max_tokens < 1:
        parser.error("requests, concurrency, and max-tokens must be positive")
    asyncio.run(main(args))
