# Caso de estudio: orden en la carpeta de descargas

**Problema**

Un administrador de sistemas gestionaba varios equipos compartidos en una oficina pequeña, y la carpeta de Descargas de cada uno acumulaba miles de archivos sin ningún criterio: instaladores viejos, capturas de pantalla, PDFs de facturas, torrents a medio bajar y copias duplicadas de documentos. Ordenar todo a mano tomaba horas cada mes, y era fácil borrar por error algo importante.

**Solución**

Con Desktop Automation Toolkit, definió un archivo `automate_rules.json` con reglas simples: eliminar automáticamente cualquier `.torrent`, mover imágenes (`.jpg`, `.png`, `.gif`) a una carpeta de "Imágenes" y dejar los PDF de facturas intactos en una carpeta de "Documentos". Antes de aplicar los cambios, usó el modo `--dry-run` del comando `organize` para revisar exactamente qué archivos se moverían o borrarían, sin riesgo de perder nada por accidente.

**Resultado**

Una carpeta con más de 2.000 archivos mezclados quedó organizada en segundos, con una reducción de desorden cercana al 95%. La misma configuración de reglas se reutiliza ahora en todos los equipos de la oficina, y la limpieza que antes tomaba una tarde completa se ejecuta hoy con un solo comando.
