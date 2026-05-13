from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *

# --- TODAS AS VIEWS NECESSÁRIAS ---

class MunicipioViewSet(viewsets.ModelViewSet):
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']

class EmpresaTransporteViewSet(viewsets.ModelViewSet):
    queryset = EmpresaTransporte.objects.select_related('municipio').all()
    serializer_class = EmpresaTransporteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['municipio']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('data_cadastro')
    serializer_class = UsuarioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'email', 'cpf']

# ESTA É A QUE ESTAVA A FALTAR:
class TipoTicketViewSet(viewsets.ModelViewSet):
    queryset = TipoTicket.objects.all()
    serializer_class = TipoTicketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nome', 'ativo'] # Conforme solicitado na Questão 19 [cite: 125]

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('usuario', 'tipo').all().order_by('data_compra')
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['usuario', 'tipo', 'status']

class TransporteViewSet(viewsets.ModelViewSet):
    queryset = Transporte.objects.select_related('empresa').all()
    serializer_class = TransporteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo', 'empresa', 'ativo']
    search_fields = ['identificacao', 'nome']

class ValidadorViewSet(viewsets.ModelViewSet):
    queryset = Validador.objects.select_related('transporte').all()
    serializer_class = ValidadorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'transporte', 'ativo']

class ValidacaoViewSet(viewsets.ModelViewSet):
    queryset = Validacao.objects.select_related(
        'ticket__usuario', 'ticket__tipo', 'validador', 'transporte'
    ).all().order_by('data_hora')
    serializer_class = ValidacaoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ticket', 'validador', 'transporte', 'dentro_janela_integracao']