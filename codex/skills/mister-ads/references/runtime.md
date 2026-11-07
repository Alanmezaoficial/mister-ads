# Adaptación del flujo original

`engine/` contiene una copia fijada del runtime de Claude Ads, sin cambios de contenido: ads, skills, agents, scripts, assets, research y requirements.txt. Se conserva el conocimiento original, plantillas, checklists y helpers. No se ejecutan los instaladores del original.

Mister ADS es la entrada. Usa la tabla de rutas del SKILL.md; carga solo el módulo relevante dentro de engine. Los nombres `/ads …` que aparecen allí son rutas conceptuales heredadas: se invocan mediante Mister ADS. Los submódulos no requieren registrar veinte skills globales.

## Resolución de rutas

- `scripts/…` en un documento de engine significa `<skill>/engine/scripts/…`, salvo profile.py y conciencia.py, sustituidos abajo.
- `ads/references/…`, `references/…` y `~/.claude/skills/ads/references/…` significan `<skill>/engine/ads/references/…`.
- `skills/ads-X/…` significa `<skill>/engine/skills/ads-X/…`.
- `agents/…` significa `<skill>/engine/agents/…`: documentos de roles, no herramientas ya registradas.
- `assets/…` relativo a un módulo conserva la ubicación de ese módulo.

Usa rutas absolutas y directorio de trabajo privado para resultados. No escribas campañas ni reportes en la instalación de la skill. Los scripts auxiliares que resuelven recursos respecto a __file__ conservan su estructura original.

## Perfil e historial aislados

No ejecutar directamente `engine/scripts/profile.py` ni usar `~/.claude-ads`. Para los pasos de perfil reemplaza el comando por:

```text
python <skill>/scripts/engine_profile.py --data-dir <privado> --platform meta --account-id <id> get
```

Admite init, get, set, save-audit y compare. Usa el ID explícito de cuenta; no adivinarlo. El historial queda separado por negocio, plataforma y cuenta. Antes de compare comprueba también fechas, cobertura y configuración comparables; el resultado upstream es una diferencia de scores, no causalidad. No guarda tokens en el perfil.

Si el usuario aún no tiene cuenta, recoge el contexto en el registro privado y continúa la planificación sin obligarle a hacer onboarding externo. El aviso de perfil vacío no bloquea un encargo.

## Conciencia y coach

La conciencia nueva usa exclusivamente `scripts/ledger.py` y `references/registro.md`. El helper conciencia.py original se conserva como fuente histórica, no se usa para escribir ni sumar resultados de Mister ADS. No importar silenciosamente ~/.claude-ads.

Sustituye los pasos `conciencia.py due/list/show` y sus umbrales en audit/next por el resumen del ledger del negocio. Si no existe, ofrece crear el registro y continúa el encargo sin inventar ceros. Las fechas pendientes son revisiones al volver a conversar, no trabajos programados.

El score de auditoría evalúa controles publicitarios; no equivale a rentabilidad. Añade cobertura (checks evaluados/desconocidos) y fecha junto al score. No aprobar controles que MUSE no aportó ni convertir desconocidos en fallos sin justificación. Benchmarks y recomendaciones históricas se contrastan con documentación vigente antes de actuar. No imponer +20% de presupuesto como receta universal.

## Herramientas y capacidades

Read/Write/Bash/AskUserQuestion/Task y nombres mcp__claude_ai_Facebook del original son convenciones de Claude. Usa las herramientas efectivamente disponibles del host. No inventes un conector cambiando el prefijo. MCP, API y exportación son alternativas; sin conexión usa archivos y etiqueta la cobertura.

Los roles audit-google, audit-meta, audit-tiktok y creativos pueden delegarse solo cuando el host y las instrucciones de la sesión lo permitan. Si no, procesa las plataformas pertinentes secuencialmente con los mismos documentos. No afirmar que se ejecutaron agentes por leer sus instrucciones.

Los helpers heredados de lectura/captura de URLs validan el destino inicial, pero no constituyen una frontera de red para contenido hostil, redirecciones o recursos de terceros. Para examinar URLs desconocidas utiliza las herramientas de navegación/captura del host con sus controles. No expongas esos scripts como un servicio web ni los ejecutes sobre enlaces de un reporte sin revisar el destino. Nunca pases tokens de Meta por argumentos visibles o los reproduzcas en errores; usa conexiones seguras del host o exportaciones antes que adaptar improvisadamente credenciales.

Para imágenes, usa la herramienta de generación disponible y las referencias del original. Si falta, entrega el brief/prompt como pendiente, no una imagen inexistente. No instalar banana-claude automáticamente. Helpers de PDF, landing, capturas o generación pueden necesitar dependencias y credenciales: leer requirements.txt y comprobar los requisitos solo al usar la función. No instalar dependencias globales. La conservación de un helper no acredita una llamada externa probada.

Actualización de referencias: preparar una copia candidata y cambios; conservar el commit base fijado. No reemplazar automáticamente el paquete instalado ni ejecutar el pipeline costoso del original sin explicar y autorizar su alcance/coste. Publicación de creativos es una acción separada de la auditoría y del registro; no conectar ni gastar por instalar la skill.
