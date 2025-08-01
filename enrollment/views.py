# views.py

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required # Импортируем permission_required
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Q
from itertools import groupby
from django.views.decorators.http import require_POST

from handbooks.models import Qualification, Specialty


from .models import Applicant
from .forms import ApplicantForm
from .filters import ApplicantFilter
import pandas as pd
from django.contrib import messages

from django.core.serializers.json import DjangoJSONEncoder

@require_POST # Эта функция будет принимать только POST-запросы
@permission_required('enrollment.change_applicant', raise_exception=True)
def toggle_enrollment_status(request, pk):
    """Переключает статус абитуриента 'К зачислению'."""
    applicant = get_object_or_404(Applicant, pk=pk)
    applicant.is_ready_for_enrollment = not applicant.is_ready_for_enrollment
    applicant.save()
    return redirect('applicant_list')

@login_required
def applicant_list(request):
    """Список абитуриентов с фильтрацией."""
    f = ApplicantFilter(request.GET, queryset=Applicant.objects.all())
    return render(request, 'enrollment/applicant_list.html', {'filter': f})

# ИСПРАВЛЕНО: Заменяем @writer_required на стандартный декоратор
@permission_required('enrollment.add_applicant', raise_exception=True)
def add_applicant(request):
    if request.method == 'POST':
        form = ApplicantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('applicant_list')
    else:
        form = ApplicantForm()
    return render(request, 'enrollment/applicant_form.html', {'form': form})

# ИСПРАвлено: Заменяем @editor_required на стандартный декоратор
@permission_required('enrollment.change_applicant', raise_exception=True)
def edit_applicant(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    if request.method == 'POST':
        form = ApplicantForm(request.POST, instance=applicant)
        if form.is_valid():
            form.save()
            return redirect('applicant_list')
    else:
        form = ApplicantForm(instance=applicant)
    return render(request, 'enrollment/applicant_form.html', {'form': form})



@login_required
def export_applicants_to_excel(request):
    """
    Экспортирует данные абитуриентов в Excel файл с учетом новых полей.
    """
    f = ApplicantFilter(request.GET, queryset=Applicant.objects.select_related('specialty', 'qualification').all())
    queryset = f.qs

    data = list(queryset.values(
        'full_name', 'iin', 'specialty__name', 'qualification__name', 
        'payment_type', 'payment_status', 'study_form', 'base_education', 
        'gpa', 'birth_date', 'school', 'graduation_year', 'with_honors', 
        'study_language', 'social_status', 'citizenship', 'nationality', 
        'gender', 'phone_number', 'home_address', 'parents_info', 
        'has_incomplete_docs', 'needs_dormitory', 'application_date', 
        'is_ready_for_enrollment'
    ))
    df = pd.DataFrame(data)

    # Переименовываем столбцы для красоты
    df.rename(columns={
        'full_name': 'ФИО', 'iin': 'ИИН', 'specialty__name': 'Специальность', 
        'qualification__name': 'Квалификация', 'payment_type': 'Тип финансирования',
        'payment_status': 'Статус оплаты', 'study_form': 'Форма обучения',
        'base_education': 'На базе', 'gpa': 'Средний балл аттестата', 
        'birth_date': 'Дата рождения', 'school': 'Школа/Колледж',
        'graduation_year': 'Год окончания', 'with_honors': 'С отличием',
        'study_language': 'Язык обучения', 'social_status': 'СП',
        'citizenship': 'Гражданство', 'nationality': 'Национальность',
        'gender': 'Пол', 'phone_number': 'Контакты', 'home_address': 'Дом. адрес',
        'parents_info': 'ФИО родителей', 'has_incomplete_docs': 'Неполный пакет документов',
        'needs_dormitory': 'Общежитие', 'application_date': 'Дата подачи заявления',
        'is_ready_for_enrollment': 'Готов к зачислению'
    }, inplace=True)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="applicants_{timezone.now().strftime("%Y-%m-%d")}.xlsx"'
    df.to_excel(response, index=False)
    return response


@permission_required('enrollment.add_applicant', raise_exception=True)
def import_applicants_from_excel(request):
    """
    Импортирует абитуриентов из Excel файла (исправленная и обновленная версия).
    """
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, "Файл не был предоставлен.")
            return redirect('applicant_list')

        try:
            # Читаем все данные как строки, чтобы избежать проблем с форматами
            df = pd.read_excel(excel_file, dtype=str).where(pd.notna, None)
            
            required_columns = ['ФИО', 'ИИН', 'Специальность', 'Квалификация']
            if not all(col in df.columns for col in required_columns):
                messages.error(request, f"Ошибка: в файле отсутствуют обязательные столбцы. Требуются: {', '.join(required_columns)}")
                return redirect('applicant_list')

            # Кэшируем данные, чтобы не делать запросы в цикле
            all_specialties = {s.name: s for s in Specialty.objects.all()}
            all_qualifications = {f"{q.name}|{q.specialty.name}": q for q in Qualification.objects.select_related('specialty').all()}
            
            imported_count = 0
            for index, row in df.iterrows():
                iin = row.get('ИИН')
                spec_name = row.get('Специальность')
                qual_name = row.get('Квалификация')
                
                if not all([iin, spec_name, qual_name, row.get('ФИО')]):
                    messages.warning(request, f"Строка {index + 2}: пропущена из-за отсутствия ИИН, ФИО, специальности или квалификации.")
                    continue

                specialty = all_specialties.get(spec_name.strip())
                if not specialty:
                    messages.warning(request, f"Строка {index + 2} ({row['ФИО']}): специальность '{spec_name}' не найдена.")
                    continue
                
                qual_key = f"{qual_name.strip()}|{specialty.name}"
                qualification = all_qualifications.get(qual_key)
                if not qualification:
                    messages.warning(request, f"Строка {index + 2} ({row['ФИО']}): квалификация '{qual_name}' не найдена для специальности '{specialty.name}'.")
                    continue

                # Обрабатываем дату
                try:
                    app_date = pd.to_datetime(row.get('Дата подачи заявления')).date() if row.get('Дата подачи заявления') else timezone.now().date()
                    birth_date = pd.to_datetime(row.get('Дата рождения')).date() if row.get('Дата рождения') else None
                except (ValueError, TypeError):
                    app_date = timezone.now().date()
                    birth_date = None
                    messages.warning(request, f"Строка {index + 2} ({row['ФИО']}): неверный формат даты. Даты не были установлены.")

                Applicant.objects.update_or_create(
                    iin=iin,
                    defaults={
                        'full_name': row.get('ФИО'),
                        'specialty': specialty, # Assuming 'specialty' object is retrieved separately
                        'qualification': qualification, # Assuming 'qualification' object is retrieved separately
                        'application_date': app_date, # Assuming 'app_date' is parsed/converted separately
                        'iin': row.get('ИИН'), # Added IIN
                        'study_form': row.get('Форма обучения'),
                        'base_education': row.get('На базе'),
                        'school': row.get('Школа/Колледж'),
                        'graduation_year': row.get('Год окончания'),
                        'with_honors': row.get('С отличием') in ['Да', 'True', '1'], # Example of boolean conversion
                        'gpa': row.get('Средний балл аттестата'),
                        'birth_date': birth_date, # Assuming 'birth_date' is parsed/converted separately
                        'study_language': row.get('Язык обучения'),
                        'social_status': row.get('Социальный статус'),
                        'citizenship': row.get('Гражданство'),
                        'nationality': row.get('Национальность'),
                        'gender': row.get('Пол'),
                        'phone_number': row.get('Контакты'),
                        'home_address': row.get('Дом. адрес'),
                        'parents_info': row.get('ФИО родителей'),
                        'has_incomplete_docs': row.get('Неполный пакет документов') in ['Да', 'True', '1'],
                        'needs_dormitory': row.get('Общежитие') in ['Да', 'True', '1'],
                        'photo': None, # Images usually require specific handling for import, setting to None for now
                        'is_ready_for_enrollment': row.get('К зачислению') in ['Да', 'True', '1'],
                        'payment_type': row.get('Тип финансирования'),
                        'payment_status': row.get('Статус оплаты'),
                    }
                )
                imported_count += 1

            messages.success(request, f"Импорт успешно завершен! Обработано записей: {imported_count}.")
        
        except Exception as e:
            messages.error(request, f"Произошла критическая ошибка при импорте: {e}")

    return redirect('applicant_list')


@login_required
def dashboard_view(request):
    """
    Отображает дашборд со сводной статистикой по абитуриентам.
    """
    qualifications_data = Qualification.objects.annotate(
        total_applicants=Count('applicant'),

        # Подсчет по базе 9
        base9_rus=Count('applicant', filter=Q(
            applicant__base_education='9 классов',
            applicant__study_language__icontains='рус'
        ) & ~Q(applicant__study_form='Дуальная')),
        base9_kaz=Count('applicant', filter=Q(
            applicant__base_education='9 классов',
            applicant__study_language__icontains='каз'
        ) & ~Q(applicant__study_form='Дуальная')),

        # Подсчет по базе 11
        base11_rus=Count('applicant', filter=Q(
            applicant__base_education='11 классов',
            applicant__study_language__icontains='рус'
        ) & ~Q(applicant__study_form='Дуальная')),
        base11_kaz=Count('applicant', filter=Q(
            applicant__base_education='11 классов',
            applicant__study_language__icontains='каз'
        ) & ~Q(applicant__study_form='Дуальная')),

        # ДОБАВЛЕНО: Подсчет по базе ТиПО
        tipo_rus=Count('applicant', filter=Q(
            applicant__base_education='ТиПО',
            applicant__study_language__icontains='рус'
        ) & ~Q(applicant__study_form='Дуальная')),
        tipo_kaz=Count('applicant', filter=Q(
            applicant__base_education='ТиПО',
            applicant__study_language__icontains='каз'
        ) & ~Q(applicant__study_form='Дуальная')),

        # Подсчет дуальщиков
        dual=Count('applicant', filter=Q(applicant__study_form='Дуальная')),

    ).values(
        'name', 'specialty__name', 'specialty_id', 'total_applicants',
        'base9_rus', 'base9_kaz', 'base11_rus', 'base11_kaz',
        'tipo_rus', 'tipo_kaz',  # ДОБАВЛЕНО
        'dual'
    ).order_by('specialty__name', 'name')

    # --- Группировка остается без изменений ---
    grouped_data = []
    for key, group in groupby(qualifications_data, key=lambda x: x['specialty__name']):
        qualifications = list(group)
        specialty_total = sum(q['total_applicants'] for q in qualifications)
        grouped_data.append({
            'specialty_name': key,
            'qualifications': qualifications,
            'specialty_total': specialty_total,
        })

    # --- Обновляем итоговые суммы ---
    totals = {
        'total_base9_rus': sum(item['base9_rus'] for item in qualifications_data),
        'total_base9_kaz': sum(item['base9_kaz'] for item in qualifications_data),
        'total_base11_rus': sum(item['base11_rus'] for item in qualifications_data),
        'total_base11_kaz': sum(item['base11_kaz'] for item in qualifications_data),
        'total_tipo_rus': sum(item['tipo_rus'] for item in qualifications_data),  # ДОБАВЛЕНО
        'total_tipo_kaz': sum(item['tipo_kaz'] for item in qualifications_data),  # ДОБАВЛЕНО
        'total_dual': sum(item['dual'] for item in qualifications_data),
        'grand_total': sum(item['specialty_total'] for item in grouped_data)
    }

    context = {
        'grouped_data': grouped_data,
        'totals': totals,
    }
     # --- НАЧАЛО: НОВЫЙ КОД ДЛЯ ГРАФИКОВ ---

    # 1. Данные для круговой диаграммы (по базе)
    base_data = Applicant.objects.values('base_education', 'study_form').annotate(count=Count('id'))
    
    chart_base_counts = {
        '9 классов': 0,
        '11 классов': 0,
        'ТиПО': 0,
        'Дуальное': 0,
    }
    for item in base_data:
        if item['study_form'] == 'Дуальная':
            chart_base_counts['Дуальное'] += item['count']
        else:
            if item['base_education'] in chart_base_counts:
                chart_base_counts[item['base_education']] += item['count']

    # 2. Данные для гистограммы (по специальностям)
    chart_specialty_labels = [data['specialty_name'] for data in grouped_data]
    chart_specialty_counts = [data['specialty_total'] for data in grouped_data]

    # --- КОНЕЦ: НОВЫЙ КОД ДЛЯ ГРАФИКОВ ---

    context = {
        'grouped_data': grouped_data,
        'totals': totals,
        # Передаем данные для графиков в контекст
        'chart_base_labels': json.dumps(list(chart_base_counts.keys())),
        'chart_base_data': json.dumps(list(chart_base_counts.values())),
        'chart_specialty_labels': json.dumps(chart_specialty_labels, cls=DjangoJSONEncoder),
        'chart_specialty_data': json.dumps(chart_specialty_counts),
    }
    return render(request, 'enrollment/dashboard.html', context)

# НОВАЯ ФУНКЦИЯ ДЛЯ ЭКСПОРТА
@login_required
def export_dashboard_excel(request):
    """
    Формирует и отдает Excel-файл на основе данных из таблицы дашборда.
    """
    # Этот код полностью повторяет логику получения данных из dashboard_view.
    # В идеале, эту логику можно вынести в отдельную функцию, чтобы избежать дублирования.
    qualifications_data = Qualification.objects.annotate(
        total_applicants=Count('applicant'),
        base9_rus=Count('applicant', filter=Q(applicant__base_education='9 классов', applicant__study_language__icontains='рус') & ~Q(applicant__study_form='Дуальная')),
        base9_kaz=Count('applicant', filter=Q(applicant__base_education='9 классов', applicant__study_language__icontains='каз') & ~Q(applicant__study_form='Дуальная')),
        base11_rus=Count('applicant', filter=Q(applicant__base_education='11 классов', applicant__study_language__icontains='рус') & ~Q(applicant__study_form='Дуальная')),
        base11_kaz=Count('applicant', filter=Q(applicant__base_education='11 классов', applicant__study_language__icontains='каз') & ~Q(applicant__study_form='Дуальная')),
        tipo_rus=Count('applicant', filter=Q(applicant__base_education='ТиПО', applicant__study_language__icontains='рус') & ~Q(applicant__study_form='Дуальная')),
        tipo_kaz=Count('applicant', filter=Q(applicant__base_education='ТиПО', applicant__study_language__icontains='каз') & ~Q(applicant__study_form='Дуальная')),
        dual=Count('applicant', filter=Q(applicant__study_form='Дуальная')),
    ).values(
        'name', 'specialty__name', 'total_applicants', 'base9_rus', 'base9_kaz',
        'base11_rus', 'base11_kaz', 'tipo_rus', 'tipo_kaz', 'dual'
    ).order_by('specialty__name', 'name')

    # Формируем данные для DataFrame
    records = []
    for q in qualifications_data:
        records.append({
            'Образовательная программа': q['specialty__name'],
            'Квалификация': q['name'],
            'База 9 (рус)': q['base9_rus'],
            'База 9 (каз)': q['base9_kaz'],
            'База 11 (рус)': q['base11_rus'],
            'База 11 (каз)': q['base11_kaz'],
            'База ТиПО (рус)': q['tipo_rus'],
            'База ТиПО (каз)': q['tipo_kaz'],
            'Дуальное': q['dual'],
            'Всего по квалификации': q['total_applicants']
        })
    df = pd.DataFrame(records)

    # Создаем HTTP-ответ с Excel файлом
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="dashboard_report_{timezone.now().strftime("%Y-%m-%d")}.xlsx"'
    df.to_excel(response, index=False)
    
    return response

