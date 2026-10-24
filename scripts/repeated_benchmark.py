
import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--url", default="http://127.0.0.1:8000/v1/chat/completions")
    p.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    p.add_argument("--requests", type=int, default=5)
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--concurrency", type=int, nargs="+", default=[1, 2])
    p.add_argument("--max-tokens", type=int, default=32)
    p.add_argument("--timeout", type=float, default=180)
    p.add_argument("--output-dir", default="results/raw")
    p.add_argument("--prefix", default="qwen-cpu-auto")
    p.add_argument("--stream", action="store_true")
    a = p.parse_args()

    a.repo = a.repo.resolve()
    out_dir = a.repo / a.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    trials = []
    requests = []

    for c in a.concurrency:
        for trial in range(1, a.trials + 1):
            csv_path = out_dir / f"{a.prefix}-c{c}-trial{trial}.csv"
            cmd = [
                sys.executable, "-m", "src.benchmark.client",
                "--url", a.url, "--model", a.model,
                "--requests", str(a.requests),
                "--concurrency", str(c),
                "--max-tokens", str(a.max_tokens),
                "--timeout", str(a.timeout),
                "--output", str(csv_path),
            ]
            if a.stream:
                cmd.append("--stream")

            print(f"\n=== Concurrency {c}, trial {trial}/{a.trials} ===", flush=True)
            result = subprocess.run(
                cmd, cwd=a.repo, capture_output=True, text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if result.returncode:
                raise RuntimeError(f"Trial failed: {cmd}")

            decoder = json.JSONDecoder()
            summary = None
            for i, char in enumerate(result.stdout):
                if char == "{":
                    try:
                        obj, _ = decoder.raw_decode(result.stdout[i:])
                    except json.JSONDecodeError:
                        continue
                    if "wall_time_s" in obj and "request_throughput_rps" in obj:
                        summary = obj
                        break
            if summary is None:
                raise ValueError("Could not parse benchmark summary JSON.")

            summary.update({
                "concurrency": c,
                "trial": trial,
                "stream": a.stream,
                "csv_path": str(csv_path.relative_to(a.repo)),
            })
            trials.append(summary)

            frame = pd.read_csv(csv_path)
            frame["concurrency"] = c
            frame["trial"] = trial
            frame["stream"] = a.stream
            requests.append(frame)

    trial_df = pd.DataFrame(trials)
    request_df = pd.concat(requests, ignore_index=True)

    trial_df.to_csv(out_dir / f"{a.prefix}-trial-summary.csv", index=False)
    request_df.to_csv(out_dir / f"{a.prefix}-all-requests.csv", index=False)

    aggregate = trial_df.groupby("concurrency").agg(
        trials=("trial", "count"),
        total_requests=("total_requests", "sum"),
        successful_requests=("successful_requests", "sum"),
        failed_requests=("failed_requests", "sum"),
        mean_throughput_rps=("request_throughput_rps", "mean"),
        std_throughput_rps=("request_throughput_rps", "std"),
        mean_token_throughput_tps=("token_throughput_tps", "mean"),
        mean_latency_s=("mean_latency_s", "mean"),
        mean_p50_latency_s=("p50_latency_s", "mean"),
        mean_p95_latency_s=("p95_latency_s", "mean"),
        mean_wall_time_s=("wall_time_s", "mean"),
    ).reset_index()

    aggregate.to_csv(out_dir / f"{a.prefix}-aggregate-summary.csv", index=False)

    print("\n=== TRIAL RESULTS ===")
    print(trial_df.to_string(index=False))
    print("\n=== AGGREGATE RESULTS ===")
    print(aggregate.to_string(index=False))
    print(f"\nSaved benchmark artifacts to: {out_dir}")


if __name__ == "__main__":
    main()
