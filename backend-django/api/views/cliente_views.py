import json

from django.db.models import ProtectedError
from django.http import JsonResponse

from api.models import Cliente


def cliente_to_dict(cliente):
    return {
        'id': cliente.id,
        'nome': cliente.nome,
        'cpf': cliente.cpf,
        'telefone': cliente.telefone,
        'email': cliente.email,
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

    nome = dados.get('nome')
    if not isinstance(nome, str) or not nome.strip():
        return None, erro("Campo 'nome' é obrigatório", 400)
    cpf = dados.get('cpf')
    if not isinstance(cpf, str) or not cpf.strip():
        return None, erro("Campo 'cpf' é obrigatório", 400)

    return dados, None


def lista_clientes(request):
    if request.method == 'GET':
        clientes = Cliente.objects.all().order_by('nome')
        return JsonResponse([cliente_to_dict(c) for c in clientes], safe=False)

    if request.method == 'POST':
        dados, resposta_erro = validar_dados(request)
        if resposta_erro:
            return resposta_erro

        if Cliente.objects.filter(cpf=dados['cpf']).exists():
            return erro('CPF já cadastrado', 409)

        cliente = Cliente.objects.create(
            nome=dados['nome'],
            cpf=dados['cpf'],
            telefone=dados.get('telefone'),
            email=dados.get('email'),
        )
        return JsonResponse(cliente_to_dict(cliente), status=201)

    return erro('Método não permitido', 405)


def detalhe_cliente(request, id):
    if request.method not in ('GET', 'PUT', 'DELETE'):
        return erro('Método não permitido', 405)

    try:
        cliente = Cliente.objects.get(id=id)
    except Cliente.DoesNotExist:
        return erro('Cliente não encontrado', 404)

    if request.method == 'GET':
        return JsonResponse(cliente_to_dict(cliente))

    if request.method == 'PUT':
        dados, resposta_erro = validar_dados(request)
        if resposta_erro:
            return resposta_erro

        if Cliente.objects.filter(cpf=dados['cpf']).exclude(id=id).exists():
            return erro('CPF já cadastrado', 409)

        cliente.nome = dados['nome']
        cliente.cpf = dados['cpf']
        cliente.telefone = dados.get('telefone')
        cliente.email = dados.get('email')
        cliente.save()
        return JsonResponse(cliente_to_dict(cliente))

    try:
        cliente.delete()
    except ProtectedError:
        return erro('Não é possível excluir cliente com veículos cadastrados', 409)
    return JsonResponse({'message': 'Cliente excluído com sucesso'})
