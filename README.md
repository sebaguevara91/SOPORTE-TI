# Plataforma de Registro de Visitas y Soporte TI - SLEP Valle Diguillín

Sistema web integral para el control de acceso, registro, seguimiento, notificaciones por correo, reportería y mantenedores de visitas técnicas y soporte a instituciones educacionales y usuarios del área TI.

---

## 🔐 Acceso y Autenticación (Login)

La plataforma cuenta con un sistema de autenticación por correo y contraseña con perfil unificado de acceso:

- **Correo de acceso:** `admin@soporteti.cl`
- **Contraseña:** `admin123`
- **Perfil asignado:** `Administrador General TI`
- **Opciones:**
  - Botón de **Autocompletar** con 1 clic para acceso rápido.
  - Alternador para ver/ocultar contraseña.
  - Cierre de sesión seguro con confirmación (`Cerrar Sesión` en la barra superior).

---

## 🚀 Características Principales

### 1. 📊 Dashboard Operativo en Tiempo Real
- **Tarjetas KPI**: Total de visitas, Pendientes, En Proceso, Realizadas, Directorio de Establecimientos y % de Cumplimiento.
- **Gráficos Dinámicos (Chart.js)**: Distribución de estados (gráfico Donut) y volumen de atenciones por categoría de soporte técnico (gráfico de Barras).
- **Panel de Alertas y Urgencias**: Listado priorizado de próximas visitas y atenciones críticas.

### 2. 🏫 Mantenedor de Establecimientos (CRUD + Excel)
- **Directorio de Colegios**: Gestión de RBD, Nombre, Comuna, Dirección, Correo institucional del colegio, Director(a), Correo electrónico del director, Teléfono, Matrícula, Dependencia y Encargado de Enlaces TI.
- **Operaciones CRUD**: Crear, Editar datos in-situ y Eliminar instituciones.
- **Importador de Excel (.xlsx / .csv)**: Carga masiva con mapeo automático de columnas y vista previa antes de confirmar.
- **Exportador de Excel**: Descarga instantánea de toda la base de datos de colegios en `.xlsx`.
- **Plantilla de Carga**: Descarga de formato de ejemplo para rellenar.

### 3. 📋 Mantenedor de Visitas a Terreno & Notificación por Correo
- **Equipo Técnico Oficial**: Selección entre `Sebastian Guevara`, `Rodrigo Bravo` y `Claudio Rojas`.
- **Notificación por Correo con ID de Atención**:
  - Envío de orden de atención y confirmación de visita técnica al correo registrado de cada colegio (`correo_establecimiento` y dirección escolar).
  - Generación de **ID de Atención** formal (ej. `OT-2026-0001` / `#1`) para trazabilidad, recepción y consultas.
  - Modal de previsualización formal con plantilla HTML, envío vía servidor API REST y enlace directo a cliente de correo (`mailto:`).
- **Estados de Atención**:
  - `Pendiente` (🟡 Pausada / Espera de repuesto o autorización).
  - `En Proceso` (🔵 Técnico en terreno o atención activa).
  - `Realizada` (🟢 Trabajo finalizado con conformidad y firma).
  - `Programada` (🟣 Agendada a futuro).
- **Vistas Duales**: Alternancia entre **Vista Tabla Interactiva** (con buscador y filtros) y **Vista Tablero Kanban**.
- **Bitácora de Seguimiento**: Registro cronológico de notas, avances técnicos y confirmaciones de correos enviados.

### 4. 📈 Reportería Avanzada & Actas de Servicio Imprimibles
- Filtros por rango de fechas (desde/hasta), colegio, técnico responsable, categoría y estado.
- Resumen estadístico del período consultado.
- Exportación del reporte filtrado a formato Excel (`.xlsx`).
- **Generador de Acta de Atención Técnica Imprimible**: Formato formal con datos institucionales, motivo, diagnóstico, tareas realizadas y recuadros para firma del técnico y recepción conforme de la dirección escolar.

### 5. ⚡ Modo Híbrido (Autónomo + Backend REST)
- **Autónomo:** Puedes abrir directamente `frontend/index.html` en cualquier navegador y funcionará al 100% persistiendo los datos en `localStorage`.
- **Servidor REST:** Si ejecutas `backend/server.py`, el sistema se conectará automáticamente a la base de datos SQLite persistente con endpoints REST documentados en Swagger.

---

## 💻 Instrucciones de Uso

### Opción A: Ejecutar con Servidor Backend (Recomendado)
1. Haz doble clic en el archivo `run.bat` o abre una terminal en la carpeta y ejecuta:
   ```bash
   python backend/server.py
   ```
2. Abre tu navegador web en: **[http://localhost:8080](http://localhost:8080)** (o `http://localhost:8000`)
3. Ingresa con:
   - **Correo:** `admin@soporteti.cl`
   - **Contraseña:** `admin123`
4. Documentación interactiva Swagger: **[http://localhost:8080/docs](http://localhost:8080/docs)**

### Opción B: Uso Directo sin Servidor (Standalone)
- Abre directamente el archivo `frontend/index.html` en tu navegador preferido. Todo funcionará de forma autónoma.
