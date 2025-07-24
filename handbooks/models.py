from django.db import models

# Create your models here.
class Specialty(models.Model):
    code = models.CharField(
        max_length=50, 
        verbose_name="Код специальности", 
        default='' # Добавляем пустую строку как значение по умолчанию
    )
    name = models.CharField(max_length=255, verbose_name="Наименование специальности")

    def __str__(self):
        return f"{self.code} {self.name}"
    
    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"

class Qualification(models.Model):
    code = models.CharField(
        max_length=50, 
        verbose_name="Код специальности", 
        default='' # Добавляем пустую строку как значение по умолчанию
    )
    name = models.CharField(max_length=255, verbose_name="Наименование квалификации")
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name="qualifications", verbose_name="Специальность")
    is_worker_qualification = models.BooleanField(default=False, verbose_name="Рабочая квалификация")
    def __str__(self):
        return f"{self.name} ({self.specialty.name})"
    class Meta:
        verbose_name = "Квалификация"
        verbose_name_plural = "Квалификации"