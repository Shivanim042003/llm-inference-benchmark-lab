import math


def percentile(values, p):
    """Calculate a linearly interpolated percentile."""
    values = sorted(float(v) for v in values if math.isfinite(float(v)))
    if not values:
        return 0.0
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    position = (len(values) - 1) * p / 100
    low = int(position)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def summarize(rows, wall_time_s):
    successful = [r for r in rows if 200 <= r["status_code"] < 300]
    latencies = [r["latency_s"] for r in successful]
    token_count = sum(r["generated_tokens"] for r in successful)
    return {
        "total_requests": len(rows),
        "successful_requests": len(successful),
        "failed_requests": len(rows) - len(successful),
        "wall_time_s": wall_time_s,
        "request_throughput_rps": len(successful) / wall_time_s if wall_time_s > 0 else 0,
        "mean_latency_s": sum(latencies) / len(latencies) if latencies else 0,
        "p50_latency_s": percentile(latencies, 50),
        "p95_latency_s": percentile(latencies, 95),
        "generated_tokens": token_count,
        "token_throughput_tps": token_count / wall_time_s if wall_time_s > 0 else 0,
    }
