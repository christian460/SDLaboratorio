/**
 * SGA - Control de Alumnos
 * Lógica del Cliente Web (Vanilla JS)
 */

document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // SELECCIÓN DE ELEMENTOS DEL DOM
    // ==========================================
    const studentForm = document.getElementById('student-form');
    const studentIdInput = document.getElementById('student-id');
    const nombreInput = document.getElementById('nombre');
    const apellidoInput = document.getElementById('apellido');
    const carreraInput = document.getElementById('carrera');
    const edadInput = document.getElementById('edad');
    const correoInput = document.getElementById('correo');

    const formActionTitle = document.getElementById('form-action-title');
    const formTitleIcon = document.getElementById('form-title-icon');
    const btnSubmit = document.getElementById('btn-submit');
    const btnCancel = document.getElementById('btn-cancel');

    const studentsTbody = document.getElementById('students-tbody');
    const studentCountBadge = document.getElementById('student-count-badge');
    const toastContainer = document.getElementById('toast-container');

    // Elementos del Modal de Confirmación
    const confirmModal = document.getElementById('confirm-modal');
    const deleteStudentName = document.getElementById('delete-student-name');
    const btnModalCancel = document.getElementById('btn-modal-cancel');
    const btnModalConfirm = document.getElementById('btn-modal-confirm');

    // API URL Base
    const API_URL = '/estudiantes';

    // Estado global de la aplicación cliente
    let editMode = false;
    let studentIdToDelete = null;

    // ==========================================
    // SISTEMA DE NOTIFICACIONES (TOASTS)
    // ==========================================
    /**
     * Muestra una notificación flotante en la pantalla.
     * @param {string} title Título del toast
     * @param {string} message Mensaje detallado
     * @param {string} type Tipo de toast ('success' | 'error' | 'info')
     */
    function showToast(title, message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let iconClass = 'fa-circle-info';
        if (type === 'success') iconClass = 'fa-circle-check';
        if (type === 'error') iconClass = 'fa-circle-exclamation';

        toast.innerHTML = `
            <i class="fa-solid ${iconClass}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close"><i class="fa-solid fa-xmark"></i></button>
        `;

        toastContainer.appendChild(toast);

        // Evento para cerrar manualmente
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            toast.classList.add('toast-fade-out');
            setTimeout(() => toast.remove(), 300);
        });

        // Autocerrado después de 4 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('toast-fade-out');
                setTimeout(() => toast.remove(), 300);
            }
        }, 4000);
    }

    // ==========================================
    // CONSUMO DE LA API Y RENDERIZADO
    // ==========================================
    /**
     * Consulta la API (GET /estudiantes) y actualiza la lista en la interfaz.
     */
    async function cargarEstudiantes() {
        try {
            // Mostrar estado de carga si la tabla está vacía
            if (studentsTbody.children.length === 0) {
                studentsTbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="empty-state">
                            <i class="fa-solid fa-spinner fa-spin"></i> Cargando lista de estudiantes...
                        </td>
                    </tr>
                `;
            }

            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error('No se pudo establecer conexión con el servidor API.');
            }
            
            const estudiantes = await response.json();
            renderizarTabla(estudiantes);
        } catch (error) {
            console.error('Error al cargar estudiantes:', error);
            studentsTbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state" style="color: var(--accent-danger);">
                        <i class="fa-solid fa-circle-exclamation"></i> Error al conectar con la API: ${error.message}
                    </td>
                </tr>
            `;
            studentCountBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Offline`;
            studentCountBadge.style.color = '#fda4af';
        }
    }

    /**
     * Inserta los datos de los estudiantes en la tabla HTML con animaciones.
     * @param {Array} estudiantes Lista de diccionarios de estudiantes
     */
    function renderizarTabla(estudiantes) {
        studentsTbody.innerHTML = '';
        
        // Actualizar contador en el navbar
        studentCountBadge.innerHTML = `
            <i class="fa-solid fa-users"></i>
            <span>Total Alumnos: ${estudiantes.length}</span>
        `;
        studentCountBadge.style.color = '';

        if (estudiantes.length === 0) {
            studentsTbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        <i class="fa-solid fa-user-slash"></i> No hay estudiantes registrados en este momento.
                    </td>
                </tr>
            `;
            return;
        }

        estudiantes.forEach((estudiante, index) => {
            const tr = document.createElement('tr');
            tr.className = 'row-animate';
            // Retardo secuencial de animación de fila para un efecto visual fluido
            tr.style.animationDelay = `${index * 50}ms`;

            tr.innerHTML = `
                <td><strong>#${estudiante.id}</strong></td>
                <td>
                    <div style="font-weight: 600; color: var(--text-primary);">${estudiante.nombre}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">${estudiante.apellido}</div>
                </td>
                <td><span class="career-badge">${estudiante.carrera}</span></td>
                <td>${estudiante.edad} años</td>
                <td>
                    <a href="mailto:${estudiante.correo}" style="color: #818cf8; text-decoration: none; font-size: 0.9rem; display: flex; align-items: center; gap: 0.35rem;">
                        <i class="fa-regular fa-envelope"></i> ${estudiante.correo}
                    </a>
                </td>
                <td>
                    <div class="student-actions">
                        <button class="btn btn-edit-sm btn-sm btn-editar" data-id="${estudiante.id}" title="Editar estudiante">
                            <i class="fa-regular fa-pen-to-square"></i> Editar
                        </button>
                        <button class="btn btn-delete-sm btn-sm btn-eliminar" data-id="${estudiante.id}" data-nombre="${estudiante.nombre} ${estudiante.apellido}" title="Eliminar estudiante">
                            <i class="fa-regular fa-trash-can"></i> Eliminar
                        </button>
                    </div>
                </td>
            `;
            
            studentsTbody.appendChild(tr);
        });

        // Registrar eventos para los botones de editar y eliminar
        registrarEventosAccion();
    }

    /**
     * Registra event listeners dinámicamente para los botones dentro de la tabla.
     */
    function registrarEventosAccion() {
        // Botones Editar
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                prepararEdicion(id);
            });
        });

        // Botones Eliminar
        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', (e) => {
                studentIdToDelete = e.currentTarget.getAttribute('data-id');
                const nombreCompleto = e.currentTarget.getAttribute('data-nombre');
                abrirConfirmModal(nombreCompleto);
            });
        });
    }

    // ==========================================
    // AGREGAR / EDITAR ESTUDIANTE
    // ==========================================
    /**
     * Envía los datos del formulario a la API (POST para registrar, PUT para actualizar).
     */
    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Obtener valores
        const nombre = nombreInput.value.trim();
        const apellido = apellidoInput.value.trim();
        const carrera = carreraInput.value.trim();
        const edad = edadInput.value.trim();
        const correo = correoInput.value.trim();

        // Validaciones en el cliente antes del envío
        if (!nombre || !apellido || !carrera || !edad || !correo) {
            showToast('Formulario Incompleto', 'Por favor, rellene todos los campos del formulario.', 'error');
            return;
        }

        if (nombre.length < 2) {
            showToast('Nombre Inválido', 'El nombre debe tener al menos 2 caracteres.', 'error');
            return;
        }

        if (apellido.length < 2) {
            showToast('Apellido Inválido', 'El apellido debe tener al menos 2 caracteres.', 'error');
            return;
        }

        if (carrera.length < 3) {
            showToast('Carrera Inválida', 'La carrera debe tener al menos 3 caracteres.', 'error');
            return;
        }

        const edadInt = parseInt(edad, 10);
        if (isNaN(edadInt) || edadInt <= 0 || edadInt > 120) {
            showToast('Edad Inválida', 'Ingrese una edad realista entre 1 y 120 años.', 'error');
            return;
        }

        const emailPattern = /^[\w\.-]+@[\w\.-]+\.\w+$/;
        if (!emailPattern.test(correo)) {
            showToast('Correo Inválido', 'Por favor, introduzca una dirección de correo válida.', 'error');
            return;
        }

        // Crear payload
        const payload = {
            nombre,
            apellido,
            carrera,
            edad: edadInt,
            correo
        };

        const targetUrl = editMode ? `${API_URL}/${studentIdInput.value}` : API_URL;
        const method = editMode ? 'PUT' : 'POST';

        try {
            // Deshabilitar botón durante el envío para evitar clicks dobles
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Guardando...`;

            const response = await fetch(targetUrl, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Ocurrió un error inesperado al procesar la petición.');
            }

            // Exito
            if (editMode) {
                showToast('Actualizado', `Datos de ${result.nombre} actualizados con éxito.`, 'success');
                cancelarEdicion();
            } else {
                showToast('Registrado', `${result.nombre} ha sido ingresado al sistema.`, 'success');
                studentForm.reset();
            }

            // Actualizar tabla dinámicamente
            cargarEstudiantes();

        } catch (error) {
            console.error('Error al guardar:', error);
            showToast('Error de Validación', error.message, 'error');
        } finally {
            // Reestablecer estilo de botón
            btnSubmit.disabled = false;
            actualizarEstadoBotonFormulario();
        }
    });

    /**
     * Carga los datos de un estudiante en el formulario para su edición.
     * @param {string|number} id ID del estudiante
     */
    async function prepararEdicion(id) {
        try {
            const response = await fetch(`${API_URL}/${id}`);
            if (!response.ok) {
                throw new Error('No se pudieron recuperar los datos del estudiante.');
            }

            const estudiante = await response.json();

            // Rellenar formulario
            studentIdInput.value = estudiante.id;
            nombreInput.value = estudiante.nombre;
            apellidoInput.value = estudiante.apellido;
            carreraInput.value = estudiante.carrera;
            edadInput.value = estudiante.edad;
            correoInput.value = estudiante.correo;

            // Activar modo edición
            editMode = true;
            formActionTitle.textContent = 'Editar Estudiante';
            formTitleIcon.className = 'fa-solid fa-user-pen';
            btnCancel.style.display = 'inline-flex';
            
            // Enfocar primer campo
            nombreInput.focus();
            
            actualizarEstadoBotonFormulario();
            showToast('Modo Edición', `Cargados datos de ${estudiante.nombre} ${estudiante.apellido}`, 'info');

        } catch (error) {
            console.error('Error al preparar edición:', error);
            showToast('Error', error.message, 'error');
        }
    }

    /**
     * Cancela el modo de edición y limpia el formulario.
     */
    function cancelarEdicion() {
        studentForm.reset();
        studentIdInput.value = '';
        editMode = false;
        formActionTitle.textContent = 'Registrar Estudiante';
        formTitleIcon.className = 'fa-solid fa-user-plus';
        btnCancel.style.display = 'none';
        actualizarEstadoBotonFormulario();
    }

    /**
     * Modifica el aspecto visual del botón submit según el modo actual (Agregar: Verde vs Editar: Azul)
     */
    function actualizarEstadoBotonFormulario() {
        if (editMode) {
            btnSubmit.className = 'btn btn-info';
            btnSubmit.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Guardar Cambios`;
        } else {
            btnSubmit.className = 'btn btn-success';
            btnSubmit.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> Registrar Estudiante`;
        }
    }

    btnCancel.addEventListener('click', cancelarEdicion);

    // ==========================================
    // CONTROL DEL MODAL Y ELIMINACIÓN
    // ==========================================
    /**
     * Abre el modal de confirmación de borrado.
     * @param {string} nombre Nombre completo del estudiante a eliminar
     */
    function abrirConfirmModal(nombre) {
        deleteStudentName.textContent = nombre;
        confirmModal.classList.add('active');
    }

    /**
     * Cierra el modal de confirmación de borrado.
     */
    function cerrarConfirmModal() {
        confirmModal.classList.remove('active');
        studentIdToDelete = null;
    }

    /**
     * Confirma la eliminación y llama al endpoint DELETE de la API.
     */
    async function confirmarEliminacion() {
        if (!studentIdToDelete) return;

        try {
            const response = await fetch(`${API_URL}/${studentIdToDelete}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'No se pudo eliminar el estudiante.');
            }

            showToast('Eliminado', result.mensaje, 'success');
            
            // Si el estudiante eliminado estaba cargado en el formulario, cancelar edición
            if (editMode && studentIdInput.value === studentIdToDelete) {
                cancelarEdicion();
            }

            // Recargar la tabla
            cargarEstudiantes();

        } catch (error) {
            console.error('Error al eliminar:', error);
            showToast('Error', error.message, 'error');
        } finally {
            cerrarConfirmModal();
        }
    }

    btnModalCancel.addEventListener('click', cerrarConfirmModal);
    btnModalConfirm.addEventListener('click', confirmarEliminacion);

    // Cerrar modal al hacer click fuera del contenido del modal
    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) {
            cerrarConfirmModal();
        }
    });

    // ==========================================
    // INICIALIZACIÓN DE LA APLICACIÓN
    // ==========================================
    cargarEstudiantes();
});
