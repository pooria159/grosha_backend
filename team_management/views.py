from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import StoreRole
from .serializers import (
    StoreRoleSerializer,
    CreateStoreRoleSerializer,
    UserSerializer
)
from django.contrib.auth import get_user_model
from sellers.models import Seller

User = get_user_model()

class SellerStoresView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            return Response({
                'id': seller.id,
                'name': seller.shop_name,
                'address': seller.address
            })
        except Seller.DoesNotExist:
            return Response(
                {"detail": "شما فروشنده نیستید."},
                status=status.HTTP_403_FORBIDDEN
            )

class StoreRoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            roles = StoreRole.objects.filter(seller=seller)
            serializer = StoreRoleSerializer(roles, many=True)
            return Response(serializer.data)
        except Seller.DoesNotExist:
            return Response(
                {"detail": "شما فروشنده نیستید."},
                status=status.HTTP_403_FORBIDDEN
            )

class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        search_term = request.query_params.get('search', '')

        try:
            seller = Seller.objects.get(user=request.user)
            existing_users = StoreRole.objects.filter(
                seller=seller
            ).values_list('user_id', flat=True)
            users = User.objects.exclude(id__in=existing_users)

            if search_term:
                users = users.filter(
                    models.Q(username__icontains=search_term) |
                    models.Q(first_name__icontains=search_term) |
                    models.Q(last_name__icontains=search_term) |
                    models.Q(email__icontains=search_term)
                )

            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Seller.DoesNotExist:
            return Response(
                {"detail": "شما فروشنده نیستید."},
                status=status.HTTP_403_FORBIDDEN
            )

class StoreRoleCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
        except Seller.DoesNotExist:
            return Response(
                {"detail": "شما فروشنده نیستید."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateStoreRoleSerializer(data=request.data)
        if serializer.is_valid():
            if StoreRole.objects.filter(
                user=serializer.validated_data['user'],
                seller=seller
            ).exists():
                return Response(
                    {"detail": "این کاربر قبلاً به فروشگاه شما اضافه شده است."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            role = StoreRole.objects.create(
                user=serializer.validated_data['user'],
                seller=seller,
                role=serializer.validated_data['role']
            )
            return Response(
                StoreRoleSerializer(role).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoreRoleDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, role_id):
        try:
            seller = Seller.objects.get(user=request.user)
            role = StoreRole.objects.get(id=role_id, seller=seller)
            role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Seller.DoesNotExist:
            return Response(
                {"detail": "شما فروشنده نیستید."},
                status=status.HTTP_403_FORBIDDEN
            )
        except StoreRole.DoesNotExist:
            return Response(
                {"detail": "نقش یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )

class StoreRoleToggleActiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, role_id):
        try:
            seller = Seller.objects.get(user=request.user)
            role = StoreRole.objects.get(id=role_id, seller=seller)
            role.is_active = not role.is_active
            role.save()
            return Response(
                {"is_active": role.is_active},
                status=status.HTTP_200_OK
            )
        except Seller.DoesNotExist:
            return Response(
                {"detail": "شما فروشنده نیستید."},
                status=status.HTTP_403_FORBIDDEN
            )
        except StoreRole.DoesNotExist:
            return Response(
                {"detail": "نقش یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )