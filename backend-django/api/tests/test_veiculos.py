import json

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo


class VeiculoApiTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Ana", cpf="111")

    def payload(self, placa="ABC1D23"):
        return {
            "placa": placa,
            "marca": "Fiat",
            "modelo": "Uno",
            "cor": "Prata",
            "clienteId": self.cliente.id,
        }

    def test_crud_serialization_and_plate_ordering(self):
        z = self.client.post(
            "/api/veiculos",
            data=json.dumps(self.payload("ZZZ9Z99")),
            content_type="application/json",
        ).json()
        created = self.client.post(
            "/api/veiculos/",
            data=json.dumps(self.payload()),
            content_type="application/json",
        )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["clienteNome"], "Ana")
        self.assertEqual(
            [item["placa"] for item in self.client.get("/api/veiculos").json()],
            ["ABC1D23", "ZZZ9Z99"],
        )
        self.assertEqual(
            self.client.get(f"/api/veiculos/{z['id']}").status_code, 200
        )
        self.assertEqual(
            self.client.delete(f"/api/veiculos/{z['id']}").status_code, 200
        )

    def test_missing_client_returns_not_found(self):
        data = self.payload()
        data["clienteId"] = 99999

        response = self.client.post(
            "/api/veiculos", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)

    def test_duplicate_plate_returns_conflict(self):
        Veiculo.objects.create(cliente=self.cliente, **{
            "placa": "ABC1D23", "marca": "Fiat", "modelo": "Uno", "cor": "Prata"
        })

        response = self.client.post(
            "/api/veiculos",
            data=json.dumps(self.payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)

    def test_vehicle_with_parking_record_cannot_be_deleted(self):
        veiculo = Veiculo.objects.create(cliente=self.cliente, **{
            "placa": "ABC1D23", "marca": "Fiat", "modelo": "Uno", "cor": "Prata"
        })
        vaga = Vaga.objects.create(numero="C01", tipo="CARRO")
        Permanencia.objects.create(veiculo=veiculo, vaga=vaga)

        response = self.client.delete(f"/api/veiculos/{veiculo.id}")

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Veiculo.objects.filter(id=veiculo.id).exists())
