# Layout Spec — Germany's Accident Black Spots (Power BI)

Modern end-to-end project style: slicer header, KPI row, bookmark metric
switching, drill-through district page, navigation buttons. Palette mirrors
the web edition: warm paper background `#f7f5f2`, ink `#221d1a`, signal red
`#b91c1c`, amber `#d97706`, slate `#475569`, severity scale
slight `#ead9d2` → serious `#e8a13a` → fatal `#b91c1c`.

## Global elements (every page)

- **Header band:** title left, page-navigation buttons right
  (Overview · Map · When · Patterns · Districts).
- **Slicer row:** Year (chiclet), Severity (chiclet), Road user (dropdown,
  from FactInvolvement), Land (dropdown). A persistent footnote strip:
  *"Coverage: 8 Länder in 2016 → all 16 from 2020. Pre-2020 totals are not
  Germany totals."*
- **Footer:** data source line — Unfallatlas, Statistische Ämter des Bundes
  und der Länder, dl-de/by-2-0.

## Page 1 — Overview

- KPI row (6 cards): Accidents · Fatal · Serious-injury · Slight-injury ·
  Bicycle Share % · Darkness Share %, each with a YoY delta visual.
- **Line chart:** accidents per year (bookmark buttons switch the measure to
  Fatal Accidents); the 2016–2019 segment carries the coverage footnote.
- **Funnel:** all → serious-or-fatal → fatal.
- **Waffle (custom visual):** severity split per 100 accidents.
- **Column chart:** accidents by month (June highlighted).

## Page 2 — Black-spot map

- **Filled map (choropleth):** districts coloured by
  [Accidents per 100k Inhabitants (per Year)], Year slicer preset to
  2020–2024; toggle bookmark switches to total accidents.
- **Table (right rail):** top 10 districts by rate and top 10 by count,
  with population shown.
- Drill-through target: District page (below).

## Page 3 — When it happens

- **Matrix heatmap:** weekday (Mon-first) × hour from FactTimePattern.
- **Area chart:** accidents by hour of day; annotation callouts for the
  16:00 peak and the 22:00–06:00 fatal-rate doubling.
- **Multi-line chart:** monthly accidents 2019 / 2020 / 2021 (COVID dip),
  April 2020 −28.2% callout.

## Page 4 — Patterns

- **Treemap:** accident type (UTYP1).
- **Bar chart:** collision kind (UART) top 8.
- **Bar chart:** road-user involvement with fatal-rate data labels
  (pedestrian 1.56% callout).
- **Donut:** light conditions. **Stacked column:** road surface × severity.
- **Slope chart:** Land totals 2019 → 2024 (custom visual or line chart
  with two year points per Land).

## Page 5 — District drill-through

- Drill-through on KreisAGS: district KPI cards (accidents, rate per 100k,
  fatal share, population), yearly trend line, involvement bars, and the
  district's rank by rate — the "black spot profile" a road-safety officer
  would ask for.

## Build order

1. Load the 14 CSVs from `powerbi/data/`, set relationships per
   `model_diagram.md`.
2. Paste measures from `DAX_measures.md` into `_Measures`.
3. Build pages top-down; set the Year slicer default per page as noted.
4. Publish; the web edition (index.html) is the visual reference.
