document.addEventListener('DOMContentLoaded', () => {
    // CONFIGURACIÓN DE ZONA HORARIA ---
    const zonaHoraria = Intl.DateTimeFormat().resolvedOptions().timeZone;
    console.log("[SYSTEM] Zona horaria activa:", zonaHoraria);

    const zonaInput = document.getElementById("zona_horaria_input");
    if (zonaInput) zonaInput.value = zonaHoraria;

    document.querySelectorAll("form").forEach(form => {
        if (!form.querySelector("input[name='zona_horaria']")) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "zona_horaria";
            input.value = zonaHoraria;
            form.appendChild(input);
        }
    });

    // CONTROL DE PANTALLA DE CARGA GLOBAL---
    const loader = document.getElementById('loading-indicator');
    
    if (loader) {
        document.querySelectorAll('form').forEach(form => {
            if (!form.classList.contains('no-loader')) {
                form.addEventListener('submit', () => {
                    loader.style.display = 'flex';
                });
            }
        });

        const originalFetch = window.fetch;
        window.fetch = function (...args) {
            const url = args[0];
            //Si la peticion es el sondeo de replica no bloquea la UI
            const esPeticionSilenciosa = url.includes('/api/estado_replicacion/');

            if (!esPeticionSilenciosa) {
                loader.style.display = 'flex';
            }

            return originalFetch(...args)
                .then(response => {
                    if (!esPeticionSilenciosa) loader.style.display = 'none';
                    return response;
                })
                .catch(error => {
                    loader.style.display = 'none';
                    throw error;
                });
        };

        window.addEventListener('load', () => {
            loader.style.display = 'none';
        });
    }

    // ANIMACIONES DE FORMULARIOS (LOGIN/SIGNUP) ---
    document.querySelectorAll('.input-box input').forEach(input => {
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
    });

    // VISIBILIDAD DE CONTRASEÑAS ---
    const togglePassword = document.getElementById('login-eye');
    const passwordInput = document.getElementById('passwordInput');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            this.classList.toggle('ri-eye-line', isPassword);
            this.classList.toggle('ri-eye-off-line', !isPassword);
        });
    }

    // CIERRE MANUAL DE NOTIFICACIONES TOAST ---
    const botonesCerrar = document.querySelectorAll('.toast-close');
    botonesCerrar.forEach(boton => {
        boton.addEventListener('click', (e) => {
            const toast = e.target.closest('.toast');
            if (toast) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(10px)';
                setTimeout(() => toast.remove(), 300);
            }
        });
    })

    // CIERRE AUTOMÁTICO DE NOTIFICACIONES TOAST ---
    const toastExistentes = document.querySelectorAll('.toast');
    if (toastExistentes.length > 0) {
        setTimeout(() => {
            toastExistentes.forEach(toast =>  {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(10px)';
                setTimeout(() => toast.remove(), 300);
            });
        }, 5000);
    }

    //  RELOJ DINÁMICO UTC ---
    const spanUTC = document.getElementById("hora-utc");
    if (spanUTC) {
        setInterval(() => {
            let fechaActual = new Date(spanUTC.innerText + ' UTC');
            fechaActual.setSeconds(fechaActual.getSeconds() + 1);
            // Formateo manual limpio compatible con entornos distribuidos
            spanUTC.innerText = fechaActual.toISOString().slice(0, 19).replace('T', ' ');
        }, 1000);
    }

    // MONITOREO DE REPLICACIÓN DE BASE DE DATOS ---
    const widgetReplicacion = document.getElementById('estado_replicacion_container');
    const textoReplicacion = document.getElementById('estado_replicacion');

    if (widgetReplicacion && textoReplicacion) {
        function verificarReplicacion() {
            const originalFetch = window.fetch;
            originalFetch('/api/estado_replicacion/') 
                .then(response => response.json())
                .then(data => {
                    widgetReplicacion.className = "replicacion-widget";

                    if (data.modo_debug) {
                        textoReplicacion.textContent = 'Modo DEBUG activo (Simulación)';
                        widgetReplicacion.classList.add('warning');
                    } else if (data.replicacion_activa) {
                        textoReplicacion.textContent = `Réplica al día. Lag: ${data.seconds_behind}s.`;
                        widgetReplicacion.classList.add('success');
                    } else {
                        textoReplicacion.textContent = `Desincronización crítica. Lag: ${data.seconds_behind}s.`;
                        widgetReplicacion.classList.add('error');
                    }
                })
                .catch(error => {
                    console.error('[MONITOR] Fallo en telemetría de réplica:', error);
                    textoReplicacion.textContent = 'Servicio de réplica inaccesible.';
                    widgetReplicacion.className = "replicacion-widget error";
                });
        }
        verificarReplicacion();
        setInterval(verificarReplicacion, 30000);
    }

    // --- LÓGICA DEL MENÚ HAMBURGUESA ---
    const menuToggle = document.getElementById('menu-toggle');
    const navLinks = document.getElementById('nav-links');

    if (menuToggle && navLinks) {
        const iconMenu = menuToggle.querySelector('i');

        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');

            if (navLinks.classList.contains('active')) {
                iconMenu.classList.remove('ri-menu-line');
                iconMenu.classList.add('ri-close-line');
            } else {
                iconMenu.classList.remove('ri-close-line');
                iconMenu.classList.add('ri-menu-line');
            }
        });

        document.addEventListener('click', (e) => {
            if (!navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
                navLinks.classList.remove('active');
                iconMenu.classList.remove('ri-close-line');
                iconMenu.classList.add('ri-menu-line');
            }
        });
    }
});