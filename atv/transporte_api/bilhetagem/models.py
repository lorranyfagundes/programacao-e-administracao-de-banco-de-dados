from django.db import models
from datetime import timedelta
from django.utils import timezone

# Municipio, EmpresaTransporte, Usuario, TipoTicket, Ticket, Transporte, Validador, Validacao

class Municipio(models.Model):
    nome = models.CharField(max_length=120) #nome do municipio
    uf = models.CharField(max_length=2) #sigla do estado
    endereco_sede = models.CharField(max_length=200, blank = True) # endereço da sede do municipio
    ativo = models.BooleanField(default=True) #indica se o municipio está ativo ou não

    def __str__(self):
        return self.nome

class EmpresaTransporte(models.Model):
    razao_social = models.CharField(max_length=200) # nome da empresa de transporte
    nome_fantasia = models.CharField(max_length=150, blank=True) # nome fantasia da empresa de transporte
    cnpj = models.CharField(max_length=18, unique=True) # CNPJ da empresa de transporte #ver o formato!
    endereco = models.CharField(max_length=200, blank = True) # endereço da empresa de transporte
    municipio = models.ForeignKey(Municipio, on_delete= models.PROTECT, related_name='empresas') # municipio onde a empresa de transporte atua

    def __str__(self):
        return self.nome_fantasia if self.nome_fantasia else self.razao_social


class Usuario(models.Model):
    nome = models.CharField(max_length=150) # nome do usuário
    email = models.EmailField(unique=True) # email do usuário
    telefone = models.CharField(max_length=20, blank=True) # telefone do usuário
    cpf = models.CharField(max_length=14, unique=True) # CPF do usuário #verificar formato!
    endereco = models.CharField(max_length=200, blank=True) # endereço do usuário
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0) # saldo do usuário
    data_cadastro = models.DateTimeField(auto_now_add=True) # data de cadastro do usuário
    
    def __str__(self):
        return self.nome
    

class TipoTicket(models.Model):
    tipo_ticket = [
        ('Avulso', 'Avulso'),
        ('Diário', 'Diário'),
        ('Semanal', 'Semanal'),
        ('Mensal', 'Mensal'),
        ('Anual', 'Anual'),                  
    ]
    duracao_ticket = [
    (1, '1 dia (Avulso/Diário)'),
    (7, '7 dias (Semanal)'),
    (30, '30 dias (Mensal)'),
    (365, '365 dias (Anual)'),
    ]
    nome = models.CharField(max_length=20, choices = tipo_ticket) # tipo do ticket
    descricao = models.TextField(blank=True) # descrição do tipo de ticket
    valor = models.DecimalField(max_digits=8, decimal_places=2) # valor do ticket
    duracao_dias = models.PositiveSmallIntegerField(choices=duracao_ticket) # duração do ticket em dias
    janela_integracao_minutos = models.PositiveSmallIntegerField(default=60) # janela de integração em minutos
    ativo = models.BooleanField(default=True) # indica se o tipo de ticket está ativo

    def __str__(self):
        return self.nome

class Ticket(models.Model):
    STATUS_TICKET = [
    ("ativo", "Ativo"),
    ("expirado", "Expirado"),
    ("cancelado", "Cancelado"),
    ("consumido", "Consumido"),
]
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='tickets') # usuário que possui o ticket
    tipo = models.ForeignKey(TipoTicket, on_delete=models.PROTECT, related_name='tickets') # tipo do ticket
    data_compra = models.DateTimeField(auto_now_add=True) # data de compra do ticket
    data_validade = models.DateTimeField(editable=False)
    status = models.CharField(max_length=10, choices=STATUS_TICKET, default="ativo") # status do ticket)

    def __str__(self):
        return f"{self.tipo.nome} - {self.usuario.nome}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # salva primeiro para ter data_compra

        if not self.data_validade:
            self.data_validade = self.data_compra + timedelta(days=self.tipo.duracao_dias)
            super().save(update_fields=['data_validade'])

class Transporte(models.Model):
    TIPOS_TRANSPORTE = [
    ("parada", "Parada"),
    ("onibus", "Ônibus"),
    ("trem", "Trem"),
]
    identificacao = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS_TRANSPORTE)
    nome = models.CharField(max_length=150)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    empresa = models.ForeignKey(EmpresaTransporte, on_delete=models.PROTECT, related_name='transportes')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.identificacao} - {self.nome}"

class Validador(models.Model):
    TIPOS_VALIDADOR = [
    ("cartao", "Cartão"),
    ("celular", "Celular"),
]
    codigo = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS_VALIDADOR)
    transporte = models.ForeignKey(Transporte, on_delete=models.PROTECT, related_name='validadores',null=True,blank=True)
    data_instalacao = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo

class Validacao(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT, related_name='validacoes')
    validador = models.ForeignKey(Validador, on_delete=models.PROTECT, related_name='validacoes')
    transporte = models.ForeignKey(Transporte, on_delete=models.PROTECT, related_name='validacoes')

    data_hora = models.DateTimeField(auto_now_add=True)

    dentro_janela_integracao = models.BooleanField(default=False)
    valor_debitado = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Validação {self.ticket} em {self.transporte}"