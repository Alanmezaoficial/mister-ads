# Mister ADS

Anuncios, registro comercial desde cero y reportes manuales de MUSE para **Codex y Claude Code**. Versión 1.0.0.

Adaptación de Alanmeza.ai sobre Claude Ads de agricidaniel y Enrique Rocha / tododeia. Conserva los recursos del original fijados por commit; [autoría](ATTRIBUTION.md), [LICENSE](LICENSE) y [NOTICE](NOTICE).

## Empezar

- [Instalación y guía Codex](docs/guia-codex.md).
- [Instalación y guía Claude Code](docs/guia-claude.md).
- [Formato y registro comercial](shared/references/registro.md).
- [Qué hace la integración MUSE](shared/references/muse.md).
- [Pruebas y límites](docs/validacion.md).

Puedes empezar sin CRM, sin anuncios activos y sin MUSE. El asistente ayuda a registrar oportunidades, ventas acordadas, cobros y reembolsos en archivos privados. El importador comprueba negocio, moneda, duplicados y referencias; conserva revisiones. Los reportes publicitarios son snapshots y no se suman entre sí automáticamente.

## Alcance

Se conserva el material para auditorías Meta/Google/TikTok, estrategia, creativos, landing, presupuesto, experimentos, PDF y seguimiento. Las funciones externas requieren herramientas, dependencias o credenciales disponibles en el host. No se prometen llamadas a proveedores que no se han probado.

MUSE entrega archivos que el usuario comparte. No incluye una API entrante a MUSE, sincronización entre asistentes, tareas programadas ni cambios automáticos de presupuesto. Los datos comerciales no se envían a Alanmeza.ai ni pertenecen al repositorio público.

## Desarrollo

Python 3.11+ para scripts nuevos, sin dependencias adicionales. `python scripts/build.py --package` construye ambas ediciones y los ZIP. `python -m unittest discover -s tests -v` valida el núcleo y los instaladores. Los helpers opcionales del original conservan su requirements.txt y se preparan en un entorno aislado solo si se requieren.

`upstream/` es la base fijada; `shared/` contiene la mejora propia; `codex/` y `claude/` son las ediciones generadas. No editar las copias generadas: cambiar shared y reconstruir. `upstream.lock.json` verifica integridad antes de empaquetar.
