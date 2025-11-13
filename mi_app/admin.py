from django.contrib import admin
from .models import Payment, Invoice, ConceptoFactura

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'consultation', 'monto_total', 'monto_pagado', 'estado', 'metodo_pago', 'fecha_creacion']
    list_filter = ['estado', 'metodo_pago', 'fecha_creacion']
    search_fields = ['consultation__patient__nombres', 'consultation__patient__apellidos', 'referencia']
    date_hierarchy = 'fecha_creacion'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['folio', 'cliente_nombre', 'total', 'tipo_comprobante', 'cancelada', 'fecha_emision']
    list_filter = ['tipo_comprobante', 'cancelada', 'fecha_emision']
    search_fields = ['folio', 'cliente_nombre', 'cliente_rfc']
    date_hierarchy = 'fecha_emision'

@admin.register(ConceptoFactura)
class ConceptoFacturaAdmin(admin.ModelAdmin):
    list_display = ['factura', 'descripcion', 'cantidad', 'precio_unitario', 'importe']
    search_fields = ['descripcion', 'factura__folio']

# Register your models here.
