"""Build the offline, self-contained dashboard from auditable JSON inputs."""
import json, pathlib, hashlib, datetime, sys
ROOT = pathlib.Path(__file__).resolve().parent
WORK = ROOT.parent.parent / 'work'
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def safe_json(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
def render(data):
    (ROOT/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    template=(ROOT/'src'/'template.html').read_text(encoding='utf-8')
    html=template.replace('/*__STYLE__*/',(ROOT/'src'/'style.css').read_text(encoding='utf-8')).replace('/*__APP__*/',(ROOT/'src'/'app.js').read_text(encoding='utf-8')).replace('__DATA__',safe_json(data))
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    print(json.dumps({'companies':len(data['companies']),'records':data['sourceRecordCount'],'version':data['version'],'bytes':len(html.encode())}))
if '--data' in sys.argv or ((ROOT/'data.json').exists() and '--reset-from-research' not in sys.argv):
    data=read(pathlib.Path(sys.argv[sys.argv.index('--data')+1]) if '--data' in sys.argv else ROOT/'data.json')
    assert data['schemaVersion']==1 and isinstance(data['companies'],list)
    render(data)
    raise SystemExit(0)
input_dir=ROOT/'inputs' if (ROOT/'inputs'/'source.json').exists() else WORK
rows = read(input_dir / 'source.json')
research = {}
for p in sorted((input_dir / 'research').glob('result*.json')):
    for r in read(p): research[r['name']] = r
groups = {}
canonical = {'明源雲':'明源云 909','德琪醫藥':'德琪医药','德琪医疗 6996':'德琪医药'}
for i,r in enumerate(rows):
    name=canonical.get(r['项目编号'].strip(),r['项目编号'].strip())
    groups.setdefault(name, []).append(dict(r, recordId=f'r{i+1:03d}'))
companies=[]
for name, records in groups.items():
    x=research.get(name,{})
    if not x:
        x=next((research[r['项目编号']] for r in records if research.get(r['项目编号'])),{})
    def vals(k): return list(dict.fromkeys(r[k] for r in records if r.get(k)))
    companies.append(dict(id='p-'+hashlib.sha256(name.encode()).hexdigest()[:12],name=name,
      aliases=list(dict.fromkeys([name]+vals('项目编号')+vals('项目名称')+x.get('aliases',[]))),records=records,
      summary=x.get('summary') or '；'.join(vals('项目描述')) or '现有资料尚不足以说明产品和业务，需补充公司全称、官网或 BP。',
      sector=x.get('sector','其他/待分类'),subsector=x.get('subsector','待分类'),products=x.get('products',[]),customers=x.get('customers',''),
      people=x.get('people',[]),school=x.get('school',''),sources=x.get('sources',[]),queries=x.get('queries',[]),
      status=x.get('status','unresolved'),gaps=x.get('gaps',[]) if x else ['尚待公开资料核验'],
      review=x.get('review',{'focus':'先确认主体、产品及最新进展，再补齐管理判断。','questions':['最新业务进展与当前融资计划是什么？','我方下一步需要完成什么，谁负责？','有哪些需要决议或补充的材料？']}),
      metrics=[],events=[],decisions=[]))
# Classifications grounded in explicit source descriptions, not company-name guesses.
overrides={'镓倍HYBAY':('硬科技','氮化镓功率器件'),'长光辰芯':('硬科技','CMOS图像传感器'),
 'Action Brain（具身智能动作大脑）':('硬科技','具身智能'),'AI 多模态传感器':('硬科技','智能传感'),
 '利泰制药':('生命健康','药品研发与制造'),'華希生物':('生命健康','动物疫苗'),
 '华希生物':('生命健康','动物疫苗'),
 '醫渡科技':('生命健康','医疗数据智能'),'卓越商企服务 6989':('互联网与企业服务','商业物业管理')}
for c in companies:
    if c['name'] in overrides: c['sector'],c['subsector']=overrides[c['name']]
    for r in c['records']:
        if r['项目编号']!=c['name']: c.setdefault('entityNotes',[]).append('原名 '+r['项目编号']+' 已归并；原始业务记录完整保留。')
people_file=input_dir/'research'/'people-enrichment.json'
if people_file.exists():
    for entry in read(people_file):
        c=next((c for c in companies if entry['projectName'] in c['aliases']),None)
        if c:
            if entry.get('people'):
                c['people']=[dict(p,position=p.get('role',''),role='原表关联；创始人角色待核实') for p in entry['people']]
            c['sources'] += [s for s in entry.get('sources',[]) if s.get('url') not in {x.get('url') for x in c['sources']}]
            c['gaps']=list(dict.fromkeys(c['gaps']+entry.get('notes',[])))
data=dict(schemaVersion=1,version='2026-11-09.1',dataDate='2026-11-09',title='项目 Universe',
 sourceName='项目运营中台 - 核心数据库_项目总库.csv',sourceRecordCount=len(rows),companies=companies,
 researchDate='2026-11-09',history=[],weeklyImports=[],meta={'sourceDateKnown':False,'investmentOwner':'我方（含中楷）'})
data['version']='2026-11-09.1-'+hashlib.sha256(safe_json(companies).encode()).hexdigest()[:8]
render(data)
