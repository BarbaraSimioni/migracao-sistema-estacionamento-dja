import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.services.permanencia_service import _calcular_valor

class PermanenciaValidationTests(TestCase):
    def test_entry_rejects_non_numeric_ids_with_400(self):
        response = self.client.post(
            "/api/permanencias/entrada",
            data=json.dumps({"veiculoId": "abc", "vagaId": "xyz"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"error": "Campos 'veiculoId' e 'vagaId' devem ser números inteiros positivos"},
        )

    def test_entry_rejects_fractional_ids_with_400(self):
        response = self.client.post(
            "/api/permanencias/entrada",
            data=json.dumps({"veiculoId": 1.5, "vagaId": 1}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


class PermanenciaApiTests(TestCase):
    def setUp(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        self.veiculo = Veiculo.objects.create(
            placa="ABC1D23",
            marca="Fiat",
            modelo="Uno",
            cor="Prata",
            cliente=cliente,
        )
        self.vaga = Vaga.objects.create(numero="C01", tipo="CARRO")

    def entry(self):
        return self.client.post(
            "/api/permanencias/entrada/",
            data=json.dumps(
                {"veiculoId": self.veiculo.id, "vagaId": self.vaga.id}
            ),
            content_type="application/json",
        )

    def test_entry_and_exit_keep_space_and_record_consistent(self):
        entry = self.entry()

        self.assertEqual(entry.status_code, 201)
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "OCUPADA")
        self.assertEqual(entry.json()["status"], "ABERTO")
        self.assertIn("T", entry.json()["dataHoraEntrada"])

        exit_response = self.client.put(
            f"/api/permanencias/{entry.json()['id']}/saida"
        )
        self.assertEqual(exit_response.status_code, 200)
        self.assertEqual(exit_response.json()["status"], "FINALIZADO")
        self.assertEqual(exit_response.json()["valorTotal"], 5.0)
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, "LIVRE")

    def test_second_open_entry_for_vehicle_returns_conflict(self):
        self.assertEqual(self.entry().status_code, 201)
        another = Vaga.objects.create(numero="C02", tipo="CARRO")

        response = self.client.post(
            "/api/permanencias/entrada",
            data=json.dumps(
                {"veiculoId": self.veiculo.id, "vagaId": another.id}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)

    def test_entry_in_occupied_space_returns_conflict(self):
        self.vaga.status = "OCUPADA"
        self.vaga.save()

        self.assertEqual(self.entry().status_code, 409)

    def test_second_exit_returns_conflict(self):
        permanence_id = self.entry().json()["id"]
        self.assertEqual(
            self.client.put(f"/api/permanencias/{permanence_id}/saida").status_code,
            200,
        )

        self.assertEqual(
            self.client.put(f"/api/permanencias/{permanence_id}/saida").status_code,
            409,
        )

    def test_listing_filters_by_status(self):
        permanence_id = self.entry().json()["id"]

        open_items = self.client.get("/api/permanencias?status=ABERTO").json()
        closed_items = self.client.get(
            "/api/permanencias?status=FINALIZADO"
        ).json()

        self.assertEqual([item["id"] for item in open_items], [permanence_id])
        self.assertEqual(closed_items, [])

    def test_started_fraction_of_second_hour_is_charged_as_two_hours(self):
        entrance = datetime(2026, 1, 1, 10, 0, 0)
        exit_time = entrance + timedelta(hours=1, seconds=1)

        self.assertEqual(_calcular_valor(entrance, exit_time), Decimal("10.00"))

    def test_missing_resources_return_not_found(self):
        response = self.client.post(
            "/api/permanencias/entrada",
            data=json.dumps({"veiculoId": 99999, "vagaId": self.vaga.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            self.client.put("/api/permanencias/99999/saida").status_code, 404
        )
