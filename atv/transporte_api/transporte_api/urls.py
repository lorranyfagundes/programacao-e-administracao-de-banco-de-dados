from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bilhetagem.views import *

# 1. Cria o Router
router = DefaultRouter()

# 2. Regista os ViewSets com os prefixos exigidos 
router.register(r'municipios', MunicipioViewSet)
router.register(r'empresas', EmpresaTransporteViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'tipos-ticket', TipoTicketViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'transportes', TransporteViewSet)
router.register(r'validadores', ValidadorViewSet)
router.register(r'validacoes', ValidacaoViewSet)

# 3. Define as URLs principais
urlpatterns = [
    path('admin/', admin.site.id),
    path('api/', include(router.urls)), # Todos os caminhos começam com api/
    ]