import unittest
from src.benchmark.metrics import percentile, summarize


class MetricsTests(unittest.TestCase):
    def test_empty_percentile(self):
        self.assertEqual(percentile([], 50), 0.0)

    def test_interpolated_median(self):
        self.assertEqual(percentile([1, 2, 3, 4], 50), 2.5)

    def test_unsorted_values(self):
        self.assertEqual(percentile([4, 1, 3, 2], 0), 1.0)

    def test_summary(self):
        rows = [
            {"status_code": 200, "latency_s": 1.0, "generated_tokens": 10},
            {"status_code": 500, "latency_s": 2.0, "generated_tokens": 0},
        ]
        result = summarize(rows, 2.0)
        self.assertEqual(result["successful_requests"], 1)
        self.assertEqual(result["failed_requests"], 1)
        self.assertEqual(result["generated_tokens"], 10)

    def test_empty_summary(self):
        result = summarize([], 0)
        self.assertEqual(result["request_throughput_rps"], 0)


if __name__ == "__main__":
    unittest.main()
