import json

from django.db.models import ProtectedError
from django.http import JsonResponse

from api.models import Cliente, Veiculo


# ---------------------------------------------------------------------------
# Serialização (Tarefa 4)
# ---------------------------------------------------------------------------

def veiculo_to_dict(veiculo):
    return {
        "id": veiculo.id,
        "placa": veiculo.placa,
        "marca": veiculo.marca,
        "modelo": veiculo.modelo,
        "cor": veiculo.cor,
        "clienteId": veiculo.cliente_id,
        "clienteNome": veiculo.cliente.nome,
    }


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------

def _erro(mensagem, status):
    return JsonResponse({"error": mensagem}, status=status)


def _ler_json(request):
    """Devolve o corpo como dict, ou None se o JSON for inválido."""
    try:
        dados = json.loads(request.body)
    except ValueError:  # json.JSONDecodeError e erros de decodificação
        return None
    return dados if isinstance(dados, dict) else None


def _texto(valor):
    """Texto sem espaços nas pontas; None vira string vazia (como o trim() do Java)."""
    if valor is None:
        return ""
    return str(valor).strip()


def _validar(dados):
    """Valida os campos na ordem do contrato.
    Devolve (campos, None) se estiver tudo certo, ou (None, resposta_de_erro)."""
    campos = {}
    for nome in ("placa", "marca", "modelo", "cor"):
        valor = _texto(dados.get(nome))
        if not valor:
            return None, _erro(f"Campo '{nome}' é obrigatório", 400)
        campos[nome] = valor

    cliente_id = _texto(dados.get("clienteId"))
    if not cliente_id:
        return None, _erro("Campo 'clienteId' é obrigatório", 400)
    try:
        campos["cliente_id"] = int(cliente_id)
    except ValueError:
        return None, _erro("Campo 'clienteId' deve ser um número", 400)

    return campos, None


# ---------------------------------------------------------------------------
# Views (Tarefa 3)
# ---------------------------------------------------------------------------

def lista_veiculos(request):
    if request.method == "GET":
        veiculos = Veiculo.objects.select_related("cliente").order_by("placa")
        return JsonResponse([veiculo_to_dict(v) for v in veiculos], safe=False)

    if request.method == "POST":
        dados = _ler_json(request)
        if dados is None:
            return _erro("JSON inválido", 400)

        campos, erro = _validar(dados)
        if erro:
            return erro

        try:
            cliente = Cliente.objects.get(id=campos["cliente_id"])
        except Cliente.DoesNotExist:
            return _erro("Cliente não encontrado", 404)

        if Veiculo.objects.filter(placa=campos["placa"]).exists():
            return _erro("Placa já cadastrada", 409)

        veiculo = Veiculo.objects.create(
            placa=campos["placa"],
            marca=campos["marca"],
            modelo=campos["modelo"],
            cor=campos["cor"],
            cliente=cliente,
        )
        return JsonResponse(veiculo_to_dict(veiculo), status=201)

    return _erro("Método não permitido", 405)


def detalhe_veiculo(request, id):
    if request.method not in ("GET", "PUT", "DELETE"):
        return _erro("Método não permitido", 405)

    try:
        veiculo = Veiculo.objects.select_related("cliente").get(id=id)
    except Veiculo.DoesNotExist:
        return _erro("Veículo não encontrado", 404)

    if request.method == "GET":
        return JsonResponse(veiculo_to_dict(veiculo))

    if request.method == "PUT":
        dados = _ler_json(request)
        if dados is None:
            return _erro("JSON inválido", 400)

        campos, erro = _validar(dados)
        if erro:
            return erro

        try:
            cliente = Cliente.objects.get(id=campos["cliente_id"])
        except Cliente.DoesNotExist:
            return _erro("Cliente não encontrado", 404)

        # exclude(id=id): o veículo não pode conflitar com ele mesmo
        if Veiculo.objects.filter(placa=campos["placa"]).exclude(id=veiculo.id).exists():
            return _erro("Placa já cadastrada", 409)

        veiculo.placa = campos["placa"]
        veiculo.marca = campos["marca"]
        veiculo.modelo = campos["modelo"]
        veiculo.cor = campos["cor"]
        veiculo.cliente = cliente
        veiculo.save()
        return JsonResponse(veiculo_to_dict(veiculo))

    # DELETE
    try:
        veiculo.delete()
    except ProtectedError:
        return _erro("Não é possível excluir veículo com permanências registradas", 409)
    return JsonResponse({"message": "Veículo excluído com sucesso"})