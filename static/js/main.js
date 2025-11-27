// Funcionalidades generales del sitio
document.addEventListener('DOMContentLoaded', function() {
    // Cerrar mensajes automáticamente
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Menú móvil
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Contador de intentos de login
    let loginAttempts = 0;
    const loginForm = document.querySelector('.login-form form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            loginAttempts++;
            if (loginAttempts >= 3) {
                alert('Has excedido el número máximo de intentos. Por favor contacta al administrador.');
                e.preventDefault();
            }
        });
    }

    // Actualizar cantidad en carrito
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '';
                }
            });

            if (!valid) {
                e.preventDefault();
                alert('Por favor completa todos los campos requeridos.');
            }
        });
    });
});

// Funciones para el carrito
function updateCartQuantity(itemId, change) {
    const quantityInput = document.querySelector(`#quantity-${itemId}`);
    let newQuantity = parseInt(quantityInput.value) + change;
    
    if (newQuantity < 1) newQuantity = 1;
    
    quantityInput.value = newQuantity;
    
    // Enviar actualización automáticamente
    const form = quantityInput.closest('form');
    if (form) {
        form.submit();
    }
}

// Búsqueda en tiempo real
function searchProducts(query) {
    if (query.length < 2) return;
    
    fetch(`/buscar/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            // Actualizar resultados de búsqueda
            console.log(data);
        });
}