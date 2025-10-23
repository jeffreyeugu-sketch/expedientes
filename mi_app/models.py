# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date

class Doctor(models.Model):
    """Modelo para doctores/médicos"""
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula_profesional = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"
        
    def __str__(self):
        return f"Dr. {self.nombres} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

class Patient(models.Model):
    """Modelo principal para pacientes"""
    
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('no_especifica', 'Prefiero no especificar'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
        ('union_libre', 'Unión libre'),
    ]
    
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('desconocido', 'Desconocido'),
    ]
    
    # Datos personales
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, verbose_name="Género")
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, verbose_name="Estado Civil")
    ocupacion = models.CharField(max_length=100, blank=True, verbose_name="Ocupación")
    documento_id = models.CharField(max_length=50, unique=True, verbose_name="Documento de Identidad")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    
    # Información médica
    tipo_sangre = models.CharField(max_length=11, choices=TIPO_SANGRE_CHOICES, blank=True, verbose_name="Tipo de Sangre")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    altura = models.IntegerField(null=True, blank=True, verbose_name="Altura (cm)")
    alergias = models.TextField(blank=True, verbose_name="Alergias")
    medicamentos_actuales = models.TextField(blank=True, verbose_name="Medicamentos Actuales")
    enfermedades_cronicas = models.TextField(blank=True, verbose_name="Enfermedades Crónicas")
    antecedentes_familiares = models.TextField(blank=True, verbose_name="Antecedentes Familiares")
    fuma = models.CharField(max_length=10, choices=[('si', 'Sí'), ('no', 'No'), ('ocasional', 'Ocasional')], blank=True)
    alcohol = models.CharField(max_length=10, choices=[('si', 'Sí'), ('no', 'No'), ('ocasional', 'Ocasional')], blank=True)
    
    # Contacto
    telefono_principal = models.CharField(max_length=20, verbose_name="Teléfono Principal")
    telefono_alternativo = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Alternativo")
    email = models.EmailField(blank=True, verbose_name="Email")
    email_alternativo = models.EmailField(blank=True, verbose_name="Email Alternativo")
    
    # Contacto de emergencia
    emergencia_nombre = models.CharField(max_length=100, verbose_name="Contacto de Emergencia")
    emergencia_parentesco = models.CharField(max_length=50, verbose_name="Parentesco")
    emergencia_telefono = models.CharField(max_length=20, verbose_name="Teléfono de Emergencia")
    emergencia_telefono2 = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Emergencia 2")
    
    # Seguro médico
    seguro_medico = models.CharField(max_length=100, blank=True, verbose_name="Seguro Médico")
    numero_poliza = models.CharField(max_length=50, blank=True, verbose_name="Número de Póliza")
    
    # Control interno
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['apellidos', 'nombres']
        
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    @property
    def estado_paciente(self):
        """Determina si el paciente está activo, nuevo, etc."""
        from datetime import timedelta, date
        
        hoy = date.today()
        
        # Si es nuevo (registrado hace menos de 30 días)
        if self.fecha_registro.date() > hoy - timedelta(days=30):
            return 'nuevo'
        
        return 'activo'

class Consultation(models.Model):
    """Modelo para consultas médicas"""
    
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió'),
    ]
    
    TIPO_CHOICES = [
        ('general', 'Consulta General'),
        ('seguimiento', 'Seguimiento'),
        ('urgencia', 'Urgencia'),
        ('control', 'Control'),
        ('primera_vez', 'Primera Vez'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Doctor")
    fecha_consulta = models.DateTimeField(verbose_name="Fecha y Hora")
    tipo_consulta = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Consulta")
    motivo = models.TextField(verbose_name="Motivo de la Consulta")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programada', verbose_name="Estado")
    
    # Información clínica (se llena durante/después de la consulta)
    sintomas = models.TextField(blank=True, verbose_name="Síntomas")
    exploracion_fisica = models.TextField(blank=True, verbose_name="Exploración Física")
    diagnostico = models.TextField(blank=True, verbose_name="Diagnóstico")
    tratamiento = models.TextField(blank=True, verbose_name="Tratamiento")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    proxima_cita = models.DateField(null=True, blank=True, verbose_name="Próxima Cita")
    
    # Signos vitales
    presion_arterial = models.CharField(max_length=20, blank=True, verbose_name="Presión Arterial")
    frecuencia_cardiaca = models.IntegerField(null=True, blank=True, verbose_name="Frecuencia Cardíaca")
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Temperatura")
    peso_consulta = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso en Consulta")
    
    # Control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['-fecha_consulta']
        
    def __str__(self):
        return f"{self.patient.nombre_completo} - {self.fecha_consulta.strftime('%d/%m/%Y %H:%M')}"

class MedicalRecord(models.Model):
    """Historial médico detallado"""
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    
    # Antecedentes médicos detallados
    cirugias_previas = models.TextField(blank=True, verbose_name="Cirugías Previas")
    hospitalizaciones = models.TextField(blank=True, verbose_name="Hospitalizaciones")
    traumatismos = models.TextField(blank=True, verbose_name="Traumatismos")
    
    # Antecedentes gineco-obstétricos (para mujeres)
    menarquia = models.CharField(max_length=50, blank=True, verbose_name="Menarquía")
    ciclo_menstrual = models.CharField(max_length=100, blank=True, verbose_name="Ciclo Menstrual")
    embarazos = models.IntegerField(null=True, blank=True, verbose_name="Embarazos")
    partos = models.IntegerField(null=True, blank=True, verbose_name="Partos")
    cesareas = models.IntegerField(null=True, blank=True, verbose_name="Cesáreas")
    abortos = models.IntegerField(null=True, blank=True, verbose_name="Abortos")
    
    # Notas importantes
    notas_importantes = models.TextField(blank=True, verbose_name="Notas Importantes")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Expediente Médico"
        verbose_name_plural = "Expedientes Médicos"
        
    def __str__(self):
        return f"Expediente de {self.patient.nombre_completo}"
    

class Prescription(models.Model):
    """Modelo para recetas médicas"""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, verbose_name="Consulta")
    medicamento = models.CharField(max_length=200, verbose_name="Medicamento")
    dosis = models.CharField(max_length=100, verbose_name="Dosis")
    frecuencia = models.CharField(max_length=100, verbose_name="Frecuencia")
    duracion = models.CharField(max_length=100, verbose_name="Duración del Tratamiento")
    indicaciones = models.TextField(blank=True, verbose_name="Indicaciones Especiales")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"{self.medicamento} - {self.consultation.patient.nombre_completo}"