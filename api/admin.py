from django.contrib import admin

from api.models import Cliente, Produto, ContratacaoPlano, AporteExtra, Resgate


@admin.register(Cliente)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'nome', 'email', 'dataDeNascimento', 'sexo', 'rendaMensal',)
    list_filter = ('sexo',)
    search_fields = ('cpf', 'nome', 'email',)
    list_per_page = 50


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'susep', 'expiracaoDeVenda', 'valorMinimoAporteInicial', 'valorMinimoAporteExtra',
        'idadeDeEntrada', 'idadeDeSaida', 'carenciaInicialDeResgate', 'carenciaEntreResgates'
    )
    search_fields = ('nome', 'susepe',)
    list_per_page = 50


@admin.register(ContratacaoPlano)
class ContratacaoPlanoAdmin(admin.ModelAdmin):
    list_display = ('idCliente', 'idProduto', 'aporte', 'dataDaContratacao',)
    list_per_page = 50


@admin.register(AporteExtra)
class AporteExtraAdmin(admin.ModelAdmin):
    list_display = ('idCliente', 'idPlano', 'valorAporte',)
    list_per_page = 50


@admin.register(Resgate)
class ResgateAdmin(admin.ModelAdmin):
    list_display = ('idPlano', 'valorResgate',)
    list_per_page = 50
