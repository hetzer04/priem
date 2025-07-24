# orders/views.py
# ---------------
from itertools import groupby
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.contrib import messages
from docxtpl import DocxTemplate
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

# Импортируем все необходимое из других приложений
from enrollment.models import Applicant, Student
from enrollment.filters import ApplicantFilter
from .models import Order
from .forms import OrderForm

@login_required
def generate_order_docx(request, pk):
    order = get_object_or_404(Order, pk=pk)
    doc = DocxTemplate("templates/enrollment/docx_templates/prikaz_template.docx")

    # Получаем всех студентов и сортируем их в правильном порядке для группировки
    all_students = order.student_set.select_related(
        'specialty', 'qualification'
    ).order_by(
        'qualification__is_worker_qualification', # Сначала обычные, потом рабочие
        'specialty__name', 
        'qualification__name', 
        'base_education', 
        'study_language', 
        'full_name'
    )

    # Разделяем студентов на две группы
    regular_students = [s for s in all_students if not s.qualification.is_worker_qualification]
    worker_students = [s for s in all_students if s.qualification.is_worker_qualification]
    
    # Функция для группировки списка студентов
    def group_student_list(student_list):
        grouped_data = []
        # Группируем по специальности
        for specialty, specialty_group in groupby(student_list, key=lambda s: s.specialty):
            sub_groups = []
            
            # ИСПРАВЛЕНИЕ: Используем lambda вместо itemgetter
            sub_group_key = lambda s: (s.qualification, s.base_education, s.study_language)
            
            # Группируем внутренний список по составному ключу
            for key, group in groupby(specialty_group, key=sub_group_key):
                sub_groups.append({
                    'qualification': key[0],
                    'base_education': key[1],
                    'study_language': key[2],
                    'students': list(group)
                })
            grouped_data.append({'specialty': specialty, 'sub_groups': sub_groups})
        return grouped_data

    # Готовим контекст для шаблона
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    context = {
        'order_number': order.order_number,
        'order_date': order.order_date,
        'order_date_month_str': months[order.order_date.month - 1] if order.order_date else '',
        'title': order.title,
        'preamble': order.preamble,
        'grouped_regular_students': group_student_list(regular_students),
        'grouped_worker_students': group_student_list(worker_students),
        'signer_name': order.signed_by.get_full_name() if order.signed_by else " ",
        'signer_title': order.signer_title,
    }
    
    doc.render(context)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="prikaz_{order.order_number}.docx"'
    doc.save(response)
    
    return response

@permission_required('enrollment.add_order', raise_exception=True)
def order_create(request):
    """Создание нового приказа с фильтрацией абитуриентов."""
    # Используем тот же фильтр, что и на главной
    applicant_filter = ApplicantFilter(request.GET, queryset=Applicant.objects.filter(is_ready_for_enrollment=True))
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Получаем список ID абитуриентов, выбранных в таблице
            selected_applicant_ids = request.POST.getlist('selected_applicants')
            
            if not selected_applicant_ids:
                messages.error(request, "Не выбрано ни одного абитуриента!")
                # Возвращаемся на ту же страницу, сохраняя фильтры
                return render(request, 'enrollment/order_form.html', {
                    'form': form,
                    'filter': applicant_filter,
                })

            # Создаем приказ, но пока не сохраняем в базу
            order = form.save(commit=False)
            order.created_by = request.user
            order.save() # Сохраняем, чтобы получить ID

            # Добавляем выбранных абитуриентов в приказ
            order.applicants.set(selected_applicant_ids)
            
            messages.success(request, "Черновик приказа успешно создан.")
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()

    return render(request, 'enrollment/order_form.html', {
        'form': form,
        'filter': applicant_filter,
    })


@permission_required('enrollment.change_order', raise_exception=True)
def order_update(request, pk):
    """Редактирование приказа с фильтрацией."""
    order = get_object_or_404(Order, pk=pk)
    
    # Проверка прав доступа, как в старом test_func
    if not (request.user.is_superuser or order.status == 'draft'):
        raise PermissionDenied("Вы можете редактировать только черновики.")

    applicant_filter = ApplicantFilter(request.GET, queryset=Applicant.objects.filter(is_ready_for_enrollment=True))
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            selected_applicant_ids = request.POST.getlist('selected_applicants')
            
            if not selected_applicant_ids:
                messages.error(request, "Не выбрано ни одного абитуриента!")
                return render(request, 'enrollment/order_form.html', {
                    'form': form,
                    'filter': applicant_filter,
                    'object': order, # для шаблона
                })

            order = form.save()
            order.applicants.set(selected_applicant_ids)
            
            messages.success(request, "Приказ успешно обновлен.")
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)

    return render(request, 'enrollment/order_form.html', {
        'form': form,
        'filter': applicant_filter,
        'object': order, # для шаблона, чтобы знать ID уже добавленных
    })

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'enrollment/order_list.html'
    context_object_name = 'orders'

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'enrollment/order_detail.html'

class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    template_name = 'enrollment/order_confirm_delete.html'
    success_url = reverse_lazy('order_list')

    def test_func(self):
        user = self.request.user
        if not user.has_perm('enrollment.delete_order'):
            return False
        order = self.get_object()
        return user.is_superuser or order.status == 'draft'

@require_POST
@permission_required('enrollment.change_order', raise_exception=True)
@transaction.atomic # Гарантирует, что все операции либо выполнятся успешно, либо отменятся
def sign_order(request, pk):
    """
    Подписывает приказ и выполняет зачисление абитуриентов,
    перенося их в таблицу студентов.
    """
    order = get_object_or_404(Order, pk=pk)
    order_number_from_form = request.POST.get('order_number')

    if not order_number_from_form:
        messages.error(request, "Номер приказа не может быть пустым.")
        return redirect('order_detail', pk=pk)

    if Order.objects.filter(order_number=order_number_from_form).exclude(pk=order.pk).exists():
        messages.error(request, f"Ошибка: Приказ с номером '{order_number_from_form}' уже существует!")
        return redirect('order_detail', pk=pk)

    if order.status == 'draft':
        # 1. Подписываем сам приказ
        order.status = 'signed'
        order.order_number = order_number_from_form
        order.order_date = timezone.now().date()
        order.signed_by = request.user
        order.save()

        # 2. Начинаем процесс перевода абитуриентов в студенты
        applicants_to_enroll = list(order.applicants.all()) # Создаем копию списка
        for applicant in applicants_to_enroll:
            # Создаем студента, копируя все поля
            student = Student.objects.create(
                full_name=applicant.full_name,
                iin=applicant.iin,
                specialty=applicant.specialty,
                qualification=applicant.qualification,
                study_form=applicant.study_form,
                base_education=applicant.base_education,
                school=applicant.school,
                graduation_year=applicant.graduation_year,
                with_honors=applicant.with_honors,
                gpa=applicant.gpa,
                birth_date=applicant.birth_date,
                study_language=applicant.study_language,
                social_status=applicant.social_status,
                citizenship=applicant.citizenship,
                nationality=applicant.nationality,
                gender=applicant.gender,
                phone_number=applicant.phone_number,
                home_address=applicant.home_address,
                parents_info=applicant.parents_info,
                has_incomplete_docs=applicant.has_incomplete_docs,
                needs_dormitory=applicant.needs_dormitory,
                payment_type=applicant.payment_type,
                application_date=applicant.application_date,
                photo=applicant.photo
            )
            # Добавляем приказ в историю перемещений студента
            student.movement_history.add(order)
            
            # Удаляем абитуриента
            applicant.delete()

        messages.success(request, f"Приказ №{order.order_number} подписан. Зачислено студентов: {len(applicants_to_enroll)}.")
    else:
        messages.warning(request, "Этот приказ уже был подписан ранее.")

    return redirect('order_detail', pk=pk)