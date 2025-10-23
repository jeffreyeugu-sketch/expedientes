# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import Patient, Doctor, Consultation, MedicalRecord
from datetime import datetime, timedelta, date
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Consultation
import json


def lista_pacientes(request):
    """Lista de todos los pacientes desde la base de datos"""
    
    # Obtener pacientes reales de la base de datos
    pacientes = Patient.objects.filter(activo=True).order_by('-fecha_registro')
    
    # Preparar datos para el template de forma simple
    pacientes_data = []
    hoy = date.today()
    hace_30_dias = hoy - timedelta(days=30)
    
    for paciente in pacientes:
        # Determinar estado simple
        if paciente.fecha_registro.date() >= hace_30_dias:
            estado = 'nuevo'
        else:
            estado = 'activo'
        
        pacientes_data.append({
            'id': paciente.id,
            'nombre': paciente.nombre_completo,
            'edad': paciente.edad,
            'telefono': paciente.telefono_principal,
            'email': paciente.email or 'Sin email',
            'ultima_consulta': 'Sin consultas',
            'dias_desde_consulta': 0,
            'estado': estado,
        })
    
    # Estadísticas reales
    ahora = datetime.now()
    total_pacientes = Patient.objects.filter(activo=True).count()
    nuevos_mes = Patient.objects.filter(
        activo=True,
        fecha_registro__month=ahora.month,
        fecha_registro__year=ahora.year
    ).count()
    
    context = {
        'pacientes': pacientes_data,
        'total_pacientes': total_pacientes,
        'nuevos_mes': nuevos_mes,
        'activos_mes': total_pacientes,
        'citas_pendientes': 0,
    }
    return render(request, 'mi_app/lista_pacientes.html', context)

def dashboard(request):
    """Dashboard con datos reales de la base de datos"""
    
    ahora = datetime.now()
    total_pacientes = Patient.objects.filter(activo=True).count()
    pacientes_nuevos = Patient.objects.filter(
        fecha_registro__month=ahora.month,
        fecha_registro__year=ahora.year
    ).count()
    
    context = {
        'total_pacientes': total_pacientes,
        'consultas_hoy': 0,  # Por implementar
        'consultas_semana': 0,  # Por implementar  
        'pacientes_nuevos': pacientes_nuevos,
    }
    return render(request, 'mi_app/dashboard.html', context)

def nuevo_paciente(request):
    """Formulario para registrar nuevo paciente"""
    if request.method == 'POST':
        try:
            # Crear el paciente con todos los datos del formulario
            patient = Patient.objects.create(
                # Datos personales
                nombres=request.POST.get('nombres'),
                apellidos=request.POST.get('apellidos'),
                fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                genero=request.POST.get('genero'),
                ocupacion=request.POST.get('ocupacion', ''),
                documento_id=request.POST.get('documento_id'),
                direccion=request.POST.get('direccion', ''),
                
                # Información médica
                tipo_sangre=request.POST.get('tipo_sangre', ''),
                peso=request.POST.get('peso') or None,
                altura=request.POST.get('altura') or None,
                alergias=request.POST.get('alergias', ''),
                medicamentos_actuales=request.POST.get('medicamentos_actuales', ''),
                
                # Contacto
                telefono_principal=request.POST.get('telefono_principal'),
                email=request.POST.get('email', ''),
                
                # Contacto de emergencia
                emergencia_nombre=request.POST.get('emergencia_nombre'),
                emergencia_parentesco=request.POST.get('emergencia_parentesco'),
                emergencia_telefono=request.POST.get('emergencia_telefono'),
                
                # Seguro médico
                seguro_medico=request.POST.get('seguro_medico', ''),
            )
            
            # Crear expediente médico vacío
            MedicalRecord.objects.create(patient=patient)
            
            # Mostrar mensaje de éxito
            messages.success(request, f'Paciente {patient.nombre_completo} registrado exitosamente. ID: #{patient.id:04d}')
            
            # Redirigir al mismo formulario para ver el mensaje
            return render(request, 'mi_app/nuevo_paciente_simple.html')
            
        except Exception as e:
            # Si hay error, mostrar mensaje
            messages.error(request, f'Error al registrar paciente: {str(e)}')
            print(f"Error: {e}")  # Para debugging
    
    # Si es GET, mostrar el formulario
    return render(request, 'mi_app/nuevo_paciente_simple.html')

def detalle_paciente(request, paciente_id):
    """Detalle completo del paciente con historial de consultas mejorado - ACTUALIZADO"""
    try:
        paciente = Patient.objects.get(id=paciente_id)
        
        # Obtener TODAS las consultas del paciente ordenadas por fecha descendente
        consultas = Consultation.objects.filter(
            patient=paciente
        ).select_related('doctor').order_by('-fecha_consulta')
        
        # Separar consultas por estado (INCLUIR CANCELADAS)
        consultas_completadas = consultas.filter(estado='completada')
        consultas_programadas = consultas.filter(estado='programada')
        consultas_en_curso = consultas.filter(estado='en_curso')
        consultas_canceladas = consultas.filter(estado='cancelada')  # ← AGREGAR ESTA LÍNEA
        
        # Obtener expediente médico
        try:
            expediente = MedicalRecord.objects.get(patient=paciente)
        except MedicalRecord.DoesNotExist:
            expediente = MedicalRecord.objects.create(patient=paciente)
        
        # Estadísticas del paciente
        total_consultas = consultas.count()
        ultima_consulta = consultas_completadas.first()
        proxima_consulta = consultas_programadas.first()
        
        # Calcular días desde última consulta
        dias_desde_ultima = None
        if ultima_consulta:
            from datetime import date
            dias_desde_ultima = (date.today() - ultima_consulta.fecha_consulta.date()).days
        
        context = {
            'paciente': paciente,
            'consultas': consultas[:20],  # Primeras 20 para mostrar inicialmente
            'consultas_completadas': consultas_completadas,
            'consultas_programadas': consultas_programadas,
            'consultas_en_curso': consultas_en_curso,
            'consultas_canceladas': consultas_canceladas,  # ← AGREGAR ESTA LÍNEA
            'expediente': expediente,
            'total_consultas': total_consultas,
            'ultima_consulta': ultima_consulta,
            'proxima_consulta': proxima_consulta,
            'dias_desde_ultima': dias_desde_ultima,
        }
        return render(request, 'mi_app/detalle_paciente.html', context)
        
    except Patient.DoesNotExist:
        messages.error(request, 'Paciente no encontrado')
        return redirect('lista_pacientes')

def lista_consultas(request):
    """Lista de consultas"""
    consultas_ejemplo = [
        {'id': 1, 'paciente': 'Juan Pérez', 'fecha': '2025-09-25', 'hora': '10:00', 'motivo': 'Consulta general'},
        {'id': 2, 'paciente': 'María González', 'fecha': '2025-09-25', 'hora': '11:30', 'motivo': 'Seguimiento'},
        {'id': 3, 'paciente': 'Carlos López', 'fecha': '2025-09-25', 'hora': '14:00', 'motivo': 'Dolor de cabeza'},
    ]
    context = {'consultas': consultas_ejemplo}
    return render(request, 'mi_app/lista_consultas.html', context)

def agenda_consultas(request):
    """Vista de agenda - consultas del día"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    from zoneinfo import ZoneInfo
    
    # Obtener fecha/hora actual en México
    mexico_tz = ZoneInfo('America/Mexico_City')
    ahora_mexico = timezone.now().astimezone(mexico_tz)
    hoy = ahora_mexico.date()
    
    # Crear rango del día en timezone de México
    inicio_dia = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=mexico_tz)
    fin_dia = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=mexico_tz)
    
    # Consultas de hoy
    consultas_hoy = Consultation.objects.filter(
        fecha_consulta__gte=inicio_dia,
        fecha_consulta__lte=fin_dia,
        estado__in=['programada', 'en_curso']
    ).select_related('patient', 'doctor').order_by('fecha_consulta')
    
    # Próximas consultas (próximos 7 días)
    inicio_manana = fin_dia + timedelta(seconds=1)
    fin_proximos_7_dias = datetime.combine(
        hoy + timedelta(days=7), 
        datetime.max.time()
    ).replace(tzinfo=mexico_tz)
    
    proximas_consultas = Consultation.objects.filter(
        fecha_consulta__gte=inicio_manana,
        fecha_consulta__lte=fin_proximos_7_dias,
        estado='programada'
    ).select_related('patient', 'doctor').order_by('fecha_consulta')
    
    # Estadísticas del día
    total_hoy = consultas_hoy.count()
    completadas_hoy = Consultation.objects.filter(
        fecha_consulta__gte=inicio_dia,
        fecha_consulta__lte=fin_dia,
        estado='completada'
    ).count()
    pendientes_hoy = consultas_hoy.filter(estado='programada').count()
    
    context = {
        'consultas_hoy': consultas_hoy,
        'proximas_consultas': proximas_consultas,
        'fecha_hoy': hoy,
        'total_hoy': total_hoy,
        'completadas_hoy': completadas_hoy,
        'pendientes_hoy': pendientes_hoy,
    }
    
    return render(request, 'mi_app/agenda_consultas.html', context)

def nueva_consulta(request):
    """Formulario para programar nueva consulta"""
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            tipo_consulta = request.POST.get('tipo_consulta')
            motivo = request.POST.get('motivo')
            
            # Validaciones básicas
            if not all([patient_id, doctor_id, fecha, hora, tipo_consulta, motivo]):
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('nueva_consulta')
            
            # Convertir hora al formato correcto
            if len(hora) == 5:
                hora = hora + ":00"
            
            fecha_hora_str = f"{fecha} {hora}"
            
            # Crear datetime y hacer timezone aware
            from django.utils import timezone
            fecha_hora_naive = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
            fecha_hora = timezone.make_aware(fecha_hora_naive)
            
            # Verificar que no sea en el pasado
            if fecha_hora < timezone.now():
                messages.error(request, 'No se puede programar una consulta en el pasado')
                return redirect('nueva_consulta')
            
            # Crear consulta
            consulta = Consultation.objects.create(
                patient_id=int(patient_id),
                doctor_id=int(doctor_id),
                fecha_consulta=fecha_hora,
                tipo_consulta=tipo_consulta,
                motivo=motivo,
                estado='programada'
            )
            
            # CAMBIO: Mostrar mensaje y renderizar template (no redirigir)
            messages.success(
                request, 
                f'Consulta programada exitosamente para {consulta.patient.nombre_completo} '
                f'el {consulta.fecha_consulta.strftime("%d/%m/%Y a las %H:%M")}'
            )
            
            # Renderizar template con el mensaje (modal se mostrará automáticamente)
            context = {
                'pacientes': Patient.objects.filter(activo=True).order_by('apellidos', 'nombres'),
                'doctores': Doctor.objects.filter(activo=True).order_by('apellidos', 'nombres'),
                'fecha_hoy': datetime.now().date(),
            }
            return render(request, 'mi_app/nueva_consulta.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al programar consulta: {str(e)}')
    
    # Contexto para GET
    context = {
        'pacientes': Patient.objects.filter(activo=True).order_by('apellidos', 'nombres'),
        'doctores': Doctor.objects.filter(activo=True).order_by('apellidos', 'nombres'),
        'fecha_hoy': datetime.now().date(),
    }
    
    return render(request, 'mi_app/nueva_consulta.html', context)

def get_nueva_consulta_context():
    """Helper function para obtener contexto de nueva consulta"""
    return {
        'pacientes': Patient.objects.filter(activo=True).order_by('apellidos', 'nombres'),
        'doctores': Doctor.objects.filter(activo=True).order_by('apellidos', 'nombres'),
        'fecha_hoy': datetime.now().date(),
    }

def detalle_consulta(request, consulta_id):
    """Vista detallada de una consulta específica"""
    try:
        consulta = Consultation.objects.select_related('patient', 'doctor').get(id=consulta_id)
        
        if request.method == 'POST':
            try:
                # Actualizar signos vitales
                consulta.presion_arterial = request.POST.get('presion_arterial', '')
                
                # Manejar campos numéricos que pueden estar vacíos
                frecuencia = request.POST.get('frecuencia_cardiaca', '')
                consulta.frecuencia_cardiaca = int(frecuencia) if frecuencia else None
                
                temperatura = request.POST.get('temperatura', '')
                consulta.temperatura = float(temperatura) if temperatura else None
                
                peso = request.POST.get('peso_consulta', '')
                consulta.peso_consulta = float(peso) if peso else None
                
                # Actualizar información médica
                consulta.sintomas = request.POST.get('sintomas', '')
                consulta.exploracion_fisica = request.POST.get('exploracion_fisica', '')
                consulta.diagnostico = request.POST.get('diagnostico', '')
                consulta.tratamiento = request.POST.get('tratamiento', '')
                consulta.observaciones = request.POST.get('observaciones', '')
                
                # Próxima cita
                proxima_cita = request.POST.get('proxima_cita', '')
                if proxima_cita:
                    consulta.proxima_cita = proxima_cita
                else:
                    consulta.proxima_cita = None
                
                # Determinar estado de la consulta
                if consulta.diagnostico.strip():
                    # Si tiene diagnóstico, marcar como completada
                    consulta.estado = 'completada'
                elif consulta.sintomas.strip() or consulta.exploracion_fisica.strip():
                    # Si tiene síntomas o exploración, está en curso
                    consulta.estado = 'en_curso'
                # Si no tiene nada, mantener estado actual
                
                consulta.save()
                
                # Actualizar peso del paciente si se registró
                if consulta.peso_consulta:
                    consulta.patient.peso = consulta.peso_consulta
                    consulta.patient.save()
                
                messages.success(request, f'Consulta actualizada exitosamente - Estado: {consulta.get_estado_display()}')
                
                # Si se completó, redirigir a agenda
                if consulta.estado == 'completada':
                    messages.success(request, '¡Consulta completada! Se ha guardado en el expediente del paciente.')
                    return redirect('agenda_consultas')
                
            except ValueError as e:
                messages.error(request, f'Error en los datos numéricos: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error al guardar consulta: {str(e)}')
                print(f"Error en detalle_consulta: {e}")
        
        context = {
            'consulta': consulta,
        }
        return render(request, 'mi_app/detalle_consulta.html', context)
        
    except Consultation.DoesNotExist:
        messages.error(request, 'Consulta no encontrada')
        return redirect('agenda_consultas')
    
@require_POST
def cancelar_consulta(request, consulta_id):
    """Cancelar una consulta programada"""
    try:
        consulta = get_object_or_404(Consultation, id=consulta_id)
        
        # Solo se pueden cancelar consultas programadas o en curso
        if consulta.estado not in ['programada', 'en_curso']:
            return JsonResponse({
                'success': False,
                'message': f'No se puede cancelar una consulta con estado: {consulta.get_estado_display()}'
            }, status=400)
        
        # Obtener motivo de cancelación desde el request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            motivo = data.get('motivo', '')
        else:
            motivo = request.POST.get('motivo', '')
        
        # Cambiar estado a cancelada
        consulta.estado = 'cancelada'
        
        # Agregar motivo a observaciones
        if motivo:
            if consulta.observaciones:
                consulta.observaciones += f"\n\n--- CANCELACIÓN ---\nMotivo: {motivo}"
            else:
                consulta.observaciones = f"CONSULTA CANCELADA\nMotivo: {motivo}"
        else:
            if consulta.observaciones:
                consulta.observaciones += f"\n\n--- CONSULTA CANCELADA ---"
            else:
                consulta.observaciones = "CONSULTA CANCELADA"
        
        consulta.save()
        
        # Si es petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Consulta cancelada exitosamente',
                'consulta_id': consulta.id,
                'nuevo_estado': consulta.estado
            })
        else:
            # Si es petición normal, redirigir con mensaje
            messages.success(request, f'Consulta cancelada exitosamente.')
            return redirect('detalle_paciente', paciente_id=consulta.patient.id)
            
    except Consultation.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Consulta no encontrada'
            }, status=404)
        else:
            messages.error(request, 'Consulta no encontrada')
            return redirect('lista_pacientes')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al cancelar consulta: {str(e)}'
            }, status=500)
        else:
            messages.error(request, f'Error al cancelar consulta: {str(e)}')
            return redirect('lista_pacientes')

# -*- coding: utf-8 -*-
# VERIFICAR QUE ESTOS IMPORTS ESTÉN AL INICIO DE views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Patient, Doctor, Consultation, MedicalRecord
from datetime import datetime, timedelta, date
import json

# ============================================
# VERIFICAR QUE ESTA FUNCIÓN EXISTA EN views.py
# Si NO existe, copiarla completa
# ============================================

def editar_consulta(request, consulta_id):
    """Editar una consulta programada"""
    try:
        consulta = get_object_or_404(Consultation, id=consulta_id)
        
        # Solo se pueden editar consultas programadas
        if consulta.estado != 'programada':
            messages.error(
                request, 
                f'Solo se pueden editar consultas programadas. Esta consulta está: {consulta.get_estado_display()}'
            )
            return redirect('detalle_consulta', consulta_id=consulta.id)
        
        if request.method == 'POST':
            try:
                # Obtener datos del formulario
                patient_id = request.POST.get('patient_id')
                doctor_id = request.POST.get('doctor_id')
                fecha = request.POST.get('fecha')
                hora = request.POST.get('hora')
                tipo_consulta = request.POST.get('tipo_consulta')
                motivo = request.POST.get('motivo')
                observaciones_adicionales = request.POST.get('observaciones', '')
                
                # Validaciones básicas
                if not all([patient_id, doctor_id, fecha, hora, tipo_consulta, motivo]):
                    messages.error(request, 'Todos los campos obligatorios deben estar completos')
                    return redirect('editar_consulta', consulta_id=consulta.id)
                
                # Convertir hora al formato correcto
                if len(hora) == 5:
                    hora = hora + ":00"
                
                fecha_hora_str = f"{fecha} {hora}"
                
                # Crear datetime y hacer timezone aware
                fecha_hora_naive = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
                fecha_hora = timezone.make_aware(fecha_hora_naive)
                
                # Verificar que no sea en el pasado
                if fecha_hora < timezone.now():
                    messages.error(request, 'No se puede programar una consulta en el pasado')
                    return redirect('editar_consulta', consulta_id=consulta.id)
                
                # Verificar conflictos de horario (mismo doctor, misma fecha/hora)
                conflictos = Consultation.objects.filter(
                    doctor_id=doctor_id,
                    fecha_consulta=fecha_hora,
                    estado='programada'
                ).exclude(id=consulta.id)  # Excluir la consulta actual
                
                if conflictos.exists():
                    messages.error(
                        request, 
                        f'El Dr. {Doctor.objects.get(id=doctor_id).nombre_completo} ya tiene una consulta programada a esa hora'
                    )
                    return redirect('editar_consulta', consulta_id=consulta.id)
                
                # Guardar datos anteriores para historial
                datos_anteriores = {
                    'paciente': consulta.patient.nombre_completo,
                    'doctor': consulta.doctor.nombre_completo,
                    'fecha': consulta.fecha_consulta.strftime('%d/%m/%Y %H:%M'),
                    'tipo': consulta.get_tipo_consulta_display(),
                    'motivo': consulta.motivo
                }
                
                # Actualizar la consulta
                consulta.patient_id = int(patient_id)
                consulta.doctor_id = int(doctor_id)
                consulta.fecha_consulta = fecha_hora
                consulta.tipo_consulta = tipo_consulta
                consulta.motivo = motivo
                
                # Agregar nota de modificación a observaciones
                nota_cambio = f"\n\n--- CONSULTA EDITADA el {timezone.now().strftime('%d/%m/%Y %H:%M')} ---"
                nota_cambio += f"\nDatos anteriores:"
                nota_cambio += f"\n  - Doctor: {datos_anteriores['doctor']}"
                nota_cambio += f"\n  - Fecha: {datos_anteriores['fecha']}"
                nota_cambio += f"\n  - Tipo: {datos_anteriores['tipo']}"
                
                if observaciones_adicionales:
                    nota_cambio += f"\nMotivo del cambio: {observaciones_adicionales}"
                
                if consulta.observaciones:
                    consulta.observaciones += nota_cambio
                else:
                    consulta.observaciones = nota_cambio
                
                consulta.save()
                
                # Mensaje de éxito
                messages.success(
                    request, 
                    f'Consulta actualizada exitosamente. Nueva fecha: {consulta.fecha_consulta.strftime("%d/%m/%Y a las %H:%M")}'
                )
                
                # Redirigir al detalle del paciente
                return redirect('detalle_paciente', paciente_id=consulta.patient.id)
                
            except ValueError as e:
                messages.error(request, f'Error en los datos: {str(e)}')
                return redirect('editar_consulta', consulta_id=consulta.id)
            except Exception as e:
                messages.error(request, f'Error al actualizar consulta: {str(e)}')
                print(f"Error en editar_consulta: {e}")
                return redirect('editar_consulta', consulta_id=consulta.id)
        
        # GET - Mostrar formulario
        context = {
            'consulta': consulta,
            'pacientes': Patient.objects.filter(activo=True).order_by('apellidos', 'nombres'),
            'doctores': Doctor.objects.filter(activo=True).order_by('apellidos', 'nombres'),
            'fecha_hoy': date.today(),
            'es_edicion': True,
        }
        
        return render(request, 'mi_app/editar_consulta.html', context)
        
    except Consultation.DoesNotExist:
        messages.error(request, 'Consulta no encontrada')
        return redirect('agenda_consultas')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        print(f"Error general en editar_consulta: {e}")
        return redirect('agenda_consultas')
