"""UI de planes editables y simulaciones; sin servicios ni ejecución comercial."""
import streamlit as st
import pandas as pd
from pathlib import Path
from html import escape
from growth_engine import STRATEGIES, STATUS, default_plan, action_artifacts, plan_signature, regional_rows, simulate

def card(label,text):
 st.markdown(f'<div class="glass"><div class="analyst-label">{escape(label)}</div><div class="analyst-text">{escape(str(text))}</div></div>',unsafe_allow_html=True)

def open_action(op_id):
 if st.session_state.get('action_active_op')!=op_id:
  st.session_state['action_step']=1
 st.session_state['action_active_op']=op_id
 st.session_state['action_op']=op_id
 st.session_state['workspace_nav']='⤴ Action Hub'

def hub_step(step): st.session_state['action_step']=step

def choose_op():
 st.session_state['action_active_op']=st.session_state['action_op']
 st.session_state['action_step']=1

def choose_strategy(scope,strategy):
 st.session_state.setdefault('action_choices',{})[scope]=strategy

def save_field(plan_key,field,widget_key):
 st.session_state['action_plans'][plan_key][field]=st.session_state[widget_key]

def prepare_action(op,plan,sid):
 """Materializar archivos de la selección actual; nunca ejecutar una acción comercial."""
 try:
  _,csv=action_artifacts(op,plan,sid)
  st.session_state['action_generated']={
   'signature':plan_signature(op,plan,sid),
   'csv':csv,'op':dict(op),'plan':dict(plan),'status':STATUS}
  st.session_state.pop('action_generation_error',None)
 except Exception as exc:
  st.session_state.pop('action_generated',None)
  st.session_state['action_generation_error']='No se pudo preparar el plan: '+str(exc)

def render_action(ops,sid):
 title,illustration=st.columns([3,1])
 with title:
  st.markdown('## MercaYa Action Hub')
  st.caption('De la evidencia a una acción preparada para Marketing. Motor determinístico; aprobación humana.')
 with illustration:
  st.image(str(Path(__file__).parent/'assets'/'action-automation.svg'),width=200)
 if not ops:
  st.info('No hay oportunidades comerciales sustentadas. Carga fuentes válidas en Data Connect.');return
 by_id={op['id']:op for op in ops}
 if st.session_state.get('action_active_op') not in by_id:
  st.session_state['action_active_op']=ops[0]['id']
  st.session_state['action_step']=1
 step=st.session_state.setdefault('action_step',1)
 labels=['Elegir estrategia','Diseñar experimento','Preparar acción']
 st.progress(step/3,text=f'Paso {step} de 3 · {labels[step-1]}')
 st.markdown('<div class="hub-steps">'+''.join(f'<span class="{("current" if i==step else "done" if i<step else "")}" '+('aria-current="step"' if i==step else '')+f'><b>{i}</b> {label}</span>' for i,label in enumerate(labels,1))+'</div>',unsafe_allow_html=True)
 if step==1:
  if st.session_state.get('action_op') not in by_id: st.session_state['action_op']=st.session_state['action_active_op']
  st.selectbox('Oportunidad detectada',list(by_id),format_func=lambda k:by_id[k]['title'],key='action_op',on_change=choose_op)
 op=by_id[st.session_state['action_active_op']]
 scope=sid+'|'+op['id']
 choices=st.session_state.setdefault('action_choices',{})
 strategy=choices.get(scope,next(iter(STRATEGIES[op['kind']])))
 if strategy not in STRATEGIES[op['kind']]: strategy=next(iter(STRATEGIES[op['kind']]))
 choices[scope]=strategy
 if step==1:
  priority='Revisión prioritaria · términos / presupuesto' if op['kind']=='promotion' else 'Oportunidad comercial · por validar'
  st.markdown(f'<div class="hub-context"><span class="priority high">{escape(priority)}</span><h3>{escape(op["title"])}</h3><p>{escape(op["fact"])}</p><small>Fuente: {escape(", ".join(op["source"]))}</small></div>',unsafe_allow_html=True)
  st.caption('Prioridad de revisión, no impacto estimado. '+op['cutoff'])
  st.markdown('### ¿Qué quieres probar?')
  for i,(col,name) in enumerate(zip(st.columns(len(STRATEGIES[op['kind']])),STRATEGIES[op['kind']])):
   proposed=default_plan(op,name);chosen=strategy==name
   with col:
    with st.container(border=True):
     # Esquema de intervención/control, sin métricas ni datos inventados.
     st.markdown(f'<div class="strategy-art" aria-hidden="true"><span>◎</span><i>→</i><span>{["▤","↗","◇"][i]}</span><i>→</i><span>✓</span></div><span class="priority {"high" if chosen else "medium"}">{"Seleccionada" if chosen else "Alternativa "+str(i+1)}</span><h3>{escape(name)}</h3><p class="hub-card-copy">{escape(proposed["action"])}</p><div class="note">Medir: {escape(proposed["kpi"])}</div>',unsafe_allow_html=True)
     st.button('✓ '+name if chosen else 'Elegir '+name,key='strategy_'+str(i),type='primary' if chosen else 'secondary',on_click=choose_strategy,args=(scope,name),width='stretch')
  with st.expander('Qué falta validar antes de implementar'):
   st.write(op['hypothesis']);st.write(op['missing'])
  st.button('Continuar →',key='hub_continue_1',type='primary',on_click=hub_step,args=(2,))
  return
 plan_key=scope+'|'+strategy
 plans=st.session_state.setdefault('action_plans',{})
 if plan_key not in plans: plans[plan_key]=default_plan(op,strategy)
 plan=plans[plan_key]
 if step==2:
  st.markdown('### '+strategy)
  st.caption('Propuesta precargada · edita lo esencial. El experimento todavía no se ha ejecutado.')
  with st.container(border=True):
   c1,c2=st.columns(2)
   essential=[('hypothesis','Hipótesis verificable'),('kpi','KPI principal'),('control','Grupo de control / diseño'),('protections','Métricas de protección'),('owner','Responsable propuesto'),('success','Condición de éxito')]
   for i,(field,label) in enumerate(essential):
    with (c1 if i%2==0 else c2):
     widget='action_edit_'+field
     st.text_input(label,value=plan[field],key=widget,on_change=save_field,args=(plan_key,field,widget))
  st.caption('Observado en la fuente: '+op['fact'])
  st.info('Por validar: causalidad, elegibilidad, tamaño de muestra, duración y criterio de éxito. No se estiman automáticamente.')
  with st.expander('Configuración avanzada · acción y alcance'):
   for field,label in [('title','Título ejecutivo'),('action','Acción concreta'),('population','Población objetivo / elegibilidad'),('duration','Duración y muestra'),('next_steps','Próximos pasos')]:
    widget='action_edit_'+field
    st.text_input(label,value=plan[field],key=widget,on_change=save_field,args=(plan_key,field,widget))
   st.caption(op['missing'])
  valid=all(str(v).strip() for v in plan.values())
  if not valid: st.warning('Completa los campos vacíos antes de continuar.')
  c1,c2=st.columns(2)
  c1.button('← Anterior',key='hub_back_2',on_click=hub_step,args=(1,))
  c2.button('Continuar →',key='hub_continue_2',type='primary',on_click=hub_step,args=(3,),disabled=not valid)
  return
 signature=plan_signature(op,plan,sid)
 st.session_state['action_current_draft']={'op':op['id'],'plan':dict(plan),'signature':signature,'source':sid}
 st.markdown('### Preparar acción para Marketing')
 st.caption(strategy+' · '+plan['owner'])
 st.button('Preparar acción para Marketing',type='primary',key='generate',on_click=prepare_action,args=(dict(op),dict(plan),sid))
 if st.session_state.get('action_generation_error'):
  st.error(st.session_state['action_generation_error'])
 generated=st.session_state.get('action_generated')
 if generated and generated['signature']==signature and 'csv' in generated:
  st.success('Plan generado correctamente')
  st.caption(generated['status']+' · No se han ejecutado acciones externas.')
  saved=generated['plan']
  with st.container(border=True):
   st.markdown('### Acción preparada')
   st.markdown('**'+escape(generated['op']['title'])+'**')
   st.write(saved['action'])
   c1,c2,c3=st.columns(3)
   with c1: card('ESTRATEGIA',saved['strategy'])
   with c2: card('RESPONSABLE PROPUESTO',saved['owner'])
   with c3: card('KPI PARA VALIDAR',saved['kpi'])
   st.caption('Siguiente paso: '+saved['next_steps'])
  st.download_button('Descargar tracker CSV',generated['csv'],'tracker_growth.csv','text/csv',key='download_tracker',width='stretch',on_click='ignore')
  st.caption(f'Tracker: {len(generated["csv"]):,} bytes · 1 acción preparada')
 elif generated: st.info('El plan cambió. Prepara de nuevo la acción para generar los archivos de esta selección.')
 with st.expander('Condiciones para implementar'):
  from growth_engine import GUARDRAILS
  st.write(GUARDRAILS);st.write(op['missing']);st.write('Población: '+plan['population']);st.write('Duración y muestra: '+plan['duration'])
 st.button('← Anterior',key='hub_back_3',on_click=hub_step,args=(2,))

def render_growth(ops,valid):
 title,illustration=st.columns([3,1])
 with title:
  st.markdown('## Growth Decision Lab')
  st.caption('Oportunidades comerciales primero. Incidencias de calidad y términos promocionales siguen siendo bloqueos para la aprobación.')
 with illustration:
  st.image(str(Path(__file__).parent/'assets'/'growth-commerce.svg'),width=220)
 for start in range(0,len(ops),2):
  for col,op in zip(st.columns(2),ops[start:start+2]):
   with col:
    with st.container(border=True):
     st.markdown('### '+op['title']);st.write(op['fact'])
     st.caption('Evidencia: '+', '.join(op['source']))
     first=next(iter(STRATEGIES[op['kind']]))
     st.markdown(f'**Estrategia propuesta:** {first}  \n**KPI:** {default_plan(op,first)["kpi"]}')
     with st.expander('Hipótesis y requisitos antes de actuar'):
      st.write(op['hypothesis']);st.write(op['missing']);st.caption(op['cutoff'])
     st.button('Diseñar acción →',key='growth_'+op['id'],on_click=open_action,args=(op['id'],),width='stretch')
 st.markdown('### Simulador what-if · región')
 rows,notes=regional_rows(valid)
 if notes:
  with st.expander('Calidad regional · exclusiones y comparabilidad',expanded=True):
   for note in notes: st.warning(note)
 st.caption('Medellín/Medellin no se fusionan. No se confirma igualdad de períodos entre regiones ni con las horas de negocio; no se construye ranking regional. Forecast es una referencia descriptiva, no un contrafactual.')
 if not rows:
  st.info('Sin regiones inequívocas con sesiones y CVR válidas para simular.');return
 with st.expander('Referencias regionales · descriptivas, sin ranking causal'):
  st.dataframe(pd.DataFrame([{'Región':r['region'],'Sesiones':r['sessions'],'CVR reportada':f"{r['observed']:.2%}",'Forecast de referencia':f"{r['forecast']:.2%}" if r['forecast'] is not None else 'No disponible'} for r in rows]),hide_index=True,width='stretch')
  st.caption('Sin corte regional explícito: confirmar períodos, definición de forecast y mix antes de comparar desempeño. No se incluyen registros ambiguos Medellín/Medellin.')
 lookup={r['region']:r for r in rows}
 region=st.selectbox('Región a simular',list(lookup),key='sim_region');r=lookup[region]
 st.markdown(f'**Observado:** {r["sessions"]:,.0f} sesiones · CVR reportada {r["observed"]:.2%}')
 # No hay pedidos regionales / AOV comparable: no inferir ticket desde NMV no conciliado.
 st.caption('No hay ticket promedio regional comparable ni pedidos regionales observados. Introduce un ticket supuesto; no se deriva de NMV sin conciliar.')
 target=st.slider('Conversión objetivo supuesta (%)',0.,100.,min(100.,round(r['observed']*100+.5,2)),step=.05,key='sim_target_'+region)/100
 ticket=st.number_input('Ticket promedio supuesto (COP)',min_value=0.,value=0.,step=1000.,key='sim_ticket_'+region)
 if ticket==0: st.info('Introduce un ticket supuesto mayor que cero para ilustrar valor bruto. Con cero solo se interpretan pedidos hipotéticos.')
 scenarios=simulate(r['sessions'],r['observed'],target,ticket)
 for col,row in zip(st.columns(3),scenarios):
  with col:
   with st.container(border=True):
    st.markdown('**'+row['Escenario']+'**')
    st.metric('Pedidos adicionales hipotéticos',f'{row["Pedidos adicionales hipotéticos"]:+,.1f}')
    st.caption(f'CVR supuesta: {row["CVR supuesta"]:.2%}')
    if ticket>0: st.write(f'Valor bruto ilustrativo: COP {row["Valor bruto ilustrativo COP"]:+,.0f}')
 st.caption('Supuestos: mismas sesiones y demás condiciones constantes; escenarios = 0,5× / 1× / 1,5× del cambio propuesto, limitados a tasas entre 0 y 100%. Pedidos = sesiones × (CVR supuesta − CVR observada). Valor = pedidos × ticket supuesto; no es NMV, beneficio ni predicción. Objetivos menores producen diferencias negativas.')
 st.download_button('Descargar escenarios y supuestos CSV',pd.DataFrame([{**s,'Region':region,'Sesiones':r['sessions'],'CVR_observada':r['observed'],'Ticket_supuesto_COP':ticket,'Tipo':'Simulación; no predicción'} for s in scenarios]).to_csv(index=False).encode('utf-8-sig'),'escenarios_what_if.csv','text/csv')
