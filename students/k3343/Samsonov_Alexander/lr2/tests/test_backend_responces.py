import unittest

import httpx


class TestBackend(unittest.TestCase):
    def setUp(self):
        self.client = httpx.Client(base_url='http://localhost:8000', timeout=60)

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)

    def test_endpoints(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

        res = self.client.get("/api/v1/topstories")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

        res = self.client.get("/api/v1/newstories")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)


if __name__ == '__main__':
    unittest.main()
