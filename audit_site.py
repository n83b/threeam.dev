from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urlparse,urljoin
from pathlib import Path
import xml.etree.ElementTree as ET,json,csv,re,hashlib,time,os
BASE='https://www.threeam.com.au/'
OUT=Path('audit'); RAW=OUT/'raw'/'pages'; ASSETS=OUT/'assets'
RAW.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(parents=True,exist_ok=True)
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[]
for p in (OUT/'raw').glob('*-sitemap.xml'):
 try: urls += [n.find('s:loc',ns).text for n in ET.parse(p).getroot().findall('s:url',ns)]
 except: pass
urls=list(dict.fromkeys(urls))
class P(HTMLParser):
 def __init__(self):
  super().__init__();self.title='';self.desc='';self.canon='';self.robots='';self.og={};self.h=[];self.links=[];self.images=[];self.forms=[];self.text=[];self.stack=[];self.form=None;self.jsonld=[]
 def handle_starttag(self,t,a):
  d=dict(a);self.stack.append(t)
  if t=='meta':
   k=(d.get('name') or d.get('property') or '').lower(); v=d.get('content','')
   if k=='description':self.desc=v
   elif k=='robots':self.robots=v
   elif k.startswith('og:'):self.og[k]=v
  elif t=='link' and d.get('rel')=='canonical':self.canon=d.get('href','')
  elif t=='a' and d.get('href'):self.links.append((d['href'],d.get('title','')))
  elif t=='img' and d.get('src'):self.images.append((d['src'],d.get('alt','')))
  elif t=='form': self.form={'action':d.get('action',''),'method':d.get('method','get'),'fields':[]};self.forms.append(self.form)
  elif t in ('input','textarea','select','button') and self.form is not None:self.form['fields'].append({'tag':t,'name':d.get('name',''),'type':d.get('type',''),'label':d.get('aria-label','') or d.get('placeholder','')})
 def handle_endtag(self,t):
  if t=='form':self.form=None
  if self.stack:self.stack.pop()
 def handle_data(self,d):
  x=' '.join(d.split())
  if not x:return
  if 'title' in self.stack:self.title += x+' '
  if any(h in self.stack for h in ('h1','h2','h3')):
   tag=next(h for h in ('h1','h2','h3') if h in self.stack);self.h.append((tag,x))
  if not any(t in self.stack for t in ('script','style','noscript')):self.text.append(x)
def get(u):
 r=Request(u,headers={'User-Agent':'Mozilla/5.0 (compatible; ThreeamAudit/1.0)'});return urlopen(r,timeout=45).read()
def fname(u):
 p=urlparse(u); ext=os.path.splitext(p.path)[1].lower()[:8]; return hashlib.sha1(u.encode()).hexdigest()[:16]+(ext if ext and len(ext)<7 else '.bin')
assets={}; records=[]
for i,u in enumerate(urls,1):
 print(f'[{i}/{len(urls)}] {u}',flush=True)
 rec={'url':u,'sitemap_type':next((p.name.replace('-sitemap.xml','') for p in (OUT/'raw').glob('*-sitemap.xml') if u.encode() in p.read_bytes()),'')}
 try:
  raw=get(u); (RAW/(hashlib.sha1(u.encode()).hexdigest()+'.html')).write_bytes(raw)
  p=P();p.feed(raw.decode('utf-8','ignore')); text=' '.join(p.text)
  img=[]
  for src,alt in p.images:
   au=urljoin(u,src)
   if urlparse(au).netloc.endswith('threeam.com.au') and urlparse(au).path.lower().split('?')[0].endswith(('.jpg','.jpeg','.png','.webp','.gif','.svg','.pdf')):
    img.append({'url':au,'alt':alt})
    assets.setdefault(au,{'url':au,'alt_texts':set(),'used_on':[]})['alt_texts'].add(alt);assets[au]['used_on'].append(u)
  rec.update({'status':200,'title':p.title.strip(),'meta_description':p.desc,'canonical':p.canon,'robots':p.robots,'open_graph':p.og,'headings':[{'level':a,'text':b} for a,b in p.h],'word_count':len(re.findall(r'\b[\w’\'-]+\b',text)),'copy':text,'links':[{'url':urljoin(u,x),'title':t} for x,t in p.links],'images':img,'forms':p.forms})
 except Exception as e: rec.update({'status':'ERROR','error':str(e)})
 records.append(rec)
# download deduplicated internal assets, max 20MB each
for i,(u,a) in enumerate(assets.items(),1):
 print(f'asset {i}/{len(assets)} {u}',flush=True);dest=ASSETS/fname(u)
 try:
  raw=get(u)
  if len(raw)<=20_000_000:dest.write_bytes(raw);a['file']=str(dest.relative_to(OUT));a['bytes']=len(raw)
  else:a['error']='Skipped: file over 20MB'
 except Exception as e:a['error']=str(e)
 a['alt_texts']=sorted(x for x in a['alt_texts'] if x)
with open(OUT/'inventory.json','w') as f:json.dump({'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':BASE,'pages':records,'assets':list(assets.values())},f,indent=2,ensure_ascii=False)
with open(OUT/'page-inventory.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['URL','Type','Status','Title','Meta description','Canonical','Words','H1','Images','Forms'])
 for x in records:w.writerow([x.get('url'),x.get('sitemap_type'),x.get('status'),x.get('title'),x.get('meta_description'),x.get('canonical'),x.get('word_count'), ' | '.join(z['text'] for z in x.get('headings',[]) if z['level']=='h1'),len(x.get('images',[])),len(x.get('forms',[]))])
