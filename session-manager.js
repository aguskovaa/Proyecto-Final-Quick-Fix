// session-manager.js
class SessionManager {
  constructor() {
    this.init();
  }

  init() {
    this.loadSession();
    this.setupEventListeners();
    this.checkAuthState();
  }

  loadSession() {
    this.userType = localStorage.getItem('userType');
    this.isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    console.log('Session loaded:', { userType: this.userType, isLoggedIn: this.isLoggedIn });
  }

  saveSession(userType) {
    localStorage.setItem('userType', userType);
    localStorage.setItem('isLoggedIn', 'true');
    this.userType = userType;
    this.isLoggedIn = true;
    console.log('Session saved:', { userType: this.userType, isLoggedIn: this.isLoggedIn });
    this.updateUI();
  }

  clearSession() {
    localStorage.removeItem('userType');
    localStorage.removeItem('isLoggedIn');
    this.userType = null;
    this.isLoggedIn = false;
    console.log('Session cleared');
    this.updateUI();
    window.location.href = 'Home.html';
  }

  checkAuthState() {
    const protectedRoutes = {
      'Browser.html': '1',
      'AceptarTrabajos.html': '2'
    };
    
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedRoutes[currentPage] && protectedRoutes[currentPage] !== this.userType) {
      this.showUnauthorizedMessage();
    }
  }

  showUnauthorizedMessage() {
    document.body.innerHTML = `
      <div style="text-align: center; padding: 50px;">
        <h1 style="color: red;">Acceso no autorizado</h1>
        <p>No tienes permiso para acceder a esta página.</p>
        <a href="Home.html" style="color: blue;">Volver al inicio</a>
      </div>
    `;
  }

  updateUI() {
    this.updateAuthButtons();
    this.updateNavigation();
  }

  updateAuthButtons() {
    const authContainer = document.getElementById('auth-buttons');
    if (!authContainer) return;

    if (this.isLoggedIn) {
      const destination = this.userType === '1' ? 'Browser.html' : 'AceptarTrabajos.html';
      const buttonText = this.userType === '1' ? 'Buscar Profesionales' : 'Buscar Trabajos';
      
      authContainer.innerHTML = `
        <a href="${destination}" class="cta-button primary">
          ${buttonText}
          <i class="fas fa-arrow-right"></i>
        </a>
        <button id="logout-btn" class="cta-button secondary">
          Cerrar sesión
        </button>
      `;

      document.getElementById('logout-btn').addEventListener('click', () => this.clearSession());
    } else {
      authContainer.innerHTML = `
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

  updateNavigation() {
    const nav = document.querySelector('.nav');
    if (!nav) return;

    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) logoutBtn.remove();

    if (this.isLoggedIn) {
      const newLogoutBtn = document.createElement('a');
      newLogoutBtn.href = '#';
      newLogoutBtn.className = 'nav-item logout-btn';
      newLogoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Cerrar sesión';
      newLogoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.clearSession();
      });
      
      nav.insertBefore(newLogoutBtn, nav.lastChild);
    }
  }

  setupEventListeners() {
    // Login
    document.querySelector('.btn-login')?.addEventListener('click', () => {
      const role = document.querySelector('input[name="rol"]:checked')?.value;
      if (role) {
        const userType = { 'cliente': '1', 'trabajador': '2', 'desempleado': '3' }[role];
        this.saveSession(userType);
        window.location.href = 'Home.html';
      }
    });

    // Register
    document.querySelector('.btn-register')?.addEventListener('click', () => {
      const role = document.querySelector('input[name="rol"]:checked')?.value;
      if (role) {
        const userType = { 'cliente': '1', 'trabajador': '2', 'desempleado': '3' }[role];
        this.saveSession(userType);
        window.location.href = 'Home.html';
      }
    });
  }
}

// Inicialización
const sessionManager = new SessionManager();

// Para desarrollo - Carga inicial
if (!localStorage.getItem('userType') && window.location.pathname.endsWith('Home.html')) {
  const userType = prompt("Modo desarrollo: Selecciona tipo de usuario\n1. Cliente\n2. Trabajador\n3. Desempleado");
  if (userType && ['1', '2', '3'].includes(userType)) {
    localStorage.setItem('userType', userType);
    localStorage.setItem('isLoggedIn', 'true');
    window.location.reload();
  }
}