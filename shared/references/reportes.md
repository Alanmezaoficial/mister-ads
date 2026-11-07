# Reportes

La base anuncia `/ads report` pero no incluye un submódulo ads-report. El helper real es `engine/scripts/generate_report.py`. No intentar abrir una ruta inexistente.

Lee su ayuda y contrato de entrada antes de usarlo, comprueba las dependencias opcionales y ejecuta su modo `--check` antes de generar. Usa el JSON de auditoría validado con engine/ads/references/audit-output-schema.json, no el ledger comercial como si fuera una auditoría.

Si el host ofrece una skill de PDF adecuada, puede usarse para el reporte propio combinando fuentes citadas. En ambos casos renderiza y revisa márgenes, tablas, cifras y cobertura antes de entregar. Sin herramientas/dependencias para PDF, entrega Markdown y explica qué falta; no presentes ese archivo como PDF.
