import unittest
import alertbot
import json

examples = [{"name": "Grafana Alert",
             "filepath": "../alert_examples/grafana_alert.json",
             "expected_response": "",
             "type": "grafana-alert"},
            {"name": "Grafana Resolved",
             "filepath": "../alert_examples/grafana_resolved.json",
             "expected_response": "",
             "type": "grafana-resolved"},
            {"name": "Uptime Kuma 503 Alert",
             "filepath": "../alert_examples/uptime-kuma-503-alert.json",
             "expected_response": "",
             "type": "uptime-kuma-alert"},
            {"name": "Prometheus Alert",
             "filepath": "../alert_examples/prometheus_alert.json",
             "expected_response": "",
             "type": "prometheus-alert"},
            ]


class ParseResponses(unittest.TestCase):
    def test_classification(self):
        for example in examples:
            print(f"Example: {example['name']}")
            with open(example["filepath"]) as file:
                alert_data = json.load(file)
            found_type = alertbot.find_alert_type(alert_data)
            self.assertEqual(found_type, example["type"])


if __name__ == '__main__':
    unittest.main()
