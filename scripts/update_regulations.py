# Official rules page default
DEFAULT_RULES_URL="https://www.seoulmetro.co.kr/kr/board.do?menuIdx=518"
import os,re,json,hashlib,tempfile
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'regulations.json'
TARGETS=['승무원지도운용내규','운전관계직원업무내규','운전무사고성적심사규정','운전취급규정','운전취급세부요령','차량기지운전취급내규','철도차량운전면허교육훈련운영규정']
SOURCE=os.getenv('SEOULMETRO_RULES_URL','').strip()
if not SOURCE: raise SystemExit('SEOULMETRO_RULES_URL GitHub Repository Variable에 서울교통공사 정관 및 사규 페이지 주소를 등록하세요.')
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 regulation-update-checker/1.0'

def fetch(url):
    r=S.get(url,timeout=30); r.raise_for_status(); return r

def text_hwpx(b):
    import io
    out=[]
    with ZipFile(io.BytesIO(b)) as z:
        for n in sorted(x for x in z.namelist() if re.match(r'Contents/section\d+\.xml$',x)):
            root=ET.fromstring(z.read(n))
            out += [(e.text or '').strip() for e in root.iter() if e.tag.endswith('}t') and (e.text or '').strip()]
    return '\n'.join(out)

def text_pdf(b):
    import io
    return '\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(b)).pages)

def latest(text):
    ms=re.findall(r'(?:개정|제정)\s*(\d{4}\.\d{2}\.\d{2}\.)\s*(규정|내규|예규)\s*제(\d+)호',text)
    return f'{ms[-1][0]} {ms[-1][1]} 제{ms[-1][2]}호' if ms else ''

def articles(text):
    text=re.sub(r'제\s*\n?\s*(\d+)\s*\n?\s*조',r'제\1조',text)
    parts=re.compile(r'(?=제\d+조(?:의\d+)?(?:\([^\n]{0,80}\))?)').split(text)
    out=[]
    for x in parts:
        m=re.match(r'(제\d+조(?:의\d+)?)(?:\(([^\n]{0,80})\))?\s*(.*)',x,re.S)
        if m: out.append({'article':m.group(1),'title':m.group(2) or '', 'text':re.sub(r'\n{2,}','\n',m.group(3)).strip()[:9000]})
    return out

def discover(page_url):
    # Handles direct attachment links and common onclick/download patterns when the URL itself is present.
    soup=BeautifulSoup(fetch(page_url).text,'html.parser'); found={}
    for a in soup.find_all('a'):
        label=' '.join(a.stripped_strings); href=a.get('href') or ''
        blob=label+' '+href+' '+(a.get('onclick') or '')
        for name in TARGETS:
            if name in blob and href and not href.lower().startswith('javascript:'):
                found[name]=urljoin(page_url,href)
    return found

links=discover(SOURCE)
old=json.loads(DATA.read_text('utf-8')) if DATA.exists() else {'documents':[]}
oldmap={d['name']:d for d in old.get('documents',[])}; docs=[]; changed=[]; missing=[]
for name in TARGETS:
    if name not in links:
        if name in oldmap: docs.append(oldmap[name])
        missing.append(name); continue
    url=links[name]; b=fetch(url).content
    try:
        text=text_hwpx(b) if b[:2]==b'PK' else text_pdf(b)
        doc={'name':name,'revision':latest(text),'source_url':url,'source_page':SOURCE,'sha256':hashlib.sha256(b).hexdigest(),'articles':articles(text)}
        if not doc['articles']: raise ValueError('조문 추출 실패')
        if oldmap.get(name,{}).get('sha256') != doc['sha256'] or oldmap.get(name,{}).get('revision') != doc['revision']: changed.append(name)
        docs.append(doc)
    except Exception as e:
        docs.append(oldmap.get(name,{'name':name,'revision':'','articles':[]})); missing.append(f'{name}(파싱 실패: {e})')
from datetime import datetime,timezone
DATA.write_text(json.dumps({'generated':datetime.now(timezone.utc).isoformat(),'source_page':SOURCE,'changed':changed,'missing_or_unresolved':missing,'documents':docs},ensure_ascii=False),encoding='utf-8')
print('changed=',changed); print('missing=',missing)
