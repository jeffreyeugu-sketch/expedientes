from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
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
]