# Data Model — Germany's Accident Black Spots

Star schema built from the 2,098,019 Unfallatlas microdata records
(2016–2024). The microdata itself is **not** shipped: every fact below is a
pre-aggregated count of accidents (`AccidentCount`), so the six facts sum —
where the grain allows — back to exactly 2,098,019.

```
                        DimKreis (401)
                       /   |        \
DimLand (16) — FactKreisYear (54,572) — DimSeverity (3)
                       \   |        /
                        DimAccidentType (7)        DimDate (108 year-months)
                                |
FactInvolvement (50,290) — Kreis × Year × RoadUser × Severity
FactInvolvementMonthly (1,908) — Year × Month × RoadUser × Severity
FactMonthlyLand (4,517) — Land × Year × Month × Severity
FactTimePattern (4,525) — Year × Weekday × Hour × Severity  + DimWeekday (7)
FactConditions (243) — Year × Light × Surface × Severity    + DimLight (3), DimSurface (3)
```

## Facts

| Fact | Grain | Rows | Sums to |
|---|---|---|---|
| FactKreisYear | Kreis × Year × Severity × AccidentType (UTYP1) | 54,572 | 2,098,019 |
| FactInvolvement | Kreis × Year × RoadUser × Severity | 50,290 | 3,055,312 involvements* |
| FactMonthlyLand | Land × Year × Month × Severity | 4,517 | 2,098,019 |
| FactTimePattern | Year × Weekday × Hour × Severity | 4,525 | 2,098,019 |
| FactConditions | Year × Light × Surface × Severity | 243 | 2,098,019 |
| FactInvolvementMonthly | Year × Month × RoadUser × Severity | 1,908 | 3,055,312 involvements* |

\* Involvement facts are multi-counted by design: one accident involving a car
and a bicycle contributes one row to each road-user group. Never sum them
against accident totals — use the share measures in `DAX_measures.md`.

## Dimensions

- **DimKreis** — 401 districts: `KreisAGS` (5-digit official code), name,
  Land code/name, `Population2024` (Destatis Gemeindeverzeichnis, 31 Dec 2024,
  municipalities aggregated to districts). Hamburg and Berlin are rolled up
  from the sub-district coding of the police data to `02000` / `11000`.
  Eisenach keeps its historical code `16056` here (it joined Wartburgkreis in
  2021); the *map* merges it, the model keeps the record honest.
- **DimLand** — the 16 Länder.
- **DimSeverity** — 1 Fatal · 2 Serious injury · 3 Slight injury (worst injury
  in the accident, official UKATEGORIE).
- **DimAccidentType** — the 7 UTYP1 types (driving accident, turning off,
  turning into/crossing, pedestrian crossing, stationary traffic, longitudinal
  traffic, other).
- **DimDate** — Year × Month rows 2016–2024 with a `YearMonth` label.
- **DimLight** — Daylight / Twilight / Darkness. **DimSurface** — Dry /
  Wet-damp / Winter-slippery. **DimWeekday** — source coding 1 = Sunday …
  7 = Saturday.

## Relationships (all single-direction, dimension → fact)

- DimKreis[KreisAGS] → FactKreisYear, FactInvolvement
- DimLand[LandCode] → FactKreisYear (via DimKreis), FactMonthlyLand
- DimSeverity[SeverityCode] → every fact
- DimAccidentType[AccidentTypeCode] → FactKreisYear
- DimDate[Year] (+Month) → every fact
- DimLight / DimSurface → FactConditions; DimWeekday → FactTimePattern

## Why aggregated facts?

The dashboard's questions are all count questions over categorical cuts, so
aggregation loses nothing and keeps the PBIX small and instant. Analysts who
need the microdata (e.g. point maps) can rebuild from the raw yearly files in
`data/` with `prep.py` — the script documents every normalisation it applies
(column-name variants across years, the Hamburg/Berlin roll-up, the
2016–2017 goods-vehicle coding).
