from django.http import JsonResponse


def dashboard(request):
    return JsonResponse({'error': 'não implementado'}, status=501)
