from django.http import JsonResponse


def lista_permanencias(request):
    return JsonResponse({'error': 'não implementado'}, status=501)


def entrada(request):
    return JsonResponse({'error': 'não implementado'}, status=501)


def saida(request, id):
    return JsonResponse({'error': 'não implementado'}, status=501)
