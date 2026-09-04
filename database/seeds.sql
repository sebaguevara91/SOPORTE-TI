-- ==============================================================================
-- DATOS SEMILLA INICIALES (SOLO PARA BASE DE DATOS NUEVA / VACÍA)
-- ==============================================================================

INSERT INTO usuarios (email, password, nombre, rol, activo)
VALUES
('admin@soporteti.cl', 'admin123', 'Administrador General', 'Administrador TI', 1);

INSERT INTO establecimientos (rbd, nombre, comuna, direccion, correo_establecimiento, director, correo_director, telefono, matricula, dependencia, contacto_enlaces, tipo_establecimiento, activo)
VALUES
(1024, 'Liceo Bicentenario Industrial de Antofagasta', 'Antofagasta', 'Av. Iquique 4520', 'contacto@liceoindustrialantofagasta.cl', 'Carlos Mendoza Silva', 'director.lbia@educacion.cl', '+56 55 2234501', 850, 'SLEP', 'Ing. Pedro Valdivia', 'Liceo', 1),
(1025, 'Colegio Técnico Don Bosco', 'Antofagasta', 'Av. Rendic 3200', 'secretaria@donboscoantofagasta.cl', 'Hermano Patricio Araya', 'paraya@donbosco.cl', '+56 55 2891200', 1200, 'Particular Subvencionado', 'Prof. Marco Cortés', 'Liceo', 1),
(1026, 'Escuela Básica Gabriela Mistral D-68', 'Calama', 'Calle Lasana 1520', 'contacto@escuelamistralcalama.cl', 'Marcela Gómez Valdés', 'mgomez@escuelamistral.cl', '+56 55 2341122', 450, 'Municipal', 'Carla Monroy', 'Escuela', 1),
(1027, 'Liceo Politécnico América', 'Calama', 'Av. Granaderos 2810', 'liceo.america@calamaeduca.cl', 'Roberto Morales Peña', 'rmorales@politecnicoamerica.cl', '+56 55 2789900', 920, 'SLEP', 'Jorge Benítez', 'Liceo', 1),
(1028, 'Escuela Básica Bernardo O''Higgins E-42', 'Tocopilla', 'Calle 21 de Mayo 430', 'e42.tocopilla@educacion.cl', 'Patricia Fuentes Jara', 'pfuentes@escuelatocopilla.cl', '+56 55 2613344', 380, 'Municipal', 'Rodrigo Araya', 'Escuela', 1),
(1029, 'Liceo Diego Portales Palazuelos', 'Mejillones', 'Calle Almirante Castillo 880', 'contacto@liceomejillones.cl', 'Gonzalo Tapia Ríos', 'gtapia@liceomejillones.cl', '+56 55 2421188', 610, 'Municipal', 'Fabiola Rojas', 'Liceo', 1);

INSERT INTO visitas (id, rbd, tecnico_responsable, estado, tipo_soporte, prioridad, fecha_programada, fecha_realizada, motivo, detalle_hardware, seguimiento_bitacora, observaciones_cierre, firma_recepcion)
VALUES
(
    1,
    1024,
    'Sebastian Guevara',
    'Realizada',
    'Problemas de Conectividad',
    'Alta',
    '2026-08-15',
    '2026-08-15 16:30:00',
    'Mantenimiento preventivo e instalación de puntos de acceso Wi-Fi para laboratorios.',
    '{"red_ubiquiti": [{"tipo": "AP UniFi U6-Pro", "cantidad": 4, "estado": "Operativo"}], "impresoras": [{"marca": "Ricoh", "modelo": "MP 3055", "ubicacion": "Secretaría"}]}',
    '[{"fecha": "2026-08-15 09:30", "autor": "Sebastian Guevara", "nota": "Llegada al establecimiento. Se inicia levantamiento de cobertura de señal."}, {"fecha": "2026-08-15 14:00", "autor": "Sebastian Guevara", "nota": "Montaje de 4 APs UniFi U6-Pro finalizado con PoE activo y VLAN de alumnos configurada."}]',
    'Se realizó el despliegue de 4 APs Ubiquiti UniFi y se verificó cobertura en laboratorio 1 y 2. Impresora Ricoh reconfigurada con segmento IP fijo.',
    'Carlos Mendoza Silva - Director'
),
(
    2,
    1026,
    'Rodrigo Bravo',
    'Pendiente',
    'Soporte Correctivo',
    'Urgente',
    '2026-08-20',
    '2026-08-20',
    'Falla en enlace de fibra óptica interior y conmutación de switch de distribución de administración.',
    '{"red_ubiquiti": [{"tipo": "EdgeSwitch 24 Lite", "estado": "Intermitencia en puertos"}], "impresoras": [{"marca": "Kyocera", "modelo": "ECOSYS M2040dn", "estado": "Pendiente tóner"}]}',
    '[{"fecha": "2026-08-20 11:15", "autor": "Rodrigo Bravo", "nota": "Diagnóstico inicial: Módulo SFP de fibra dañado por sobretensión."}, {"fecha": "2026-08-20 13:00", "autor": "Rodrigo Bravo", "nota": "Se deja en estado Pendiente a la espera de repuesto de módulo SFP monomodo."}]',
    'Visita pausada: requiere reemplazo de módulo transceptor SFP y entrega de tóner Kyocera.',
    NULL
),
(
    3,
    1027,
    'Claudio Rojas',
    'En Proceso',
    'Problemas de Conectividad',
    'Media',
    '2026-09-01',
    NULL,
    'Revisión semestral de infraestructura tecnológica, rack principal y auditoría de red de laboratorios.',
    '{"red_ubiquiti": [{"tipo": "UDM-Pro", "estado": "En diagnóstico"}, {"tipo": "Switch Pro 48 PoE", "estado": "Operativo"}]}',
    '[{"fecha": "2026-09-01 10:00", "autor": "Claudio Rojas", "nota": "Inicio de auditoría de cableado estructurado y actualización de firmware en UDM-Pro."}]',
    NULL,
    NULL
),
(
    4,
    1028,
    'Sebastian Guevara',
    'Programada',
    'Impresoras y Periféricos',
    'Baja',
    '2026-09-05',
    NULL,
    'Instalación y configuración de 2 impresoras multifuncionales en sala de profesores y enlace a red docente.',
    '{"impresoras": [{"marca": "Brother", "modelo": "DCP-L5650DN", "cantidad": 2, "estado": "Por instalar"}]}',
    '[{"fecha": "2026-08-30 16:00", "autor": "Sebastian Guevara", "nota": "Visita coordinada con la dirección escolar."}]',
    NULL,
    NULL
);
