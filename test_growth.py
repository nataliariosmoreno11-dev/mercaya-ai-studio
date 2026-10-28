import io
import unittest
import zipfile
import pandas as pd
from engine import read_sources,analyze,fingerprint
from growth_engine import opportunities,regional_rows,simulate,default_plan,action_artifacts,plan_signature,STRATEGIES

class GrowthTests(unittest.TestCase):
 def setUp(self):
  self.data,self.brief,_=read_sources(None)
  self.valid,self.paid,self.alerts,_=analyze(self.data,self.brief)
  self.ops=opportunities(self.valid,self.alerts,self.paid)
 def test_bogota_and_ambiguous_regions(self):
  op=self.ops[0]
  self.assertEqual(op['title'],'Recuperación de conversión en Bogotá')
  self.assertIn('-0.70 pp',op['fact'])
  self.assertIn('no contrafactual',op['fact'])
  rows,notes=regional_rows(self.valid)
  self.assertNotIn('medellin',[r['region'].lower() for r in rows])
  self.assertNotIn('Medellín',[r['region'] for r in rows])
  self.assertEqual(len(notes),2)
  self.assertFalse(any('medellin' in op['id'] for op in self.ops))
 def test_simulator_formula(self):
  rows=simulate(185000,.029,.036,80000)
  self.assertAlmostEqual(rows[1]['Pedidos adicionales hipotéticos'],1295)
  self.assertAlmostEqual(rows[1]['Valor bruto ilustrativo COP'],103600000)
  self.assertAlmostEqual(rows[0]['Pedidos adicionales hipotéticos'],647.5)
  self.assertAlmostEqual(rows[2]['Pedidos adicionales hipotéticos'],1942.5)
 def test_simulator_boundaries(self):
  self.assertEqual(simulate(100,.1,.1,0)[1]['Pedidos adicionales hipotéticos'],0)
  self.assertLess(simulate(100,.2,.1,10)[1]['Pedidos adicionales hipotéticos'],0)
  self.assertEqual(simulate(100,.8,1,10)[2]['CVR supuesta'],1)
  for values in [(0,.1,.2,10),(10,-.1,.2,10),(10,.1,1.1,10),(10,.1,.2,-1),(10,.1,float('nan'),10)]:
   with self.assertRaises(ValueError): simulate(*values)
 def test_missing_optional_regional_columns(self):
  self.valid['03_regions.csv']=self.valid['03_regions.csv'][['region','actual_nmv_cop_mm']]
  rows,notes=regional_rows(self.valid)
  self.assertEqual(rows,[])
  self.assertTrue(notes)
  opportunities(self.valid,self.alerts,self.paid) # no crash with minimal contract
 def test_different_strategies_create_different_experiments(self):
  op=self.ops[0];a=default_plan(op,'Optimizar checkout');b=default_plan(op,'Validar calidad del tráfico')
  for field in ['action','hypothesis','kpi','control','protections']:
   self.assertNotEqual(a[field],b[field])
  self.assertNotEqual(set(STRATEGIES['paid']),set(STRATEGIES['crm']))
 def test_professional_exports_editable_and_pending(self):
  op=self.ops[0];plan=default_plan(op,'Optimizar checkout');plan['owner']='Equipo Bogotá';plan['success']='CVR mayor al control con IC 95% y sin deterioro de protecciones; muestra por validar'
  md,csv=action_artifacts(op,plan,'sample')
  self.assertTrue(md.startswith('# Recuperación'))
  self.assertIn('Equipo Bogotá',md)
  self.assertNotIn('SHA256',md.split('## Metadatos técnicos')[0])
  row=pd.read_csv(io.BytesIO(csv)).iloc[0]
  self.assertEqual(row.owner,'Equipo Bogotá')
  self.assertTrue(pd.isna(row.Aprobado_por))
  self.assertEqual(row.Estado,'Pendiente de aprobación humana')
  self.assertIn('20%',md);self.assertIn('Finanzas',md)
  self.assertEqual((md,csv),action_artifacts(op,plan,'sample'))
  before=plan_signature(op,plan,'sample');plan['owner']='Otro responsable'
  self.assertNotEqual(before,plan_signature(op,plan,'sample'))
 def test_required_fields_and_csv_safety(self):
  op=self.ops[0];plan=default_plan(op,'Optimizar checkout');plan['owner']=''
  with self.assertRaises(ValueError): action_artifacts(op,plan,'s')
  plan['owner']='=1+1'
  _,csv=action_artifacts(op,plan,'s')
  self.assertEqual(pd.read_csv(io.BytesIO(csv)).iloc[0].owner,"'=1+1")
 def test_new_zip_recalculates_opportunity(self):
  buf=io.BytesIO();self.data['03_regions.csv'].loc[0,'actual_cvr']=.04
  with zipfile.ZipFile(buf,'w') as z:
   for name,df in self.data.items(): z.writestr('sources/'+name,df.to_csv(index=False))
  buf.seek(0);data,brief,_=read_sources(buf);valid,paid,alerts,_=analyze(data,brief)
  self.assertFalse(any(o['id']=='G-REG-bogota' for o in opportunities(valid,alerts,paid)))
  self.assertEqual(len(opportunities({},[],None)),0)

class ActionUITests(unittest.TestCase):
 def app(self):
  from streamlit.testing.v1 import AppTest
  return AppTest.from_file('app.py').run(timeout=30)
 def prepare(self,at):
  at.button(key='hub_continue_1').click().run()
  at.button(key='hub_continue_2').click().run()
  at.button(key='generate').click().run()
  self.assertEqual(len(at.exception),0)
  return at.session_state['action_generated']
 def test_edits_strategy_and_stale_downloads(self):
  at=self.app()
  at.button(key='strategy_1').click().run()
  at.button(key='hub_continue_1').click().run()
  at.text_input(key='action_edit_owner').set_value('Growth Bogotá').run()
  at.button(key='hub_continue_2').click().run()
  at.button(key='generate').click().run()
  self.assertIn('Growth Bogotá',at.session_state['action_generated']['csv'].decode('utf-8-sig'))
  self.assertIn('landing',at.session_state['action_generated']['csv'].decode('utf-8-sig'))
  at.button(key='hub_back_3').click().run()
  at.text_input(key='action_edit_owner').set_value('Nuevo responsable').run()
  at.button(key='hub_continue_2').click().run()
  self.assertFalse(any('Descargar tracker CSV' in d.label for d in at.get('download_button')))
  at.button(key='generate').click().run()
  self.assertIn('Nuevo responsable',at.session_state['action_generated']['csv'].decode('utf-8-sig'))
  self.assertEqual(len(at.exception),0)

 def test_single_step_navigation_and_persistence(self):
  at=self.app()
  self.assertEqual(len(at.text_input),0)
  self.assertEqual(len(at.text_area),0)
  self.assertFalse(any(b.key=='generate' for b in at.button))
  at.button(key='strategy_1').click().run()
  at.button(key='hub_continue_1').click().run()
  self.assertFalse(any(b.key=='strategy_1' for b in at.button))
  at.text_input(key='action_edit_owner').set_value('Dueña del experimento').run()
  at.button(key='hub_continue_2').click().run()
  self.assertEqual(len(at.text_input),0)
  self.assertEqual(len(at.text_area),0)
  self.assertTrue(any(b.label=='Preparar acción para Marketing' for b in at.button))
  self.assertFalse(any('SHA256' in m.value for m in at.markdown if 'Action Hub' in m.value))
  at.button(key='hub_back_3').click().run()
  self.assertEqual(at.text_input(key='action_edit_owner').value,'Dueña del experimento')
  at.button(key='hub_back_2').click().run()
  self.assertTrue(at.button(key='strategy_1').label.startswith('✓'))
  at.button(key='hub_continue_1').click().run()
  self.assertEqual(at.text_input(key='action_edit_owner').value,'Dueña del experimento')
  self.assertEqual(len(at.exception),0)

 def test_strategy_changes_real_exports_and_preserves_separate_drafts(self):
  at=self.app();first=self.prepare(at)
  at.button(key='hub_back_3').click().run()
  at.text_input(key='action_edit_owner').set_value('Checkout Lead').run()
  at.button(key='hub_back_2').click().run()
  at.button(key='strategy_1').click().run()
  second=self.prepare(at)
  self.assertNotIn('markdown',first)
  self.assertNotIn('markdown',second)
  self.assertTrue(any(s.value=='Plan generado correctamente' for s in at.success))
  self.assertFalse(any(d.label=='Descargar brief' for d in at.get('download_button')))
  self.assertTrue(any(d.label=='Descargar tracker CSV' for d in at.get('download_button')))
  self.assertNotEqual(first['csv'],second['csv'])
  row=pd.read_csv(io.BytesIO(second['csv'])).iloc[0]
  self.assertEqual(row.strategy,'Validar calidad del tráfico')
  self.assertTrue(pd.isna(row.Aprobado_por))
  at.button(key='hub_back_3').click().run();at.button(key='hub_back_2').click().run()
  at.button(key='strategy_0').click().run();at.button(key='hub_continue_1').click().run()
  self.assertEqual(at.text_input(key='action_edit_owner').value,'Checkout Lead')

 def test_generation_error_is_visible_and_recoverable(self):
  from unittest.mock import patch
  at=self.app()
  at.button(key='hub_continue_1').click().run()
  at.button(key='hub_continue_2').click().run()
  with patch('growth_views.action_artifacts',side_effect=ValueError('Falta validar el KPI')):
   at.button(key='generate').click().run()
  self.assertEqual(len(at.exception),0)
  self.assertTrue(any('Falta validar el KPI' in err.value for err in at.error))
  self.assertFalse(any(d.label=='Descargar brief' for d in at.get('download_button')))
  at.button(key='generate').click().run()
  self.assertTrue(any(s.value=='Plan generado correctamente' for s in at.success))
  self.assertFalse(any(d.label=='Descargar brief' for d in at.get('download_button')))
  self.assertEqual(len(at.exception),0)

 def test_download_payloads_match_edited_parameters(self):
  import tempfile
  from pathlib import Path
  at=self.app()
  at.button(key='strategy_1').click().run()
  at.button(key='hub_continue_1').click().run()
  at.text_input(key='action_edit_owner').set_value('Growth Marketing Bogotá').run()
  at.text_input(key='action_edit_kpi').set_value('Pedidos por sesión elegible').run()
  at.button(key='hub_continue_2').click().run()
  at.button(key='generate').click().run()
  generated=at.session_state['action_generated']
  self.assertIn('landing',generated['csv'].decode('utf-8-sig'))
  self.assertIn('Pedidos por sesión elegible',generated['csv'].decode('utf-8-sig'))
  self.assertIn('Growth Marketing Bogotá',generated['csv'].decode('utf-8-sig'))
  self.assertIn('Pendiente de aprobación humana',generated['csv'].decode('utf-8-sig'))
  with tempfile.TemporaryDirectory() as folder:
   tracker=Path(folder)/'tracker_growth.csv'
   tracker.write_bytes(generated['csv'])
   row=pd.read_csv(tracker).iloc[0]
   self.assertEqual(row.owner,'Growth Marketing Bogotá')
   self.assertEqual(row.kpi,'Pedidos por sesión elegible')
   self.assertEqual(row.strategy,'Validar calidad del tráfico')
   self.assertTrue(pd.isna(row.Aprobado_por))
  # La vista previa proviene de la misma instantánea de los archivos.
  self.assertEqual(generated['plan']['kpi'],'Pedidos por sesión elegible')
  visible=' '.join(m.value for m in at.markdown)
  self.assertIn('Acción preparada',visible)
  self.assertIn('Pedidos por sesión elegible',visible)
  self.assertIn('Growth Marketing Bogotá',visible)
  self.assertIn(generated['plan']['action'],visible)
  self.assertFalse(any(d.label=='Descargar brief' for d in at.get('download_button')))
  self.assertEqual(len(at.exception),0)

 def test_empty_required_field_stops_continuation(self):
  at=self.app();at.button(key='hub_continue_1').click().run()
  at.text_input(key='action_edit_owner').set_value('').run()
  self.assertTrue(at.button(key='hub_continue_2').disabled)
  self.assertFalse(any(b.key=='generate' for b in at.button))

 def test_new_zip_resets_wizard_without_blocking_ui(self):
  from unittest.mock import patch
  data,_,_=read_sources(None)
  buf=io.BytesIO();data['03_regions.csv'].loc[0,'actual_cvr']=.04
  with zipfile.ZipFile(buf,'w') as z:
   for name,df in data.items(): z.writestr('new/'+name,df.to_csv(index=False))
  at=self.app();self.prepare(at)
  original=at.session_state['source_id']
  buf.seek(0)
  with patch('streamlit.file_uploader',return_value=buf): at.run()
  self.assertEqual(len(at.exception),0)
  self.assertNotEqual(at.session_state['source_id'],original)
  self.assertEqual(at.session_state['action_step'],1)
  self.assertNotEqual(at.session_state['action_active_op'],'G-REG-bogota')
  self.assertNotIn('action_generated',at.session_state)
  self.assertTrue(any(b.key=='hub_continue_1' for b in at.button))

if __name__=='__main__': unittest.main()
