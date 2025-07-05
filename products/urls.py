from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryListAPIView,
    SubcategoryListAPIView,
    ProductCommentsList,
    delete_comment,
    user_comments
)
from django.urls import path

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='products')

urlpatterns = [
    path('api/categories/<str:category_name>/', CategoryListAPIView.as_view(), name='category-detail'),
    path('api/subcategories/<str:subcategory_name>/', SubcategoryListAPIView.as_view(), name='subcategory-detail'),
    path('api/products/<int:pk>/update-stock/', ProductViewSet.as_view({'patch': 'update_stock'}), name='product-update-stock'),
    path('api/products/<int:pk>/stock/', ProductViewSet.as_view({'patch': 'update_stock'}), name='product-stock'),

    path('<int:product_id>/comments/', ProductCommentsList.as_view(), name='product-comments'),
    path('user/comments/', user_comments, name='user-comments'),
    path('comments/<int:comment_id>/', delete_comment, name='delete-comment'),

]

urlpatterns += router.urls