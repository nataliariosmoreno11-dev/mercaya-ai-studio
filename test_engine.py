import io, unittest, zipfile
from pathlib import Path
import pandas as pd
from engine import *

class EngineTests(unittest.TestCase):
 def setUp(self): self.data,self.brief,_=read_sources(None)
 def test_sample_priority_and_evidence(self):
  valid,paid,alerts,checks=analyze(self.data,self.brief)
  self.assertTrue(all(c['Estado']=='Válida' for c in checks))
  self.assertEqual(alerts[0]['ID'],'R03')
  self.assertEqual(len(paid),len(self.data[REQUIRED[1]].drop_duplicates()))
  self.assertTrue(all(a['Fuentes'] and a['Regla'] for a in alerts))
 def test_invalid_source_excluded(self):
  self.data[REQUIRED[0]].loc[0,'actual_cvr']=1.5
  valid,_,alerts,checks=analyze(self.data,self.brief)
  self.assertNotIn(REQUIRED[0],valid)
  self.assertNotIn('R05',[a['ID'] for a in alerts])
 def test_missing_columns_and_empty(self):
  self.data[REQUIRED[1]]=pd.DataFrame({'channel':[]})
  valid,checks=validate(self.data)
  self.assertNotIn(REQUIRED[1],valid)
 def test_exports_reproducible_pending_approval(self):
  _,_,alerts,_=analyze(self.data,self.brief)
  sid=fingerprint(self.data,self.brief)
  txt,csv=artifacts([alerts[0]],sid)
  self.assertEqual((txt,csv),artifacts([alerts[0]],sid))
  tracker=pd.read_csv(io.BytesIO(csv))
  self.assertEqual(len(tracker),1)
  self.assertTrue(tracker.Aprobado_por.isna().all())
  self.assertIn(sid,txt)
 def test_new_zip_nested(self):
  buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w') as z:
   for name,df in self.data.items(): z.writestr('nuevo/'+name,df.to_csv(index=False))
  buf.seek(0);data,brief,names=read_sources(buf)
  self.assertEqual(set(data),set(self.data))
  self.assertEqual(fingerprint(data,brief),fingerprint(data.copy(),brief))
 def test_changed_package_changes_fingerprint(self):
  before=fingerprint(self.data,self.brief)
  self.data[REQUIRED[0]].loc[0,'orders']+=1
  self.assertNotEqual(before,fingerprint(self.data,self.brief))
 def test_missing_sources(self):
  valid,_,alerts,checks=analyze({},'')
  self.assertEqual(alerts,[]);self.assertEqual(len(checks),6)

class InterfaceTests(unittest.TestCase):
 def test_generate_and_select(self):
  from streamlit.testing.v1 import AppTest
  at=AppTest.from_file('app.py').run(timeout=30)
  self.assertEqual(len(at.exception),0)
  if at.session_state.get('action_step',1)==1: at.button(key='hub_continue_1').click().run()
  if at.session_state.get('action_step',1)==2: at.button(key='hub_continue_2').click().run()
  at.button(key='generate').click().run()
  self.assertEqual(len(at.exception),0)
  generated=at.session_state['action_generated']
  self.assertIn('Optimizar checkout',generated['csv'].decode('utf-8-sig'))
  self.assertIn('Pendiente de aprobación humana',generated['csv'].decode('utf-8-sig'))
  at.button(key='hub_back_3').click().run()
  at.button(key='hub_back_2').click().run()
  at.selectbox(key='action_op').select('G-R07').run()
  self.assertEqual(len(at.exception),0)
  self.assertNotIn('Descargar tracker CSV',[d.label for d in at.get('download_button')])
  if at.session_state.get('action_step',1)==1: at.button(key='hub_continue_1').click().run()
  if at.session_state.get('action_step',1)==2: at.button(key='hub_continue_2').click().run()
  at.button(key='generate').click().run()
  self.assertIn('G-R07',at.session_state['action_current_draft']['op'])
  self.assertTrue(any('Descargar tracker CSV' in d.label for d in at.get('download_button')))
  at.button(key='legacy_generate').click().run()
  csv=at.session_state['deliverable']
  self.assertIn('R03',csv.decode('utf-8-sig'))
  self.assertIn('R01',csv.decode('utf-8-sig'))
  self.assertFalse(any(d.label=='Descargar brief' for d in at.get('download_button')))

 def test_cards_and_navigation(self):
  from streamlit.testing.v1 import AppTest
  at=AppTest.from_file('app.py').run(timeout=30)
  at.button(key='case_R01').click().run()
  self.assertEqual(len(at.exception),0)
  self.assertEqual(at.session_state['workspace_nav'],'◎ Decision Studio')
  self.assertEqual(at.selectbox(key='selected_case').value,1)
  self.assertEqual(len(at.multiselect),0)
  self.assertGreater(len([b for b in at.button if b.key and b.key.startswith('case_')]),1)
  at.button(key='next_step').click().run()
  self.assertEqual(at.session_state['workspace_nav'],'⤴ Action Hub')
  if at.session_state.get('action_step',1)==1: at.button(key='hub_continue_1').click().run()
  if at.session_state.get('action_step',1)==2: at.button(key='hub_continue_2').click().run()
  at.button(key='generate').click().run()
  at.button(key='growth_G-REG-bogota').click().run()
  self.assertEqual(at.session_state['action_active_op'],'G-REG-bogota')
  self.assertEqual(len(at.exception),0)

if __name__=='__main__': unittest.main()
