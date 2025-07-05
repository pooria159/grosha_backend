from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Category, Subcategory
from django.shortcuts import get_object_or_404
from .serializers import CategorySerializer, ProductSerializer, SubcategorySerializer
from rest_framework.views import APIView
from sellers.serializers import SellerSerializer 
from django.db.models import Min, Count
from rest_framework import status
from rest_framework import generics, permissions
from .models import ProductComment
from .serializers import ProductCommentSerializer, CreateProductCommentSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_comments(request):
    comments = ProductComment.objects.filter(user=request.user).select_related('product')
    serializer = ProductCommentSerializer(comments, many=True)
    return Response(serializer.data)



class ProductCommentsList(generics.ListCreateAPIView):
    serializer_class = ProductCommentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductComment.objects.filter(product_id=product_id).select_related('user')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProductCommentSerializer
        return ProductCommentSerializer

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'seller'):
            queryset = queryset.filter(seller=self.request.user.seller)
            return queryset
        
        if self.action == 'list':
            distinct_products = Product.objects.values(
                'name', 'category', 'subcategory'
            ).annotate(
                min_id=Min('id'),
                sellers_count=Count('id', distinct=True)
            ).order_by('name')

            product_ids = [p['min_id'] for p in distinct_products if p['sellers_count'] > 0]
            queryset = queryset.filter(id__in=product_ids)
        
        category_name = self.request.query_params.get('category')
        subcategory_name = self.request.query_params.get('subcategory')
        
        if category_name:
            queryset = queryset.filter(category__name=category_name)
        if subcategory_name:
            queryset = queryset.filter(subcategory__name=subcategory_name)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        similar_products_count = Product.objects.filter(
            name=instance.name,
            category=instance.category,
            subcategory=instance.subcategory
        ).exclude(id=instance.id).count()
        
        if similar_products_count > 0:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'seller'):
            raise PermissionError("فقط فروشندگان می‌توانند محصول ایجاد کنند.")
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='by-subcategory/(?P<subcategory_name>[^/]+)')
    def by_subcategory(self, request, subcategory_name=None):
        subcategory_name = subcategory_name.replace('-', ' ')
        subcategory = get_object_or_404(Subcategory, name=subcategory_name)
        distinct_products = Product.objects.filter(
            subcategory=subcategory
        ).values(
            'name', 'category', 'subcategory'
        ).annotate(
            min_id=Min('id')
        )
        
        product_ids = [p['min_id'] for p in distinct_products]
        products = Product.objects.filter(id__in=product_ids, subcategory=subcategory)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_name>[^/]+)')
    def by_category(self, request, category_name=None):
        category_name = category_name.replace('-', ' ')
        category = get_object_or_404(Category, name=category_name)
        distinct_products = Product.objects.filter(
            category=category
        ).values(
            'name', 'category', 'subcategory'
        ).annotate(
            min_id=Min('id')
        )
        
        product_ids = [p['min_id'] for p in distinct_products]
        products = Product.objects.filter(id__in=product_ids, category=category)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='sellers')
    def product_sellers(self, request, pk=None):
        product = self.get_object()
        similar_products = Product.objects.filter(
            name=product.name,
            category=product.category,
            subcategory=product.subcategory
        ).select_related('seller')

        sellers_data = []
        for p in similar_products:
            is_own_product = p.seller.user.id

            sellers_data.append({
                'seller': SellerSerializer(p.seller, context={'request': request}).data,
                'price': p.price,
                'stock': p.stock,
                'product_id': p.id,
                'is_own_product': is_own_product
            })
        return Response(sellers_data)
        
    @action(detail=True, methods=['patch'], url_path='update-stock')
    def update_stock(self, request, pk=None):
        try:
            product = Product.objects.get(id=pk)
            quantity = int(request.data.get('quantity', 0))
            
            if product.stock < quantity:
                return Response(
                    {'error': f'موجودی کافی نیست (موجودی: {product.stock}, درخواستی: {quantity})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product.stock -= quantity
            product.save()
            
            return Response({
                'message': 'موجودی با موفقیت به‌روزرسانی شد',
                'new_stock': product.stock,
                'product_id': product.id,
                'seller_id': product.seller.id
            })
            
        except Product.DoesNotExist:
            return Response(
                {'error': 'محصول یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class CategoryListAPIView(APIView):
    def get(self, request, category_name=None):
        category = get_object_or_404(Category, name=category_name)  
        serializer = CategorySerializer(category)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryListAPIView(APIView):
    def get(self, request, subcategory_name=None):
        subcategory = get_object_or_404(Subcategory, name=subcategory_name)  
        serializer = SubcategorySerializer(subcategory)
        return Response(serializer.data)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = ProductComment.objects.get(id=comment_id, user=request.user)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ProductComment.DoesNotExist:
        return Response({'error': 'Comment not found or not yours'}, status=status.HTTP_404_NOT_FOUND)
