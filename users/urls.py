from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ActiveDiscountsView, CheckDuplicatesView, CustomTokenObtainPairView, AdminTicketUpdateView, DiscountViewSet, 
    TicketReplyCreateView, RegisterUser, TicketRetrieveView, 
    UserProfileView, AddressListCreateView, AddressRetrieveUpdateDestroyView, 
    SetDefaultAddressView, BankCardListCreateView, BankCardRetrieveUpdateDestroyView, 
    TicketListCreateView, apply_discount
)

router = DefaultRouter()
router.register(r'discount', DiscountViewSet, basename='list_discount')


urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressRetrieveUpdateDestroyView.as_view(), name='address_detail'),
    path('addresses/<int:pk>/set_default/', SetDefaultAddressView.as_view(), name='set_default_address'),
    path('bank-cards/', BankCardListCreateView.as_view(), name='bank_card_list_create'),
    path('bank-cards/<int:pk>/', BankCardRetrieveUpdateDestroyView.as_view(), name='bank_card_detail'),
    path('tickets/', TicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<int:ticket_id>/reply/', TicketReplyCreateView.as_view(), name='ticket-reply'),
    path('admin/tickets/<int:pk>/', AdminTicketUpdateView.as_view(), name='admin-ticket-update'),
    path('tickets/<int:pk>/', TicketRetrieveView.as_view(), name='ticket-detail'),
    path('check-duplicates/', CheckDuplicatesView.as_view(), name='check_duplicates'),
    path('discounts/', ActiveDiscountsView.as_view() , name='list_of_discount'),
    path('discounts/apply/', apply_discount, name='apply_discount'),
]

urlpatterns += router.urls