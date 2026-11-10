---
title: "Mister ADS · Guía Codex"
---

# Mister ADS para Codex

Planea tus anuncios, registra lo que pasa con tus ventas y cruza ambos resultados. Puedes empezar sin CRM, sin campañas activas y sin MUSE. Versión 1.0.0.

## Qué necesitas

Codex con acceso a archivos y ejecución local. Python 3.11 o posterior para el registro y el importador; comprueba el ejecutable disponible. No es un prompt que se instala pegándolo en cualquier chat sin herramientas. Los helpers opcionales para PDF, imágenes y análisis de páginas tienen requisitos adicionales y se preparan cuando se necesitan.

## Instalar

Repositorio: [Alanmezaoficial/mister-ads](https://github.com/Alanmezaoficial/mister-ads).

Puedes pedirle a tu asistente que lea esta guía e instale la edición Codex, o descargar el ZIP de esa edición desde el Bunker. Descargar no instala por sí solo. Conserva la carpeta completa, incluidos engine, scripts, referencias, ejemplos, LICENSE y NOTICE. Si ya existe, revisa la versión antes de sustituirla.

Instalación manual en PowerShell, con Git y Python disponibles:

```powershell
git clone https://github.com/Alanmezaoficial/mister-ads.git
cd mister-ads
python scripts/install.py --skills-dir "$env:USERPROFILE/.agents/skills"
```

Si tu Codex configura otra carpeta de skills, pasa esa ruta a --skills-dir. Para un ZIP extraído, copia mister-ads completa a esa carpeta sin sustituir una existente. El instalador del repositorio verifica los hashes copiados.

Abre una sesión nueva y comprueba que aparece la skill/plugin. Prueba `$mister-ads` o selecciónala desde el host. La aparición y una conversación real son comprobaciones distintas de copiar archivos.

## Primera conversación

> Usa Mister ADS. Quiero mejorar mis anuncios y todavía no llevo registro de ventas. Ayúdame a empezar.

Te preguntará por tu negocio, moneda, zona horaria y qué consideras una venta. Prepara una carpeta privada que puedas recuperar; no necesitas conocer JSON ni editarlo a mano. Si ya utilizas CRM, hoja o tienda, indícalo para conservar ese sistema como fuente.

## Registrar resultados

> Registra un interesado nuevo. No sé de qué anuncio vino.

> La oportunidad O-0001 cerró por 5,000 MXN. Hoy recibí 1,000 de anticipo.

> Registra otro abono de 2,000 para O-0001 y muéstrame el resumen.

Son ejemplos ficticios, no ventas tuyas. Una oportunidad no se duplica por recibir otro pago. Las correcciones conservan historial. Lo desconocido queda sin atribuir. Si solo tienes totales diarios, el asistente los conserva como notas separadas sin inventar personas ni sumarlos a registros individuales del mismo grupo.

## Trabajar con MUSE

Pide al asistente el prompt incluido para MUSE. En MUSE elige la cuenta y autoriza su lectura si lo deseas. Comparte el archivo que entregue y pide:

> Revisa este reporte de MUSE, comprueba la cuenta y el periodo e impórtalo en mi registro. Explica qué datos faltan antes de recomendar cambios.

La versión 1.0 intercambia archivos manualmente. No conecta automáticamente tus cuentas ni sincroniza MUSE, Codex y el teléfono. Un Space o un destino compartido se evalúan después con pruebas reales. La lectura de Meta depende de los permisos y herramientas de tu MUSE.

## Qué puedes pedir además

Auditar Meta, Google o TikTok; revisar anuncios, landing y presupuesto; planear campañas; preparar briefs y pruebas; revisar próximos pasos. Las imágenes, los PDF y las conexiones externas dependen de las herramientas y requisitos disponibles: la guía no promete accesos que no existen.

## Leer el resultado

Separa ventas acordadas de cobros y reembolsos. No confunde un coste por contacto bajo con rentabilidad, no trata falta de registros como cero ventas y no adjudica una venta a un anuncio desconocido. El resumen publicitario utiliza un snapshot; no suma ventanas solapadas.

El asistente debe indicar fuente, fechas, moneda y limitaciones. Un score publicitario no demuestra beneficio. Tampoco una comparación antes/después demuestra que un cambio causó el resultado.

## Datos y recuperación

El registro queda en la carpeta privada elegida, fuera de la instalación. Haz un respaldo privado. Compartir el ZIP de la skill no comparte tus datos; tampoco subirlos a un chat los sincroniza automáticamente. No pongas archivos de clientes en el repositorio ni en el Bunker. Un solo escritor principal evita copias divergentes.

## Límites de la entrega

El núcleo se prueba con archivos sintéticos, operaciones locales y copias aisladas. La activación conversacional en tu sesión, lectura real de Meta, servicios creativos y automatización MUSE se verifican por separado. No se realizan cambios publicitarios ni gastos por instalarla.

## Créditos

Los avisos de procedencia y licencia se incluyen en la descarga.
