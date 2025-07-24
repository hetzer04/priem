# orders/models.py
# -----------------
from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('signed', 'Подписан'),
    ]

    title = models.CharField(
        max_length=500, 
        verbose_name="Заголовок приказа", 
        default="Приказ о зачислении"
    )
    signer_title = models.CharField(
        max_length=255, 
        default="Директор колледжа", 
        verbose_name="Должность подписанта"
    )
    preamble = models.TextField(verbose_name="Преамбула (основание)", blank=True, null=True)
    order_number = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Номер приказа")
    order_date = models.DateField(blank=True, null=True, verbose_name="Дата приказа")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    group_name = models.CharField(max_length=100, verbose_name="Название группы")
    
    # Связь теперь указывает на модель в приложении enrollment
    applicants = models.ManyToManyField(
        'enrollment.Applicant', 
        related_name="orders", 
        verbose_name="Абитуриенты в приказе"
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_orders', verbose_name="Кем создан")
    signed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='signed_orders', null=True, blank=True, verbose_name="Кем подписан")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Приказ №{self.order_number or 'б/н'} от {self.order_date or 'Черновик'}"

    class Meta:
        verbose_name = "Приказ"
        verbose_name_plural = "Приказы"
        ordering = ['-order_date', '-created_at']