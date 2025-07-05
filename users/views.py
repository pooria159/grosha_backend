from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, DiscountSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, permissions
from .models import Ticket,Discount, Address, BankCard, CustomUser
from .serializers import TicketSerializer, TicketReplySerializer, AddressSerializer, BankCardSerializer,UserSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from .models import Discount
from order.models import Order
from .permissions import IsSellerOrAdmin

class TicketPagination(PageNumberPagination):
    page_size = 10 

class TicketListCreateView(generics.ListCreateAPIView):
    pagination_class = TicketPagination
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Ticket.objects.none()
            
        if self.request.user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("کاربر احراز هویت نشده است")
            
        serializer.save(user=self.request.user)


class TicketReplyCreateView(generics.CreateAPIView):
    serializer_class = TicketReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        ticket = get_object_or_404(Ticket, id=self.kwargs['ticket_id'])
        serializer.save(
            ticket=ticket,
            user=self.request.user,
            is_staff_reply=self.request.user.is_staff 
        )


class AdminTicketUpdateView(generics.UpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Ticket.objects.all()
    
    def perform_update(self, serializer):
        if 'status' not in serializer.validated_data:
            serializer.validated_data['status'] = self.get_object().status
        serializer.save()
        
        
class TicketRetrieveView(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=self.request.user)

class BankCardListCreateView(generics.ListCreateAPIView):
    serializer_class = BankCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BankCardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BankCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)
        
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if not Address.objects.filter(user=self.request.user).exists():
            serializer.save(user=self.request.user, is_default=True)
        else:
            serializer.save(user=self.request.user)

class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

class SetDefaultAddressView(generics.UpdateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(is_default=True)
        

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "phone": request.user.phone,
            "date_joined": request.user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
        })

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterUser(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            
            if CustomUser.objects.filter(email=email).exists():
                return Response(
                    {'email': ['این ایمیل قبلاً ثبت شده است.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if CustomUser.objects.filter(phone=phone).exists():
                return Response(
                    {'phone': ['این شماره تلفن قبلاً ثبت شده است.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = self.perform_create(serializer)
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)    
         
            
            return Response({
                'user': serializer.data,
                'user_id': user.id,
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def perform_create(self, serializer):
        return serializer.save()


class CheckDuplicatesView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        
        response_data = {
            'email_exists': False,
            'phone_exists': False,
            'errors': {}
        }
        
        if email:
            if CustomUser.objects.filter(email=email).exists():
                response_data['email_exists'] = True
                response_data['errors']['email'] = ['این ایمیل قبلاً ثبت شده است.']
        
        if phone:
            if CustomUser.objects.filter(phone=phone).exists():
                response_data['phone_exists'] = True
                response_data['errors']['phone'] = ['این شماره تلفن قبلاً ثبت شده است.']
        
        return Response(response_data, status=status.HTTP_200_OK)

class DiscountViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, IsSellerOrAdmin]
    filterset_fields = ['is_active', 'for_first_purchase', 'seller']
    search_fields = ['title', 'code', 'description']
    
    def get_queryset(self):
        queryset = Discount.objects.all()
        
        if not self.request.user.is_staff:
            if hasattr(self.request.user, 'seller'):
                queryset = queryset.filter(seller=self.request.user.seller)
            else:
                queryset = queryset.none()
                
        if self.action == 'list' and not self.request.user.is_staff:
            queryset = queryset.filter(
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'seller'):
            serializer.save(seller=self.request.user.seller)
        else:
            serializer.save()
            

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_discount(request):
    code = request.data.get('code')
    seller_id = request.data.get('seller_id') or request.data.get('store_id')
    order_total = request.data.get('order_total', 0) 
    
    if not code:
        return Response(
            {'error': 'کد تخفیف الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        discount = Discount.objects.get(
            code=code,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        
        if discount.min_order_amount > 0 and float(order_total) < discount.min_order_amount:
            return Response(
                {
                    'error': f'برای استفاده از این کد تخفیف، حداقل مبلغ خرید باید {discount.min_order_amount} تومان باشد',
                    'min_order_amount': discount.min_order_amount
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if discount.seller:
            try:
                if int(discount.seller.id) != int(seller_id):
                    return Response(
                        {'error': 'این کد تخفیف برای این فروشگاه معتبر نیست'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'مشکل در شناسه فروشگاه'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if discount.for_first_purchase:
            has_previous_orders = Order.objects.filter(
                user=request.user,
                created_at__lt=timezone.now()
            ).exists()
            
            if has_previous_orders:
                return Response(
                    {'error': 'این تخفیف فقط برای اولین خرید قابل استفاده است'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if discount.is_single_use:
            used_before = Order.objects.filter(
                user=request.user,
                discount=discount
            ).exists()
            
            if used_before:
                return Response(
                    {'error': 'شما قبلاً از این کد تخفیف استفاده کرده‌اید'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response({
            'id': discount.id,
            'title': discount.title,
            'code': discount.code,
            'percentage': discount.percentage,
            'seller_id': discount.seller.id if discount.seller else None,
            'shop_name': discount.seller.shop_name if discount.seller else None,
            'description': discount.description,
            'min_order_amount': discount.min_order_amount,
            'for_first_purchase': discount.for_first_purchase
        })
        
    except Discount.DoesNotExist:
        return Response(
            {'error': 'کد تخفیف نامعتبر یا منقضی شده است'},
            status=status.HTTP_400_BAD_REQUEST
        )
            
            
class ActiveDiscountsView(generics.ListAPIView):
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Discount.objects.filter(is_active=True)
