"""Builds the public website in docs/ from the dashboard page and the exported data.

Run scripts/export_dashboard.py first if the data changed. GitHub Pages serves docs/ as it is.
"""
import os,shutil

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS=os.path.join(ROOT,'docs')
TITLE='50 Years of Indian Cinema'
DESCRIPTION='Five decades of Indian box office: genres, languages, directors, and what films cost against what they made.'

page=open(os.path.join(ROOT,'scripts','dashboard_page.html'),encoding='utf-8').read()
page=page.replace('<meta name="dash-one-writer">\n','',1)

head=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESCRIPTION}">
<link rel="icon" href="data:,">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<style>
:root {{ --font-anthropic-sans: Inter, system-ui, -apple-system, 'Segoe UI', sans-serif; --cds-dur-slow: 300ms; }}
html, body {{ margin: 0; background: #fff; }}
.fy .fy-scope[hidden] {{ display: none; }}
.fy .fy-stat-value[data-field=gross_total] {{ font-size: clamp(15px, 1.6vw, 24px); overflow-wrap: normal; white-space: nowrap; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
<script src="runtime.js"></script>
</head>
<body>
<div id="dash-root">
'''

os.makedirs(os.path.join(DOCS,'data'),exist_ok=True)
with open(os.path.join(DOCS,'index.html'),'w',encoding='utf-8') as f:
    f.write(head+page+'\n</div>\n</body>\n</html>\n')
shutil.copy(os.path.join(ROOT,'scripts','site_runtime.js'),os.path.join(DOCS,'runtime.js'))
shutil.copy(os.path.join(ROOT,'output','dashboard_films.json'),os.path.join(DOCS,'data','films.json'))
shutil.copy(os.path.join(ROOT,'output','dashboard_directors.json'),os.path.join(DOCS,'data','directors.json'))
open(os.path.join(DOCS,'.nojekyll'),'w').close()
print('built',DOCS)
