# enrollment/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView 
from . import views

urlpatterns = [
    # Главная страница - теперь это Дашборд
    path('', views.dashboard_view, name='dashboard'),

    # Абитуриенты (список теперь по новому адресу)
    path('applicants/list/', views.applicant_list, name='applicant_list'),
    path('applicants/add/', views.add_applicant, name='add_applicant'),
    path('applicants/edit/<int:pk>/', views.edit_applicant, name='edit_applicant'),

    path('applicants/<int:pk>/toggle-enrollment/', views.toggle_enrollment_status, name='toggle_enrollment_status'),

    # Экспорт и Импорт
    path('export/excel/', views.export_applicants_to_excel, name='export_applicants_excel'),
    path('import/excel/', views.import_applicants_from_excel, name='import_applicants_excel'),
    path('dashboard/export/excel/', views.export_dashboard_excel, name='export_dashboard_excel'),

    # Приказы
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_update, name='order_update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('orders/<int:pk>/sign/', views.sign_order, name='sign_order'),
    path('orders/<int:pk>/download/', views.generate_order_docx, name='download_order'),

    # Авторизация
    path('login/', LoginView.as_view(template_name='enrollment/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]