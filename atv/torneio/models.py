from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# models: Grupo, Selecao, Tecnico, Jogador, Jogo, EventoJogo

class Tecnico(models.Model):
    nome = models.CharField(max_length=150)
    nacionalidade = models.CharField(max_length=100)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome

class Grupo(models.Model):
    nome = models.CharField(max_length=1, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"Grupo {self.nome}"

class Selecao(models.Model):
    CONFEDERACAO_CHOICES = [
        ('UEFA', 'UEFA'), ('CONMEBOL', 'CONMEBOL'), ('CONCACAF', 'CONCACAF'),
        ('AFC', 'AFC'), ('CAF', 'CAF'), ('OFC', 'OFC'),
    ]

    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=3, unique=True)
    confederacao = models.CharField(max_length=10, choices=CONFEDERACAO_CHOICES)
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT, related_name='selecoes')
    tecnico = models.OneToOneField(Tecnico, on_delete=models.SET_NULL, null=True, related_name='selecao')
    escudo_url = models.URLField(blank=True)

    def __str__(self):
        return self.nome

class Jogador(models.Model):
    POSICAO_CHOICES = [
        ('goleiro', 'Goleiro'), ('zagueiro', 'Zagueiro'), ('lateral', 'Lateral'),
        ('volante', 'Volante'), ('meia', 'Meia'), ('atacante', 'Atacante'),
    ]
    
    nome = models.CharField(max_length=150)
    nome_guerra = models.CharField(max_length=50)
    selecao = models.ForeignKey(Selecao, on_delete=models.PROTECT, related_name='jogadores')
    posicao = models.CharField(max_length=20, choices=POSICAO_CHOICES) 
    numero_camisa = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(26)]) # Entre 1 e 26
    data_nascimento = models.DateField()
    suspenso = models.BooleanField(default=False)

    def __str__(self):
        return self.nome_guerra

class Jogo(models.Model):
    FASE_CHOICES = [
        ('grupos', 'Grupos'), ('fase32', 'Fase de 32'), ('oitavas', 'Oitavas'),
        ('quartas', 'Quartas'), ('semifinal', 'Semifinal'), ('final', 'Final'),
    ]
    STATUS_CHOICES = [
        ('agendado', 'Agendado'), ('em_andamento', 'Em Andamento'),
        ('encerrado', 'Encerrado'), ('cancelado', 'Cancelado'),
    ]

    selecao_mandante = models.ForeignKey('Selecao', related_name='jogos_mandante', on_delete=models.PROTECT)
    selecao_visitante = models.ForeignKey('Selecao', related_name='jogos_visitante', on_delete=models.PROTECT)
    fase = models.CharField(max_length=20, choices=FASE_CHOICES) 
    grupo = models.ForeignKey('Grupo', on_delete=models.PROTECT, null=True, blank=True)
    data_hora = models.DateTimeField()
    estadio = models.CharField(max_length=150, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    gols_mandante = models.PositiveSmallIntegerField(default=0)
    gols_visitante = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado')

class EventoJogo(models.Model):
    TIPO_CHOICES = [
        ('gol', 'Gol'), ('cartao_amarelo', 'Cartão Amarelo'),
        ('cartao_vermelho', 'Cartão Vermelho'), ('gol_contra', 'Gol Contra'),
    ]

    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='eventos')
    jogador = models.ForeignKey('Jogador', on_delete=models.PROTECT, related_name='eventos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    minuto = models.PositiveSmallIntegerField()
    acrescimo = models.BooleanField(default=False)