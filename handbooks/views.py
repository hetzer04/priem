# handbooks/views.py
# ------------------
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Specialty, Qualification
from .forms import SpecialtyForm, QualificationForm

# --- CRUD для Специальностей ---

class SpecialtyListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Specialty
    permission_required = 'handbooks.view_specialty'
    template_name = 'handbooks/specialty_list.html'
    context_object_name = 'specialties'

class SpecialtyCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Specialty
    form_class = SpecialtyForm
    permission_required = 'handbooks.add_specialty'
    template_name = 'handbooks/specialty_form.html'
    success_url = reverse_lazy('specialty_list')

class SpecialtyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Specialty
    form_class = SpecialtyForm
    permission_required = 'handbooks.change_specialty'
    template_name = 'handbooks/specialty_form.html'
    success_url = reverse_lazy('specialty_list')

class SpecialtyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Specialty
    permission_required = 'handbooks.delete_specialty'
    template_name = 'handbooks/confirm_delete.html'
    success_url = reverse_lazy('specialty_list')
    extra_context = {'object_name': 'специальность'}


# --- CRUD для Квалификаций ---

class QualificationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Qualification
    permission_required = 'handbooks.view_qualification'
    template_name = 'handbooks/qualification_list.html'
    context_object_name = 'qualifications'
    queryset = Qualification.objects.select_related('specialty').all()

class QualificationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Qualification
    form_class = QualificationForm
    permission_required = 'handbooks.add_qualification'
    template_name = 'handbooks/qualification_form.html'
    success_url = reverse_lazy('qualification_list')

class QualificationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Qualification
    form_class = QualificationForm
    permission_required = 'handbooks.change_qualification'
    template_name = 'handbooks/qualification_form.html'
    success_url = reverse_lazy('qualification_list')

class QualificationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Qualification
    permission_required = 'handbooks.delete_qualification'
    template_name = 'handbooks/confirm_delete.html'
    success_url = reverse_lazy('qualification_list')
    extra_context = {'object_name': 'квалификацию'}