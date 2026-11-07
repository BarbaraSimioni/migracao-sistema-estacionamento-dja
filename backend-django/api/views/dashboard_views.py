from django.http import JsonResponse

from api.models import Permanencia, Vaga


def dashboard(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    return JsonResponse(
        {
            'totalVagas': Vaga.objects.count(),
            'vagasLivres': Vaga.objects.filter(status='LIVRE').count(),
            'vagasOcupadas': Vaga.objects.filter(status='OCUPADA').count(),
            'veiculosEstacionados': Permanencia.objects.filter(
                status='ABERTO'
            ).count(),
        }
    )
