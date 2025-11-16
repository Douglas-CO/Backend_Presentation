from rest_framework import generics
from .models import Pais
from .serializers import PaisSerializer
from backend_simple.permissions import RequirePermission

class PaisPermission(RequirePermission):
    permission_map = {
        "GET": "administration.view_pais",
        "POST": "administration.add_pais",
        "PATCH": "administration.change_pais",
    }

# LIST
class PaisListView(generics.ListAPIView):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [PaisPermission]

# LIST + POST
class PaisListCreateView(generics.ListCreateAPIView):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [PaisPermission]


# GET(id) + PATCH
class PaisDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [PaisPermission]
    http_method_names = ["get", "patch", "post"]
