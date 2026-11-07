import json

from django.test import TestCase

from api.models import Cliente, Veiculo


class ClienteApiTests(TestCase):
    def test_crud_and_alphabetical_listing(self):
        second = self.client.post(
            "/api/clientes",
            data=json.dumps({"nome": "Zeca", "cpf": "222"}),
            content_type="application/json",
        ).json()
        first_response = self.client.post(
            "/api/clientes/",
            data=json.dumps({"nome": "Ana", "cpf": "111"}),
            content_type="application/json",
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(
            [item["nome"] for item in self.client.get("/api/clientes").json()],
            ["Ana", "Zeca"],
        )

        update = self.client.put(
            f"/api/clientes/{second['id']}",
            data=json.dumps({"nome": "Beto", "cpf": "222"}),
            content_type="application/json",
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["nome"], "Beto")
        self.assertEqual(
            self.client.delete(f"/api/clientes/{second['id']}").status_code,
            200,
        )

    def test_duplicate_cpf_returns_conflict(self):
        Cliente.objects.create(nome="Ana", cpf="111")

        response = self.client.post(
            "/api/clientes",
            data=json.dumps({"nome": "Outra", "cpf": "111"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)

    def test_client_with_vehicle_cannot_be_deleted(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        Veiculo.objects.create(
            placa="ABC1D23",
            marca="Fiat",
            modelo="Uno",
            cor="Prata",
            cliente=cliente,
        )

        response = self.client.delete(f"/api/clientes/{cliente.id}")

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Cliente.objects.filter(id=cliente.id).exists())
