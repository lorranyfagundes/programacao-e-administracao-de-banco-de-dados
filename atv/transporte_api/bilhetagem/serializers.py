from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import (
    Municipio, EmpresaTransporte, Usuario, 
    TipoTicket, Ticket, Transporte, Validador, Validacao
)

# 8. MunicipioSerializer
class MunicipioSerializer(serializers.ModelSerializer):  #serializer para o modelo Municipio
    class Meta:
        model = Municipio
        fields = '__all__'

# 9. EmpresaTransporteSerializer
class EmpresaTransporteSerializer(serializers.ModelSerializer):
    municipio_nome = serializers.CharField(source='municipio.nome', read_only=True)
    class Meta:
        model = EmpresaTransporte
        fields = ['id', 'nome_fantasia', 'cnpj', 'municipio', 'municipio_nome']

# 10. UsuarioSerializer
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['saldo'] # Regra 10: saldo como read_only

# 11. TipoTicketSerializer
class TipoTicketSerializer(serializers.ModelSerializer):
    nome_display = serializers.CharField(source='get_nome_display', read_only=True)

    class Meta:
        model = TipoTicket
        fields = [
            'id', 
            'nome', 
            'nome_display',
            'valor', 
            'duracao_dias', 
            'ativo'
        ]

# 12. TicketSerializer
class TicketSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    tipo_nome = serializers.CharField(source='tipo.nome_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'usuario', 'usuario_nome', 'tipo', 'tipo_nome', 
            'data_compra', 'data_validade', 'status', 'status_display'
        ]
        read_only_fields = ['data_validade']

# 13. TransporteSerializer
class TransporteSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    empresa_nome = serializers.CharField(source='empresa.nome_fantasia', read_only=True)

    class Meta:
        model = Transporte
        fields = '__all__'

# 14. ValidadorSerializer
class ValidadorSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    transporte_identificacao = serializers.CharField(
        source='transporte.identificacao', 
        read_only=True, 
        allow_null=True
    )

    class Meta:
        model = Validador
        fields = '__all__'

class ValidacaoSerializer(serializers.ModelSerializer):
    # Campos calculados para exibição
    usuario_nome = serializers.CharField(source='ticket.usuario.nome', read_only=True)
    mensagem = serializers.SerializerMethodField()

    class Meta:
        model = Validacao
        fields = '__all__'
        read_only_fields = ['valor_debitado', 'dentro_janela_integracao']

    def get_mensagem(self, obj):
        return 'Integração tarifária' if obj.dentro_janela_integracao else 'Nova passagem'

    # REGRA: Ticket deve estar ativo (Retorna HTTP 400 se falhar)
    def validate(self, data):
        ticket = data['ticket']
        if ticket.status != 'ativo':
            raise serializers.ValidationError({"ticket": "Este ticket não está ativo e não pode ser validado."})
        
        # Opcional: Checar se a data de validade do ticket expirou
        if ticket.data_validade < timezone.now().date():
             raise serializers.ValidationError({"ticket": "Este ticket está expirado."})
             
        return data

    def create(self, validated_data):
        ticket = validated_data['ticket']
        usuario = ticket.usuario
        agora = timezone.now()
        
        # 1. Verificar Janela de Integração (60 min padrão)
        janela = ticket.tipo.janela_integracao_minutos or 60
        limite_tempo = agora - timedelta(minutes=janela)

        foi_integracao = Validacao.objects.filter(
            ticket__usuario=usuario,
            data_hora__gte=limite_tempo
        ).exists()

        # 2. Aplicar lógica de débito ou integração
        if foi_integracao:
            validated_data['dentro_janela_integracao'] = True
            validated_data['valor_debitado'] = 0
        else:
            valor_passagem = ticket.tipo.preco
            if usuario.saldo < valor_passagem:
                raise serializers.ValidationError("Saldo insuficiente.")
            
            usuario.saldo -= valor_passagem
            usuario.save()
            
            validated_data['dentro_janela_integracao'] = False
            validated_data['valor_debitado'] = valor_passagem

        # 3. Regra do Ticket Avulso (Consumir após a primeira integração/uso)
        # Se for avulso e não for integração, ou se você quiser que ele morra 
        # após o tempo de integração da primeira vez:
        if ticket.tipo.categoria == 'avulso' and not foi_integracao:
            # Aqui depende da interpretação: se o avulso só pode ser usado uma vez 
            # (com integração), marcamos como consumido após o uso inicial.
            ticket.status = 'consumido'
            ticket.save()

        return super().create(validated_data)