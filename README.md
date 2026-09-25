# Plataforma de Registro de Visitas y Soporte TI - SLEP Valle Diguillín

Sistema web y API REST para el control de acceso, registro, seguimiento técnico, notificaciones por correo, reportería y gestión de visitas a establecimientos educacionales del **Servicio Local de Educación Pública (SLEP) Valle Diguillín**.

---

## 🗄️ Arquitectura de Base de Datos y Rediseño de Persistencia

La plataforma cuenta con una arquitectura de persistencia unificada mediante el módulo `backend/db.py`, diseñada para evitar pérdida o desincronización de datos entre los técnicos del equipo:

### 1. Motor Centralizado en la Nube (PostgreSQL / Supabase) - *Recomendado para el Equipo TI*
Permite que todos los técnicos (Sebastian, Rodrigo, Claudio y Administrador) registren y consulten visitas simultáneamente desde cualquier computador o terreno sin colisiones ni desfases.

- **Configuración rápida:** Agrega tu connection string en el archivo `.env`:
  ```env
  DATABASE_URL="postgresql://postgres.xxx:password@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
  ```
- **Migración automática en 1 clic:** Sube toda la base de datos (132 colegios y 180 visitas) a Supabase/PostgreSQL ejecutando:
  ```bash
  python scripts/migrate_to_postgres.py
  ```

### 2. Motor Local Persistente (SQLite en modo WAL)
Si `DATABASE_URL` no está definida en `.env`, el sistema utiliza de forma transparente `database/soporte_ti.db` con soporte para claves foráneas (`PRAGMA foreign_keys = ON`) y transacciones concurrentes seguras (`PRAGMA journal_mode = WAL`).

---

## 🔐 Acceso y Autenticación (Login)

La plataforma cuenta con usuarios oficiales preconfigurados:

| Usuario | Correo Electrónico | Contraseña | Rol |
| :--- | :--- | :--- | :--- |
| **Administrador General** | `admin@soporteti.cl` | `admin123` | Administrador TI |
| **Sebastian Guevara** | `sguevara@eduvallediguillin.gob.cl` | `admin123` | Técnico TI |
| **Rodrigo Bravo** | `rbravo@eduvallediguillin.gob.cl` | `admin123` | Técnico TI |
| **Claudio Rojas** | `crojas@eduvallediguillin.gob.cl` | `admin123` | Técnico TI |

- **Opciones de acceso:**
  - Botón **Autocompletar** con 1 clic para acceso rápido.
  - Alternador para ver/ocultar contraseña.
  - Cierre de sesión seguro en la barra superior.

---

## 🚀 Características Principales

### 1. 📊 Dashboard Operativo en Tiempo Real
- **Tarjetas KPI**: Total de visitas (180), Pendientes, En Proceso, Realizadas, Directorio de Establecimientos (132 colegios) y % de Cumplimiento.
- **Gráficos Dinámicos (Chart.js)**: Distribución de estados, volumen por categoría técnica y distribución por comuna (Chillán, Chillán Viejo, Bulnes, San Ignacio, Yungay, Pemuco).
- **Panel de Alertas y Urgencias**: Listado priorizado de próximas visitas y atenciones críticas.

### 2. 🏫 Mantenedor de Establecimientos (132 Colegios Reales)
- Directorio de colegios de SLEP Valle Diguillín con RBD, Nombre, Comuna, Dirección, Correo institucional, Director(a), Teléfono, Matrícula, Dependencia y Encargado de Enlaces TI.
- Operaciones CRUD completas (Crear, Editar, Eliminar/Archivar).
- Importación y exportación masiva en formato Excel (`.xlsx`).

### 3. 📋 Mantenedor de Visitas a Terreno & Notificación por Correo
- Asignación oficial a técnicos (`Sebastian Guevara`, `Rodrigo Bravo`, `Claudio Rojas`).
- Notificación formal por correo con **ID de Atención** generado (ej. `OT-2026-0001` / `#1`).
- Modal de previsualización formal con plantilla HTML y soporte para servidor SMTP institucional / Outlook / Gmail.
- Estados: `Pendiente`, `En Proceso`, `Realizada`, `Programada`.
- Vistas duales: **Tabla Interactiva** y **Tablero Kanban**.
- Bitácora cronológica de seguimiento por atención.

### 4. 📈 Reportería Avanzada & Actas Imprimibles
- Filtros por fechas, colegio, técnico, categoría y estado.
- Exportación del reporte a Excel (`.xlsx`).
- Generador de **Acta de Atención Técnica Imprimible** con firma técnica y recepción conforme.

---

## 💻 Instrucciones de Ejecución

1. Haz doble clic en el archivo `run.bat` o ejecuta en una terminal:
   ```bash
   python backend/server.py
   ```
2. Abre tu navegador web en: **[http://localhost:8080](http://localhost:8080)** (o `http://localhost:8000`)
3. Documentación interactiva de la API (Swagger UI): **[http://localhost:8080/docs](http://localhost:8080/docs)**
