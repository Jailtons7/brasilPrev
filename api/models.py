import uuid
from typing import Union
from datetime import date
from decimal import Decimal

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models

from api.error_messages import (
    PRAZO_EXPIRADO, APORTE_MINIMO, IDADE_INVALIDA, APORTE_EXTRA_MINIMO,
    APORTE_INSUFICIENTE, CARENCIA_INICIAL, CARENCIA_ENTRE_RESGATES,
)


class Cliente(models.Model):
    class OpcoesSexo(models.TextChoices):
        M = ('M', 'Masculino')
        F = ('F', 'Feminino')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=11, db_index=True, unique=True, help_text='Apenas números')
    nome = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        validators=[validators.EmailValidator()],
        error_messages={
            'unique': "Esse e-mail já existe.",
        }
    )
    dataDeNascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=OpcoesSexo.choices)
    rendaMensal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.nome}'

    def get_idade(self, data: date = date.today()) -> int:
        """ Retorna a idade do cliente na data passada """
        return int(round((data - self.dataDeNascimento).days / 365.242189, 1))


class Produto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=150)
    susep = models.CharField(max_length=20)
    expiracaoDeVenda = models.DateField(validators=[])
    valorMinimoAporteInicial = models.DecimalField(max_digits=12, decimal_places=2)
    valorMinimoAporteExtra = models.DecimalField(max_digits=12, decimal_places=2)
    idadeDeEntrada = models.SmallIntegerField()
    idadeDeSaida = models.SmallIntegerField()
    carenciaInicialDeResgate = models.SmallIntegerField()
    carenciaEntreResgates = models.SmallIntegerField()
    dataUltimoResgate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome}'

    def venda_expirada(self, data_contratacao: date = date.today()) -> bool:
        return data_contratacao > self.expiracaoDeVenda

    def aporte_insuficente(self, valor_aporte: Union[float | Decimal] = 0.0) -> bool:
        return valor_aporte < self.valorMinimoAporteInicial

    def aporte_extra_insuficiente(self, valor_aporte_extra: Union[float | Decimal] = 0.0) -> bool:
        return valor_aporte_extra < self.valorMinimoAporteExtra

    def idade_insuficiente(self, idade_cliente: int) -> bool:
        return idade_cliente < self.idadeDeEntrada

    def idade_superior(self, idade_cliente: int) -> bool:
        return idade_cliente > self.idadeDeSaida


class ContratacaoPlano(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idCliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, db_column='idCliente')
    idProduto = models.ForeignKey('Produto', on_delete=models.PROTECT, db_column='idProduto')
    aporte = models.DecimalField(max_digits=12, decimal_places=2)
    dataDaContratacao = models.DateField()

    def __str__(self):
        return f'{self.id} {self.dataDaContratacao}'

    def resgate_negado(self, valor):
        return self.aporte < valor

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        produto = self.idProduto
        cliente = self.idCliente
        if produto.venda_expirada(data_contratacao=self.dataDaContratacao):
            raise ValidationError(PRAZO_EXPIRADO)
        if produto.aporte_insuficente(valor_aporte=self.aporte):
            raise ValidationError(APORTE_MINIMO.format(produto.valorMinimoAporteInicial))
        idade_cliente = cliente.get_idade(self.dataDaContratacao)
        idades_invalidas = [
            produto.idade_insuficiente(idade_cliente=idade_cliente),
            produto.idade_superior(idade_cliente=idade_cliente)
        ]
        if any(idades_invalidas):
            raise ValidationError(IDADE_INVALIDA.format(
                produto.idadeDeEntrada, produto.idadeDeSaida
            ))

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)


class AporteExtra(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idCliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, db_column='idCliente')
    idPlano = models.ForeignKey('ContratacaoPlano', on_delete=models.PROTECT, db_column='idPlano')
    valorAporte = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.id} {self.valorAporte}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        plano = self.idPlano
        produto = plano.idProduto
        if produto.aporte_extra_insuficiente(self.valorAporte):
            raise ValidationError(APORTE_EXTRA_MINIMO.format(produto.valorMinimoAporteExtra))
        # incremento no aporte
        plano.aporte += self.valorAporte
        plano.save()
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)


class Resgate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idPlano = models.ForeignKey('ContratacaoPlano', on_delete=models.PROTECT, db_column='idPlano')
    valorResgate = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.id} {self.valorResgate}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        plano = self.idPlano
        produto = plano.idProduto
        data_resgate = date.today()
        if plano.resgate_negado(valor=self.valorResgate):
            raise ValidationError(APORTE_INSUFICIENTE.format(plano.aporte))
        if (data_resgate - plano.dataDaContratacao).days < produto.carenciaInicialDeResgate:
            raise ValidationError(CARENCIA_INICIAL.format(produto.carenciaInicialDeResgate))
        if produto.dataUltimoResgate:
            if (data_resgate - produto.dataUltimoResgate).days < produto.carenciaEntreResgates:
                raise ValidationError(CARENCIA_ENTRE_RESGATES.format(produto.carenciaEntreResgates))

        produto.dataUltimoResgate = data_resgate
        produto.save()
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)
