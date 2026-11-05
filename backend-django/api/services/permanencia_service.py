import math
from datetime import datetime
from decimal import Decimal

from django.db import transaction

from api.models import Permanencia, Veiculo, Vaga

TARIFA_POR_HORA = Decimal('5.00')

class NaoEncontrado(ValueError):
    """Subclasse de ValueError: a view captura esta primeiro (404) e ValueError depois (409)."""


def _calcular_valor(entrada, saida):
    minutos = int((saida - entrada).total_seconds() // 60)
    horas = math.ceil(minutos / 60)
    if horas < 1:
        horas = 1
    return TARIFA_POR_HORA * horas


def registrar_entrada(veiculo_id, vaga_id):
    with transaction.atomic():
        try:
            veiculo = Veiculo.objects.get(id=veiculo_id)
        except Veiculo.DoesNotExist:
            raise NaoEncontrado("Veículo não encontrado.")

        if Permanencia.objects.filter(veiculo_id=veiculo_id, status='ABERTO').exists():
            raise ValueError("Veículo já possui uma permanência em aberto.")

        try:
            vaga = Vaga.objects.get(id=vaga_id)
        except Vaga.DoesNotExist:
            raise NaoEncontrado("Vaga não encontrada.")

        if vaga.status == 'OCUPADA':
            raise ValueError("Vaga já está ocupada.")

        vaga.status = 'OCUPADA'
        vaga.save()

        return Permanencia.objects.create(
            veiculo=veiculo,
            vaga=vaga,
            data_hora_entrada=datetime.now(),
            status='ABERTO'
        )

def registrar_saida(permanencia_id):
    with transaction.atomic():
        try:
            permanencia = Permanencia.objects.get(id=permanencia_id)
        except Permanencia.DoesNotExist:
            raise NaoEncontrado("Permanência não encontrada.")

        if permanencia.status == 'FINALIZADO':
            raise ValueError("Permanência já foi finalizada.")

        saida = datetime.now()
        permanencia.valor_total = _calcular_valor(permanencia.data_hora_entrada, saida)
        permanencia.data_hora_saida = saida
        permanencia.status = 'FINALIZADO'
        permanencia.save()

        vaga = permanencia.vaga
        vaga.status = 'LIVRE'
        vaga.save()

        return permanencia