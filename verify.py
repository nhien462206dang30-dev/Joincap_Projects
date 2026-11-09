import json, pathlib, re, collections
root=pathlib.Path(__file__).resolve().parent
data=json.loads((root/'data.json').read_text(encoding='utf-8'))
assert len({c['id'] for c in data['companies']})==len(data['companies'])
records=[r for c in data['companies'] for r in c['records']]
assert len(records)==183 and len({r['recordId'] for r in records})==183
assert all(c['summary'] and c['queries'] for c in data['companies'])
assert all(c['sector'] in ['硬科技','生命健康','新材料','能源环保','消费','互联网与企业服务','其他/待分类'] for c in data['companies'])
assert len(next(c for c in data['companies'] if c['name']=='丰疆智能')['records'])==2
assert len(next(c for c in data['companies'] if c['name']=='快手科技')['records'])==2
html=(root/'index.html').read_text(encoding='utf-8')
embedded=json.loads(re.search(r'<script id="app-data" type="application/json">(.*?)</script>',html,re.S).group(1))
assert embedded==data
assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://',html)
test=root.parent.parent/'work'/'export-test.html'
if test.exists():
    s=test.read_text(encoding='utf-8')
    exported=json.loads(re.search(r'<script id="app-data" type="application/json">(.*?)</script>',s,re.S).group(1))
    company=next(c for c in exported['companies'] if c['name']=='丰疆智能')
    assert company['metrics'][0]['value']==1234.56
    assert company['metrics'][0]['period']=='2026 Q3（功能验证）'
    assert exported['history'][-1]['kind']=='metric'
    assert 'id="modal" open' not in s
print(json.dumps({'checks':'passed','companies':len(data['companies']),'records':len(records),'with_sources':sum(bool(c['sources']) for c in data['companies']),'statuses':dict(collections.Counter(c['status'] for c in data['companies']))},ensure_ascii=True))
