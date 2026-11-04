import re, pandas as pd
LABELS=[('rel',r'Release[sd]? [Dd]ate\s*:'),('relon',r'Released on'),('lang',r'Language\s*:'),
 ('budget',r'Budget\s*[:\-]'),('fdw',r'First Day Collection Worldwide\s*:'),('fdi',r'First Day Collection India\s*:'),
 ('ww',r'(?:Worldwide Collection|Worldwide Gross|Total Gross|Box-office)\s*[:\-]'),('share',r'Share\s*:'),
 ('inet',r'India Net Collection\s*:'),('igross',r'India Gross Collection\s*:'),('os',r'Overseas Collection\s*:'),
 ('verdict',r'(?:Verdict|Vardit)\s*[:\-]'),('note',r'Note\s*:'),('ind',r'•')]
def num(seg):
    seg=seg.replace(',','')
    m=re.search(r'(\d+(?:\.\d+)?)',seg)
    if not m: return None
    v=float(m.group(1)); low=seg.lower()
    if '$' in seg or 'million' in low: return None
    if 'lakh' in low or 'laksh' in low: v/=100
    return round(v,2)
def parse(d):
    out={}
    if pd.isna(d): return out
    t=str(d)
    hits=sorted([(m.start(),m.end(),k) for k,p in LABELS for m in re.finditer(p,t)])
    for i,(s,e,k) in enumerate(hits):
        seg=t[e:hits[i+1][0] if i+1<len(hits) else len(t)]
        seg=re.sub(r'(cr|crore)?\s*\(?\s*$','',seg.strip()) if k!='share' else seg
        if 'still running' in seg: out['status']='Still running'
        if k=='lang': out['lang']=re.sub(r'[^A-Za-z]','',seg).replace('Tanil','Tamil')
        elif k in('rel','relon'):
            s2=re.sub(r'\s*in India\s*$','',seg).strip(); out['rel']=pd.to_datetime(s2,errors='coerce',dayfirst=True)
        elif k=='verdict':
            v=re.sub(r'\s+',' ',seg).strip()
            if 'as of now' in v.lower(): out['status']='Still running'; v=re.sub(r'(?i)\s*as of now','',v)
            out['verdict']=v.strip().title()
        elif k=='note': out['status']=(out.get('status','')+' – ' if out.get('status') else '')+seg.strip()
        elif k=='ind': out['ind']=seg.strip().title().replace('In ','in ')
        else:
            v=num(seg)
            if k=='budget' and v is None and seg.strip(): out['bnote']=seg.strip()
            if v is not None and k not in out: out[k]=v
    return out
