# Generated by Django 5.2.4 on 2025-07-30 07:35

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('handbooks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('iin', models.CharField(max_length=12, unique=True, verbose_name='ИИН')),
                ('study_form', models.CharField(blank=True, choices=[('Очная', 'Очная'), ('Дуальная', 'Дуальная')], max_length=50, null=True, verbose_name='Форма обучения')),
                ('base_education', models.CharField(blank=True, choices=[('9 классов', '9 классов'), ('11 классов', '11 классов'), ('ТиПО', 'ТиПО')], max_length=50, null=True, verbose_name='На базе')),
                ('school', models.CharField(blank=True, max_length=255, null=True, verbose_name='Школа/Колледж')),
                ('graduation_year', models.IntegerField(blank=True, null=True, verbose_name='Год окончания')),
                ('with_honors', models.BooleanField(default=False, verbose_name='С отличием')),
                ('gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='Средний балл аттестата')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('study_language', models.CharField(blank=True, max_length=50, null=True, verbose_name='Язык обучения')),
                ('social_status', models.CharField(blank=True, max_length=100, null=True, verbose_name='Социальный статус')),
                ('citizenship', models.CharField(blank=True, default='Республика Казахстан', max_length=100, null=True, verbose_name='Гражданство')),
                ('nationality', models.CharField(blank=True, max_length=100, null=True, verbose_name='Национальность')),
                ('gender', models.CharField(blank=True, choices=[('Мужской', 'Мужской'), ('Женский', 'Женский')], max_length=10, null=True, verbose_name='Пол')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Контакты')),
                ('home_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Дом. адрес')),
                ('parents_info', models.TextField(blank=True, null=True, verbose_name='ФИО родителей')),
                ('has_incomplete_docs', models.BooleanField(default=False, verbose_name='Неполный пакет документов')),
                ('needs_dormitory', models.BooleanField(default=False, verbose_name='Общежитие')),
                ('application_date', models.DateField(default=django.utils.timezone.now, verbose_name='Дата подачи заявления')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='applicant_photos/', verbose_name='Фото 3x4')),
                ('is_ready_for_enrollment', models.BooleanField(default=False, verbose_name='К зачислению')),
                ('payment_type', models.CharField(blank=True, choices=[('Госзаказ', 'Госзаказ'), ('Платное', 'Платное')], default='Платное', max_length=20, null=True, verbose_name='Тип финансирования')),
                ('payment_status', models.CharField(blank=True, choices=[('Оплачено', 'Оплачено'), ('Не оплачено', 'Не оплачено')], default='Не оплачено', max_length=20, null=True, verbose_name='Статус оплаты')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('qualification', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='handbooks.qualification', verbose_name='Квалификация')),
                ('specialty', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='handbooks.specialty', verbose_name='Специальность')),
            ],
            options={
                'verbose_name': 'Абитуриент',
                'verbose_name_plural': 'Абитуриенты',
                'ordering': ['-created_at'],
            },
        ),
    ]
