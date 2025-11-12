from django.urls import path
from . import views

urlpatterns = [

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Perfil del usuario (AGREGAR ESTA LÍNEA)
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    
    # Pacientes
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.nuevo_paciente, name='nuevo_paciente'),
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    
    # Consultas - ORDEN IMPORTANTE: Las rutas específicas ANTES de las genéricas
    path('consultas/nueva/', views.nueva_consulta, name='nueva_consulta'),
    path('consultas/<int:consulta_id>/editar/', views.editar_consulta, name='editar_consulta'),
    path('consultas/<int:consulta_id>/cancelar/', views.cancelar_consulta, name='cancelar_consulta'),
    path('consultas/<int:consulta_id>/', views.detalle_consulta, name='detalle_consulta'),
    path('consultas/', views.agenda_consultas, name='agenda_consultas'),
    path('consultas/calendario/', views.calendario_consultas, name='calendario_consultas'),

    # Usuarios (nuevo)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/nuevo/', views.nuevo_usuario, name='nuevo_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),

    # Pagos y Facturación
    path('consultas/<int:consulta_id>/pago/', views.registrar_pago, name='registrar_pago'),
    path('pagos/', views.lista_pagos, name='lista_pagos'),
    path('pagos/<int:pago_id>/factura/', views.generar_factura, name='generar_factura'),
    path('facturas/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
]