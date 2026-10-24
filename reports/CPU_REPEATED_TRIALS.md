# Repeated CPU Inference Benchmark

## Environment

- Model: Qwen/Qwen2.5-0.5B-Instruct
- Runtime: Google Colab CPU
- Reported CPU cores: 2
- Device: CPU
- Maximum new tokens: 32
- Requests per trial: 5
- Trials per concurrency setting: 3
- Configurations: concurrency 1 and 2
- Streaming: disabled

## Results

All 30 measured requests succeeded.

Request throughput and token throughput are summarized in
`cpu-throughput-summary.csv`; per-trial measurements are in
`cpu-throughput-trials.csv`.

The mean measured request throughput was approximately 0.0899 requests/s
at concurrency 1 and 0.1354 requests/s at concurrency 2, an observed
increase of approximately 51%.

Mean request latency across successful requests was approximately
11.47 seconds at concurrency 1 and 13.20 seconds at concurrency 2.
Thus, higher concurrency improved observed throughput but increased
mean latency in this experiment.

## Artifacts

- `cpu-repeated-trial-summary.csv`: per-trial latency summary
- `cpu-throughput-trials.csv`: measured throughput for each trial
- `cpu-throughput-summary.csv`: throughput summary by concurrency
- `cpu-repeated-trial-throughput.png`: trial throughput chart

## Limitations

This is a preliminary CPU-only experiment with three trials of five
requests per configuration in a temporary Colab environment. Runtime
load, CPU scheduling, model state, and input/output lengths can affect
the measurements. The results should not be interpreted as production
capacity or a general scaling law. P95 latency estimates are especially
uncertain with these small samples.
