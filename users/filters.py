import django_filters
from .models import Discount
from django.utils import timezone

class DiscountFilter(django_filters.FilterSet):
    active = django_filters.BooleanFilter(method='filter_active')
    upcoming = django_filters.BooleanFilter(method='filter_upcoming')
    expired = django_filters.BooleanFilter(method='filter_expired')
    min_percentage = django_filters.NumberFilter(field_name='percentage', lookup_expr='gte')
    max_percentage = django_filters.NumberFilter(field_name='percentage', lookup_expr='lte')
    shop_name = django_filters.CharFilter(field_name='seller__shop_name', lookup_expr='icontains')

    class Meta:
        model = Discount
        fields = ['is_active', 'for_first_purchase', 'seller']

    def filter_active(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                is_active=True,
                valid_from__lte=now,
                valid_to__gte=now
            )
        return queryset

    def filter_upcoming(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                valid_from__gt=now
            )
        return queryset

    def filter_expired(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                valid_to__lt=now
            )
        return queryset