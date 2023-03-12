import json
from datetime import date, timedelta

from rest_framework import status
from django.test import Client as App  # Para evitar confusões com o Cliente
from django.urls import reverse

from api.models import Cliente, ContratacaoPlano
from api.tests.tests_unit import BaseTestCase
from api.error_messages import (
    PRAZO_EXPIRADO, APORTE_MINIMO, IDADE_INVALIDA, APORTE_EXTRA_MINIMO,
    APORTE_INSUFICIENTE, CARENCIA_INICIAL, CARENCIA_ENTRE_RESGATES,
)

app = App()


class ClienteIntegrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.novo_cliente_valido = {
            'cpf': '98765432198', 'nome': 'Maria Henriques', 'email': 'mhrq@gmail.com',
            'dataDeNascimento': str(self.data_nascimento), 'sexo': 'F', 'rendaMensal': 2500.00
        }

    def test_add_cliente(self):
        response = app.post(
            reverse('cliente-list'),
            data=json.dumps(self.novo_cliente_valido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = app.post(
            reverse('cliente-list'),
            data=json.dumps(self.novo_cliente_valido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProdutoIntegrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.novo_produto_valido = {
            'nome': "Produto 2", 'susep': '75414.915840/2018-13',
            'expiracaoDeVenda': str(self.expiracao_venda), 'valorMinimoAporteInicial': self.valor_minimo_aporte_inicial,
            'valorMinimoAporteExtra': self.valor_minimo_aporte_extra, 'idadeDeEntrada': 18,
            'idadeDeSaida': 65, 'carenciaInicialDeResgate': 90, 'carenciaEntreResgates': 30
        }

    def test_add_produto(self):
        response = app.post(
            reverse('produto-list'),
            data=json.dumps(self.novo_produto_valido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ContratacaoPlanoIntegrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.data_menor_idade = date(2021, 10, 22)
        self.data_maior_idade = date(1940, 10, 22)
        self.cliente_menor = Cliente.objects.create(
            cpf='98765432109', nome='Maria Henriques', email='mhrq@gmail.com',
            dataDeNascimento=self.data_menor_idade, sexo='F', rendaMensal=2500.00
        )
        self.cliente_maior = Cliente.objects.create(
            cpf='91111111111', nome='Antônio Henriques', email='ahrq@gmail.com',
            dataDeNascimento=self.data_maior_idade, sexo='F', rendaMensal=2500.00
        )
        self.nova_contratacao_valida = {
            'idCliente': str(self.cliente.id), 'idProduto': str(self.produto.id),
            'aporte': self.valor_minimo_aporte_inicial, 'dataDaContratacao': str(self.data_contratacao)
        }
        self.nova_contratacao_aporte_invalido = {
            'idCliente': str(self.cliente.id), 'idProduto': str(self.produto.id),
            'aporte': self.valor_minimo_aporte_inicial - 0.1, 'dataDaContratacao': str(self.data_contratacao)
        }
        data_contratacao_expirada = self.expiracao_venda + timedelta(days=1)
        self.nova_contratacao_data_expirada = {
            'idCliente': str(self.cliente.id), 'idProduto': str(self.produto.id),
            'aporte': self.valor_minimo_aporte_inicial, 'dataDaContratacao': str(data_contratacao_expirada)
        }
        self.nova_contratacao_menor_idade = {
            'idCliente': str(self.cliente_menor.id), 'idProduto': str(self.produto.id),
            'aporte': self.valor_minimo_aporte_inicial, 'dataDaContratacao': str(self.data_contratacao)
        }
        self.nova_contratacao_maior_idade = {
            'idCliente': str(self.cliente_maior.id), 'idProduto': str(self.produto.id),
            'aporte': self.valor_minimo_aporte_inicial, 'dataDaContratacao': str(self.data_contratacao)
        }

    def test_add_contratacao(self):
        response = app.post(
            reverse('contratacaoplano-list'),
            data=json.dumps(self.nova_contratacao_valida),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_contratacao_aporte_invalido(self):
        response = app.post(
            reverse('contratacaoplano-list'),
            data=json.dumps(self.nova_contratacao_aporte_invalido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            APORTE_MINIMO.format(self.valor_minimo_aporte_inicial)
        )

    def test_add_contratacao_data_invalida(self):
        response = app.post(
            reverse('contratacaoplano-list'),
            data=json.dumps(self.nova_contratacao_data_expirada),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], PRAZO_EXPIRADO)

    def test_add_contratacao_menor_idade(self):
        response = app.post(
            reverse('contratacaoplano-list'),
            data=json.dumps(self.nova_contratacao_menor_idade),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            IDADE_INVALIDA.format(
                self.produto.idadeDeEntrada, self.produto.idadeDeSaida
            )
        )

    def test_add_contratacao_maior_idade(self):
        response = app.post(
            reverse('contratacaoplano-list'),
            data=json.dumps(self.nova_contratacao_maior_idade),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            IDADE_INVALIDA.format(
                self.produto.idadeDeEntrada, self.produto.idadeDeSaida
            )
        )


class AporteExtraIntegrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.aporte_extra_valido = {
            'idCliente': str(self.cliente.id), 'idPlano': str(self.contratacao.id),
            'valorAporte': self.valor_minimo_aporte_extra
        }
        self.aporte_extra_invalido = {
            'idCliente': str(self.cliente.id), 'idPlano': str(self.contratacao.id),
            'valorAporte': self.valor_minimo_aporte_extra - 0.1
        }

    def test_aporte_extra_minimo(self):
        response = app.post(
            reverse('aporteextra-list'),
            data=json.dumps(self.aporte_extra_valido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_aporte_extra_minimo_invalido(self):
        response = app.post(
            reverse('aporteextra-list'),
            data=json.dumps(self.aporte_extra_invalido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], APORTE_EXTRA_MINIMO)


class ResgateIntegrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        today = date.today()
        self.valor_resgate = self.contratacao.aporte
        self.contratacao_carencia_invalida = ContratacaoPlano.objects.create(
            idCliente=self.cliente,
            idProduto=self.produto,
            aporte=self.valor_minimo_aporte_inicial,
            dataDaContratacao=today
        )
        self.resgate_valido = {
            'idPlano': str(self.contratacao.id),
            'valorResgate': self.valor_resgate
        }
        self.resgate_valor_invalido = {
            'idPlano': str(self.contratacao.id),
            'valorResgate': self.valor_resgate + 0.1
        }
        self.resgate_carencia_inicial_invalido = {
            'idPlano': str(self.contratacao_carencia_invalida.id),
            'valorResgate': self.valor_resgate
        }

    def test_resgate_valido(self):
        response = app.post(
            reverse('resgate-list'),
            data=json.dumps(self.resgate_valido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_resgate_valor_invalido(self):
        response = app.post(
            reverse('resgate-list'),
            data=json.dumps(self.resgate_valor_invalido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            APORTE_INSUFICIENTE.format(self.contratacao.aporte)
        )

    def test_resgate_carencia_inicial_invalida(self):
        response = app.post(
            reverse('resgate-list'),
            data=json.dumps(self.resgate_carencia_inicial_invalido),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            CARENCIA_INICIAL.format(self.produto.carenciaInicialDeResgate)
        )

    def test_resgate_carencia_entre_aportes(self):
        response1 = app.post(
            reverse('resgate-list'),
            data=json.dumps(self.resgate_valido),
            content_type='application/json'
        )
        response2 = app.post(
            reverse('resgate-list'),
            data=json.dumps(self.resgate_valido),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response2.data['error'],
            CARENCIA_ENTRE_RESGATES.format(self.produto.carenciaEntreResgates)
        )
