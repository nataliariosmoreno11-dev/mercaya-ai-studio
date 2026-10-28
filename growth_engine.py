"""Extensión determinística de Growth; no modifica las reglas R01–R07."""
import hashlib
import io
import json
import math
import pandas as pd
from engine import norm

STATUS = 'Pendiente de aprobación humana'
GUARDRAILS = ('No ejecutar cambios sin autorización. Cambios mayores al 20% de presupuesto por canal requieren Marketing Lead. '
              'Cambios de presupuesto de cupones requieren Finanzas. Verificar términos promocionales antes de enviar comunicaciones. '
              'Recomendaciones de inversión deben considerar ROAS, volumen incremental y pacing. Sin uplift causal demostrado; asignaciones y aprobaciones se realizan fuera de la app.')

# Cada estrategia tiene plan, hipótesis verificable, KPI, control y protecciones propios.
STRATEGIES = {
 'conversion': {
  'Optimizar checkout': ('Investigar abandono por paso del checkout y diseñar una prueba controlada de simplificación.',
   'Una simplificación del paso con abandono confirmado aumentaría la conversión frente al checkout actual.',
   'Tasa de conversión', 'Checkout actual, con asignación aleatoria persistente por usuario elegible.', 'Errores de pago, ingresos por sesión, cancelaciones y latencia'),
  'Validar calidad del tráfico': ('Instrumentar fuente/dispositivo y probar una variante de landing dentro del mismo canal y región.',
   'Una landing alineada con la intención del tráfico mejoraría la conversión frente a la landing actual.',
   'Conversión por sesión elegible', 'Landing actual dentro del mismo canal y dispositivo; asignación aleatoria.', 'Coste por sesión, rebote y margen por pedido'),
  'Clarificar oferta y condiciones': ('Auditar claridad de costes y condiciones; probar una presentación más explícita sin modificar precios.',
   'Mostrar costes y condiciones antes del checkout aumentaría la conversión frente a la presentación actual.',
   'Tasa de conversión', 'Presentación actual con asignación aleatoria por usuario.', 'Reclamos, margen por pedido y abandono')},
 'paid': {
  'Probar calidad de tráfico': ('Comparar variantes creativas dentro del mismo canal manteniendo presupuesto y audiencia aprobados.',
   'Una creatividad alineada con la landing mejoraría la conversión de sesiones elegibles.',
   'Conversión post-clic', 'Creatividad actual con asignación aleatoria y exposición equivalente.', 'CPA, gasto total y frecuencia'),
  'Medir incrementalidad': ('Diseñar un holdout del canal candidato antes de solicitar reasignación de inversión.',
   'El canal genera pedidos incrementales frente a un grupo comparable sin exposición.',
   'Pedidos incrementales por usuario elegible', 'Holdout sin exposición, sujeto a viabilidad y aprobación.', 'Ingresos totales, contaminación entre grupos y gasto')},
 'crm': {
  'Probar claridad del mensaje': ('Preparar variantes de mensaje manteniendo oferta, horario y audiencia aprobados.',
   'Un mensaje más claro mejoraría la conversión post-clic frente al mensaje actual.',
   'Conversión post-clic', 'Mensaje actual; asignación aleatoria entre destinatarios con consentimiento confirmado.', 'Bajas, spam y reclamos'),
  'Validar frecuencia de contacto': ('Auditar solapamiento de envíos y diseñar un test de frecuencia con grupo de control.',
   'Una frecuencia menor mantendría pedidos reduciendo bajas frente a la frecuencia actual.',
   'Pedidos por destinatario elegible', 'Frecuencia actual con asignación aleatoria persistente.', 'Bajas, spam, entregabilidad e ingresos por destinatario')},
 'promotion': {
  'Validar términos y comunicación': ('Conciliar términos oficiales, sistema y mensajes; preparar una propuesta de comunicación para aprobación.',
   'Una comunicación de términos verificados reduciría consultas y reclamos frente al mensaje actual; no exponer términos incorrectos.',
   'Reclamos por redención', 'Revisión documental inicial; control válido solo tras verificar términos de ambas variantes.', 'Redenciones rechazadas, coste del cupón y reclamos'),
  'Diseñar monitoreo de consumo': ('Solicitar ritmo de redenciones y preparar umbrales de alerta; no cambiar presupuesto ni vigencia.',
   'Alertas tempranas permitirían detectar agotamiento antes de enviar nuevas comunicaciones.',
   'Tiempo de detección de riesgo de agotamiento', 'Comparación operativa con registro histórico validado; no atribuye causalidad.', 'Presupuesto consumido, rechazos y términos vigentes')}
}

def regional_rows(valid):
 """Contrato extra del simulador, sin agregar etiquetas normalizadas ambiguas."""
 df=valid.get('03_regions.csv');rows=[];notes=[]
 if df is None: return rows,['Fuente regional ausente o bloqueada.']
 aliases=df.region.map(norm)
 for idx,row in df.iterrows():
  name=str(row.region)
  if (aliases==norm(name)).sum()>1:
   notes.append(f'{name}: etiqueta regional ambigua; no se suma ni simula hasta confirmar grano.');continue
  try:
   sessions=float(row['actual_sessions']);observed=float(row['actual_cvr'])
   if not math.isfinite(sessions) or sessions<=0 or not math.isfinite(observed) or not 0<=observed<=1: raise ValueError()
   forecast=float(row.get('forecast_cvr',float('nan')))
   rows.append({'region':name,'sessions':sessions,'observed':observed,'forecast':forecast if math.isfinite(forecast) and 0<=forecast<=1 else None})
  except (KeyError,ValueError,TypeError): notes.append(f'{name}: faltan sesiones positivas o CVR válida; no se simula.')
 return rows,notes

def opportunities(valid,alerts,paid):
 result=[]
 def add(id,title,kind,fact,hypothesis,missing,source,rule,owner,population,cutoff):
  result.append(dict(id=id,title=title,kind=kind,fact=fact,hypothesis=hypothesis,missing=missing,source=source,rule=rule,owner=owner,population=population,cutoff=cutoff,status=STATUS))
 rows,_=regional_rows(valid)
 for r in rows:
  if r['forecast'] is not None and r['observed']<r['forecast']:
   name=r['region'];gap=(r['observed']-r['forecast'])*100
   add('G-REG-'+norm(name),f'Recuperación de conversión en {name}','conversion',
       f'{name}: CVR reportada {r["observed"]:.2%} vs forecast {r["forecast"]:.2%}; brecha {gap:+.2f} pp; {r["sessions"]:,.0f} sesiones observadas. Forecast es referencia, no contrafactual.',
       'Podría existir fricción de checkout, intención de tráfico o claridad de oferta; ninguna causa está confirmada.',
       'Confirmar corte y definición del forecast regional; abandono por paso, errores de pago, dispositivo y fuente de tráfico. No hay cruce región-canal.',
       ['03_regions.csv'],'G01: fila regional inequívoca y CVR reportada < forecast; comparación descriptiva pendiente de alinear cortes.',
       'Producto / E-commerce / Growth',f'Sesiones de {name}; elegibilidad, usuarios únicos y consentimiento por confirmar.',
       'Fuente regional sin fecha/corte explícito; no se asume el corte del archivo horario.')
 for a in alerts:
  kinds={'R05':'conversion','R07':'paid','R03':'promotion','R04':'promotion'}
  if a['ID'] not in kinds: continue
  fact=a['Hecho']
  if a['ID']=='R07' and paid is not None:
   g=paid.groupby('channel')[['spend_cop_mm','attributed_revenue_cop_mm']].sum()
   values=[f'{name}: ROAS {r.attributed_revenue_cop_mm/r.spend_cop_mm:.2f}, inversión {r.spend_cop_mm:g} MM COP' for name,r in g.iterrows() if r.spend_cop_mm>0]
   fact+=' '+ '; '.join(values)+'. Canales no son grupos de control comparables.'
  add('G-'+a['ID'],a['Senal'],kinds[a['ID']],fact,a['Hipotesis'],a['Dato_faltante'],a['Fuentes'],a['Regla'],a['Responsable'],
      'Población elegible por definir; agregados disponibles no identifican usuarios ni habilitan segmentación.',
      'Corte de cada fuente por confirmar; no mezclar períodos sin conciliación.')
 crm=valid.get('05_crm.csv')
 if crm is not None and {'communication','post_click_cvr'}.issubset(crm):
  rates=pd.to_numeric(crm.post_click_cvr,errors='coerce')
  if len(crm)>1 and rates.notna().all() and rates.between(0,1).all() and rates.nunique()>1:
   facts='; '.join(f'{row.communication}: {float(row.post_click_cvr):.2%}' for _,row in crm.iterrows())
   add('G-CRM','Optimización de conversión CRM','crm',facts+'. Comparación descriptiva: audiencias y ofertas diferentes; sin denominadores post-clic.',
       'Claridad o frecuencia podrían influir en la respuesta; diferencias actuales no prueban efecto del mensaje.',
       'Clics únicos y pedidos por envío, consentimiento, audiencias, solapamiento y cortes comparables.',
       ['05_crm.csv'],'G02: al menos dos comunicaciones con CVR post-clic válida y distinta; no ranking causal.',
       'CRM / Growth','Destinatarios elegibles por confirmar; no inferir audiencias desde el título del envío.', 'CRM sin fecha completa; corte por confirmar.')
 for op in result:
  if op['id']=='G-R05' and '01_business_hourly.csv' in valid:
   hours=valid['01_business_hourly.csv']
   op['cutoff']=f"Corte horario observado: {hours.timestamp.min()} → {hours.timestamp.max()}; no equivale al día completo."
  elif op['id']=='G-R07' and paid is not None and 'time_block' in paid:
   op['cutoff']='Bloques de medios: '+', '.join(sorted(paid.time_block.astype(str).unique()))+'. Fecha completa y comparabilidad entre canales por confirmar.'
 result.sort(key=lambda op: {"conversion":0,"paid":1,"crm":2,"promotion":3}[op["kind"]])
 return result

def simulate(sessions,observed,target,ticket):
 values=[sessions,observed,target,ticket]
 if not all(math.isfinite(float(x)) for x in values) or sessions<=0 or ticket<0 or not 0<=observed<=1 or not 0<=target<=1:
  raise ValueError('Sesiones positivas, tasas en [0,1] y ticket supuesto no negativo son obligatorios.')
 delta=target-observed;scenarios=[]
 for name,factor in [('Conservador',.5),('Base',1.),('Ambicioso',1.5)]:
  rate=min(1.,max(0.,observed+delta*factor));extra=sessions*(rate-observed)
  scenarios.append({'Escenario':name,'CVR supuesta':rate,'Pedidos adicionales hipotéticos':extra,'Valor bruto ilustrativo COP':round(extra*ticket,2)})
 return scenarios

def default_plan(op,strategy):
 plan,hypothesis,kpi,control,protections=STRATEGIES[op['kind']][strategy]
 return dict(title=op['title'],strategy=strategy,action=plan,hypothesis=hypothesis,kpi=kpi,control=control,protections=protections,
             owner=op['owner'],population=op['population'],duration='Por definir tras estimar muestra y ciclo de compra',
             success='Definir MDE, tamaño muestral e intervalo de confianza antes de iniciar; sin deterioro de métricas de protección.',
             next_steps='Validar datos faltantes y elegibilidad; acordar diseño y criterio de éxito; solicitar aprobaciones antes de implementar.')

def plan_signature(op,plan,sid):
 return hashlib.sha256(json.dumps([op,plan,sid],sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def action_artifacts(op,plan,sid):
 required=['title','strategy','action','hypothesis','kpi','control','protections','owner','population','duration','success','next_steps']
 if any(not str(plan.get(k,'')).strip() for k in required): raise ValueError('Completa todos los campos del plan antes de generar.')
 if plan['strategy'] not in STRATEGIES[op['kind']]: raise ValueError('Estrategia no pertinente para esta oportunidad.')
 def safe(v): return str(v).replace('<','&lt;').replace('>','&gt;')
 sections=[('# '+safe(plan['title'])),f'**Estado:** {STATUS}',
  '## Problema y oportunidad\n'+safe(op['fact']), '## Evidencia y fuente\n'+', '.join(op['source'])+'\n\n'+safe(op['cutoff']),
  '## Hipótesis verificable\n'+safe(plan['hypothesis']), '## Datos faltantes y restricciones\n'+safe(op['missing']),
  '## Estrategia seleccionada\n'+safe(plan['strategy']), '## Acción concreta\n'+safe(plan['action']),
  '## Plan de experimentación\n'+f'**Población:** {safe(plan["population"])}\n\n**Control:** {safe(plan["control"])}\n\n**Duración:** {safe(plan["duration"])}',
  '## Medición\n'+f'**KPI principal:** {safe(plan["kpi"])}\n\n**Condición de éxito:** {safe(plan["success"])}\n\n**Protecciones:** {safe(plan["protections"])}',
  '## Responsable y aprobaciones\n'+safe(plan['owner'])+'\n\nAprobaciones pendientes: responsable del área y Marketing Lead; Finanzas si hay cambios de presupuesto de cupones.',
  '## Próximos pasos\n'+safe(plan['next_steps']), '## Guardrails\n'+GUARDRAILS,
  '## Metadatos técnicos\n'+f'Regla: {op["rule"]}\n\nPaquete SHA256: {sid}\n\nMotor determinístico; sin IA generativa en ejecución.']
 row={**plan,'Oportunidad_ID':op['id'],'Hecho':op['fact'],'Fuentes':', '.join(op['source']),'Datos_faltantes':op['missing'],'Corte':op['cutoff'],
      'Estado':STATUS,'Aprobaciones_requeridas':'Responsable del área y Marketing Lead; Finanzas si aplica','Guardrails':GUARDRAILS,
      'Aprobado_por':'','Fecha_aprobacion':'','Resultado_observado':'','Paquete_SHA256':sid,'Regla':op['rule']}
 # Evitar fórmulas al abrir contenido editable en una hoja de cálculo.
 row={k:("'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v) for k,v in row.items()}
 return '\n\n'.join(sections),pd.DataFrame([row]).to_csv(index=False).encode('utf-8-sig')
