# MercaYa AI Studio | Growth Decision Copilot

**Problema.** Un reporte de incidencias no basta para decidir qué probar, cómo medirlo y qué aprobar antes de actuar.

**Solución.** Fuentes → validación → oportunidad → estrategia → experimento editable → tracker accionable. La portada prioriza oportunidades comerciales; las incidencias técnicas y promocionales siguen como guardrails.

**Caso demostrable.** Bogotá reporta CVR 2,9% vs forecast 3,6% (−0,7 pp), con 185.000 sesiones. Se propone investigar abandono por paso y diseñar una prueba controlada de simplificación de checkout. Es una hipótesis; no existe evidencia actual de que checkout cause la brecha. Los cortes regionales deben confirmarse.

**Decisión interactiva.** Elegir checkout, calidad del tráfico o claridad de oferta cambia plan, hipótesis, control, KPI y protecciones. Editar responsable, éxito, población y duración cambia realmente las salidas. Medios, CRM y promociones tienen estrategias específicas, sin inventar audiencias ni impactos.

**Simulación explícita.** Sesiones × diferencia de conversión produce pedidos hipotéticos. El valor bruto usa ticket supuesto; escenarios 0,5×/1×/1,5× no son predicciones. Medellín/Medellin se excluyen hasta aclarar grano.

**Automatización efectiva.** Asistente de tres pasos, vista ejecutiva de cinco elementos, tracker CSV descargable directamente, con evidencia, responsable propuesto, experimento y aprobaciones pendientes. Descarga invalidada tras editar el plan; borradores conservados en sesión. Tracker técnico CSV disponible.

**Arquitectura.** Streamlit + pandas + reglas originales R01–R07 intactas + extensión determinística Growth. Sin LLM, APIs comerciales ni ejecución externa. IA generativa asistió construcción y revisión; no se simula en producción.

**Controles.** No se modifican presupuestos. >20% entre canales requiere Marketing Lead; cupones requieren Finanzas; comunicaciones requieren términos oficiales. Inversión considera ROAS, incrementalidad y pacing. Estado: Pendiente de aprobación humana.

**Validación y límites.** Tests de motor/UI, ZIP, escenarios, estrategias y exportaciones. Sin potencia estadística, ticket regional comparable, integración de aprobaciones, datos de pagos ni causalidad demostrada. Próximo piloto: medir tiempo hasta plan revisado y proporción de planes aprobados; sin impacto logrado atribuido.
