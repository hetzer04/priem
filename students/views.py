# students/views.py
# -----------------
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import Student
from .forms import StudentForm

class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    permission_required = 'students.view_student'
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 25
    queryset = Student.objects.select_related('specialty', 'qualification').all()

class StudentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Student
    permission_required = 'students.view_student'
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    permission_required = 'students.change_student'
    template_name = 'students/student_form.html'
    
    def get_success_url(self):
        return reverse_lazy('student_detail', kwargs={'pk': self.object.pk})

class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Student
    permission_required = 'students.delete_student'
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')
    extra_context = {'object_name': 'студента'}