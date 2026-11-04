"""Builds dashboard-ready summary tables from Indian_Box_Office_Refined.xlsx (All Years sheet)."""
import pandas as pd, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
SRC=os.path.join(ROOT,'output','Indian_Box_Office_Refined.xlsx')
a=pd.read_excel(SRC,sheet_name='All Years',header=1)
a=a[a['Language']!='English'].copy()  # drop Hollywood films counted for India earnings only
a['Box Office Year']=a['List'].astype(int)
def dec(y): return '1970s (1976–79)' if y<1980 else ('2020s (2020–26)' if y>=2020 else f'{y//10*10}s')
a['Decade']=a['Box Office Year'].map(dec)
WW='Worldwide Gross (₹ Cr)'
HIT={'Hit','Super Hit','Blockbuster','Super Blockbuster','All Time Blockbuster','Sami Hit'}
a['Is Hit']=a['Verdict'].isin(HIT)

# Genres: one row per film per genre
g=a.assign(Genre=a['Genres'].str.split(r',\s*')).explode('Genre')
gy=g.groupby(['Box Office Year','Genre']).agg(Films=('Title','count'),**{'Total Gross (₹ Cr)':(WW,'sum')}).reset_index()
gy['Share of Year\'s Films']=gy['Films']/gy['Box Office Year'].map(a.groupby('Box Office Year').size())
gd=g.groupby(['Decade','Genre']).agg(Films=('Title','count'),**{'Total Gross (₹ Cr)':(WW,'sum'),'Avg IMDb Rating':('IMDb Rating','mean'),'Hits':('Is Hit','sum')}).reset_index()
gd['Share of Decade\'s Films']=gd['Films']/gd['Decade'].map(a.groupby('Decade').size())

# Directors: one row per film per director
d=a.assign(Director=a['Directors'].str.split(r',\s*')).explode('Director').dropna(subset=['Director'])
dd=d.groupby(['Director','Decade']).agg(Films=('Title','count'),**{'Total Gross (₹ Cr)':(WW,'sum'),'Avg IMDb Rating':('IMDb Rating','mean'),'Hits':('Is Hit','sum'),'Biggest Film':('Title','first')}).reset_index()
tot=d.groupby('Director')['Title'].count()
dd['Career Films in Dataset']=dd['Director'].map(tot)
big=d.sort_values(WW,ascending=False).groupby(['Director','Decade'])['Title'].first()
dd['Biggest Film']=[big[(x,y)] for x,y in zip(dd['Director'],dd['Decade'])]
dd=dd[dd['Career Films in Dataset']>=3].sort_values(['Career Films in Dataset','Director','Decade'],ascending=[False,True,True])

# Top films per decade: by gross and by IMDb votes
cols=['Decade','Rank','Title','Box Office Year','Language','Directors',WW,'Votes','IMDb Rating','Verdict']
tg=a.sort_values([WW,'Votes','Title'],ascending=[False,False,True],kind='stable').groupby('Decade').head(5).copy(); tg['Rank']=tg.groupby('Decade').cumcount()+1; tg['Ranked By']='Worldwide Gross'  # ties: more votes, then title
tv=a.sort_values(['Votes',WW,'Title'],ascending=[False,False,True],kind='stable').groupby('Decade').head(5).copy(); tv['Rank']=tv.groupby('Decade').cumcount()+1; tv['Ranked By']='IMDb Votes'
top=pd.concat([tg,tv])[['Ranked By']+cols].sort_values(['Ranked By','Decade','Rank'],ascending=[False,True,True])

wb=load_workbook(SRC)
hf=Font(name='Arial',bold=True,color='FFFFFF'); fill=PatternFill('solid',fgColor='1F3864'); bf=Font(name='Arial',size=10)
def add(name,df,note):
    if name in wb.sheetnames: del wb[name]
    ws=wb.create_sheet(name,2+[n for n in ['Top Films by Decade','Genre by Decade','Genre by Year','Director by Decade']].index(name))
    ws.append([note]); ws['A1'].font=Font(name='Arial',italic=True,bold=True,size=11,color='1F3864')
    ws.append(list(df.columns))
    for c in ws[2]: c.font=hf; c.fill=fill; c.alignment=Alignment(wrap_text=True,vertical='center')
    for r in df.itertuples(index=False): ws.append([None if pd.isna(v) else v for v in r])
    for row in ws.iter_rows(min_row=3):
        for c in row:
            c.font=bf
            h=ws.cell(2,c.column).value
            if '₹ Cr' in h or 'Rating' in h: c.number_format='#,##0.0'
            elif 'Share' in h: c.number_format='0.0%'
            elif h=='Votes': c.number_format='#,##0'
    for i,h in enumerate(df.columns,1): ws.column_dimensions[get_column_letter(i)].width=max(12,min(40,len(str(h))+4))
    ws.freeze_panes='A3'; ws.auto_filter.ref=f'A2:{get_column_letter(ws.max_column)}{ws.max_row}'
add('Top Films by Decade',top,'Top 5 films per decade, ranked two ways. Gross is not inflation-adjusted, and 1990s "Total Gross" may be India-only, so compare within a decade, not across decades')
add('Genre by Decade',gd,'One film counts once in every genre IMDb gives it, so shares add to more than 100%')
add('Genre by Year',gy,'One film counts once in every genre IMDb gives it, so shares add to more than 100%')
add('Director by Decade',dd,'Directors with 3 or more films in the dataset. Co-directed films count for each director. English-language Hollywood films (13, India earnings only) are excluded from all summary sheets')
wb.save(SRC)
print(top[top['Ranked By']=='Worldwide Gross'].groupby('Decade').head(1)[['Decade','Title',WW]].to_string(index=False))
print(top[top['Ranked By']=='IMDb Votes'].groupby('Decade').head(1)[['Decade','Title','Votes']].to_string(index=False))
print(dd.groupby('Director')['Career Films in Dataset'].first().sort_values(ascending=False).head(12).to_string())
print(gd.sort_values('Films',ascending=False).head(8)[['Decade','Genre','Films']].to_string(index=False))
