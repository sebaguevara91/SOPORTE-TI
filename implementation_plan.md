# Plan Maestro de Implementación: Plataforma de Registro de Visitas de Soporte TI

Este documento define la arquitectura técnica, modelo de datos y la hoja de ruta paso a paso para el desarrollo integral del backend (API REST) y frontend (dashboard y control de visitas) para la gestión técnica en establecimientos educacionales de la región.

---

## 1. Arquitectura del Sistema y Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (SPA)                        │
│   TailwindCSS + Lucide Icons + Vanilla JS / Alpine.js       │
│   • Dashboard de KPIs y Métricas                            │
│   • Tabla de Control de Visitas con Filtros Reactivos       │
│   • Formularios de Programación y Cierre Técnico            │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON / HTTP REST
┌──────────────────────────────▼──────────────────────────────┐
│                    Backend API (FastAPI)                    │
│   Python 3.10+ / Pydantic / Uvicorn                         │
│   • Endpoints RESTful (/api/establecimientos, /api/visitas) │
│   • Estadísticas y Agregaciones (/api/dashboard/stats)      │
│   • Middleware CORS, Validaciones y Manejo de Errores       │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLite / PostgreSQL
┌──────────────────────────────▼──────────────────────────────┐
│                     Capa de Persistencia                    │
│   • Tabla establecimientos (RBD, comuna, director, etc.)    │
│   • Tabla visitas (Estados: Programada, Pendiente, etc.)    │
│   • Índices optimizados y compatibilidad SQL estándar       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Modelo de Datos y Esquema Relacional

### 2.1 Tabla `establecimientos`
Contiene los datos base de los colegios y liceos de la región:
- **`rbd`** (INTEGER, PK): Rol Base de Datos único del establecimiento.
- **`nombre`** (VARCHAR(255), NOT NULL): Nombre oficial de la institución.
- **`comuna`** (VARCHAR(100), NOT NULL): Comuna donde se ubica (ej. Antofagasta, Calama, Mejillones, Tocopilla).
- **`direccion`** (VARCHAR(255)): Dirección física.
- **`correo_establecimiento`** (VARCHAR(150)): Correo electrónico institucional o de contacto del establecimiento.
- **`director`** (VARCHAR(150), NOT NULL): Nombre del director(a) o encargado del colegio.
- **`correo_director`** (VARCHAR(150), NOT NULL): Correo electrónico del director para notificaciones e informes.
- **`telefono`** (VARCHAR(50)): Teléfono de contacto institucional.
- **`matricula`** (INTEGER): Cantidad total de estudiantes.
- **`dependencia`** (VARCHAR(50)): SLEP / Municipal / Particular Subvencionado.
- **`contacto_enlaces`** (VARCHAR(150)): Encargado de Enlaces o Coordinador TI del colegio.
- **`created_at` / `updated_at`** (TIMESTAMP): Trazabilidad de registros.

### 2.2 Tabla `visitas`
Gestiona el ciclo de vida de cada visita técnica y su detalle operativo:
- **`id`** (INTEGER, PK AUTOINCREMENT / SERIAL): Identificador único de la visita.
- **`rbd`** (INTEGER, FK): Referencia a `establecimientos(rbd)`.
- **`tecnico_responsable`** (VARCHAR(150), NOT NULL): Nombre del técnico asignado.
- **`estado`** (VARCHAR(20), NOT NULL): Restringido estrictamente a:
  - `'Programada'`
  - `'Pendiente'`
  - `'Realizada'`
- **`fecha_programada`** (DATE, NOT NULL): Fecha planificada de la visita.
- **`fecha_realizada`** (TIMESTAMP, NULL): Fecha y hora exacta de ejecución o cierre.
- **`motivo`** (TEXT, NOT NULL): Descripción del requerimiento o contingencia.
- **`detalle_hardware`** (TEXT/JSON): Especificación de equipos atendidos:
  - **Redes Ubiquiti:** Puntos de acceso UniFi (U6-Pro, LR, Lite), switches PoE gestionables, gateways UDM-Pro / EdgeRouters.
  - **Impresoras:** Equipos multifuncionales y de red (Ricoh, Kyocera, HP LaserJet, Brother).
- **`observaciones_cierre`** (TEXT, NULL): Resumen técnico de trabajos realizados o causas de estado pendiente.
- **`firma_recepcion`** (VARCHAR(150), NULL): Nombre y cargo de quien valida el servicio en el colegio.

---

## 3. Plan de Desarrollo Paso a Paso

### Fase 1: Base de Datos y Persistencia
- [x] Crear DDL relacional en `database/schema.sql`.
- [x] Configurar restricciones `CHECK` para estados válidos (`Programada`, `Pendiente`, `Realizada`).
- [x] Implementar índices de aceleración para filtros por `rbd`, `estado`, `fecha_programada` y `comuna`.
- [x] Incorporar datos semilla con establecimientos de la región y visitas de ejemplo.
- [ ] Implementar soporte opcional para migración hacia PostgreSQL mediante SQLAlchemy o psycopg3.

### Fase 2: Backend API (FastAPI / Python)
- [x] Estructurar servidor en `backend/server.py` con inicialización automática de SQLite.
- [x] Modelado de esquemas con Pydantic (`EstablecimientoBase`, `VisitaCreate`, `VisitaUpdate`, `VisitaResponse`).
- [x] Endpoints CRUD para establecimientos:
  - `GET /api/establecimientos` (búsqueda y filtro por comuna)
  - `GET /api/establecimientos/{rbd}`
  - `POST /api/establecimientos`
- [x] Endpoints CRUD para visitas técnicas:
  - `GET /api/visitas` (filtros por `estado`, `rbd`, `tecnico`)
  - `GET /api/visitas/{id}`
  - `POST /api/visitas`
  - `PUT /api/visitas/{id}` (cierre de visita, cambio de estado, observaciones)
  - `DELETE /api/visitas/{id}`
- [x] Endpoint de métricas agregadas `GET /api/dashboard/stats`.
- [ ] Agregar generación de reportes de visitas en formato PDF descargable para entrega al director.

### Fase 3: Frontend y Experiencia de Usuario
- [x] Crear interfaz reactiva en `frontend/index.html` con Tailwind CSS y Lucide Icons.
- [x] Panel de Métricas KPI en tiempo real (Total, Programadas, Pendientes, Realizadas, RBDs).
- [x] Tabla de Control de Visitas con buscador en vivo y pastillas de filtro por estado.
- [x] Formulario interactivo para programación de visitas con selector de colegios y checklist de hardware (Ubiquiti e impresoras).
- [x] Modal de gestión y cierre técnico para ingresar observaciones y recepcionista.
- [x] Conexión asíncrona mediante `fetch` al backend con fallback a datos locales para visualización inmediata.

### Fase 4: Pruebas y Despliegue
- [ ] Ejecutar pruebas de estrés en endpoints REST y verificar integridad referencial de claves foráneas.
- [ ] Configurar script de inicio rápido (`run.bat` / `run.sh`).

---

## 4. Guía de Ejecución Rápida

### Requisitos
- Python 3.9 o superior.
- Paquetes recomendados: `fastapi`, `uvicorn`, `pydantic`.

### Instrucciones de inicio
1. Instalar dependencias necesarias:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
2. Ejecutar el servidor backend:
   ```bash
   python backend/server.py
   ```
3. Abrir en el navegador:
   - **Dashboard Web:** [http://localhost:8000](http://localhost:8000)
   - **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
