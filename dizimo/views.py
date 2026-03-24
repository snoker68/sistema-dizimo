from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Dizimista, Pagamento
from .forms import DizimistaForm, PagamentoForm, AgenteCreationForm
from django.db.models import Sum
from django.utils import timezone
import datetime
import csv
from django.http import HttpResponse

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        inicio_semana = hoje - datetime.timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)

        pagamentos = Pagamento.objects.only('valor', 'data_pagamento')
        context['ganhos_dia'] = pagamentos.filter(data_pagamento=hoje).aggregate(Sum('valor'))['valor__sum'] or 0
        context['ganhos_semana'] = pagamentos.filter(data_pagamento__gte=inicio_semana).aggregate(Sum('valor'))['valor__sum'] or 0
        context['ganhos_mes'] = pagamentos.filter(data_pagamento__gte=inicio_mes).aggregate(Sum('valor'))['valor__sum'] or 0
        return context

class DizimistaListView(LoginRequiredMixin, ListView):
    model = Dizimista
    template_name = 'dizimista_list.html'
    context_object_name = 'dizimistas'
    ordering = ['nome']

class DizimistaCreateView(LoginRequiredMixin, CreateView):
    model = Dizimista
    form_class = DizimistaForm
    template_name = 'dizimista_form.html'
    success_url = reverse_lazy('dashboard')

class DizimistaUpdateView(LoginRequiredMixin, UpdateView):
    model = Dizimista
    form_class = DizimistaForm
    template_name = 'dizimista_form.html'
    success_url = reverse_lazy('listar_dizimistas')

class DizimistaDeleteView(LoginRequiredMixin, DeleteView):
    model = Dizimista
    success_url = reverse_lazy('listar_dizimistas')
    
    def post(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class PagamentoListView(LoginRequiredMixin, ListView):
    model = Pagamento
    template_name = 'pagamento_list.html'
    context_object_name = 'pagamentos'
    # Otimização crucial: select_related evita queries extras N+1 no banco
    queryset = Pagamento.objects.select_related('dizimista', 'registrado_por').order_by('-data_pagamento')

class PagamentoCreateView(LoginRequiredMixin, CreateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'pagamento_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)

class PagamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'pagamento_form.html'
    success_url = reverse_lazy('listar_pagamentos')

class PagamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pagamento
    success_url = reverse_lazy('listar_pagamentos')
    
    def post(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class UsuarioListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'usuario_list.html'
    context_object_name = 'usuarios'
    ordering = ['username']

class UsuarioCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = User
    form_class = AgenteCreationForm
    template_name = 'usuario_form.html'
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('is_superuser'):
            self.object.is_staff = True
            self.object.save()
        return response

class UsuarioDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('listar_usuarios')
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object != self.request.user:
            self.object.delete()
        return redirect(self.success_url)

@login_required
def exportar_pagamentos_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_pagamentos.csv"'
    response.write('\ufeff'.encode('utf8'))
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Dizimista', 'Valor (R$)', 'Data do Pagamento', 'Forma de Pagamento', 'Registrado Por'])
    
    pagamentos = Pagamento.objects.select_related('dizimista', 'registrado_por').order_by('-data_pagamento')
    for p in pagamentos:
        writer.writerow([
            p.dizimista.nome,
            str(p.valor).replace('.', ','),
            p.data_pagamento.strftime('%d/%m/%Y'),
            p.forma_pagamento,
            p.registrado_por.username if p.registrado_por else 'N/A'
        ])
    return response
