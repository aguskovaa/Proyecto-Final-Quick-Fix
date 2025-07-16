// auth.js - Gestión centralizada de autenticación

const Auth = {
  init: function() {
    // Cargar estado de autenticación al iniciar
    this.loadAuthState();
    
    // Configurar botones de autenticación
    this.setupAuthButtons();
    
    // Verificar autenticación en páginas protegidas
    this.checkProtectedPages();
  },

  loadAuthState: function() {
    // Cargar estado del localStorage
    this.isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    this.userType = localStorage.getItem('userType');
  },

  login: function(userType) {
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('userType', userType);
    this.loadAuthState();
    this.updateUI();
  },

  logout: function() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userType');
    this.loadAuthState();
    this.updateUI();
    window.location.href = 'Home.html';
  },

  updateUI: function() {
    // Actualizar botones principales
    this.updateMainButtons();
    
    // Actualizar barra de navegación
    this.updateNavbar();
  },

  updateMainButtons: function() {
    const authButtons = document.getElementById('auth-buttons');
    if (!authButtons) return;

    if (this.isLoggedIn && this.userType) {
      let mainButtonUrl, mainButtonText;
      
      if (this.userType === '1') { // Cliente
        mainButtonUrl = 'Browser.html';
        mainButtonText = 'Buscar Profesionales';
      } else { // Trabajador (2) o Desempleado (3)
        mainButtonUrl = 'AceptarTrabajos.html';
        mainButtonText = this.userType === '2' ? 'Buscar Trabajos' : 'Explorar Oportunidades';
      }

      authButtons.innerHTML = `
        <a href="${mainButtonUrl}" class="cta-button primary">
          ${mainButtonText}
          <i class="fas fa-arrow-right"></i>
        </a>
        <button class="cta-button secondary" id="logout-btn">
          Cerrar sesión
        </button>
      `;

      document.getElementById('logout-btn').addEventListener('click', () => this.logout());
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
  },

  updateNavbar: function() {
    const navContainer = document.querySelector('.nav');
    if (!navContainer) return;

    // Remover botón de cerrar sesión existente
    const existingLogout = document.querySelector('.logout-btn');
    if (existingLogout) {
      existingLogout.remove();
    }

    // Añadir botón de cerrar sesión si está logueado
    if (this.isLoggedIn) {
      const logoutBtn = document.createElement('a');
      logoutBtn.href = '#';
      logoutBtn.className = 'nav-item logout-btn';
      logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Cerrar sesión';
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.logout();
      });
      
      navContainer.insertBefore(logoutBtn, navContainer.lastChild);
    }
  },

  checkProtectedPages: function() {
    const protectedPages = {
      'Browser.html': '1',
      'AceptarTrabajos.html': '2'
    };
    
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages[currentPage] && protectedPages[currentPage] !== this.userType) {
      document.body.innerHTML = `
        <div class="unauthorized-container">
          <h1>Acceso no autorizado</h1>
          <p>Esta página es solo para ${protectedPages[currentPage] === '1' ? 'clientes' : 'trabajadores'}.</p>
          <a href="Home.html" class="home-link">Volver al inicio</a>
        </div>
      `;
    }
  },

  setupAuthButtons: function() {
    // Configurar botones de login/registro en sus respectivas páginas
    document.querySelector('.btn-login')?.addEventListener('click', () => {
      const selectedRole = document.querySelector('input[name="rol"]:checked')?.value;
      const userTypes = { 'cliente': '1', 'trabajador': '2', 'desempleado': '3' };
      if (selectedRole) this.login(userTypes[selectedRole]);
    });

    document.querySelector('.btn-register')?.addEventListener('click', () => {
      const selectedRole = document.querySelector('input[name="rol"]:checked')?.value;
      const userTypes = { 'cliente': '1', 'trabajador': '2', 'desempleado': '3' };
      if (selectedRole) this.login(userTypes[selectedRole]);
    });
  }
};

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', () => Auth.init());