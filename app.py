import zipfile
from html import escape
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from engine import read_sources, analyze, fingerprint, artifacts
from growth_engine import opportunities, STRATEGIES
from growth_views import render_action, render_growth, open_action

st.set_page_config(page_title='MercaYa · AI Studio',page_icon='✳',layout='wide')
st.markdown('<style>'+Path(__file__).with_name('styles.css').read_text()+'</style>',unsafe_allow_html=True)

def html(value): st.markdown(value,unsafe_allow_html=True)
def e(value): return escape(str(value))
def heading(kicker,title,subtitle=''):
 html(f'<div class="section-head"><div><div class="eyebrow">{e(kicker)}</div><h2>{e(title)}</h2><p>{e(subtitle)}</p></div></div>')
def badge(a):
 css={'Crítica':'critical','Alta':'high','Media':'medium'}.get(a['Prioridad'],'')
 return f'<span class="priority {css}">● {e(a["Prioridad"])} · {e(a["ID"])}</span>'
def navigate(target): st.session_state['workspace_nav']=target
def select_signal(i):
 st.session_state['selected_case']=i
 navigate('◎ Decision Studio')

def chart(fig):
 fig.update_layout(template='plotly_white',title_font_color='#151515',height=285,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(255,255,255,.6)',font=dict(color='#475467',family='Arial'),margin=dict(l=15,r=15,t=45,b=15),legend=dict(orientation='h',y=-.2),colorway=['#3483FA','#dfc600','#16A34A'])
 fig.update_xaxes(showgrid=False,color='#475467',title_font_color='#475467',tickfont_color='#475467');fig.update_yaxes(gridcolor='#e9edf1',color='#475467',title_font_color='#475467',tickfont_color='#475467')
 st.plotly_chart(fig,width='stretch',theme=None)

html('<div class="topbar"><div class="brand"><span class="brand-icon">▥</span>MercaYa <em>/ AI Studio</em></div><div class="topmeta"><span class="pill">Marketing operations</span><span class="pill">10.10 · MercaYa</span><span class="pill live">● Entorno local</span></div></div>')
if st.session_state.get('workspace_nav')=='⤴ Automation Studio': st.session_state['workspace_nav']='⤴ Action Hub'
mission,decisions,growth,automation,connect=st.tabs(['◉ Mission Control','◎ Decision Studio','↗ Growth Lab','⤴ Action Hub','⊞ Data Connect'],key='workspace_nav',on_change='rerun')
with connect:
 heading('Data connect','Todo comienza con buenas fuentes.','Carga un nuevo paquete para recalcular decisiones y entregables.')
 upload=st.file_uploader('Importar fuentes · ZIP',type=['zip'],help='CSV UTF-8 con los nombres y columnas del README. Se admiten subcarpetas; máximo 25 MB descomprimidos.')
 st.caption('Sin archivo se analiza el ejemplo local. El paquete no se envía a servicios externos.')
try:
 if upload:
  with zipfile.ZipFile(upload) as z:
   if sum(x.file_size for x in z.infolist())>25_000_000: raise ValueError('ZIP supera 25 MB descomprimidos')
   entries=[x.filename.split('/')[-1] for x in z.infolist() if not x.is_dir()]
   if len(entries)!=len(set(entries)): raise ValueError('Nombres de archivo ambiguos en el ZIP')
  upload.seek(0)
 sources,brief,names=read_sources(upload)
 valid,paid,alerts,checks=analyze(sources,brief)
except Exception as exc:
 st.error(f'No se pudo procesar el paquete: {exc}. Corrige el ZIP en Data Connect.');st.stop()
sid=fingerprint(sources,brief)
if st.session_state.get('source_id')!=sid:
 for key in list(st.session_state):
  if key in {'deliverable','selected_case','priority_filter','category_filter','sim_region'} or key.startswith(('action_','sim_target_','sim_ticket_')): st.session_state.pop(key,None)
 st.session_state['source_id']=sid
ops=opportunities(valid,alerts,paid)
valid_count=len(valid);blocked=len(checks)-valid_count
b=valid.get('01_business_hourly.csv')
period=f'{b.timestamp.min()} → {b.timestamp.max()}' if b is not None else 'Corte temporal no disponible'
with connect:
 st.success(f'{len(sources)} fuentes CSV detectadas · {valid_count} válidas · {blocked} bloqueadas')
 st.dataframe(pd.DataFrame(checks),hide_index=True,width='stretch')
 st.caption('Las fuentes bloqueadas se excluyen de reglas y gráficos. Un esquema válido no prueba exactitud ni conciliación. Duplicados exactos de medios se excluyen solo de agregados.')
 if not brief: st.warning('Documento de campaña ausente. No se puede confirmar la ventana comunicada ni los términos oficiales.')
 with st.expander('Inventario y trazabilidad'):
  st.code('SHA256: '+sid)
  st.dataframe(pd.DataFrame([{'Fuente':name,'Registros':len(df),'Columnas':len(df.columns)} for name,df in sources.items()]),hide_index=True,width='stretch')
  st.write('Documento de campaña DOCX: '+('detectado' if brief else 'no disponible'))
 st.markdown('Consulta el contrato de nombres y columnas en **README.md**. Se ignoran archivos adicionales; el XLSX no se interpreta automáticamente.')
with mission:
 left,right=st.columns([1.5,1],gap='large')
 with left:
  html('<div class="hero"><div class="eyebrow">AI Marketing Command Center</div><h1>MercaYa AI Studio</h1><div class="hero-sub">Análisis de campaña, decisiones priorizadas y acciones para aprobación.</div></div>')
  html(f'<span class="pill">Campaña 10.10</span> <span class="pill live">● Análisis calculado</span> <span class="pill">{e(len(alerts))} señales</span>')
  if st.button('Analizar campaña',type='primary',key='analyze_campaign',on_click=navigate,args=('◎ Decision Studio',)):
   st.session_state.pop('deliverable',None)
   st.success('Análisis recalculado con las fuentes actuales. Revisa Decision Studio para investigar y generar el siguiente paso.')
  st.caption('Datos observados · '+period)
 with right:
  st.image(str(Path(__file__).parent/'assets'/'mission-commerce.svg'),width='stretch')
 with st.expander('Resumen ejecutivo de la campaña'):
  first=ops[0] if ops else None
  html('<div class="glass summary"><div class="eyebrow">Lectura ejecutiva · reglas reproducibles</div><h3>Esto merece tu atención.</h3>'+f'<p><strong>Qué está pasando</strong><br>{len(alerts)} señales en {valid_count} fuentes válidas; {blocked} fuentes bloqueadas.</p>'+f'<p><strong>Prioridad de revisión</strong><br>{e(first["title"]) if first else "Sin señales con las reglas disponibles."}</p>'+f'<p><strong>Siguiente acción</strong><br>{e(next(iter(STRATEGIES[first["kind"]]))) if first else "Revisar cobertura y validaciones en Data Connect."}</p></div>')
 heading('Tu ruta de trabajo','Una señal. Una decisión. Un siguiente paso.','Cada módulo conecta una etapa real del análisis.')
 for col,(label,target) in zip(st.columns(5),[('01 · Fuentes','Data Connect'),('02 · Validación','Data Connect'),('03 · Inteligencia','Decision Studio'),('04 · Decisión','Decision Studio'),('05 · Acción','Action Hub')]):
  with col:
   html(f'<div class="stat"><small>{e(label)}</small><b>{valid_count if "01" in label or "02" in label else len(alerts)}</b><span>{e(target)}</span></div>')
   st.button('Abrir →',key='step_'+label,on_click=navigate,args=(('⊞ Data Connect' if target=='Data Connect' else '◎ Decision Studio' if target=='Decision Studio' else '⤴ Action Hub'),),width='stretch')
 heading('Oportunidades comerciales','Acciones para preparar.','Evidencia observada y estrategias por validar; sin promesas de resultados.')
 for col,op in zip(st.columns(3),ops[:3]):
  with col:
   html(f'<div class="glass signal"><span class="priority medium">Oportunidad · {e(op["id"])}</span><h3>{e(op["title"])}</h3><p class="fact">{e(op["fact"])}</p></div>')
   st.button('Preparar estrategia ↗',key=f'home_{op["id"]}',width='stretch',on_click=open_action,args=(op['id'],))
 if not ops: st.info('Sin oportunidades comerciales sustentadas. Revisa cobertura y calidad en Data Connect.')
 html('<div class="note">Inteligencia analítica determinística · Sin modelo generativo en ejecución · Datos ficticios del assessment</div>')
with decisions:
 heading('AI decision studio · incidencias y guardrails','Evidencia antes de aprobar.','Prioridad fija: Crítica → Alta → Media; empates por orden de regla. No representa impacto económico estimado.')
 filtered=list(enumerate(alerts))
 for start in range(0,len(filtered),3):
  for col,(i,a) in zip(st.columns(3),filtered[start:start+3]):
   with col:
    with st.container(border=True):
     html(badge(a)+f'<h3>{e(a["Senal"])}</h3><p class="analyst-text">{e(a["Hecho"])}</p><div class="note">{e(a["Accion"])}</div>')
     st.button('Investigar señal',key=f'case_{a["ID"]}',width='stretch',on_click=select_signal,args=(i,))
 if not filtered: st.info('No hay incidencias detectadas con las fuentes válidas. Revisa la cobertura en Data Connect.')
 if alerts:
  selected=st.selectbox('Seleccionar incidencia',range(len(alerts)),format_func=lambda i:f'{alerts[i]["ID"]} · {alerts[i]["Senal"]}',key='selected_case')
  a=alerts[selected]
  heading('AI analyst · expediente verificable',a['Senal'])
  html(badge(a))
  for cols in [[('HECHO','Hecho'),('HIPÓTESIS · sin causalidad demostrada','Hipotesis')],[('DATOS FALTANTES','Dato_faltante'),('RECOMENDACIÓN','Accion')]]:
   for col,(label,key) in zip(st.columns(2),cols):
    with col: html(f'<div class="glass"><div class="analyst-label">{e(label)}</div><div class="analyst-text">{e(a[key])}</div></div>')
  st.markdown(f'**Responsable propuesto:** {a["Responsable"]}  \n**Aprobación:** {a["Aprobacion"]}')
  st.caption('Evidencia: '+', '.join(a['Fuentes']))
  with st.expander('Evidencia original · regla · trazabilidad'):
   st.write(a['Regla']);st.write(a['Justificacion']);st.code('SHA256: '+sid)
   for name in a['Fuentes']:
    st.markdown('**'+name+'**')
    if name in sources: st.dataframe(sources[name],hide_index=True,width='stretch')
    elif name.endswith('.docx'): st.text(brief or 'Fuente ausente')
  st.button('Preparar siguiente paso →',key='next_step',type='primary',on_click=open_action,args=(('G-'+a['ID'] if any(o['id']=='G-'+a['ID'] for o in ops) else (ops[0]['id'] if ops else '')),))
with automation:
 render_action(ops,sid)
with connect:
 with st.expander('Tracker de incidencias técnicas'):
  st.caption('Formato anterior conservado. Usa MercaYa Action Hub para preparar una acción comercial.')
  if st.button('Generar exportación técnica',key='legacy_generate'):
   st.session_state['deliverable']=artifacts(alerts,sid)[1]
  if isinstance(st.session_state.get('deliverable'),bytes):
   csv=st.session_state['deliverable']
   st.download_button('Tracker técnico CSV',csv,'tracker_acciones.csv','text/csv')
with growth:
 render_growth(ops,valid)
 heading('Marketing growth lab','Métricas que respaldan decisiones.','Soporte analítico · ingresos atribuidos no equivalen a NMV incremental.')
 if b is not None:
  sessions=b.actual_sessions.sum();orders=b.orders.sum()
  for col,(label,value) in zip(st.columns(3),[('Sesiones observadas',f'{sessions:,.0f}'),('Órdenes',f'{orders:,.0f}'),('CVR ponderada',f'{orders/sessions:.2%}' if sessions else 'No calculable')]): col.metric(label,value)
  st.caption('Solo se muestran etapas presentes: sesiones → órdenes. No hay datos de carrito ni checkout. El corte parcial no se compara con una meta de día completo.')
  c1,c2=st.columns(2)
  with c1: chart(px.line(b.sort_values('timestamp'),x='timestamp',y=['actual_nmv_cop_mm','forecast_nmv_cop_mm'],title='NMV observado y forecast · MM COP',color_discrete_sequence=['#3483FA','#dfc600']))
  with c2: chart(px.line(b.sort_values('timestamp'),x='timestamp',y=['actual_cvr','forecast_cvr'],title='Conversión por hora',color_discrete_sequence=['#3483FA','#dfc600']))
 if paid is not None:
  g=paid.groupby('channel',as_index=False)[['spend_cop_mm','attributed_revenue_cop_mm']].sum();g['ROAS']=g.attributed_revenue_cop_mm/g.spend_cop_mm.replace(0,float('nan'))
  c1,c2=st.columns(2)
  with c1: chart(px.bar(g,x='channel',y='spend_cop_mm',title='Inversión por canal · MM COP',color_discrete_sequence=['#3483FA']))
  with c2: chart(px.bar(g,x='channel',y='ROAS',title='ROAS atribuido por canal',color_discrete_sequence=['#dfc600']))
  st.caption('ROAS = ingreso atribuido / inversión. Inversión cero produce ROAS no calculable. Diferencias no autorizan mover presupuesto sin verificar incrementalidad.')
 for label,name in [('Regiones','03_regions.csv'),('Promociones','04_coupons.csv'),('CRM','05_crm.csv')]:
  with st.expander(label+' · fuente validada'):
   if name in valid: st.dataframe(valid[name],hide_index=True,width='stretch')
   else: st.info('Fuente ausente o bloqueada. Consulta Data Connect.')
 with st.expander('Guardrails · incidencias de calidad y promociones'):
  for issue in alerts:
   if issue['Categoria'] in {'Calidad','Promociones'}:
    st.markdown(f"**{issue['Senal']}**  \n{issue['Hecho']}  \n{issue['Accion']}")
html('<div class="footer">MercaYa AI Studio · Inteligencia que impulsa decisiones. &nbsp; Reglas y plantillas determinísticas; construcción asistida por IA. Sin LLM conectado, integraciones comerciales ni causalidad demostrada.</div>')
