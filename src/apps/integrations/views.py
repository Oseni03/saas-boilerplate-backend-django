from rest_framework import generics, permissions

from .models import Thirdparty, Integrations
from .serializers import ThirdpartySerializer, IntegrationSerializer

# Create your views here.
class ThirdpartyListView(generics.ListAPIView):
    queryset = Thirdparty.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ThirdpartySerializer


class IntegrationView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IntegrationSerializer

    def get_queryset(self):
        return Integrations.objects.filter(users=self.request.user)