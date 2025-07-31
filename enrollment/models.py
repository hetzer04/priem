# enrollment/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from handbooks.models import Quota, Specialty, Qualification
from orders.models import Order

class Applicant(models.Model):
    # Константы
    STUDY_FORM_CHOICES = [('Очная', 'Очная'), ('Дуальная', 'Дуальная')]
    BASE_CHOICES = [('9 классов', '9 классов'), ('11 классов', '11 классов'), ('ТиПО', 'ТиПО')]
    GENDER_CHOICES = [('Мужской', 'Мужской'), ('Женский', 'Женский')]
    PAYMENT_TYPE_CHOICES = [('Госзаказ', 'Госзаказ'), ('Платное', 'Платное')]
    PAYMENT_STATUS_CHOICES = [('Оплачено', 'Оплачено'), ('Не оплачено', 'Не оплачено')]

    # --- Ключевые поля (остаются обязательными) ---
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    iin = models.CharField(max_length=12, unique=True, verbose_name="ИИН")
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, verbose_name="Специальность")
    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT, verbose_name="Квалификация")

    # --- Необязательные поля (добавляем null=True, blank=True) ---
    study_form = models.CharField(max_length=50, choices=STUDY_FORM_CHOICES, verbose_name="Форма обучения", null=True, blank=True)
    base_education = models.CharField(max_length=50, choices=BASE_CHOICES, verbose_name="На базе", null=True, blank=True)
    school = models.CharField(max_length=255, verbose_name="Школа/Колледж", null=True, blank=True)
    graduation_year = models.IntegerField(verbose_name="Год окончания", null=True, blank=True)
    with_honors = models.BooleanField(default=False, verbose_name="С отличием") # BooleanField не нуждается в null=True
    gpa = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Средний балл аттестата", null=True, blank=True)
    birth_date = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    study_language = models.CharField(max_length=50, verbose_name="Язык обучения", null=True, blank=True)
    social_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Социальный статус")
    citizenship = models.CharField(max_length=100, default='Республика Казахстан', verbose_name="Гражданство", null=True, blank=True)
    nationality = models.CharField(max_length=100, verbose_name="Национальность", null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол", null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="Контакты", null=True, blank=True)
    home_address = models.CharField(max_length=255, verbose_name="Дом. адрес", null=True, blank=True)
    parents_info = models.TextField(blank=True, null=True, verbose_name="ФИО родителей")
    has_incomplete_docs = models.BooleanField(default=False, verbose_name="Неполный пакет документов")
    needs_dormitory = models.BooleanField(default=False, verbose_name="Общежитие")
    application_date = models.DateField(default=timezone.now, verbose_name="Дата подачи заявления")
    photo = models.ImageField(upload_to='applicant_photos/', null=True, blank=True, verbose_name="Фото 3x4")
    is_ready_for_enrollment = models.BooleanField(default=False, verbose_name="К зачислению")
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='Платное', verbose_name="Тип финансирования", null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Не оплачено', verbose_name="Статус оплаты", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    quotas = models.ManyToManyField(
        Quota,
        blank=True,
        verbose_name="Квоты",
        related_name="abiturients"
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"
        ordering = ['-created_at']
