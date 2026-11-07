from django.test import SimpleTestCase


class ApiSkeletonTests(SimpleTestCase):
    def test_unimplemented_collection_views_return_501(self):
        endpoints = (
            '/api/veiculos',
            '/api/vagas',
            '/api/permanencias',
            '/api/dashboard',
        )

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(response.status_code, 501)
                self.assertEqual(response.json(), {'error': 'não implementado'})

    def test_unimplemented_detail_and_action_views_return_501(self):
        requests = (
            ('get', '/api/veiculos/1'),
            ('get', '/api/vagas/1'),
            ('post', '/api/permanencias/entrada'),
            ('put', '/api/permanencias/1/saida'),
        )

        for method, endpoint in requests:
            with self.subTest(method=method, endpoint=endpoint):
                response = getattr(self.client, method)(
                    endpoint,
                    data={},
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 501)
                self.assertEqual(response.json(), {'error': 'não implementado'})

    def test_routes_accept_an_optional_trailing_slash(self):
        endpoints = (
            '/api/veiculos/',
            '/api/vagas/',
            '/api/permanencias/',
            '/api/permanencias/entrada/',
            '/api/permanencias/1/saida/',
            '/api/dashboard/',
        )

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                method = 'post' if 'entrada' in endpoint else 'put' if 'saida' in endpoint else 'get'
                response = getattr(self.client, method)(
                    endpoint,
                    data={},
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 501)

    def test_admin_route_is_not_exposed(self):
        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 404)

    def test_service_contract_is_importable(self):
        from api.services.permanencia_service import (
            NaoEncontrado,
            registrar_entrada,
            registrar_saida,
        )

        self.assertTrue(issubclass(NaoEncontrado, ValueError))
        with self.assertRaises(NotImplementedError):
            registrar_entrada(1, 1)
        with self.assertRaises(NotImplementedError):
            registrar_saida(1)
