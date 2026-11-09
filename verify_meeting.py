"""Regression checks for provenance, identity merge and repeatable meeting import."""
import json,pathlib,tempfile,subprocess,sys,hashlib
R=pathlib.Path(__file__).resolve().parent
d=json.loads((R/'data.json').read_text(encoding='utf-8'))
old=json.loads((R/'snapshots/2026-11-09-before-meeting/data.json').read_text(encoding='utf-8'))
raw=lambda x:{r['recordId']:r for c in x['companies'] for r in c['records']}
assert raw(d)==raw(old), 'Original CSV rows must remain exactly unchanged'
assert len(d['companies'])==177
byname={c['name']:c for c in d['companies']}
li=byname['联感科技']; assert len(li['records'])==2
assert li['schoolOverride'] and li['school']=='香港中文大学'
assert set(li['aliases'])=={'智感科技','联感科技','联感医疗'}
assert d['meta']['companyRedirects']['p-606e0da37cf7']==li['id']
assert byname['Baytech']['id']=='p-963ea9374354'
assert byname['Ansun Biopharma']['sector']=='生命健康'
events=[e for c in d['companies'] for e in c['events']]
assert len(events)==8 and all(e['date']=='2026-11-09' and e['sourceTime'] for e in events)
assert not any(c['metrics'] for c in d['companies']), 'Unspecified currency/period must not become financial snapshots'
assert len(byname['丰疆智能']['decisions'])==1
assert byname['丰疆智能']['decisions'][0]['status']=='已决议'
assert len(d['weeklyImports'])==1
m=d['weeklyImports'][0];assert len(m['unresolved'])==13 and len(m['crossProject'])==4
assert not byname['忆生科技']['events'] and not byname['时维感知']['events']
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/'data.json';p.write_bytes((R/'data.json').read_bytes());before=p.read_bytes()
 subprocess.run([sys.executable,str(R/'apply_meeting.py'),str(R/'meetings/2026-11-09.json'),'--data',str(p)],check=True,capture_output=True)
 assert p.read_bytes()==before,'Reimport of the same meeting must be idempotent'
print('Meeting checks passed: 183 raw rows preserved, identity merge, dates, ambiguity isolation, no fabricated metrics, repeat import unchanged.')
