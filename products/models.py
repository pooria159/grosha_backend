from django.db import models
from sellers.models import Seller
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'زیردسته‌بندی'
        verbose_name_plural = 'زیردسته‌بندی‌ها'

class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)    
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1 ستاره'), (2, '2 ستاره'), (3, '3 ستاره'), (4, '4 ستاره'), (5, '5 ستاره')],
        null=True, blank=True
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نظر محصول'
        verbose_name_plural = 'نظرات محصولات'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_comment',
                condition=models.Q(is_approved=True),
                violation_error_message='شما قبلاً برای این محصول نظر ثبت کرده‌اید'
            )
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"