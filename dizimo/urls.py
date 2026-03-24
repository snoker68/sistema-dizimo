from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    path('dizimista/', views.DizimistaListView.as_view(), name='listar_dizimistas'),
    path('dizimista/novo/', views.DizimistaCreateView.as_view(), name='cadastrar_dizimista'),
    path('dizimista/importar/', views.importar_dizimistas_excel, name='importar_dizimistas'),
    path('dizimista/<int:pk>/editar/', views.DizimistaUpdateView.as_view(), name='editar_dizimista'),
    path('dizimista/<int:pk>/excluir/', views.DizimistaDeleteView.as_view(), name='excluir_dizimista'),
    
    path('pagamentos/', views.PagamentoListView.as_view(), name='listar_pagamentos'),
    path('pagamento/novo/', views.PagamentoCreateView.as_view(), name='registrar_pagamento'),
    path('pagamento/<int:pk>/editar/', views.PagamentoUpdateView.as_view(), name='editar_pagamento'),
    path('pagamento/<int:pk>/excluir/', views.PagamentoDeleteView.as_view(), name='excluir_pagamento'),
    
    path('usuarios/', views.UsuarioListView.as_view(), name='listar_usuarios'),
    path('usuarios/novo/', views.UsuarioCreateView.as_view(), name='cadastrar_usuario'),
    path('usuarios/<int:pk>/excluir/', views.UsuarioDeleteView.as_view(), name='excluir_usuario'),
    
    path('exportar/', views.exportar_pagamentos_csv, name='exportar_csv'),
]
