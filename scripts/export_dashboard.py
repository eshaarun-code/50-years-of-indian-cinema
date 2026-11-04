"""Exports the dashboard's data from Indian_Box_Office_Refined.xlsx (All Years sheet).

Writes output/dashboard_films.json (one row per film) and output/dashboard_directors.json
(one row per director, with gender from raw/director_gender.csv). Posters are matched from
raw/posters/<imdb id>.jpg|png|webp when present.
"""
import pandas as pd, json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,'output','Indian_Box_Office_Refined.xlsx')

# Genre groups, in the order that decides a film's lead genre. IMDb lists genres alphabetically,
# so the first listed genre is not the main one; the more specific group wins and Drama comes last.
GROUPS=[('Musical',{'Musical','Music'}),('Fantasy & horror',{'Fantasy','Horror','Sci-Fi','Mystery','Animation'}),
 ('History & sport',{'History','Biography','War','Sport','Documentary','Western'}),('Romance',{'Romance'}),
 ('Comedy',{'Comedy'}),('Thriller',{'Thriller'}),('Crime',{'Crime'}),('Family & adventure',{'Family','Adventure'}),
 ('Action',{'Action'}),('Drama',{'Drama'})]
def groups(g):
    gs=set(str(g).split(', ')) if pd.notna(g) else set()
    return [n for n,s in GROUPS if gs & s]
def dec(y): return '1970s' if y<1980 else f'{y//10*10}s'
nz=lambda v: None if pd.isna(v) else v
def release(r,y):
    # Box-office source date first, then IMDb's; only kept when it falls in the list's year (IMDb often gives a re-release)
    for c in ('Release Date (Box Office Source)','Release Date (IMDb)'):
        d=pd.to_datetime(r[c],errors='coerce')
        if pd.notna(d) and d.year==y: return d.strftime('%Y-%m-%d')
    return None

a=pd.read_excel(SRC,sheet_name='All Years',header=1)
a=a[a['Language']!='English']  # Hollywood films, counted for India earnings only
pdir=os.path.join(ROOT,'raw','posters')
posters={os.path.splitext(p)[0]:p for p in os.listdir(pdir)} if os.path.isdir(pdir) else {}
films=[]
for _,r in a.iterrows():
    imdb=str(r['IMDb Link']).rstrip('/').split('/')[-1]; y=int(r['List']); g=groups(r['Genres'])
    films.append(dict(key=f'{imdb}_{y}',imdb=imdb,title=str(r['Title']),year=y,decade=dec(y),language=nz(r['Language']),
        genres=nz(r['Genres']),genre_groups=', '.join(g),lead_genre=g[0] if g else 'Drama',directors=nz(r['Directors']),
        budget=nz(r['Budget (₹ Cr)']),gross=nz(r['Worldwide Gross (₹ Cr)']),rating=nz(r['IMDb Rating']),
        votes=None if pd.isna(r['Votes']) else int(r['Votes']),verdict=nz(r['Verdict']),poster=posters.get(imdb),
        release=release(r,y),first_day=nz(r['First Day Worldwide (₹ Cr)']),overseas=nz(r['Overseas (₹ Cr)']),
        industry_hit=nz(r['Industry Hit'])))

gender=pd.read_csv(os.path.join(ROOT,'raw','director_gender.csv')).set_index('director')
names=sorted({d for f in films for d in (f['directors'] or '').split(', ') if d})
directors=[dict(director=d,gender=gender['gender'].get(d,'man'),
    gender_source=gender['source'].get(d,'assumed, not checked')) for d in names]

out=os.path.join(ROOT,'output')
json.dump(films,open(os.path.join(out,'dashboard_films.json'),'w'),ensure_ascii=False,separators=(',',':'))
json.dump(directors,open(os.path.join(out,'dashboard_directors.json'),'w'),ensure_ascii=False,separators=(',',':'))
print(len(films),'films,',len(directors),'directors,',sum(d['gender']=='woman' for d in directors),'women,',sum(1 for f in films if f['poster']),'posters')
