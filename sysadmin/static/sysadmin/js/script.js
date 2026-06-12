window.addEventListener('DOMContentLoaded', () => {
    const zona = Intl.DateTimeFormat().resolvedOptions().timeZone;
    console.log("Zona horaria detectada:", zona);

    const zonaInput = document.getElementById("zona_horaria_input");
    if (zonaInput) {
        zonaInput.value = zona;
        console.log("Zona horaria actualizada en zona_horaria_input:", zonaInput.value);
    }

    document.querySelectorAll("form").forEach(form => {
        if (!form.querySelector("input[name='zona_horaria']")) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "zona_horaria";
            input.value = zona;
            form.appendChild(input);
            console.log(`Zona horaria agregada dinámicamente a form con action="${form.action}": ${zona}`);
        }
    });
})
;

window.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.input-box input');
    inputs.forEach(input => {
        if (input.value.trim() !== '') {
            input.classList.add('filled');
        }
        input.addEventListener('input', () => {
            if (input.value.trim() !== '') {
                input.classList.add('filled');
            } else {
                input.classList.remove('filled');
            }
        });
    });})

document.addEventListener('DOMContentLoaded', function () {
    const loading = document.getElementById('loading-indicator');
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            loading.style.display = 'flex';
        });
    });

    // Opcional: Mostrar durante llamadas AJAX (fetch)
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
        loading.style.display = 'flex';
        return originalFetch(...args)
            .then(response => {
                loading.style.display = 'none';
                return response;
            })
            .catch(error => {
                loading.style.display = 'none';
                throw error;
            });
    };
});

document.addEventListener('DOMContentLoaded', function () {
    const togglePassword = document.getElementById('login-eye');
    const passwordInput = document.getElementById('passwordInput');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');

            if (isPassword) {
                this.classList.remove('ri-eye-off-line');
                this.classList.add('ri-eye-line');
            } else {
                this.classList.remove('ri-eye-line');
                this.classList.add('ri-eye-off-line');
            }
        });
    }
});