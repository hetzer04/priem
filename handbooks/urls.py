# handbooks/urls.py
# -----------------
from django.urls import path
from . import views

urlpatterns = [
    # URL-адреса для специальностей
    path('specialties/', views.SpecialtyListView.as_view(), name='specialty_list'),
    path('specialties/add/', views.SpecialtyCreateView.as_view(), name='specialty_add'),
    path('specialties/<int:pk>/edit/', views.SpecialtyUpdateView.as_view(), name='specialty_edit'),
    path('specialties/<int:pk>/delete/', views.SpecialtyDeleteView.as_view(), name='specialty_delete'),

    # URL-адреса для квалификаций
    path('qualifications/', views.QualificationListView.as_view(), name='qualification_list'),
    path('qualifications/add/', views.QualificationCreateView.as_view(), name='qualification_add'),
    path('qualifications/<int:pk>/edit/', views.QualificationUpdateView.as_view(), name='qualification_edit'),
    path('qualifications/<int:pk>/delete/', views.QualificationDeleteView.as_view(), name='qualification_delete'),
]