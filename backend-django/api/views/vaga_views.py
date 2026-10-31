import json

from django.db.models import ProtectedError
from django.http import JsonResponse

from api.models import Vaga

TIPOS = ('CARRO', 'MOTO')
STATUSES = ('LIVRE', 'OCUPADA')


def vaga_to_dict(vaga):
    return {
        'id': vaga.id,
        'numero': vaga.numero,
        'tipo': vaga.tipo,
        'status': vaga.status,
    }


def erro(mensagem, status):
    return JsonResponse({'error': mensagem}, status=status)


def validar_dados(request):
    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return None, erro('JSON inválido', 400)
    if not isinstance(dados, dict):
        return None, erro('JSON inválido', 400)

    numero = dados.get('numero')
    if not isinstance(numero, str) or not numero.strip():
        return None, erro("Campo 'numero' é obrigatório", 400)
    if dados.get('tipo') not in TIPOS:
        return None, erro("Campo 'tipo' deve ser CARRO ou MOTO", 400)

    return dados, None


def lista_vagas(request):
    if request.method == 'GET':
        vagas = Vaga.objects.all().order_by('numero')
        status = request.GET.get('status')
        if status:
            vagas = vagas.filter(status=status)
        return JsonResponse([vaga_to_dict(v) for v in vagas], safe=False)

    if request.method == 'POST':
        dados, resposta_erro = validar_dados(request)
        if resposta_erro:
            return resposta_erro

        if Vaga.objects.filter(numero=dados['numero']).exists():
            return erro('Número de vaga já cadastrado', 409)

        # A vaga sempre nasce LIVRE, ignorando o status vindo no corpo
        vaga = Vaga.objects.create(
            numero=dados['numero'],
            tipo=dados['tipo'],
            status='LIVRE',
        )
        return JsonResponse(vaga_to_dict(vaga), status=201)

    return erro('Método não permitido', 405)


def detalhe_vaga(request, id):
    if request.method not in ('GET', 'PUT', 'DELETE'):
        return erro('Método não permitido', 405)

    try:
        vaga = Vaga.objects.get(id=id)
    except Vaga.DoesNotExist:
        return erro('Vaga não encontrada', 404)

    if request.method == 'GET':
        return JsonResponse(vaga_to_dict(vaga))

    if request.method == 'PUT':
        dados, resposta_erro = validar_dados(request)
        if resposta_erro:
            return resposta_erro

        if Vaga.objects.filter(numero=dados['numero']).exclude(id=id).exists():
            return erro('Número de vaga já cadastrado', 409)

        status = dados.get('status')
        if status not in STATUSES:
            status = 'LIVRE'  # mesmo comportamento do legado

        vaga.numero = dados['numero']
        vaga.tipo = dados['tipo']
        vaga.status = status
        vaga.save()
        return JsonResponse(vaga_to_dict(vaga))

    try:
        vaga.delete()
    except ProtectedError:
        return erro('Não é possível excluir vaga com permanências registradas', 409)
    return JsonResponse({'message': 'Vaga excluída com sucesso'})