from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Discount

@receiver(pre_save, sender=Discount)
def update_discount_status(sender, instance, **kwargs):
    if instance.pk:
        original = Discount.objects.get(pk=instance.pk)
        if original.valid_to != instance.valid_to:
            instance.is_active = instance.is_valid()
    else:
        instance.is_active = instance.is_valid()