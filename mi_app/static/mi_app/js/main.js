// Main JavaScript para Expedientes Clínicos

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar componentes
    initSearchBox();
    initPatientCards();
    initMobileMenu();
    initTooltips();
    
    console.log('MedApp - Sistema de Expedientes Clínicos cargado');
});

// Funcionalidad de búsqueda
function initSearchBox() {
    const searchBox = document.querySelector('.search-box');
    
    if (searchBox) {
        let searchTimeout;
        
        searchBox.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            // Debounce search
            searchTimeout = setTimeout(() => {
                if (query.length > 2) {
                    searchPatients(query);
                } else if (query.length === 0) {
                    clearSearchResults();
                }
            }, 300);
        });
        
        // Limpiar al hacer Escape
        searchBox.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                e.target.value = '';
                clearSearchResults();
            }
        });
    }
}

// Búsqueda de pacientes (placeholder - se conectará con backend)
function searchPatients(query) {
    console.log('Buscando pacientes:', query);
    
    // Aquí se hará la llamada AJAX al backend
    // Por ahora, solo log
    showSearchResults([
        { id: 1, name: 'Juan Pérez', age: 45 },
        { id: 2, name: 'María González', age: 32 }
    ]);
}

// Mostrar resultados de búsqueda
function showSearchResults(results) {
    // Implementar dropdown con resultados
    console.log('Resultados:', results);
}

// Limpiar resultados de búsqueda
function clearSearchResults() {
    console.log('Limpiando resultados de búsqueda');
}

// Funcionalidad de tarjetas de pacientes
function initPatientCards() {
    const patientCards = document.querySelectorAll('.patient-card');
    
    patientCards.forEach(card => {
        card.addEventListener('click', function() {
            const patientId = this.dataset.patientId;
            if (patientId) {
                window.location.href = `/pacientes/${patientId}/`;
            }
        });
        
        // Efecto hover mejorado
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02) translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateY(0)';
        });
    });
}

// Menu móvil
function initMobileMenu() {
    // Toggle sidebar en móvil
    const toggleButton = document.querySelector('.mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (toggleButton && sidebar) {
        toggleButton.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Cerrar sidebar al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !toggleButton.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });
}

// Tooltips de Bootstrap
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

// Utilidades
const Utils = {
    // Formatear fecha
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Formatear teléfono
    formatPhone: function(phone) {
        // Formato: (555) 123-4567
        return phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    },
    
    // Mostrar notificación
    showNotification: function(message, type = 'info') {
        // Implementar sistema de notificaciones
        console.log(`${type.toUpperCase()}: ${message}`);
    },
    
    // Confirmar acción
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
};

// Funciones globales para usar en templates
window.MedApp = {
    Utils: Utils,
    searchPatients: searchPatients,
    showNotification: Utils.showNotification
};