from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from api.models import Produto, Cliente, ContratacaoPlano, AporteExtra, Resgate


class BaseTestCase(TestCase):
    def setUp(self):
        self.data_nascimento = date(1991, 10, 22)
        self.expiracao_venda = date(2023, 2, 15)
        self.data_contratacao = date(2022, 9, 15)
        self.valor_minimo_aporte_inicial = 2500.00
        self.valor_minimo_aporte_extra = 200.00
        self.cliente = Cliente.objects.create(
            cpf='12345678909', nome='José Henriques', email='jhrq@gmail.com',
            dataDeNascimento=self.data_nascimento, sexo='M', rendaMensal=3500.00
        )
        self.produto = Produto.objects.create(
            nome="Produto 1", susep='15414.900840/2018-17',
            expiracaoDeVenda=self.expiracao_venda, valorMinimoAporteInicial=self.valor_minimo_aporte_inicial,
            valorMinimoAporteExtra=self.valor_minimo_aporte_extra, idadeDeEntrada=18,
            idadeDeSaida=65, carenciaInicialDeResgate=90, carenciaEntreResgates=30
        )
        self.contratacao = ContratacaoPlano.objects.create(
            idCliente=self.cliente,
            idProduto=self.produto,
            aporte=self.valor_minimo_aporte_inicial,
            dataDaContratacao=self.data_contratacao
        )


class ClienteTestCase(BaseTestCase):
    def test_idade_cliente(self):
        data = date(2022, 10, 22)
        idade = self.cliente.get_idade(data=data)
        self.assertEqual(idade, 31)


class ProdutoTestCase(BaseTestCase):
    def test_venda_expirada(self):
        data = self.expiracao_venda
        self.assertFalse(self.produto.venda_expirada(data_contratacao=data))
        data += timedelta(days=1)
        self.assertTrue(self.produto.venda_expirada(data_contratacao=data))

    def test_aporte_insuficiente(self):
        aporte = self.valor_minimo_aporte_inicial
        self.assertFalse(self.produto.aporte_insuficente(valor_aporte=aporte))
        aporte -= 0.1
        self.assertTrue(self.produto.aporte_insuficente(valor_aporte=aporte))

    def test_aporte_extra_insuficiente(self):
        aporte = self.valor_minimo_aporte_extra
        self.assertFalse(self.produto.aporte_extra_insuficiente(valor_aporte_extra=aporte))
        aporte -= 0.1
        self.assertTrue(self.produto.aporte_extra_insuficiente(valor_aporte_extra=aporte))

    def test_idade_insuficiente(self):
        data = date(2000, 10, 22)
        idade = self.cliente.get_idade(data=data)
        self.assertTrue(self.produto.idade_insuficiente(idade_cliente=idade))

    def test_idade_superior(self):
        data = date(2056, 10, 22)
        idade = self.cliente.get_idade(data=data)
        self.assertFalse(self.produto.idade_superior(idade_cliente=idade))

        data = date(2057, 10, 22)
        idade = self.cliente.get_idade(data=data)
        self.assertTrue(self.produto.idade_superior(idade_cliente=idade))


class ContratacaoPlanoTestCase(BaseTestCase):
    def test_data_expiracao_produto(self):
        """
        Dada uma data de contratação,
        Quando essa data for maior que a data de expiração do plano,
        Então verifique se lança um erro de validação
        """
        data_contratacao = date(2023, 2, 16)
        with self.assertRaises(ValidationError):
            ContratacaoPlano.objects.create(
                idCliente=self.cliente,
                idProduto=self.produto,
                aporte=3000.00,
                dataDaContratacao=data_contratacao
            )

    def test_aporte_inicial_produto(self):
        """
        Dado um aporte inicial,
        Quando esse aporte for menor que o valor mínimo do aporte inicial do plano,
        Então verifique se lança um erro de validação
        """
        aporte = 2499.99
        with self.assertRaises(ValidationError):
            ContratacaoPlano.objects.create(
                idCliente=self.cliente,
                idProduto=self.produto,
                aporte=aporte,
                dataDaContratacao=date(2023, 2, 10)
            )

    def test_idade_entrada_produto(self):
        """
        Dado uma idade de entrada do cliente,
        Quando essa idade for menor que idade mínima do plano,
        Então verifique se lança um erro de validação
        """
        idade = self.produto.idadeDeEntrada - 1
        data_contratacao = date(2023, 2, 10)
        data_nascimento = data_contratacao - timedelta(days=365 * idade)
        self.cliente.dataDeNascimento = data_nascimento
        with self.assertRaises(ValidationError):
            ContratacaoPlano.objects.create(
                idCliente=self.cliente,
                idProduto=self.produto,
                aporte=3000.00,
                dataDaContratacao=data_contratacao
            )

    def test_idade_saida_produto(self):
        """
        Dado uma idade de entrada do cliente,
        Quando essa idade for menor que idade mínima do plano,
        Então verifique se lança um erro de validação
        """
        idade = self.produto.idadeDeSaida + 1
        data_contratacao = date(2023, 2, 10)
        data_nascimento = data_contratacao - timedelta(days=365 * idade)
        self.cliente.dataDeNascimento = data_nascimento
        with self.assertRaises(ValidationError):
            ContratacaoPlano.objects.create(
                idCliente=self.cliente,
                idProduto=self.produto,
                aporte=self.valor_minimo_aporte_inicial,
                dataDaContratacao=data_contratacao
            )


class AporteExtraTestCase(BaseTestCase):
    def test_aporte_extra(self):
        """
        Dado um aporte extra,
        Quando ele for menor que o valor definido no plano,
        Então verifique se lança um erro de validação
        """
        aporte_extra = self.valor_minimo_aporte_extra - 0.1
        with self.assertRaises(ValidationError):
            AporteExtra.objects.create(
                idCliente=self.cliente,
                idPlano=self.contratacao,
                valorAporte=aporte_extra
            )


class ResgateTestCase(BaseTestCase):
    def test_resgate(self):
        """
        Dado um resgate,
        Quando ele for maior que o aporte do plano,
        Então verifique se lança um erro de validação
        """
        valor = self.valor_minimo_aporte_inicial + 0.1
        with self.assertRaises(ValidationError):
            Resgate.objects.create(
                idPlano=self.contratacao,
                valorResgate=valor
            )

    def test_carencia_resgate(self):
        """
        Dado um resgate,
        Quando ele ocorrer em um período menor que a carenciaInicialDeResgate,
        Então verifique se lança um erro de validação
        """
        data_contratacao = date(2023, 1, 1)
        self.contratacao.dataDaContratacao = data_contratacao
        valor = self.valor_minimo_aporte_inicial
        with self.assertRaises(ValidationError):
            Resgate.objects.create(
                idPlano=self.contratacao,
                valorResgate=valor
            )

    def test_carencia_entre_resgates(self):
        """
        Dado dois resgates,
        Quando esses dois resgates forem menores que a carenciaEntreResgates,
        Então verifique se lança um erro de validação
        """
        valor = self.valor_minimo_aporte_inicial
        with self.assertRaises(ValidationError):
            Resgate.objects.create(
                idPlano=self.contratacao,
                valorResgate=valor / 4
            )
            Resgate.objects.create(
                idPlano=self.contratacao,
                valorResgate=valor / 4
            )
