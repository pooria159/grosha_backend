from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer
from products.models import Product, Seller

class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.CreateAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = Product.objects.get(id=serializer.validated_data['product_id'])
            seller = Seller.objects.get(id=serializer.validated_data['seller_id'])
        except (Product.DoesNotExist, Seller.DoesNotExist):
            raise NotFound("محصول یا فروشنده یافت نشد")

        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product.id,
            seller_id=seller.id,
            defaults={
                'product_name': product.name,
                'product_price': product.price,
                'product_stock': product.stock,
                'store_name': seller.shop_name,
                'quantity': serializer.validated_data['quantity'],
            }
        )

        if not created:
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if 'quantity' in serializer.validated_data:
            pass
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def get_object(self):
        obj = super().get_object()
        if obj.cart.user != self.request.user:
            raise PermissionDenied("شما اجازه دسترسی به این آیتم را ندارید.")
        return obj


class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        return super().get_queryset().filter(cart__user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.cart.user != self.request.user:
            raise PermissionDenied("شما اجازه دسترسی به این آیتم را ندارید.")
        return obj

class ClearCartView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Cart.objects.get(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)