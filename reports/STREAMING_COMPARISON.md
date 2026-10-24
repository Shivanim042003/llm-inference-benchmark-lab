# Streaming vs Non-Streaming Inference Benchmark

## Objective

Compare streaming and non-streaming inference using the same model,
request count, output-token limit, and concurrency settings.

## Environment and methodology

- Model: Qwen/Qwen2.5-0.5B-Instruct
- Runtime: CPU-only inference
- Requests: 5 per trial
- Trials: 3 per concurrency setting
- Concurrency: 1 and 2
- Maximum generated tokens: 32
- Successful requests: 60/60 across both modes

## Results

| Mode | Concurrency | Requests | Successes | Mean latency (s) | P50 latency (s) | P95 latency (s) | Mean TTFT (s) | Mean inter-chunk interval (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| stream | 1 | 15 | 15 | 8.630 | 8.564 | 10.179 | 1.244 | 246.113 |
| stream | 2 | 15 | 15 | 13.702 | 14.878 | 16.046 | 1.923 | 392.508 |
| nonstream | 1 | 15 | 15 | 9.885 | 9.237 | 17.890 | nan | nan |
| nonstream | 2 | 15 | 15 | 14.087 | 15.411 | 16.353 | nan | nan |

## Interpretation

Streaming had lower measured mean end-to-end latency in these trials at both concurrency levels. It also exposed time-to-first-token (TTFT), which helps characterize how quickly output begins to arrive.

Increasing concurrency improved aggregate request throughput, while mean per-request latency increased in both modes.

The mean inter-chunk interval is the average time between received content chunks; it should not be interpreted as exact per-token ITL.

## Limitations

- Results are from a small experiment with three trials per setting.
- CPU contention, model warm-up, and runtime variability may affect results.
- Streaming and non-streaming latency comparisons depend on the client, server, and chunk-delivery implementation.
- Repeat with more trials and workloads before drawing broad conclusions.

## Reproducibility

Raw request-level data and trial summaries are stored under `results/raw/`.
The aggregate summary is stored at `reports/streaming-comparison-summary.csv`.
