from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions,generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Seller, ShippingMethod, PaymentGateway
from .serializers import SellerSerializer, ShippingMethodSerializer, PaymentGatewaySerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser


class SellerRegister(APIView):
    permission_classes = [permissions.IsAuthenticated]  

    def post(self, request):
        serializer = SellerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SellerLogin(APIView):
    def post(self, request):
        shop_name = request.data.get('shop_name')
        phone = request.data.get('phone')

        try:
            seller = Seller.objects.get(shop_name=shop_name, phone=phone)
            user = seller.user
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"detail": "نام غرفه یا شماره تلفن اشتباه است."}, status=status.HTTP_401_UNAUTHORIZED)

    
class SellerSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return seller
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        logo = serializer.validated_data.get('logo')
        if logo:
            instance.logo.save(logo.name, logo, save=False)
        
        self.perform_update(serializer)
        
        return Response(serializer.data)



class ShippingMethodCreateView(generics.CreateAPIView):
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)

class ShippingMethodDeleteView(generics.DestroyAPIView):
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return ShippingMethod.objects.filter(seller=seller)

class PaymentGatewayCreateView(generics.CreateAPIView):
    serializer_class = PaymentGatewaySerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        seller = get_object_or_404(Seller, user=self.request.user)
        serializer.save(seller=seller)

class PaymentGatewayDeleteView(generics.DestroyAPIView):
    serializer_class = PaymentGatewaySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return PaymentGateway.objects.filter(seller=seller)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Check_shop(request):
    try:
        seller = Seller.objects.get(user=request.user)
        return Response({'has_shop': True})
    except Seller.DoesNotExist:
        return Response({'has_shop': False})