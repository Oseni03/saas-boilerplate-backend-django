from rest_framework import generics, permissions, status

from .models import Thirdparty, Integrations
from .serializers import ThirdpartySerializer, IntegrationSerializer

# Create your views here.
class ListThirdparty(generics.ListAPIView):
    queryset = Thirdparty.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ThirdpartySerializer


class CreateIntegration(generics.CreateAPIView):
    model = Integrations
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IntegrationSerializer