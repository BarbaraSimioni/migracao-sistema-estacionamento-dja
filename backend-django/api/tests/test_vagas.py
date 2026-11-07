import json

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo


class VagaUpdateTests(TestCase):
    def setUp(self):
        self.vaga = Vaga.objects.create(
            numero="C01", tipo="CARRO", status="OCUPADA"
        )

    def test_update_without_status_preserves_current_status(self):
        response = self.client.put(
            f"/api/vagas/{self.vaga.id}",
            data=json.dumps({"numero": "C01", "tipo": "CARRO"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "OCUPADA")

    def test_update_rejects_invalid_status(self):
        response = self.client.put(
            f"/api/vagas/{self.vaga.id}",
            data=json.dumps(
                {"numero": "C01", "tipo": "CARRO", "status": "QUEBRADA"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "OCUPADA")


class VagaApiTests(TestCase):
    def test_create_always_starts_free_and_filter_by_status(self):
        response = self.client.post(
            "/api/vagas/",
            data=json.dumps(
                {"numero": "C02", "tipo": "MOTO", "status": "OCUPADA"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "LIVRE")
        free_numbers = [
            item["numero"]
            for item in self.client.get("/api/vagas?status=LIVRE").json()
        ]
        self.assertIn("C02", free_numbers)

    def test_duplicate_number_returns_conflict(self):
        response = self.client.post(
            "/api/vagas",
            data=json.dumps({"numero": "A01", "tipo": "CARRO"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)

    def test_space_with_parking_record_cannot_be_deleted(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        veiculo = Veiculo.objects.create(
            placa="ABC1D23",
            marca="Fiat",
            modelo="Uno",
            cor="Prata",
            cliente=cliente,
        )
        vaga = Vaga.objects.create(numero="C03", tipo="CARRO")
        Permanencia.objects.create(veiculo=veiculo, vaga=vaga)

        response = self.client.delete(f"/api/vagas/{vaga.id}")

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Vaga.objects.filter(id=vaga.id).exists())
