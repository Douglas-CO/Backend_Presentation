from rest_framework import generics, mixins
from .models import Provincia
from .serializers import ProvinciaSerializer


# LIST + POST
class ProvinciaListCreateView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# GET(id) + PATCH
class ProvinciaDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,   # PATCH y PUT, pero vamos a bloquear PUT
    generics.GenericAPIView
):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # Permitimos solo PATCH
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

   
