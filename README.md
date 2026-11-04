# Indian Box Office, 1976–2026 (DESG 317 · A3)

## Folders
- `raw/` original IMDb list exports (one CSV per year, 1976–2018) and `50yrs_of_Indian_box_office.xlsx` (2019–2026 sheets)
- `scripts/` preparation steps
- `output/` cleaned workbook

## Rebuild
Needs Python 3 with pandas and openpyxl (`pip install pandas openpyxl`).

    python scripts/build_refined.py   # combines lists, splits box-office text, adds notes
    python scripts/prep_views.py      # adds Top Films / Genre / Director summary sheets

## What the steps do
1. Combine one list per year, dropping repeat uploads. Each sheet is named by the list's most common year.
2. 2019–2026 come from the xlsx. Its "2008" sheet duplicates the 2007 list and is skipped.
3. Split each description into Language, Budget, First Day, Worldwide Gross, Share, India Net, India Gross, Overseas, Verdict, Industry Hit and Status, all in ₹ crore (lakh ÷ 100). USD budgets are kept as text.
4. Add the inclusion rule: ₹20 cr minimum for 2000–2023, ₹10 cr for 1994–1999 and 2024–2026, and top grossers with no cutoff for 1976–1993.
5. Add verification notes for rows checked against IMDb, Box Office Mojo and Wikipedia (3 Nov 2026).
6. Build summary sheets, excluding the 13 English-language Hollywood films.

See the About sheet in the workbook for known gaps.

## Dashboard data
    python scripts/export_dashboard.py  # writes output/dashboard_films.json and output/dashboard_directors.json

- Lead genre: IMDb lists genres alphabetically, so each film's colour comes from the first matching group in this order: Musical, Fantasy & horror, History & sport, Romance, Comedy, Thriller, Crime, Family & adventure, Action, Drama.
- `raw/director_gender.csv`: directors known to be women (some from Claude's knowledge, not checked against a source, some confirmed by the author). Everyone not listed is assumed to be a man. Correct the file and re-run the export.
- The export also carries release date (only when it falls in the list's year), opening-day and overseas gross, and the lists' "Industry Hit" record flag.
- Posters: put images in `raw/posters/` named by IMDb id (e.g. `tt0112870.jpg`) and re-run the export; they then need uploading to the dashboard.

## Website
    python scripts/build_site.py  # writes the public site to docs/

GitHub Pages serves `docs/`. The page is `scripts/dashboard_page.html`, and `scripts/site_runtime.js` runs it without the Claude dashboard runtime. After changing the data or the page, rebuild and push.

`raw/` and `output/` are not in the GitHub repository (see `.gitignore`). The site's data is in `docs/data/`.
