document.addEventListener('DOMContentLoaded', function() {
    const userType = localStorage.getItem('userType');
    const protectedPages = {
        'Browser.html': '1', // Solo clientes
        'AceptarTrabajos.html': '2' // Solo trabajadores
    };
    
    const currentPage = window.location.pathname.split('/').pop();
    
    if(protectedPages[currentPage] && protectedPages[currentPage] !== userType) {
        document.body.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; padding: 20px; text-align: center;">
                <h1 style="color: #e74c3c;">Acceso no autorizado</h1>
                <p>Esta página está destinada para ${protectedPages[currentPage] === '1' ? 'clientes' : 'trabajadores'}.</p>
                <a href="Home.html" style="margin-top: 20px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px;">
                    Volver al inicio
                </a>
                <button id="changeUserType" style="margin-top: 10px; padding: 8px 15px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Cambiar tipo de usuario
                </button>
            </div>
        `;
        
        document.getElementById('changeUserType').addEventListener('click', () => {
            localStorage.removeItem('userType');
            location.href = 'Home.html';
        });
    }
});