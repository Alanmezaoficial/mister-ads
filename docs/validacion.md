# Validación

Comprobaciones locales del 2026-11-06, Windows y Python 3.12 del runtime disponible.

- 23 pruebas unittest aprobadas: conversión de los archivos ficticios de MUSE, totales, duplicados, conflictos, revisiones, snapshots, valores desconocidos, moneda/negocio, separación real/sintético, referencias de reembolsos, fechas, escritura atómica ante errores, revisión esperada, bloqueo y exportación.
- Instalación aislada de Codex: copia íntegra y rechazo de sobrescritura. Perfil upstream ejecutado en una cuenta de prueba aislada; rechazo de auditoría de otra cuenta.
- Integridad: los 125 archivos de runtime upstream coinciden con sus hashes en ambas ediciones. Los recursos nuevos compartidos también coinciden.
- Validador de skill-creator aprobado para ambas entradas SKILL.md. El YAML se validó con PyYAML ya disponible en un directorio local de herramientas, sin instalar paquetes globales.
- Auditoría focalizada: sin Critical/High confirmados. Nueve coincidencias del scanner son tres ejemplos de credenciales ficticias repetidos en base y ediciones. Los helpers opcionales de red/dependencias heredados requieren revisión al usarlos; no se presentan como una frontera de seguridad de red.

La conservación de recursos del original no demuestra ejecución de todas sus funciones. No se probaron conexiones reales de Meta/Google/TikTok, proveedores creativos, PDF, actualización remota de referencias, publicación publicitaria, activación conversacional en una sesión nueva de Claude/Codex ni programación en MUSE. No se conectaron cuentas ni se registraron ventas reales.

El importador es local y de un escritor; no es un CRM multiusuario ni una base sincronizada. La zona horaria se conserva y se compara como identificador; no convierte fechas entre zonas. Campos numéricos y esquema se validan, pero el programa no puede autenticar la veracidad de un reporte externo.

