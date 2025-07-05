from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from sellers.models import Seller
from .serializers import OrderSerializer
from users.models import Discount
from django.db import transaction
from products.models import Product
from django.db import models

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class SellerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seller = get_object_or_404(Seller, user=request.user)
        order_items = OrderItem.objects.filter(seller=seller).select_related(
            'order', 'order__user', 'product'
        ).order_by('-order__created_at')
        
        orders = {}
        for item in order_items:
            order_id = item.order.id
            if order_id not in orders:
                orders[order_id] = {
                    'order_id': order_id,
                    'customer': {
                        'id': item.order.user.id,
                        'username': item.order.user.username,
                        'email': item.order.user.email,
                        'phone' : item.order.user.phone
                    },
                    'status': item.order.status,
                    'created_at': item.order.created_at,
                    'total_price': item.order.total_price,
                    'items': []
                }
            orders[order_id]['items'].append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.price,
                'total_price': item.price * item.quantity
            })
        
        return Response(list(orders.values()))

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            models.Q(user=self.request.user) |
            models.Q(items__seller__user=self.request.user)
        ).distinct()
        
        
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart_items = request.data.get('items', [])
        discount_code = request.data.get('discount_code')

        if not cart_items:
            return Response({'error': 'سبد خرید خالی است'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                discount = None
                if discount_code:
                    try:
                        discount = Discount.objects.get(code=discount_code, is_active=True)
                    except Discount.DoesNotExist:
                        pass

                order = Order.objects.create(
                    user=request.user,
                    discount=discount
                )
                total_price = 0

                for item in cart_items:
                    product = Product.objects.get(pk=item['product_id'])

                    if product.stock < item['quantity']:
                        raise Exception(f"موجودی محصول {product.name} کافی نیست")

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                        price=product.price,
                        seller=product.seller
                    )

                    product.stock -= item['quantity']
                    product.save()

                    total_price += product.price * item['quantity']

                order.original_price = total_price
                if discount:
                    order.total_price = int(total_price * (1 - discount.percentage / 100))
                else:
                    order.total_price = total_price
                order.save()

                serializer = self.get_serializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({'error': 'محصول یافت نشد'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        try:
            order = Order.objects.get(
                models.Q(pk=pk) & (
                    models.Q(user=self.request.user) |
                    models.Q(items__seller__user=self.request.user)
                )
            )
        except Order.DoesNotExist:
            return Response({'error': 'سفارش یافت نشد یا دسترسی ندارید'}, status=404)

        new_status = request.data.get('status')
        valid_statuses = ['pending', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return Response({'error': f'وضعیت نامعتبر است. مقادیر مجاز: {", ".join(valid_statuses)}'}, status=400)

        order.status = new_status
        order.save()
        return Response({'success': f'وضعیت سفارش به {new_status} تغییر یافت'})