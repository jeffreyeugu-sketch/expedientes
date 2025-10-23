// ============================================
// JAVASCRIPT COMPLETO PARA DETALLE DEL PACIENTE
// Y GESTIÓN DE CONSULTAS
// ============================================

// ===========================================
// FUNCIONES DE FILTRADO
// ===========================================

/**
 * Filtrar consultas por estado
 * @param {string} estado - Estado a filtrar: 'todas', 'completada', 'programada', 'en_curso', 'cancelada'
 */
function filtrarConsultas(estado) {
    const consultas = document.querySelectorAll('.consulta-timeline-item');
    const tabs = document.querySelectorAll('.filter-tab');
    
    // Actualizar tabs activos
    tabs.forEach(tab => {
        if (tab.dataset.filter === estado) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Contador de consultas visibles
    let consultasVisibles = 0;
    
    // Filtrar consultas con animación
    consultas.forEach((consulta, index) => {
        const consultaEstado = consulta.dataset.estado;
        
        if (estado === 'todas' || consultaEstado === estado) {
            consulta.style.display = 'flex';
            consultasVisibles++;
            
            // Re-animar
            consulta.style.animation = 'none';
            setTimeout(() => {
                consulta.style.animation = `slideIn 0.4s ease forwards ${index * 0.1}s`;
            }, 10);
        } else {
            consulta.style.display = 'none';
        }
    });
    
    // Actualizar mensaje si no hay resultados
    mostrarMensajeSinResultados(consultasVisibles);
    
    console.log(`Filtro aplicado: ${estado} - Consultas visibles: ${consultasVisibles}`);
}

/**
 * Mostrar mensaje cuando no hay consultas del filtro seleccionado
 * @param {number} cantidad - Cantidad de consultas visibles
 */
function mostrarMensajeSinResultados(cantidad) {
    const timeline = document.getElementById('consultasTimeline');
    const mensajeExistente = document.getElementById('mensajeNoResultados');
    
    // Remover mensaje anterior si existe
    if (mensajeExistente) {
        mensajeExistente.remove();
    }
    
    // Si no hay resultados, mostrar mensaje
    if (cantidad === 0) {
        const mensaje = document.createElement('div');
        mensaje.id = 'mensajeNoResultados';
        mensaje.className = 'alert alert-info text-center';
        mensaje.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>No hay consultas con este filtro</strong>
            <p class="mb-0 mt-2 text-muted">Intenta seleccionar otro estado</p>
        `;
        timeline.appendChild(mensaje);
    }
}

// ===========================================
// ACCIONES DE CONSULTAS - EDITAR
// ===========================================

/**
 * Editar una consulta programada
 * @param {number} consultaId - ID de la consulta a editar
 */
function editarConsulta(consultaId) {
    // Redirigir directamente a la página de edición
    window.location.href = `/consultas/${consultaId}/editar/`;
}

// ===========================================
// ACCIONES DE CONSULTAS - CANCELAR
// ===========================================

/**
 * Cancelar una consulta con modal de confirmación
 * @param {number} consultaId - ID de la consulta a cancelar
 * @param {string} nombrePaciente - Nombre del paciente
 */
function cancelarConsulta(consultaId, nombrePaciente) {
    // Crear modal de confirmación personalizado
    const modalHTML = `
        <div class="modal fade" id="modalCancelarConsulta" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Cancelar Consulta
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-warning">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Atención:</strong> Esta acción no se puede deshacer.
                        </div>
                        
                        <p class="mb-3">
                            ¿Estás seguro de que deseas cancelar la consulta de 
                            <strong>${nombrePaciente}</strong>?
                        </p>
                        
                        <div class="mb-3">
                            <label for="motivoCancelacion" class="form-label">
                                Motivo de cancelación <small class="text-muted">(opcional)</small>
                            </label>
                            <textarea 
                                class="form-control" 
                                id="motivoCancelacion" 
                                rows="3"
                                placeholder="Ej: Paciente solicitó reprogramar, Emergencia médica, etc."
                            ></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>No, mantener consulta
                        </button>
                        <button type="button" class="btn btn-danger" onclick="confirmarCancelacion(${consultaId})">
                            <i class="fas fa-ban me-2"></i>Sí, cancelar consulta
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agregar modal al body si no existe
    let modalExistente = document.getElementById('modalCancelarConsulta');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalCancelarConsulta'));
    modal.show();
}

/**
 * Confirmar y ejecutar la cancelación
 * @param {number} consultaId - ID de la consulta
 */
function confirmarCancelacion(consultaId) {
    const motivo = document.getElementById('motivoCancelacion').value.trim();
    const modal = bootstrap.Modal.getInstance(document.getElementById('modalCancelarConsulta'));
    const botonCancelar = document.querySelector('#modalCancelarConsulta .btn-danger');
    
    // Deshabilitar botón y mostrar loading
    botonCancelar.disabled = true;
    botonCancelar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Cancelando...';
    
    // Obtener CSRF token
    const csrftoken = getCookie('csrftoken');
    
    // Enviar petición AJAX
    fetch(`/consultas/${consultaId}/cancelar/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            motivo: motivo
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            modal.hide();
            
            // Mostrar notificación de éxito
            mostrarNotificacion('Consulta cancelada exitosamente', 'success');
            
            // Actualizar la interfaz
            actualizarConsultaCancelada(consultaId, motivo);
            
            // Recargar la página después de 2 segundos para ver los cambios
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            throw new Error(data.message || 'Error al cancelar consulta');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion(error.message || 'Error al cancelar la consulta', 'error');
        
        // Rehabilitar botón
        botonCancelar.disabled = false;
        botonCancelar.innerHTML = '<i class="fas fa-ban me-2"></i>Sí, cancelar consulta';
    });
}

/**
 * Actualizar la UI cuando se cancela una consulta (sin recargar)
 * @param {number} consultaId - ID de la consulta
 * @param {string} motivo - Motivo de cancelación
 */
function actualizarConsultaCancelada(consultaId, motivo) {
    // Buscar el elemento de la consulta en el timeline
    const consultas = document.querySelectorAll('.consulta-timeline-item');
    
    consultas.forEach(consulta => {
        // Buscar por el ID en los botones
        const verDetallesBtn = consulta.querySelector(`a[href*="/${consultaId}/"]`);
        
        if (verDetallesBtn) {
            // Cambiar el data-estado
            consulta.dataset.estado = 'cancelada';
            
            // Actualizar el badge de estado
            const badge = consulta.querySelector('.badge');
            if (badge) {
                badge.className = 'badge status-cancelada';
                badge.textContent = 'Cancelada';
            }
            
            // Actualizar el marcador del timeline
            const marker = consulta.querySelector('.consulta-timeline-marker i');
            if (marker) {
                marker.className = 'fas fa-times-circle';
            }
            
            // Actualizar el cuerpo de la consulta
            const body = consulta.querySelector('.consulta-timeline-body');
            if (body) {
                const alertHTML = `
                    <div class="alert alert-danger mt-3 mb-0">
                        <i class="fas fa-times-circle me-2"></i>
                        <strong>Consulta cancelada</strong>
                        ${motivo ? `<br><small>Motivo: ${motivo}</small>` : ''}
                    </div>
                `;
                
                // Buscar si ya existe un alert y reemplazarlo, o agregarlo
                const alertExistente = body.querySelector('.alert');
                if (alertExistente) {
                    alertExistente.outerHTML = alertHTML;
                } else {
                    body.insertAdjacentHTML('beforeend', alertHTML);
                }
            }
            
            // Actualizar los botones de acción
            const actions = consulta.querySelector('.consulta-timeline-actions');
            if (actions) {
                // Remover botones de editar/cancelar
                const botonesEditar = actions.querySelectorAll('.btn-outline-warning, .btn-outline-danger');
                botonesEditar.forEach(btn => btn.remove());
                
                // Agregar botón de "Cancelada" deshabilitado si no existe
                if (!actions.querySelector('.btn-outline-secondary')) {
                    const btnCancelada = document.createElement('button');
                    btnCancelada.className = 'btn btn-sm btn-outline-secondary';
                    btnCancelada.disabled = true;
                    btnCancelada.innerHTML = '<i class="fas fa-ban me-1"></i>Cancelada';
                    actions.appendChild(btnCancelada);
                }
            }
            
            // Aplicar efecto visual
            consulta.style.opacity = '0.7';
            consulta.style.transition = 'opacity 0.3s ease';
        }
    });
    
    // Actualizar contadores
    actualizarContadores();
}

/**
 * Actualizar los contadores de estados
 */
function actualizarContadores() {
    // Contar consultas por estado
    const contadores = {
        todas: 0,
        completada: 0,
        programada: 0,
        en_curso: 0,
        cancelada: 0
    };
    
    document.querySelectorAll('.consulta-timeline-item').forEach(consulta => {
        const estado = consulta.dataset.estado;
        contadores.todas++;
        if (contadores[estado] !== undefined) {
            contadores[estado]++;
        }
    });
    
    // Actualizar badges en los filtros
    document.querySelectorAll('.filter-tab').forEach(tab => {
        const filter = tab.dataset.filter;
        const badge = tab.querySelector('.badge');
        if (badge && contadores[filter] !== undefined) {
            badge.textContent = contadores[filter];
        }
    });
    
    // Actualizar quick stats
    const quickStats = document.querySelectorAll('.quick-stat-number');
    if (quickStats.length >= 4) {
        quickStats[0].textContent = contadores.completada;
        quickStats[1].textContent = contadores.programada;
        quickStats[2].textContent = contadores.en_curso;
        if (quickStats[3]) {
            quickStats[3].textContent = contadores.cancelada;
        }
    }
}

// ===========================================
// OTRAS ACCIONES DE CONSULTAS
// ===========================================

/**
 * Imprimir consulta completada
 * @param {number} consultaId - ID de la consulta a imprimir
 */
function imprimirConsulta(consultaId) {
    console.log('Imprimiendo consulta:', consultaId);
    
    // Por ahora, abrir en nueva ventana (implementar PDF después)
    window.open(`/consultas/${consultaId}/imprimir/`, '_blank');
    
    // TODO: Implementar generación de PDF
}

/**
 * Cargar más consultas (paginación)
 */
function cargarMasConsultas() {
    const boton = document.querySelector('.load-more-btn .btn');
    const textoOriginal = boton.innerHTML;
    
    // Mostrar estado de carga
    boton.disabled = true;
    boton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Cargando...';
    
    // Simulación de carga (reemplazar con AJAX real)
    setTimeout(() => {
        boton.innerHTML = textoOriginal;
        boton.disabled = false;
        mostrarNotificacion('Funcionalidad de paginación próximamente', 'info');
    }, 1500);
    
    // TODO: Implementar carga AJAX real
}

// ===========================================
// ACCIONES DEL PACIENTE
// ===========================================

/**
 * Editar información del paciente
 */
function editarPaciente() {
    const pacienteId = window.location.pathname.split('/')[2];
    
    if (confirm('¿Deseas editar la información del paciente?')) {
        window.location.href = `/pacientes/${pacienteId}/editar/`;
    }
}

// ===========================================
// UTILIDADES
// ===========================================

/**
 * Obtener cookie CSRF para peticiones AJAX
 * @param {string} name - Nombre de la cookie
 * @returns {string} Valor de la cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Mostrar notificación toast
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo: 'success', 'error', 'info', 'warning'
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    const colores = {
        success: '#28a745',
        error: '#dc3545',
        info: '#17a2b8',
        warning: '#ffc107'
    };
    
    const iconos = {
        success: 'check-circle',
        error: 'times-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle'
    };
    
    const notificacion = document.createElement('div');
    notificacion.className = 'toast-notification';
    notificacion.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        border-left: 4px solid ${colores[tipo]};
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
    
    notificacion.innerHTML = `
        <i class="fas fa-${iconos[tipo]} me-2" style="color: ${colores[tipo]}"></i>
        <strong>${mensaje}</strong>
    `;
    
    document.body.appendChild(notificacion);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        notificacion.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notificacion.remove(), 300);
    }, 3000);
}

// ===========================================
// INICIALIZACIÓN
// ===========================================

/**
 * Inicializar cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Detalle de paciente cargado');
    
    // Contar consultas
    const totalConsultas = document.querySelectorAll('.consulta-timeline-item').length;
    console.log(`Total de consultas en el historial: ${totalConsultas}`);
    
    // Detectar si hay consultas recientes para resaltar
    resaltarConsultasRecientes();
    
    // Inicializar tooltips de Bootstrap si existen
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    console.log('✓ Sistema de historial médico iniciado');
});

/**
 * Resaltar consultas recientes (últimos 7 días)
 */
function resaltarConsultasRecientes() {
    const consultas = document.querySelectorAll('.consulta-timeline-item');
    const ahora = new Date();
    const hace7Dias = new Date(ahora.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    consultas.forEach(consulta => {
        // Aquí podrías agregar lógica para identificar consultas recientes
        // y agregar una clase especial o badge de "NUEVO"
    });
}

// ===========================================
// ANIMACIONES CSS
// ===========================================

// Agregar estilos de animación para las notificaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);

// ===========================================
// EXPORTAR FUNCIONES PARA USO GLOBAL
// ===========================================

window.HistorialPaciente = {
    filtrarConsultas,
    editarConsulta,
    cancelarConsulta,
    imprimirConsulta,
    cargarMasConsultas,
    editarPaciente,
    mostrarNotificacion,
    actualizarContadores
};

console.log('✓ Módulo HistorialPaciente cargado correctamente');