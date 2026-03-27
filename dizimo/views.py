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
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import openpyxl
from decimal import Decimal
import git
import os

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
    
    def get_queryset(self):
        queryset = Dizimista.objects.all().order_by('nome')
        q = self.request.GET.get('q')
        bairro = self.request.GET.get('bairro')
        estado_civil = self.request.GET.get('estado_civil')
        
        if q:
            from django.db.models import Q
            queryset = queryset.filter(Q(nome__icontains=q) | Q(numero_dizimista__icontains=q))
        if bairro:
            queryset = queryset.filter(bairro=bairro)
        if estado_civil:
            queryset = queryset.filter(estado_civil=estado_civil)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Lista de bairros únicos para o filtro
        context['bairros'] = Dizimista.objects.values_list('bairro', flat=True).distinct().order_by('bairro')
        return context

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
    
    def get_queryset(self):
        queryset = Pagamento.objects.select_related('dizimista', 'registrado_por').order_by('-data_pagamento')
        q = self.request.GET.get('q')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        metodo = self.request.GET.get('metodo')
        
        if q:
            queryset = queryset.filter(dizimista__nome__icontains=q)
        if data_inicio:
            queryset = queryset.filter(data_pagamento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_pagamento__lte=data_fim)
        if metodo:
            queryset = queryset.filter(forma_pagamento=metodo)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Lista de formas de pagamento para o filtro
        context['formas_pagamento'] = Pagamento.FORMA_PAGAMENTO_CHOICES
        # Bairros também podem ser úteis aqui se precisarmos, mas por enquanto filtragem é por nome
        return context

class PagamentoCreateView(LoginRequiredMixin, CreateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'pagamento_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        # Define a data de pagamento automaticamente como HOJE se não estiver no formulário
        if not form.instance.data_pagamento:
            form.instance.data_pagamento = timezone.now().date()
        return super().form_valid(form)

class PagamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pagamento
    form_class = PagamentoForm
    template_name = 'pagamento_form.html'
    success_url = reverse_lazy('listar_pagamentos')

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

@login_required
def importar_dizimistas_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        # Validação do arquivo
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Formato inválido. Por favor, envie apenas arquivos .xlsx (Excel).')
            return redirect('listar_dizimistas')

        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            novos_dizimistas = []
            
            # Pula o cabeçalho (assumindo a linha 1 como cabeçalho)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0] and not row[1]: 
                    continue
                    
                numero_dizimista = str(row[0] or '').strip()
                nome = str(row[1] or '').strip()
                endereco = str(row[2] or '').strip()
                bairro = str(row[3] or '').strip()
                estado_civil = str(row[4] or 'Solteiro').strip().capitalize()
                nome_conjuge = str(row[5] or '').strip() if len(row) > 5 else ''
                
                # Tratamento financeiro tolerante a formatos de Excel
                try:
                    # Coluna: Numero(0), Nome(1), End(2), Bairro(3), EstCiv(4), Conj(5), Valor(6)
                    # O valor está na 7ª (índice 6) se houver 7 colunas, senão na 6ª (índice 5), etc
                    if len(row) > 6: val_idx = 6
                    elif len(row) > 5: val_idx = 5
                    else: val_idx = 4
                    
                    valor_str = str(row[val_idx]).replace('R$', '').replace(',', '.').strip()
                    if valor_str == 'None' or not valor_str:
                        valor = Decimal('0.00')
                    else:
                        valor = Decimal(valor_str)
                except Exception:
                    valor = Decimal('0.00')
                    
                # Filtra escolha fixa
                if estado_civil not in ['Solteiro', 'Casado']:
                    estado_civil = 'Solteiro'
                    
                novo = Dizimista(
                    numero_dizimista=numero_dizimista,
                    nome=nome,
                    endereco=endereco,
                    bairro=bairro,
                    estado_civil=estado_civil,
                    nome_conjuge=nome_conjuge if estado_civil == 'Casado' else '',
                    valor_primeira_contribuicao=valor
                )
                novos_dizimistas.append(novo)
                
            Dizimista.objects.bulk_create(novos_dizimistas)
            messages.success(request, f'{len(novos_dizimistas)} dizimistas foram importados com sucesso da sua planilha!')
            
        except Exception as e:
            messages.error(request, f'Erro inesperado ao processar o arquivo: {str(e)}')
            
    return redirect('listar_dizimistas')

@csrf_exempt
def webhook_update(request):
    """
    Endpoint para atualização automática via Git (CI/CD).
    Protegido por CSRF exempt para permitir requisições de webhooks externos.
    """
    if request.method == 'POST':
        # Token de segurança simples via parâmetro GET
        # Exemplo: /update_server/?token=meutokensecreto
        token = request.GET.get('token')
        if token != 'mudar_este_token_depois':
            return HttpResponse('Não autorizado (Token inválido ou ausente)', status=401)
        
        try:
            # Caminho absoluto para o repositório no PythonAnywhere
            repo_path = '/home/PDDFatima123/DizimosSistem'
            if not os.path.exists(os.path.join(repo_path, '.git')):
                return HttpResponse(f'Repositório Git não encontrado em {repo_path}', status=404)

            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            return HttpResponse('Servidor atualizado com sucesso via Git pull!', status=200)
        except Exception as e:
            return HttpResponse(f'Erro durante o pull: {str(e)}', status=500)
            
    return HttpResponse('Método não permitido (Use POST)', status=405)
