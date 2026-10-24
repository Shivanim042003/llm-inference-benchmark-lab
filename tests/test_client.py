import unittest
from src.benchmark.client import parse_sse_line


class SSEParserTests(unittest.TestCase):
    def test_valid_event(self):
        event = parse_sse_line('data: {"choices": []}')
        self.assertEqual(event, {"choices": []})

    def test_done_marker(self):
        self.assertIsNone(parse_sse_line("data: [DONE]"))

    def test_non_data_line(self):
        self.assertIsNone(parse_sse_line(": keep-alive"))


if __name__ == "__main__":
    unittest.main()
