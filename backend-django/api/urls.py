from django.urls import re_path

from api.views.cliente_views import lista_clientes, detalhe_cliente
from api.views.vaga_views import lista_vagas, detalhe_vaga

urlpatterns = [
    re_path(r'^clientes/?$', lista_clientes),
    re_path(r'^clientes/(?P<id>\d+)/?$', detalhe_cliente),
    re_path(r'^vagas/?$', lista_vagas),
    re_path(r'^vagas/(?P<id>\d+)/?$', detalhe_vaga),
]
