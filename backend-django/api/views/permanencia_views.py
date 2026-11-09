import json

from django.http import JsonResponse

from api.models import Permanencia
from api.services.permanencia_service import (
    NaoEncontrado,
    registrar_entrada,
    registrar_saida,
)


def permanencia_to_dict(permanencia):
    return {
        'id': permanencia.id,
        'veiculoId': permanencia.veiculo_id,
        'veiculoPlaca': permanencia.veiculo.placa,
        'veiculoModelo': permanencia.veiculo.modelo,
        'vagaId': permanencia.vaga_id,
        'vagaNumero': permanencia.vaga.numero,
        'dataHoraEntrada': (
            permanencia.data_hora_entrada.isoformat()
            if permanencia.data_hora_entrada
            else None
        ),
        'dataHoraSaida': (
            permanencia.data_hora_saida.isoformat()
            if permanencia.data_hora_saida
            else None
        ),
        'valorTotal': (
            float(permanencia.valor_total)
            if permanencia.valor_total is not None
            else None
        ),
        'status': permanencia.status,
    }


def _metodo_nao_permitido():
    return JsonResponse({'error': 'Método não permitido'}, status=405)


def _erro_service(erro, status):
    return JsonResponse({'error': str(erro)}, status=status)


def _id_positivo(valor):
    if isinstance(valor, bool):
        return None
    if isinstance(valor, float) and not valor.is_integer():
        return None
    try:
        identificador = int(valor)
    except (TypeError, ValueError):
        return None
    return identificador if identificador > 0 else None


def lista_permanencias(request):
    if request.method != 'GET':
        return _metodo_nao_permitido()

    permanencias = Permanencia.objects.select_related(
        'veiculo', 'vaga'
    ).order_by('-data_hora_entrada')

    status = request.GET.get('status')
    if status is not None:
        permanencias = permanencias.filter(status=status)

    return JsonResponse(
        [permanencia_to_dict(permanencia) for permanencia in permanencias],
        safe=False,
    )


def entrada(request):
    if request.method != 'POST':
        return _metodo_nao_permitido()

    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    if not isinstance(dados, dict):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    veiculo_id = dados.get('veiculoId')
    vaga_id = dados.get('vagaId')
    if (
        veiculo_id is None
        or (isinstance(veiculo_id, str) and not veiculo_id.strip())
        or vaga_id is None
        or (isinstance(vaga_id, str) and not vaga_id.strip())
    ):
        return JsonResponse(
            {'error': "Campos 'veiculoId' e 'vagaId' são obrigatórios"},
            status=400,
        )

    veiculo_id = _id_positivo(veiculo_id)
    vaga_id = _id_positivo(vaga_id)
    if veiculo_id is None or vaga_id is None:
        return JsonResponse(
            {
                'error': (
                    "Campos 'veiculoId' e 'vagaId' devem ser números "
                    "inteiros positivos"
                )
            },
            status=400,
        )

    try:
        permanencia = registrar_entrada(veiculo_id, vaga_id)
    except NaoEncontrado as erro:
        return _erro_service(erro, 404)
    except ValueError as erro:
        return _erro_service(erro, 409)

    return JsonResponse(permanencia_to_dict(permanencia), status=201)


def saida(request, id):
    if request.method != 'PUT':
        return _metodo_nao_permitido()

    try:
        permanencia = registrar_saida(id)
    except NaoEncontrado as erro:
        return _erro_service(erro, 404)
    except ValueError as erro:
        return _erro_service(erro, 409)

    return JsonResponse(permanencia_to_dict(permanencia))
