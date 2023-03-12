from rest_framework import serializers

from api.models import (
    Cliente,
    Produto,
    ContratacaoPlano,
    AporteExtra,
    Resgate,
)


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'


class ContratacaoPlanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratacaoPlano
        fields = '__all__'


class AporteExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = AporteExtra
        fields = '__all__'


class ResgateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resgate
        fields = '__all__'
