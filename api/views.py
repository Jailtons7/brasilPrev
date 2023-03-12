from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter

from api.serializers import (
    ClienteSerializer,
    ProdutoSerializer,
    ContratacaoPlanoSerializer,
    AporteExtraSerializer,
    ResgateSerializer,
)
from api.models import (
    Cliente,
    Produto,
    ContratacaoPlano,
    AporteExtra,
    Resgate,
)


class ClientesViewSet(ModelViewSet):
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()


class ProdutosViewSet(ModelViewSet):
    serializer_class = ProdutoSerializer
    queryset = Produto.objects.all()


class ContratacaoPlanoViewSet(ModelViewSet):
    serializer_class = ContratacaoPlanoSerializer
    queryset = ContratacaoPlano.objects.all()

    @extend_schema(description='Para contratar um plano é preciso respeitar a data de expiração '
                               'do produto, o aporte mínimo inial além das datas mínima e máxima')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class AportesExtrasViewSet(ModelViewSet):
    serializer_class = AporteExtraSerializer
    queryset = AporteExtra.objects.all()

    @extend_schema(description='O valor mínimo para aporte extra deve ser igual ao valor definido no plano')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ResgatesViewSet(ModelViewSet):
    serializer_class = ResgateSerializer
    queryset = Resgate.objects.all()

    @extend_schema(description='O valor máximo para o resgate deve ser igual ao valor de aporte do plano')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
