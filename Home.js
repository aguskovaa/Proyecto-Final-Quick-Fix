const playButton = document.getElementById('playButton');
const videoModal = document.getElementById('videoModal');
const closeModal = document.getElementById('closeModal');
const videoFrame = document.getElementById('videoFrame');

playButton.addEventListener('click', () => {
    videoFrame.src = 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1';
    videoModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
});

closeModal.addEventListener('click', () => {
    videoFrame.src = '';
    videoModal.style.display = 'none';
    document.body.style.overflow = 'auto';
});


window.addEventListener('click', (e) => {
    if (e.target === videoModal) {
        videoFrame.src = '';
        videoModal.style.display = 'none';
        document.body.style.overflow = 'auto';// Función para actualizar la UI según el estado de sesión
function updateUI() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userType = localStorage.getItem('userType');
    const authButtons = document.getElementById('auth-buttons');
    const navContainer = document.querySelector('.nav');

    // Actualizar botones principales
    if (authButtons) {
        if (isLoggedIn && userType) {
            let mainButtonUrl, mainButtonText;
            
            if (userType === '1') { // Cliente
                mainButtonUrl = 'Browser.html';
                mainButtonText = 'Buscar Profesionales';
            } else { // Trabajador o Desempleado
                mainButtonUrl = 'AceptarTrabajos.html';
                mainButtonText = userType === '2' ? 'Buscar Trabajos' : 'Explorar Oportunidades';
            }

            authButtons.innerHTML = `
                <a href="${mainButtonUrl}" class="cta-button primary">
                    ${mainButtonText}
                    <i class="fas fa-arrow-right"></i>
                </a>
            `;
        } else {
            authButtons.innerHTML = `
                <a href="Inicio de Sesion.html" class="cta-button primary">
                    Iniciar sesión
                    <i class="fas fa-sign-in-alt"></i>
                </a>
                <a href="Registro.html" class="cta-button secondary">
                    Registrarse
                </a>
            `;
        }
    }

    // Actualizar navegación (añadir botón de cerrar sesión)
    if (navContainer) {
        // Remover botón de cerrar sesión existente si hay
        const existingLogout = document.querySelector('.logout-btn');
        if (existingLogout) {
            existingLogout.remove();
        }

        // Añadir botón de cerrar sesión si está logueado
        if (isLoggedIn) {
            const logoutBtn = document.createElement('a');
            logoutBtn.href = '#';
            logoutBtn.className = 'nav-item logout-btn';
            logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Cerrar sesión';
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                localStorage.removeItem('isLoggedIn');
                localStorage.removeItem('userType');
                window.location.href = 'Home.html';
            });
            
            // Insertar antes del último elemento (normalmente "Mi Cuenta")
            navContainer.insertBefore(logoutBtn, navContainer.lastChild);
        }
    }
}

// Sistema temporal de autenticación para desarrollo
function setupDevAuth() {
    if (!localStorage.getItem('isLoggedIn') {
        const shouldAuth = confirm('¿Deseas simular inicio de sesión? (Solo para desarrollo)');
        if (shouldAuth) {
            const userType = prompt("Selecciona tu tipo de usuario:\n1. Cliente\n2. Trabajador\n3. Desempleado");
            if (userType && ['1', '2', '3'].includes(userType)) {
                localStorage.setItem('userType', userType);
                localStorage.setItem('isLoggedIn', 'true');
            }
        }
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    setupDevAuth();
    updateUI();
    
    // Escuchar cambios en el almacenamiento local
    window.addEventListener('storage', function(e) {
        if (e.key === 'isLoggedIn' || e.key === 'userType') {
            updateUI();
        }
    });
});
    }
});

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
      
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
        });
        
        item.classList.add('active');
        
        console.log(`Navigating to: ${item.textContent}`);
    });
});
function updateMainCTA() {
    const ctaContainer = document.getElementById('main-cta-container');
    const userType = localStorage.getItem('userType');

    // Limpiar contenedor
    ctaContainer.innerHTML = '';

    if (userType) {
        // Usuario logueado
        let buttonText, buttonLink;

        if (userType === '1') { // Cliente
            buttonText = 'Buscar Profesionales';
            buttonLink = 'Browser.html';
        } else if (userType === '2') { // Trabajador
            buttonText = 'Buscar Trabajos';
            buttonLink = 'AceptarTrabajos.html';
        } else { // Desempleado (o otros tipos)
            buttonText = 'Explorar Oportunidades';
            buttonLink = 'AceptarTrabajos.html';
        }

        // Crear botón principal
        const mainButton = document.createElement('a');
        mainButton.href = buttonLink;
        mainButton.className = 'cta-button primary';
        mainButton.innerHTML = `
            ${buttonText}
            <i class="fas fa-arrow-right"></i>
        `;
        ctaContainer.appendChild(mainButton);

        // Botón secundario (opcional)
        const secondaryButton = document.createElement('a');
        secondaryButton.href = '#';
        secondaryButton.className = 'cta-button secondary';
        secondaryButton.textContent = 'Mi Perfil';
        ctaContainer.appendChild(secondaryButton);
    } else {
        // Usuario no logueado - Mostrar botones de login/registro
        const loginButton = document.createElement('a');
        loginButton.href = 'Inicio de Sesion.html';
        loginButton.className = 'cta-button primary';
        loginButton.innerHTML = `
            Iniciar Sesión
            <i class="fas fa-sign-in-alt"></i>
        `;
        ctaContainer.appendChild(loginButton);

        const registerButton = document.createElement('a');
        registerButton.href = 'Registro.html';
        registerButton.className = 'cta-button secondary';
        registerButton.textContent = 'Registrarse';
        ctaContainer.appendChild(registerButton);
    }
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', updateMainCTA);

// También ejecutar cuando cambie el estado de login (opcional)
window.addEventListener('storage', function(e) {
    if (e.key === 'userType') {
        updateMainCTA();
    }
});