from django.urls import re_path

from api.views.cliente_views import lista_clientes, detalhe_cliente

urlpatterns = [
    re_path(r'^clientes/?$', lista_clientes),
    re_path(r'^clientes/(?P<id>\d+)/?$', detalhe_cliente),
]
