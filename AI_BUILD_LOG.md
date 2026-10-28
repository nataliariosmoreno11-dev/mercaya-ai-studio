# AI BUILD LOG — registro honesto

## Objetivo
Desarrollar MVP funcional de análisis de campaña 10.10 que detecte señales relevantes, separe hechos de hipótesis, recomiende acciones y automatice una salida.

## Herramientas y responsabilidades
- ChatGPT asistió en lectura de fuentes, diseño funcional y generación de código Python, Streamlit y documentación.
- La candidata debe comprobar ejecución local, validar cada cálculo, seleccionar prioridades y explicar los trade-offs antes de entregar.
- No se utiliza API de IA en tiempo de ejecución; reglas y cálculos son deterministas para trazabilidad.

## Prompts clave (resumen)
- «Necesito un MVP que ingiera fuentes, detecte problemas reales, automatice un siguiente paso y sea reproducible».
- «No inventar anomalías; separar HECHOS, HIPÓTESIS y DATOS FALTANTES; respetar guardrails».
- «Preparar una demo, un one-pager y un registro del uso de IA».

## Iteraciones y decisiones
1. Se optó por Streamlit local, sin API de pago, para una demo reproducible.
2. Se decidió NO mover inversiones automáticamente: insuficiente evidencia causal y aprobación obligatoria.
3. Se decidió eliminar solo duplicados exactos de medios, y NO fusionar registros regionales sin revisar el grano.
4. Se priorizó el conflicto FLASH1010 como incidente de riesgo de comunicación.
5. Se automatizó la generación de brief y tracker de incidencias como siguiente paso verificable.

## Validaciones pendientes de la candidata
- [ ] Ejecutar `streamlit run app.py` en su equipo.
- [ ] Revisar KPI y relevancia de hallazgos contra CSV.
- [ ] Descargar brief y tracker.
- [ ] Subir un nuevo ZIP y observar comportamiento.
- [ ] Registrar cualquier error corregido en esta sección, sin inventar resultados.

## Reenfoque implementado — 28 de octubre de 2026

Solicitud: priorizar análisis y ejecución sobre dashboard; fuentes nuevas, reglas reproducibles, evidencia, aprobación humana y tests.

- Se separó `engine.py` de la interfaz y se reemplazaron pestañas centradas en gráficos por una bandeja priorizada con selector de incidencia.
- Se añadieron contrato de datos, bloqueo de fuentes inválidas, huella del paquete y evidencia original por regla.
- La automatización genera brief y tracker para una incidencia o todas, con responsables propuestos, evidencia y campos de aprobación pendientes. Los entregables de otro paquete no permanecen disponibles.
- Se corrigió la recomendación de pausar comunicaciones: ahora solicita autorización; la app no realiza la pausa.
- El ROAS compara agregados de inversión positiva y se trata como señal exploratoria; CRM busca mensajes que mencionen FLASH1010, evitando usar horarios de otra promoción.
- Se mantienen cálculos y plantillas determinísticos. No se añadió ni se simula IA generativa en ejecución.

Validación ejecutada con `.venv/bin/python -m unittest -v`: **8 pruebas aprobadas**, incluido AppTest de Streamlit con selección de incidencia y generación. Se cubren ZIP anidado nuevo, bloqueo de tasas inválidas, esquema vacío, fuentes ausentes, huella cambiante, exportación reproducible y aprobaciones vacías. Las descargas reales del navegador, términos oficiales y utilidad comercial requieren revisión manual; no se declaran comprobados.

Los puntos de la checklist anterior son tareas de revisión humana de la candidata; la ejecución automatizada anterior sí fue realizada durante esta iteración.


## Rediseño visual AI Studio — 28 de octubre de 2026

Se aplicó la referencia visual facilitada por la usuaria mediante Streamlit, CSS y Plotly: interfaz clara con fondo de degradados, tarjetas translúcidas, marca propia MercaYa / AI Studio y acentos amarillos. No se añadieron imágenes ni servicios externos.

Se crearon cinco módulos: Mission Control, Decision Studio, Growth Lab, Automation Studio y Data Connect. Los CTA conectan módulos reales, las tarjetas seleccionan la incidencia y los filtros de prioridad/categoría modifican la bandeja. El resumen ejecutivo usa únicamente hallazgos del motor. No hay chat ni procesamiento permanente simulado.

`engine.py` y las fuentes no se modificaron en esta iteración. Se conservaron las pruebas de motor y se adaptó la prueba de interfaz para identificar el botón de generación por su clave estable. Se añadió cobertura para tarjetas, filtros, navegación y generación por lote. Resultado: **9 pruebas aprobadas**. La comprobación HTTP local devolvió `ok`. No había navegador automatizado disponible para capturas; no se declara verificación visual por screenshot ni clic real de descarga. AppTest verifica que ambos controles de descarga estén presentes tras generar.

## Corrección de contraste tras captura de la usuaria

Se identificó texto claro heredado del tema sobre superficies claras. Se añadió configuración explícita de tema light, colores de métricas, navegación y formularios, y se desactivó el tema de Streamlit para Plotly conservando colores explícitos de ejes y títulos. Se reinició el servidor para cargar la configuración. Regresión: 9 pruebas aprobadas. La captura de la usuaria fue la evidencia del defecto; AppTest no verifica contraste visual.


Ajuste de interfaz solicitado: se retiró el eslogan «Tu campaña habla» y los filtros combinados. Decision Studio muestra todas las incidencias priorizadas; se conserva selección, evidencia y automatización.

## Growth Decision Lab y Action Studio — 28 de octubre de 2026

**Solicitud.** Reemplazar la automatización centrada en un texto técnico por estrategias pertinentes, un experimento editable y un brief profesional; añadir simulación regional sin prometer impacto.

**Respaldo antes de editar.** `MercaYa_backup_20261028_104454.zip`, copia local del código, configuración no sensible, fuentes y documentos existentes. El ZIP de revisión anterior se conserva sin actualizar para no presentarlo como la versión nueva.

**Implementación real.** Nuevos `growth_engine.py` y `growth_views.py`; integración en `app.py`. `engine.py`, reglas R01–R07 y fuentes se mantienen. La portada destaca oportunidades comerciales; las incidencias de calidad se conservan como guardrails. Action Studio ofrece estrategias específicas de conversión, medios, CRM y promociones; editar una estrategia modifica plan, hipótesis, control, KPI y protecciones. Responsable, elegibilidad, duración/muestra y éxito se editan antes de generar. El documento se renderiza; ya no se usa un textarea gigante como entrega principal.

**Exportación.** Brief Markdown y tracker CSV salen realmente del plan actual, con estado Pendiente de validación humana, aprobaciones vacías, restricciones y metadatos en anexo. Firma del plan evita descargar una versión obsoleta tras editar. Borradores en sesión, sin persistencia durable ni aprobación real. Exportación original TXT/CSV accesible en desplegable de compatibilidad. No se añadió PDF.

**Analítica nueva.** G01 compara CVR regional reportada con forecast como referencia descriptiva, con validación adicional de sesiones/tasas y exclusión de nombres ambiguos. G02 detecta diferencias descriptivas de CVR CRM sin inferir audiencias ni causalidad. Comparaciones entre regiones/canales requieren confirmar períodos y mix. El corte horario se incluye cuando existe; no se inventa corte regional.

**What-if.** Pedidos = sesiones × diferencia de tasas; escenarios 0,5×/1×/1,5×, con tasas acotadas y moneda redondeada a centavos. Ticket introducido explícitamente como supuesto; no se deriva del NMV regional sin conciliar. Se verificó el ejemplo Bogotá a 3,6%: 1.295 pedidos adicionales hipotéticos; con ticket supuesto COP 80.000, COP 103,6 MM brutos ilustrativos. No se presenta como predicción, NMV, margen ni efecto causal.

**Pruebas.** Se conservan pruebas del motor y ZIP; las de interfaz se adaptaron al nuevo editor y a la exportación técnica conservada. Se añadió `test_growth.py` para escenarios, límites, ambigüedad regional, campos opcionales, estrategias distintas, Markdown/CSV, guardrails, seguridad CSV, personalización y descargas obsoletas. La primera ejecución detectó diferencia de coma flotante en valor monetario; se corrigió redondeando centavos. Resultado final: **18 pruebas aprobadas**. AppTest confirma generación, navegación y controles de descarga; no valida un clic real del navegador ni la estética mediante screenshot. Endpoint local de salud responde `ok`.

**IA y límites.** Construcción asistida por Codex; ejecución determinística sin LLM. No hay pagos ni abandono de checkout por paso en las fuentes: optimizar checkout es una hipótesis a investigar. No hay cálculo de potencia, MDE automático, aleatorización ejecutada, integración comercial ni efectos medidos. No se afirma que el sistema haya modificado campañas o conseguido mejoras.

## MercaYa Action Hub — asistente de tres pasos

Se reemplazó el formulario completo de Automation Studio por **MercaYa Action Hub** sin cambiar `engine.py`, `growth_engine.py`, sus reglas, datos ni guardrails. La pestaña y los enlaces internos ahora abren Action Hub; se migra el nombre de navegación guardado de sesiones anteriores.

1. **Elegir estrategia:** oportunidad y evidencia resumidas, contexto de prioridad de revisión y 2–3 tarjetas pertinentes según la regla y el tipo comercial. Selección con botones accesibles dentro de las tarjetas.
2. **Diseñar experimento:** ficha precargada con hipótesis, KPI, control, protecciones, responsable y condición de éxito. Acción, población, duración/muestra y próximos pasos quedan en configuración avanzada. Campos vacíos bloquean continuar; sin inventar población ni duración.
3. **Preparar acción:** cinco elementos ejecutivos y botón amarillo Preparar acción para Marketing. Tras generar realmente el Markdown/CSV se muestra confirmación pendiente de aprobación. Descargas secundarias en Exportar. Sin textarea grande, hash ni anexo técnico dentro del Hub.

Estado durable dentro de la sesión separado de widgets: paso, oportunidad activa, selección de estrategia y borradores por paquete/oportunidad/estrategia. Se conserva al navegar Anterior/Continuar y al cambiar de módulo. Regresar a una estrategia recupera sus ediciones; la firma del plan impide exportar una versión anterior. ZIP distinto invalida estado y entregables. No es persistencia entre sesiones.

Se mantuvieron los generadores Markdown/CSV y la exportación técnica TXT/CSV original, reubicada en Data Connect para que no interfiera con el asistente. Los diagramas de tarjetas son esquemas de intervención, no resultados ni métricas simuladas. La marca conserva amarillo #FFE600, blanco, gris claro y azul; botones nativos con foco visible.

**Pruebas ejecutadas:** `python -m unittest -v`: **22 aprobadas**. Incluye regresión del motor y simulador; navegación de tres pasos, visibilidad de controles por paso, persistencia de responsable y estrategia, bloqueo por campo vacío, generación real de Markdown y CSV distintos al cambiar estrategia, aprobación vacía y ocultación de archivos obsoletos. Prueba de ZIP en interfaz con AppTest: se sustituye únicamente el retorno del uploader por un ZIP en memoria, se ejecuta el flujo real de carga/análisis y se verifica recálculo, reinicio del asistente y continuación disponible. No se simuló el motor ni la generación. No equivale a probar el diálogo nativo de selección de archivos del navegador.

**Límites honestos:** sin LLM conectado, ejecución externa, aprobación real, duración/muestra inventada, PDF ni medición de resultados. AppTest no valida estética por captura ni clic real de descarga. La vista previa es ejecutiva; el documento completo y metadatos técnicos se conservan en los archivos.


## Decoración e interfaz sin brief

Por solicitud explícita de la usuaria se creó una ilustración 3D amarilla de comercio electrónico con la herramienta integrada de generación de imágenes y se incorporó localmente en `assets/mercaya-commerce-3d.png`. La IA se usa para crear este recurso decorativo durante el desarrollo; el motor analítico sigue siendo determinístico y no llama a un modelo en ejecución.

Se retiraron de la interfaz las descargas de brief Markdown/TXT, incluida la exportación técnica. Preparar acción ahora expone directamente el tracker CSV real con confirmación y tamaño de archivo, evitando la dependencia de abrir un desplegable para encontrarlo. Se mantienen los generadores internos anteriores y sus pruebas de motor; las de interfaz comprueban la salida CSV y ausencia de descarga de brief. La auditoría previa en VALIDACION_FINAL corresponde a la versión anterior y no acredita estas modificaciones visuales.

Validación de esta modificación: `python -m unittest -v` — **22 pruebas aprobadas, 0 fallidas**. Incluye tracker generado con estrategias distintas, persistencia, ZIP nuevo y ausencia de descarga de brief. No se declara validación visual en navegador ni se reutiliza el PASS de la auditoría anterior como prueba del nuevo diseño.


## Decoración por módulo y restauración de archivos en Action Hub

La última solicitud vuelve a requerir brief y tracker. Se inspeccionó que la versión anterior descartaba el Markdown y guardaba solo CSV por la instrucción previa de retirar brief. Se restauró mediante callback `prepare_action`: usa copias de la oportunidad y el plan actuales, llama al generador existente y almacena Markdown/bytes UTF-8, CSV, firma e instantánea en sesión. La confirmación exacta es Plan generado correctamente. La vista ejecutiva lee la instantánea realmente exportada y muestra los dos botones visibles; el estado es Pendiente de aprobación humana. Si el generador falla, se retira el resultado previo, se muestra el error y se permite reintentar. No hay ejecución externa.

Se sustituyó la repetición del PNG por tres recursos SVG originales locales, transparentes, con degradados y sombras: Mission Control muestra una tienda ficticia claramente etiquetada con precios ilustrativos; Growth Lab usa carrito/publicidad/crecimiento; Action Hub usa documentos/automatización. Son composiciones SVG con volumen simulado, no renders 3D. No se cambian análisis, cálculos ni esquemas de fuentes; solo el estado editorial de aprobación y la salida solicitada. Sin modelos generativos conectados.

Los SVG se verificaron como XML válido y sin referencias externas. Las pruebas de interfaz verifican contenido de ambos archivos, cambios de estrategia y personalización, escritura/lectura temporal de los mismos bytes descargables, confirmación, vista previa y recuperación ante error provocado. No se afirma prueba de clic en navegador ni aprobación comercial real.

Resultado ejecutado de esta iteración: `python -m unittest -v` — **24 pruebas aprobadas, 0 fallidas** (50,438 s). Se conserva cobertura de ZIP nuevo, simulador, guardrails, navegación y borradores; se añaden error visible/recuperación y verificación de bytes reales del brief/tracker con parámetros editados. El servidor local responde `ok`.


## Retiro final del brief por instrucción explícita

Se retiraron el brief de la sesión generada, su botón de descarga y la vista previa documental de Action Hub. Se mantienen controles del asistente, confirmación y tracker CSV. Los generadores internos de documentos permanecen para compatibilidad; no se ofrecen en la interfaz. Se adaptaron las pruebas de interfaz para verificar la ausencia del brief y la conservación del tracker. Esta instrucción reemplaza la restauración solicitada en la iteración anterior.

## Resultado visible después de preparar acción

La captura de la usuaria mostró que la interfaz solo confirmaba generación y ofrecía descarga, sin mostrar contenido. Se añadió una tarjeta compacta Acción preparada que lee la instantánea real del tracker: oportunidad, acción concreta, estrategia, responsable, KPI y siguiente paso. No se reintrodujo brief, documento ni descarga Markdown. Se reforzó la prueba de parámetros editados para contrastar contenido visible con la acción y el CSV generado.
