# Workload Scaling: Cross-Configuration Analysis

## Experimental setup

- Model: Qwen2.5-0.5B-Instruct
- Environment: Google Colab CPU
- Generation limits: 16, 32, and 64 tokens
- Concurrency: 1 and 2
- Trials: 3 per configuration
- Requests: 15 per configuration across three trials

## Results

See `workload-scaling-summary.csv` for the recorded aggregate metrics.

## Interpretation

Longer generation limits increase request latency and reduce request throughput in these measurements. Concurrency 2 improves aggregate request throughput relative to concurrency 1, while also increasing mean request latency.

These findings describe this specific CPU environment and workload. They should not be generalized to GPU inference or larger models without further experiments.

## Limitations

- Only three trials per configuration were run.
- The experiment uses a small model and a CPU-only environment.
- Aggregate values do not establish statistical significance.
