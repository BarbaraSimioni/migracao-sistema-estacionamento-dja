from django.urls import re_path

from api.views.cliente_views import lista_clientes, detalhe_cliente
from api.views.dashboard_views import dashboard
from api.views.permanencia_views import entrada, lista_permanencias, saida
from api.views.vaga_views import lista_vagas, detalhe_vaga
from api.views.veiculo_views import lista_veiculos, detalhe_veiculo

urlpatterns = [
    re_path(r'^clientes/?$', lista_clientes),
    re_path(r'^clientes/(?P<id>\d+)/?$', detalhe_cliente),
    re_path(r'^vagas/?$', lista_vagas),
    re_path(r'^vagas/(?P<id>\d+)/?$', detalhe_vaga),
    re_path(r'^veiculos/?$', lista_veiculos),
    re_path(r'^veiculos/(?P<id>\d+)/?$', detalhe_veiculo),
    re_path(r'^permanencias/?$', lista_permanencias),
    re_path(r'^permanencias/entrada/?$', entrada),
    re_path(r'^permanencias/(?P<id>\d+)/saida/?$', saida),
    re_path(r'^dashboard/?$', dashboard),
]
