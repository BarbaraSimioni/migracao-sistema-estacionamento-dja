from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo


class DashboardApiTests(TestCase):
    def test_dashboard_reports_parking_totals(self):
        cliente = Cliente.objects.create(nome="Ana", cpf="111")
        veiculo = Veiculo.objects.create(
            placa="ABC1D23", marca="Fiat", modelo="Uno", cor="Prata", cliente=cliente
        )
        vaga = Vaga.objects.create(numero="C01", tipo="CARRO", status="OCUPADA")
        Permanencia.objects.create(veiculo=veiculo, vaga=vaga, status="ABERTO")

        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["totalVagas"], 16)
        self.assertEqual(response.json()["vagasLivres"], 15)
        self.assertEqual(response.json()["vagasOcupadas"], 1)
        self.assertEqual(response.json()["veiculosEstacionados"], 1)

    def test_dashboard_rejects_non_get_methods(self):
        self.assertEqual(self.client.post("/api/dashboard").status_code, 405)
