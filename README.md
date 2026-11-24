# Germany's Accident Black Spots, 2016–2024

A data-analysis project (Python + SQL) on every police-recorded road accident
with personal injury in Germany — **2,098,019 geocoded records** from the
Destatis **Unfallatlas**, 2016–2024, across 401 districts — plus an interactive
web dashboard and a complete Power BI package that rebuilds the same report
natively in Power BI Desktop.

**Data (100% real, published source):** Unfallatlas — Statistische Ämter des
Bundes und der Länder, via
[unfallatlas.statistikportal.de](https://unfallatlas.statistikportal.de/)
(open-data CSVs served from the portal's download host), licence
**dl-de/by-2-0**. Every number below is produced by `prep.py` from the raw
yearly files; nothing is typed by hand.

## Verified record counts

| Year | Records | Länder covered |
|------|--------:|----------------|
| 2016 | 151,673 | 8 |
| 2017 | 195,229 | 12 |
| 2018 | 211,868 | 13 |
| 2019 | 268,370 | 15 |
| 2020 | 237,994 | 16 |
| 2021 | 238,826 | 16 |
| 2022 | 256,492 | 16 |
| 2023 | 269,048 | 16 |
| 2024 | 268,519 | 16 |
| **Total** | **2,098,019** | |

**Coverage caveat:** geocoding rolled out Land by Land (per the official
metadata): 2016 = 8 Länder, 2017 = 12, 2018 = 13, 2019 = 15, **2020–2024 =
all 16**. Every published record carries valid coordinates (verified: 100%
in every year); pre-2020 totals are therefore not Germany totals, and the
dashboard labels this wherever early years appear.

## Headline findings

- 2,098,019 injury accidents: **1.0% fatal, 18.0% serious, 81.1% slight**.
- Busiest cell of the week: **Tuesday 16:00**.
- Highest district rates per 100k: **Memmingen, Rosenheim, Lübeck**.
- Darkness holds 18.9% of accidents but **26.3% of fatal ones**.
- April 2020 fell **28.2% year-on-year** in the first lockdown.
- Bicycles are involved in **29.9%** of accidents — 32.2% by 2024.

## Repository layout

```
prep.py                  # load raw files, verify counts, build star schema + dashboard data
build_page.py            # inject data.json + kreis_geo.json into the dashboard template
data/
  Unfallorte{2016..2024}_EPSG25832_CSV.zip   # raw yearly files (local only, not committed)
  sample/Unfallorte2024_sample.csv          # 1,000-row sample of the 2024 file
dashboard/
  index.html             # interactive web dashboard (open in any browser)
  template.html          # dashboard source template
  data.json              # pre-aggregated dashboard data (built by prep.py)
  kreis_geo.json         # simplified district boundaries (GADM 4.1)
  README.md              # dashboard + Power BI build guide
  powerbi/
    data/                # star schema CSVs — 116,055 fact rows, 6 facts, 8 dimensions
    DAX_measures.md      # all measures, copy-paste ready
    QUESTIONS.md         # 16 business questions, each a different visual type
    layout_spec.md       # page-by-page layout
    model_diagram.md     # star-schema diagram + table dictionary
```

## Reproduce it

1. Download the nine yearly `Unfallorte{2016..2024}_EPSG25832_CSV.zip` files
   from the Unfallatlas portal into `data/` (the raw files are ~96 MB and
   are not committed; the portal link is above).
2. Run `prep.py` (Python + pandas): it verifies the per-year counts and
   100% coordinate validity, asserts the 2,098,019 total, and writes
   `dashboard/powerbi/data/*.csv` and `dashboard/data.json`.
3. Run `build_page.py` to rebuild `dashboard/index.html` from
   `template.html` + `data.json` + `kreis_geo.json`.
4. On a Windows PC with Power BI Desktop: load the CSVs, set the
   relationships in `dashboard/powerbi/model_diagram.md`, paste the DAX
   from `DAX_measures.md`, and place the visuals per `layout_spec.md`.

## Definitions & quirks, honestly stated

- Severity = the accident's official category (worst injury in the
  accident). The atlas has no per-accident casualty counts, so this project
  counts accidents by severity — never invented person counts.
- Hamburg and Berlin are coded below district level in the police data
  (districts / boroughs); they are rolled up to the city districts
  02000 / 11000.
- Goods vehicles were recorded under "other vehicle" in 2016–2017 (official
  metadata); the goods-vehicle series starts in 2018. The 2017 file has no
  goods-vehicle column at all.
- Population for per-100k rates: Destatis Gemeindeverzeichnis extract,
  population at 31 Dec 2024, aggregated from municipalities to districts
  (Germany total 83,577,140, matching the official figure).
- District boundaries: GADM 4.1, simplified for the web (Douglas-Peucker,
  ~0.4 km tolerance). Göttingen is drawn merged with Osterode (2016 reform)
  and Eisenach inside Wartburgkreis (2021 reform) to match the population
  register; the star schema keeps Eisenach's historical code.

## Dashboard

The interactive web edition is in `dashboard/` — slicers for year, severity
and road user; a choropleth black-spot map; a weekday × hour heatmap; a
severity funnel and waffle; a treemap; slope and COVID-dip charts. The live
version is published at
https://rashedrana.github.io/germany-accident-blackspots/dashboard/
