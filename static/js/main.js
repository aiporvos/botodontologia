/**
 * Dental Studio Pro - JavaScript Compartido
 * Maneja autenticación, peticiones API y utilidades
 */

// Configuración
const CONFIG = {
    API_BASE_URL: '',
    TOKEN_KEY: 'dental_access_token',
    REFRESH_BEFORE: 5 * 60 * 1000 // 5 minutos antes de expirar
};

// Utilidad para obtener token
dentalStudio.token = localStorage.getItem(CONFIG.TOKEN_KEY);
            },
            
            clear: () => {
                localStorage.removeItem(CONFIG.TOKEN_KEY);
                dentalStudio.token = null;
            }
        };

        // Mostrar error
        dentalStudio.showError = (message) => {
            // Crear alerta temporal
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
            alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
            alert.innerHTML = `
                <i class="fas fa-exclamation-circle me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        };

        // Mostrar éxito
        dentalStudio.showSuccess = (message) => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
            alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
            alert.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 3000);
        };

        // Verificar si usuario está autenticado
        dentalStudio.isAuthenticated = () => {
            return !!dentalStudio.auth.getToken();
        };

        // Logout
        dentalStudio.logout = () => {
            dentalStudio.auth.clear();
            window.location.href = '/login';
        };

        // Inicializar
        dentalStudio.token = dentalStudio.auth.getToken();

        // Agregar botón de logout al sidebar si existe
        const sidebarNav = document.querySelector('.sidebar-nav');
        if (sidebarNav && !document.getElementById('logout-link')) {
            const logoutLink = document.createElement('a');
            logoutLink.id = 'logout-link';
            logoutLink.href = '#';
            logoutLink.innerHTML = '<i class="fas fa-sign-out-alt"></i> Cerrar Sesión';
            logoutLink.onclick = (e) => {
                e.preventDefault();
                dentalStudio.logout();
            };
            logoutLink.style.cssText = 'color: rgba(255,255,255,0.6); margin-top: 20px;';
            sidebarNav.appendChild(logoutLink);
        }

        // Marcar link activo
        const currentPath = window.location.pathname;
        document.querySelectorAll('.sidebar-nav a').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        console.log('Dental Studio Pro - Sistema inicializado');
    });
})();
