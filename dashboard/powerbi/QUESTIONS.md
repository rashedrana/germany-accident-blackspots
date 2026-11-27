# Business Questions & Chart Problem-Solving
## Germany's Accident Black Spots — 16 questions, 16 visual types

Dataset: **Unfallatlas** (Statistische Ämter des Bundes und der Länder, via
unfallatlas.statistikportal.de, licence dl-de/by-2-0) — police-recorded road
accidents **with personal injury**, one record per accident, geocoded:
**2,098,019 records, 2016–2024** (2016: 151,673 · 2017: 195,229 · 2018: 211,868 ·
2019: 268,370 · 2020: 237,994 · 2021: 238,826 · 2022: 256,492 · 2023: 269,048 ·
2024: 268,519). Every answer below was computed from the project data in `data/`.

**Coverage, stated openly:** geocoding rolled out Land by Land — 2016 covers
8 Länder, 2017 → 12, 2018 → 13, 2019 → 15, and only from **2020 all 16**. Every
published record has valid coordinates; pre-2020 totals are *not* Germany totals.
**Severity** is the official accident category (UKATEGORIE): each accident is
classified by its worst injury. The atlas publishes no per-accident person
counts, so all figures count *accidents*, never invented casualties.

---

**Q1. How big is the problem, at a glance?**
Visual: **KPI cards** (Accidents, Fatal, Serious-injury, Slight-injury,
Bicycle-involved share, Darkness share).
Answer (2016–2024, covered Länder): **2,098,019 injury accidents** — **20,603
fatal (1.0%)**, **376,786 with serious injuries (18.0%)**, **1,700,630 with
slight injuries only (81.1%)**. Bicycles were involved in **29.9%**, and
**18.9%** of accidents happened in darkness.

**Q2. Are accidents rising?**
Visual: **Line chart** (accidents per year, severity / road-user slicers).
Answer: raw totals climb from 151,673 (2016) to 268,370 (2019) — but that is
mostly *coverage* growth (8 → 15 Länder). In the like-for-like full-coverage
era, accidents rose from **237,994 (2020) to 268,519 (2024), +12.8%**, back
above the pre-COVID level. Fatal accidents in 2024: **2,458**.

**Q3. Where are the black spots — per inhabitant, not just per map?**
Visual: **Choropleth map** (districts, avg accidents per year per 100,000
inhabitants, pooled 2020–2024; population: Destatis Gemeindeverzeichnis,
31 Dec 2024).
Answer: the highest rates are small city districts with heavy through-traffic:
**Memmingen 511.0**, **Rosenheim (city) 485.6**, **Lübeck 479.0** per 100k per
year. The lowest (districts with ≥500 pooled accidents): **Ilm-Kreis 178.9**,
Tuttlingen 193.5, Wolfsburg 199.6. The national average is ≈304 per 100k/year.

**Q4. When during the week does it crash?**
Visual: **Matrix heatmap** (weekday × hour).
Answer: the single busiest cell of the week is **Tuesday 16:00 — 31,826
accidents**. **Friday is the busiest day (341,372)**, Sunday the quietest
(198,727). The weekday afternoon rush (15:00–18:00) dwarfs every other block;
weekend nights form a second, smaller ridge.

**Q5. How many accidents turn deadly?**
Visual: **Funnel chart** (all → serious-or-fatal → fatal).
Answer: of 2,098,019 accidents, **397,389 (18.9%)** involved a serious or fatal
injury, and **20,603 (1.0%)** were fatal. Roughly 1 in 101 injury accidents
kills at least one person; 1 in 19 of the serious-or-fatal group is fatal.

**Q6. What does the severity split look like per 100 accidents?**
Visual: **Waffle chart** (10 × 10).
Answer: **81 slight · 18 serious · 1 fatal** per 100 injury accidents
(81.1% / 18.0% / 1.0% before rounding).

**Q7. How do accidents come about?**
Visual: **Treemap** (accident type UTYP1).
Answer: **longitudinal-traffic accidents lead with 523,985 (25.0%)**, then
turning-into/crossing 463,280 (22.1%), driving accidents (loss of control)
409,145 (19.5%), turning off the road 283,438 (13.5%), other 260,484 (12.4%),
pedestrian crossing 90,434 (4.3%) and stationary traffic 67,253 (3.2%).

**Q8. What is the most common collision pattern?**
Visual: **Horizontal bar chart** (collision kind UART, top 8).
Answer: **collision with a vehicle turning into or crossing the road —
569,915 (27.2%)**, ahead of collision with a vehicle ahead/waiting 358,639
(17.1%), "other kind" 314,724 (15.0%), leaving the carriageway to the right
173,757 (8.3%) and collision with an oncoming vehicle 154,319 (7.4%).
Vehicle–pedestrian collisions: 163,082 (7.8%).

**Q9. Who is involved — and who is most at risk when it happens?**
Visual: **Bar chart** (road-user involvement, multi-counted by design).
Answer: passenger cars are involved in **77.3%** of injury accidents, bicycles
in **29.9%**, motorcycles 13.8%, pedestrians 8.8%, goods vehicles 4.3%
(recorded separately only from 2018). But severity flips the ranking:
**pedestrian-involved accidents are fatal in 1.56%** of cases — the highest of
any group — vs 0.91% for car-involved and 0.50% for bicycle-involved.

**Q10. Does darkness kill?**
Visual: **Donut chart** (light conditions).
Answer: 75.7% of accidents happen in daylight, 5.4% at twilight, **18.9% in
darkness** — yet **26.3% of all fatal accidents** happen in darkness. The fatal
rate in darkness is **1.36%**, vs 0.98% at twilight and 0.89% in daylight.

**Q11. Are wet roads deadlier?**
Visual: **Stacked column / bar chart** (road surface).
Answer: **74.2%** of injury accidents happen on dry roads, 23.6% on wet/damp,
2.2% on winter-slippery. Per accident, wet is *not* deadlier: fatal rate
**0.99% wet vs 0.99% dry** (winter-slippery 0.72%). Exposure, not surface,
drives the totals.

**Q12. Which Länder improved, which worsened — 2019 → 2024?**
Visual: **Slope chart** (Land totals, 15 Länder covered in both years).
Answer: the biggest drops: **Saarland −11.6%**, **Bremen −11.3%**, Berlin
−7.2%, Rheinland-Pfalz −7.1%. The risers: **Schleswig-Holstein +4.0%**,
Thüringen +3.2%, Hamburg +3.0%, Nordrhein-Westfalen +2.8% (NW joined the atlas
in 2019, so its 2019 base is its first covered year).

**Q13. What did COVID-19 do to accidents?**
Visual: **Multi-line chart** (monthly, 2019 vs 2020 vs 2021).
Answer: the first lockdown cut accidents hard: **April 2020: 15,603 vs 21,741
in April 2019 (−28.2%)**; March 2020 −24.7%. The full year 2020 ended
**−11.3%** below 2019 (237,994 vs 268,370; 2019 lacks Mecklenburg-Vorpommern,
≈2% of accidents, so the true dip is a touch smaller), and 2021 stayed low
(238,826) before the 2022 rebound.

**Q14. Which districts record the most accidents in absolute terms?**
Visual: **Table** (district ranking, pooled 2020–2024).
Answer: **Berlin 60,224**, Hamburg 34,030, München (city) 23,993, Region
Hannover 22,283, Köln 21,636. Berlin alone recorded nearly three times the
accidents of the entire Land Mecklenburg-Vorpommern (22,509) in the same five
years — city scale dominates raw counts, which is why Q3 ranks by rate.

**Q15. How dangerous is the night, hour by hour?**
Visual: **Area chart** (accidents by hour of day).
Answer: the day peaks at **16:00 (186,783 accidents, 8.9% of all)** and
17:00 (180,347). Only **8.0%** of accidents occur 22:00–06:00, but their fatal
rate is **1.85% — twice the daytime rate (0.91%)**.

**Q16. Which road users are seasonal?**
Visual: **Column chart** (motorcycle-involved accidents by month).
Answer: motorcycling is the most seasonal pattern in the data: **51.8%** of
the 290,104 motorcycle-involved accidents fall in **June–September**, against
just 2.2% in January. Bicycle-involved accidents peak in June (80,319 pooled
across 2016–2024) and fall to barely a third of that by December (29,164).

---

*Method notes.* Hamburg and Berlin are coded below district level in the
police data and are rolled up to the city district. Goods vehicles were
recorded under "other" in 2016–2017 (official metadata), so that series starts
in 2018. District boundaries on the map: GADM 4.1, simplified; Göttingen is
shown merged with Osterode (2016 reform) and Eisenach inside Wartburgkreis
(2021 reform) to match the population register.
