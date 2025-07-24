# enrollment/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('/', views.OrderListView.as_view(), name='order_list'),
    path('/create/', views.order_create, name='order_create'),
    path('/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('/<int:pk>/edit/', views.order_update, name='order_update'),
    path('/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('/<int:pk>/sign/', views.sign_order, name='sign_order'),
    path('/<int:pk>/download/', views.generate_order_docx, name='download_order'),
]

    