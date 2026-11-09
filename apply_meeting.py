"""Apply an AI-prepared, reviewed meeting package; never parses raw prose as facts.
Usage: python apply_meeting.py meeting.json --data data.json
"""
import argparse, json, pathlib, datetime, hashlib, math
p=argparse.ArgumentParser();p.add_argument('meeting');p.add_argument('--data',default='data.json');a=p.parse_args()
path=pathlib.Path(a.data);data=json.loads(path.read_text(encoding='utf-8-sig'));meeting=json.loads(pathlib.Path(a.meeting).read_text(encoding='utf-8-sig'))
assert data['schemaVersion']==1
mid=meeting['meetingId']; date=meeting['date']; datetime.date.fromisoformat(date)
assert isinstance(mid,str) and mid.strip()
if any(m['meetingId']==mid for m in data.get('weeklyImports',[])):
    print('Meeting already imported; no changes.');raise SystemExit(0)
lookup={c['id']:c for c in data['companies']}
for u in meeting['updates']:
    assert u['companyId'] in lookup,'Unknown companyId; resolve the identity before applying.'
    assert isinstance(u['text'],str) and u['text'].strip()
    if 'currentStatus' in u:
        status=u['currentStatus']
        assert isinstance(status,dict) and isinstance(status.get('text'),str)
        datetime.date.fromisoformat(status['date'])
        assert status['date']==date,'Current status must use the meeting date.'
        assert 'pipeline' not in status or isinstance(status['pipeline'],bool)
        assert status['date']>=lookup[u['companyId']].get('currentStatus',{}).get('date',''),'Older meeting cannot overwrite latest status.'
    for metric in u.get('metrics',[]):
        assert isinstance(metric.get('value'),(int,float)) and not isinstance(metric['value'],bool) and math.isfinite(metric['value'])
        assert all(isinstance(metric.get(k),str) for k in ['label','currency','unit','period','round','basis','kind','asOf'])
        datetime.date.fromisoformat(metric['asOf'])
        old=next((x for x in lookup[u['companyId']]['metrics'] if x['id']==metric.get('id')),None)
        if old:
            assert metric['asOf']>=old['asOf'],'Older financial data cannot overwrite a newer snapshot.'
        key=lambda m:tuple(m.get(k,'') for k in ['label','period','round','basis','currency','kind'])
        assert not any(key(x)==key(metric) and x['id']!=metric.get('id') for x in lookup[u['companyId']]['metrics']),'Duplicate metric key; use existing ID for a correction.'
    for d in u.get('decisions',[]):
        assert d['status'] in ['待讨论','已决议','暂缓']
        assert d['title'].strip()
        assert d['status']!='已决议' or d.get('note','').strip()
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
before=json.dumps(data,ensure_ascii=False,indent=2)
for i,u in enumerate(meeting['updates']):
    c=lookup[u['companyId']]; eid='meeting-'+hashlib.sha256((mid+'|'+str(i)).encode()).hexdigest()[:16]
    if 'currentStatus' in u:
        previous=c.get('currentStatus');c['currentStatus']=dict(u['currentStatus'])
        data['history'].append(dict(id=eid+'-status',companyId=c['id'],kind='profile',targetId=c['id'],before=previous,after=c['currentStatus'],at=stamp,source=meeting.get('title',mid),note='更新当前跟进状态，保留原始阶段'))
    event={k:u.get(k,'') for k in ['text','next','owner','deadline']}
    event.update(id=eid,date=date,recordedAt=stamp,category=u.get('category','项目进展'),source=meeting.get('title',mid),meetingId=mid,sourceTime=u.get('sourceTime',''),matchBasis=u.get('matchBasis',''))
    c['events'].append(event)
    data['history'].append(dict(id=eid+'-log',companyId=c['id'],kind='event',targetId=eid,before=None,after=event,at=stamp,source=meeting.get('title',mid),note='会议纪要更新'))
    for j,m in enumerate(u.get('metrics',[])):
        metric_id=m.get('id',eid+'-metric-'+str(j));old=next((x for x in c['metrics'] if x['id']==metric_id),None)
        item=dict(m,id=metric_id,updatedAt=stamp,note=m.get('note',meeting.get('title',mid)))
        if old:c['metrics'][c['metrics'].index(old)]=item
        else:c['metrics'].append(item)
        data['history'].append(dict(id=metric_id+'-'+stamp,companyId=c['id'],kind='metric',targetId=metric_id,before=old,after=item,at=stamp,source=meeting.get('title',mid),note='会议纪要中的明确数字'))
    for j,d in enumerate(u.get('decisions',[])):
        did=d.get('id',eid+'-decision-'+str(j));old=next((x for x in c['decisions'] if x['id']==did),None)
        item=dict(d,id=did,date=date,updatedAt=stamp,source=meeting.get('title',mid),meetingId=mid)
        if old:c['decisions'][c['decisions'].index(old)]=item
        else:c['decisions'].append(item)
        data['history'].append(dict(id=did+'-'+stamp,companyId=c['id'],kind='decision',targetId=did,before=old,after=item,at=stamp,source=meeting.get('title',mid),note='会议纪要更新'))
data.setdefault('weeklyImports',[]).append(dict(meetingId=mid,date=date,title=meeting.get('title',mid),importedAt=stamp,unresolved=meeting.get('unresolved',[]),crossProject=meeting.get('crossProject',[]),excluded=meeting.get('excluded',[]),sourceFile=meeting.get('sourceFile',''),sourceSha256=meeting.get('sourceSha256','')))
data['version']=date+'.meeting-'+hashlib.sha256(mid.encode()).hexdigest()[:6]
path.with_suffix('.before-meeting.json').write_text(before,encoding='utf-8')
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Applied '+str(len(meeting['updates']))+' company updates. Rebuild index.html with --data.')
