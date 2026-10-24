# CPU Inference Benchmark Report

## Environment

- Model: Qwen/Qwen2.5-0.5B-Instruct
- Runtime: Google Colab CPU
- CPU cores reported by OS: 2
- Device: CPU
- Maximum new tokens per request: 32
- Requests per configuration: 5
- Configurations: concurrency 1 and 2
- Streaming: disabled for this experiment
- Warm-up: one request before the sweep; excluded from measured requests

## Results

|   Concurrency |   Successful requests |   Mean latency (s) |   P50 latency (s) |   P95 latency (s) |   Request throughput (req/s) |   Token throughput (tokens/s) |
|--------------:|----------------------:|-------------------:|------------------:|------------------:|-----------------------------:|------------------------------:|
|         1.000 |                 5.000 |             14.585 |             9.884 |            25.379 |                        0.069 |                         2.194 |
|         2.000 |                 5.000 |             13.339 |            14.674 |            14.819 |                        0.135 |                         4.315 |

## Initial observations

- All 10 measured requests succeeded.
- Concurrency 2 achieved 0.1349 requests/s,
  compared with 0.0686 requests/s at concurrency 1.
- Observed request-throughput change: 96.7%.
- Observed token-throughput change: 96.7%.
- Mean latency was 14.58s at concurrency 1 and
  13.34s at concurrency 2.
- P95 latency was 25.38s at concurrency 1 and
  14.82s at concurrency 2.

## Limitations

This is a small, preliminary experiment with only five requests per
configuration in a temporary Colab environment. CPU availability and
runtime load may vary. The results do not establish a general scaling
law or production capacity. Repeat each configuration across multiple
trials with more requests before drawing strong conclusions.

The throughput figures are measured in this experiment and should not
be represented as GPU or production-server performance.
