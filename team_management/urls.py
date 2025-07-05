from django.urls import path
from . import views

urlpatterns = [
    path('stores/', views.SellerStoresView.as_view(), name='seller-stores'),
    path('store-roles/', views.StoreRoleListView.as_view(), name='store-role-list'),
    path('store-roles/create/', views.StoreRoleCreateView.as_view(), name='store-role-create'),
    path('store-roles/<int:role_id>/delete/', views.StoreRoleDeleteView.as_view(), name='store-role-delete'),
    path('store-roles/<int:role_id>/toggle-active/', views.StoreRoleToggleActiveView.as_view(), name='store-role-toggle-active'),
    path('users/search/', views.UserSearchView.as_view(), name='user-search'),
]