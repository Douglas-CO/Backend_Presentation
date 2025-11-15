from rest_framework import generics, mixins
from .models import Pais
from .serializers import PaisSerializer


# LIST + POST
class PaisListCreateView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# GET(id) + PATCH
class PaisDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,   # PATCH y PUT, pero vamos a bloquear PUT
    generics.GenericAPIView
):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # Permitimos solo PATCH
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

   
