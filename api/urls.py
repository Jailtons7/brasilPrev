from rest_framework import routers

from api.views import (
    ClientesViewSet,
    ProdutosViewSet,
    ContratacaoPlanoViewSet,
    AportesExtrasViewSet,
    ResgatesViewSet,
)

router = routers.DefaultRouter()
router.register('clientes', ClientesViewSet)
router.register('produtos', ProdutosViewSet)
router.register('contratacoes', ContratacaoPlanoViewSet)
router.register('aportes-extras', AportesExtrasViewSet)
router.register('resgates', ResgatesViewSet)

urlpatterns = router.urls
