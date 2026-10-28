# MercaYa AI Studio

Copiloto local de decisiones de Growth Marketing para un e-commerce ficticio. Analiza fuentes, propone estrategias y prepara experimentos y entregables para revisión humana. Reglas y plantillas determinísticas: **no hay modelo generativo conectado ni ejecución comercial automática**.

## Ejecutar y probar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
python -m unittest -v
```

Abrir http://localhost:8501. Requiere Streamlit ≥1.66 para navegación programática. La configuración local fuerza tema claro; `styles.css` conserva amarillo, blanco y azul con contraste explícito.

## Flujo de uso

1. **Data Connect:** cargar nuevo ZIP o usar ejemplo local. Revisar validaciones y fuentes bloqueadas.
2. **Mission Control / Growth Lab:** revisar oportunidades comerciales con magnitud, referencia descriptiva, hipótesis y datos faltantes. Las incidencias de calidad siguen visibles como guardrails en Decision Studio.
3. **MercaYa Action Hub:** asistente de tres pasos. Elegir estrategia mediante tarjetas; diseñar el experimento con campos esenciales y configuración avanzada; preparar la acción desde una vista ejecutiva de cinco elementos. Solo un paso es visible a la vez.
4. Revisar oportunidad, estrategia, experimento, KPI y aprobaciones, y pulsar **Preparar acción para Marketing**. Ver la confirmación **Plan generado correctamente**, el botón visible **Descargar tracker CSV**. El tracker refleja las selecciones actuales. Cambiar cualquier campo invalida las descargas previas hasta regenerar.
5. Guardar archivos y obtener aprobaciones fuera de la aplicación. El estado siempre es **Pendiente de aprobación humana**. No se asigna trabajo ni se aprueban cambios automáticamente.

Los borradores y entregables se conservan en `st.session_state` durante la sesión. No se guardan en una base de datos ni sobreviven necesariamente al cierre del navegador. Cambiar de paquete invalida borradores, selección y exportaciones anteriores. El tracker técnico CSV sigue disponible en Data Connect. La interfaz ofrece únicamente el tracker CSV, sin brief ni vista documental. Los archivos son contenidos reales en memoria de la sesión y se guardan en el equipo al descargarlos.

## Oportunidades y estrategias

`engine.py` conserva las reglas R01–R07 y sus validaciones. `growth_engine.py` extiende esas señales sin modificar sus cálculos:

- **G01 regional:** fila inequívoca con sesiones positivas y CVR reportada menor al forecast. Bogotá: 2,9% vs 3,6%, brecha −0,7 pp; 185.000 sesiones. Se propone investigar checkout, calidad del tráfico o claridad de oferta. Ninguna causa está demostrada.
- **R05 / R07:** conversión horaria y eficiencia atribuida de medios. Las estrategias varían entre checkout/landing/oferta y creatividad/holdout. Comparar ROAS de canales no mide incrementalidad.
- **G02 CRM:** al menos dos comunicaciones con CVR post-clic válida y distinta; revisión de mensaje o frecuencia. No se inventan denominadores ni audiencias desde nombres de envíos.
- **R03 / R04 promociones:** conciliar términos o diseñar monitoreo de consumo; no cambiar vigencias ni presupuesto.

Orden de presentación comercial: conversión, medios, CRM, promociones; no es una estimación de ingresos ni una autorización. Las reglas y fuentes se incluyen en el anexo técnico del brief. Los cambios manuales son propuestas de la persona usuaria, no hallazgos derivados de los datos.

## What-if regional

Seleccionar región y CVR objetivo. Introducir ticket **supuesto**, porque no existen pedidos/ticket regionales comparables y el NMV no está conciliado.

`pedidos adicionales hipotéticos = sesiones × (CVR objetivo − CVR observada)`

Escenarios conservador/base/ambicioso aplican 0,5× / 1× / 1,5× al cambio de CVR, con tasas limitadas a [0,1]. Valor bruto ilustrativo = pedidos × ticket supuesto, redondeado a centavos. No es NMV, margen, predicción ni uplift causal. Se mantienen sesiones y otras condiciones constantes. Objetivos menores generan valores negativos. Exportación CSV incluye los supuestos.

Medellín/Medellin se excluyen de oportunidades regionales y simulación hasta confirmar si se superponen; no se suman ni se promedian. La fuente regional no tiene fecha explícita: forecast y regiones son referencias descriptivas pendientes de confirmar corte y definición. No se asume que compartan período con el archivo horario. No hay datos de pagos, carrito ni checkout por paso: estos deben solicitarse, no inventarse.

## Contrato de ZIP

CSV UTF-8, coma como separador, punto decimal. Nombres exactos; subcarpetas permitidas. Máximo 25 MB descomprimidos; nombres repetidos se rechazan. Sin extracción a disco. Fuentes parciales admitidas con menor cobertura explícita. Archivos adicionales se ignoran.

| Archivo | Columnas mínimas del motor original |
| --- | --- |
| 01_business_hourly.csv | timestamp, actual_sessions, orders, actual_cvr, actual_nmv_cop_mm, forecast_nmv_cop_mm, forecast_cvr |
| 02_paid_media.csv | channel, spend_cop_mm, attributed_revenue_cop_mm, sessions |
| 03_regions.csv | region, actual_nmv_cop_mm |
| 04_coupons.csv | coupon, budget_cop_mm, consumed_cop_mm, system_validity_window |
| 05_crm.csv | message |
| 06_competitors.csv | competitor, promotion, source_status |
| 07_campaign_brief.docx | Opcional; texto en párrafos con FLASH1010 y ventana HH:MM-HH:MM |

Extensión Growth: regiones necesita `actual_sessions` positiva y `actual_cvr` en [0,1]; `forecast_cvr` válido habilita la referencia contra forecast. CRM necesita `communication` y `post_click_cvr` válida. Sin estas columnas se omite la oportunidad correspondiente sin romper el resto del motor. Competidores solo aporta contexto. El diccionario XLSX no se interpreta automáticamente.

## Seguridad y límites

Validación estructural no prueba exactitud. No se infiere causalidad, poblaciones experimentales ni resultados logrados. Duración, muestra, MDE y criterio de éxito requieren acuerdo previo al experimento. La herramienta prepara el protocolo; no calcula potencia ni ejecuta aleatorización.

Cambios >20% de presupuesto entre canales requieren Marketing Lead; inversiones requieren ROAS, volumen incremental y pacing. Cambios de presupuesto de cupones requieren Finanzas. Verificar términos oficiales antes de comunicaciones. Ningún cambio se ejecuta desde la app. CSV editable protege campos que podrían interpretarse como fórmulas.

## Archivos y pruebas

- `engine.py`: ingestión, validación y reglas originales.
- `growth_engine.py`: oportunidades, estrategias, simulador, brief y tracker.
- `growth_views.py`: editor interactivo y vista de Growth.
- `app.py`, `styles.css`, `.streamlit/config.toml`: presentación y navegación.
- `test_engine.py`, `test_growth.py`: regresión, ZIP nuevo, matemáticas, estrategias, exportaciones, guardrails, edición y navegación con AppTest.

El backup local previo a esta mejora es `MercaYa_backup_20261028_104454.zip`. `MercaYa_AI_Studio_Revision.zip` corresponde a una revisión anterior y no se actualiza automáticamente.


## Action Hub: navegación y estado

**Anterior / Continuar** conserva las ediciones. Los borradores se separan por paquete, oportunidad y estrategia; cambiar de estrategia precarga otro plan, y regresar recupera las ediciones del anterior. Se bloquea continuar si quedan campos obligatorios vacíos. Una firma del plan impide exportar documentos de otra selección o de una versión anterior.

Las tarjetas representan estrategias determinísticas pertinentes; sus diagramas son esquemas de intervención, no gráficos de resultados. Las prioridades son de revisión, no estimaciones económicas. No se muestran SHA256 ni anexos técnicos dentro de Action Hub; la trazabilidad sigue en archivos descargados y Data Connect. El tracker técnico está disponible en Data Connect. No se implementan aprobación externa ni persistencia durable.


## Decoración y salida actual

Recursos originales SVG/CSS con volumen simulado y transparencia: `assets/mission-commerce.svg` (smartphone y tienda MercaYa ficticia), `assets/growth-commerce.svg` (crecimiento, carrito y publicidad) y `assets/action-automation.svg` (documentos y automatización). Son ilustraciones, no renders 3D ni datos del assessment. Los precios del teléfono son ficticios y su botón Comprar no tiene función. No se usan URLs externas. El PNG de una versión anterior se conserva como recurso histórico, pero ya no se repite entre páginas.

Preparar acción para Marketing ejecuta el generador con una instantánea de la oportunidad, estrategia y parámetros actuales. Al completarse, muestra **Plan generado correctamente**, una vista ejecutiva de esa misma instantánea y dos descargas directas. Editar el plan invalida los archivos anteriores hasta regenerar. Los errores se muestran y permiten reintentar. Ningún archivo se envía ni se ejecutan cambios comerciales.


Última instrucción aplicada: brief y vista previa documental retirados de Action Hub. Se conserva la confirmación y la descarga directa del tracker CSV.
