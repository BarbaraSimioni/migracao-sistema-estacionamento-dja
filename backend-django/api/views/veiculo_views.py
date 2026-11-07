from django.http import JsonResponse


def lista_veiculos(request):
    return JsonResponse({'error': 'não implementado'}, status=501)


def detalhe_veiculo(request, id):
    return JsonResponse({'error': 'não implementado'}, status=501)
