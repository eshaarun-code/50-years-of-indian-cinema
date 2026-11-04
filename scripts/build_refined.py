import pandas as pd, glob, re, sys, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parse_bo import parse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def lang(d):
    m=re.search(r'Language\s*:\s*([A-Za-z]+)',str(d)); return m.group(1) if m else ''
def verdict(d):
    m=re.search(r'(?:Verdict|Vardit)\s*[:\-]\s*([A-Za-z ]+)',str(d))
    if not m: return ''
    v=re.split(r'\s+(?:Release|Released|Note|as of)\b',m.group(1))[0]
    v=re.sub(r'(Release|Released|Note)$','',v).strip()
    return v.title()

SPEC={
 'tt0185335':'IMDb year 2016 is wrong: released 31 Oct 1997 (Wikipedia)',
 'tt0361851':'IMDb year 1993 is wrong: released 21 Dec 1990 (Wikipedia)',
 'tt1773109':'IMDb year 2010, but India release was 14 Jan 2011 (IMDb release info)',
 'tt28259207':'IMDb year 2023 is the TIFF premiere; India theatrical release 5 Jul 2024',
 'tt34365591':'IMDb year 2024 is the festival premiere; theatrical release 25 Jul 2025 (Wikipedia)',
 'tt1833673':'Release Date is a re-release; original release 20 Dec 2013 (Box Office Mojo)',
 'tt0075632':'Released 7 Jan 1977, so it appears in both the 1976 and 1977 lists',
}
def vnote(r):
    c=str(r['URL']).rstrip('/').split('/')[-1]
    if c in SPEC: return SPEC[c]
    rd=pd.to_datetime(r['Release Date'],errors='coerce')
    if pd.isna(rd): return 'IMDb has no release date' + (' or runtime' if pd.isna(r['Runtime (mins)']) else '')
    if rd.year-int(r['Year'])>=2: return f'Release Date ({rd.date()}) is a later re-release or IMDb error, not the original release'
    if rd.year-int(r['Year'])==1: return 'Release Date falls in the year after the IMDb year'
    if pd.isna(r['Runtime (mins)']): return 'IMDb has no runtime'
    return ''
def expand(d):
    P=pd.DataFrame([parse(x) for x in d['Description']],index=d.index)
    for k,c in {'rel': 'BO Release', 'lang': 'Language', 'budget': 'Budget', 'bnote': 'Budget Note', 'fdw': 'FDW', 'fdi': 'FDI', 'ww': 'WW', 'share': 'Share', 'inet': 'INet', 'igross': 'IGross', 'os': 'OS', 'verdict': 'Verdict', 'ind': 'Industry Hit', 'status': 'Status'}.items(): d[c]=P[k] if k in P else None
    d['Language']=d['Language'].replace({'TamilTelugu':'Tamil, Telugu','MarathiHindi':'Marathi, Hindi'})
    d['Release Date']=d['Release Date'].map(lambda v: pd.to_datetime(v,errors='coerce') if isinstance(v,str) and len(v)>4 else v)
    return d
lists=[]
seen={}
for f in sorted(glob.glob(os.path.join(ROOT,'raw','*.csv'))):
    seen[f[-40:]]=f
for f in seen.values():
    d=pd.read_csv(f)
    yr=int(d['Year'].mode()[0])
    d['Note']=d.apply(vnote,axis=1); d=expand(d)
    lists.append((yr,d))
X=pd.read_excel(os.path.join(ROOT,'raw','50yrs_of_Indian_box_office.xlsx'),sheet_name=None)
for k,d in X.items():
    if not k[:4].isdigit() or int(k[:4])<2019 or d.empty: continue
    d=d.copy(); d['Note']=d.apply(vnote,axis=1); d=expand(d)
    lists.append((int(k[:4]),d))
lists.sort(key=lambda x:x[0])

cols=['Position','Title','Original Title','Year','Release Date','BO Release','Language','Budget','Budget Note','FDW','FDI','WW','Share','INet','IGross','OS','Verdict','Industry Hit','Status','IMDb Rating','Runtime (mins)','Genres','Num Votes','Directors','URL','Note','Description']
heads=['Rank','Title','Original Title','Year','Release Date (IMDb)','Release Date (Box Office Source)','Language','Budget (₹ Cr)','Budget (Other Currency)','First Day Worldwide (₹ Cr)','First Day India (₹ Cr)','Worldwide Gross (₹ Cr)','Distributor Share (₹ Cr)','India Net (₹ Cr)','India Gross (₹ Cr)','Overseas (₹ Cr)','Verdict','Industry Hit','Box Office Status','IMDb Rating','Runtime (mins)','Genres','Votes','Directors','IMDb Link','Verification Note','Original Box Office Text']
widths=[7,32,28,7,14,16,12,11,13,14,12,14,13,11,12,11,20,28,30,10,10,32,10,26,38,50,60]

hf=Font(name='Arial',bold=True,color='FFFFFF'); hfill=PatternFill('solid',fgColor='1F3864')
bf=Font(name='Arial',size=10)
def rule(y):
    y=int(y)
    if y<=1993: return 'Top-grossing Indian films of the year (no minimum collection cutoff; includes films under ₹10 crore)'
    if y<=1999 or y>=2024: return 'Only Indian films that collected a minimum of ₹10 crore worldwide are considered'
    return 'Only Indian films that collected a minimum of ₹20 crore worldwide are considered'
def write(ws,df,extra_list_col=False,note=''):
    h=heads[:]; c=cols[:]; w=widths[:]
    if extra_list_col: h.insert(0,'List'); c.insert(0,'List'); w.insert(0,8); h.append('Inclusion Rule'); c.append('Rule'); w.append(70)
    ws.append([note]); ws['A1'].font=Font(name='Arial',italic=True,bold=True,size=11,color='1F3864')
    ws.row_dimensions[1].height=22
    ws.append(h)
    for cell in ws[2]: cell.font=hf; cell.fill=hfill; cell.alignment=Alignment(vertical='center')
    for r in df[c].itertuples(index=False):
        ws.append([None if pd.isna(v) else (int(v) if isinstance(v,float) and v.is_integer() and False else v) for v in r])
    for row in ws.iter_rows(min_row=3):
        for cell in row: cell.font=bf
    for i,wd in enumerate(w,1): ws.column_dimensions[get_column_letter(i)].width=wd
    ws.freeze_panes='C3' if extra_list_col else 'B3'
    ws.auto_filter.ref=f'A2:{get_column_letter(ws.max_column)}{ws.max_row}'
    for name,fmt in [('Votes','#,##0'),('Release Date (IMDb)','dd-mmm-yyyy'),('Release Date (Box Office Source)','dd-mmm-yyyy')]+[(x,'#,##0.00') for x in h if '₹ Cr' in x]:
        ci=h.index(name)+1
        for row in ws.iter_rows(min_row=3,min_col=ci,max_col=ci):
            for cell in row: cell.number_format=fmt
    for cell in ws[2]: cell.alignment=Alignment(wrap_text=True,vertical='center')
    ws.row_dimensions[2].height=32

wb=Workbook(); ws=wb.active; ws.title='All Years'
allf=pd.concat([d.assign(List=str(y),Rule=rule(y)) for y,d in lists]).sort_values(['List','Position'])
write(ws,allf,True,'Inclusion rule: minimum ₹20 crore worldwide (2000–2023) or ₹10 crore (1994–1999, 2024–2026); 1976–1993 lists are the year\'s top grossers with no cutoff')
for y,d in lists:
    write(wb.create_sheet(str(y)),d.sort_values('Position'),note=rule(y))
ab=wb.create_sheet('About',1)
rows=[('About this workbook',''),
('Source','IMDb user lists exported as CSV (one list per year); box-office figures come from the list descriptions'),
('Lists combined',f'{len(lists)} lists, {len(allf)} films, {lists[0][0]}–{lists[-1][0]}'),
('Inclusion rule','Minimum ₹20 crore worldwide collection for 2000–2023; minimum ₹10 crore for 1994–1999 and 2024–2026; 1976–1993 lists are the top grossers of each year with no cutoff. The rule is noted at the top of every sheet'),
('Verification','Checked against IMDb (via Box Office Mojo and IMDb release pages), Wikipedia and news reports on 3 Nov 2026. IMDb pages could not be scraped in bulk, so only flagged rows were checked. Issues are listed in the "Verification Note" column'),
('IMDb snapshot','Ratings, votes and runtimes are from the IMDb list export and change over time. Several Release Dates are IMDb\'s latest India re-release rather than the original release'),
('Sheet order','"All Years" first, then one sheet per year, oldest to newest'),
('Row order','Each sheet keeps the original list rank (Rank column)'),
('Year of a sheet','The most common release year in that list. A few films carry a different IMDb year (e.g. Ghulam-E-Musthafa in 1997, Lorry Driver in 1990)'),
('Split columns','The box-office description was split into Language, Budget, First Day, Worldwide Gross, Distributor Share, India Net, India Gross, Overseas, Verdict, Industry Hit and Status. All money columns are in ₹ crore (lakh figures divided by 100). US-dollar budgets of English films go in "Budget (Other Currency)". "Worldwide Gross" also holds older lists\' "Total Gross" and "Box-office" figures. "Vardit" was read as Verdict. The original text is kept in the last column'),
('Dropped columns','Const, Created, Modified, Title Type (all Movie)'),
('Known gaps','The 2025 list has 2 films with no description. Box-office formats differ by era (pre-1990 lists give rough crore totals; 2013+ give worldwide/India/overseas splits). Lists cover top grossers only, not every release. The 1976 and 1989 lists have no descriptions, so Language, Verdict and box-office details are blank there'),
]
for r in rows: ab.append(r)
ab['A1'].font=Font(name='Arial',bold=True,size=13)
for row in ab.iter_rows(min_row=2):
    row[0].font=Font(name='Arial',bold=True,size=10); row[1].font=bf
    row[1].alignment=Alignment(wrap_text=True,vertical='top'); row[0].alignment=Alignment(vertical='top')
ab.column_dimensions['A'].width=18; ab.column_dimensions['B'].width=100
wb.save(os.path.join(ROOT,'output','Indian_Box_Office_Refined.xlsx'))
print([y for y,_ in lists], len(allf))
print(allf['Verdict'].value_counts().head(20))
