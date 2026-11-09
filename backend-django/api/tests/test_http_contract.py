from django.test import TestCase


class CorsContractTests(TestCase):
    def assert_cors_headers(self, response):
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertEqual(
            response["Access-Control-Allow-Methods"],
            "GET, POST, PUT, DELETE, OPTIONS",
        )
        self.assertEqual(
            response["Access-Control-Allow-Headers"],
            "Content-Type, Authorization",
        )

    def test_success_response_contains_cors_headers(self):
        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assert_cors_headers(response)

    def test_not_found_response_contains_cors_headers(self):
        response = self.client.get("/api/rota-inexistente")

        self.assertEqual(response.status_code, 404)
        self.assert_cors_headers(response)

    def test_options_returns_empty_204_with_cors_headers(self):
        response = self.client.options("/api/rota-inexistente")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assert_cors_headers(response)

    def test_admin_route_is_not_exposed(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 404)
