# DAX Measures — Germany's Accident Black Spots (Power BI)

Model tables: `FactKreisYear`, `FactInvolvement`, `FactMonthlyLand`,
`FactTimePattern`, `FactConditions`, `FactInvolvementMonthly`, with dimensions
`DimKreis`, `DimLand`, `DimSeverity`, `DimAccidentType`, `DimDate`, `DimLight`,
`DimSurface`, `DimWeekday`.
Create a dedicated measure table (`_Measures`) in Power BI and paste these in
one by one. All measures respond to the Year, Land/Kreis, Severity and
Accident-Type slicers unless stated otherwise. The facts are **pre-aggregated**
from the 2,098,019 Unfallatlas microdata records, so every measure is a SUM of
`AccidentCount` — the model stays fast at any slicer combination.

---

## Core measures (FactKreisYear)

```dax
Accidents =
SUM ( FactKreisYear[AccidentCount] )
```

```dax
Fatal Accidents =
CALCULATE ( [Accidents], DimSeverity[Severity] = "Fatal" )
```

```dax
Serious-Injury Accidents =
CALCULATE ( [Accidents], DimSeverity[Severity] = "Serious injury" )
```

```dax
Slight-Injury Accidents =
CALCULATE ( [Accidents], DimSeverity[Severity] = "Slight injury" )
```

```dax
Fatal Share % =
DIVIDE ( [Fatal Accidents], [Accidents] ) * 100
```

```dax
Serious-or-Fatal Accidents =
[Fatal Accidents] + [Serious-Injury Accidents]
```

## Rates & geography (choropleth, rankings)

```dax
Accidents per 100k Inhabitants (per Year) =
VAR YearsInScope = COUNTROWS ( VALUES ( DimDate[Year] ) )
RETURN
    DIVIDE ( [Accidents], YearsInScope * SUM ( DimKreis[Population2024] ) ) * 100000
```

```dax
District Rank by Rate =
RANKX (
    ALL ( DimKreis[KreisAGS] ),
    [Accidents per 100k Inhabitants (per Year)],
    ,
    DESC,
    DENSE
)
```

```dax
Accidents YoY % =
VAR Prev =
    CALCULATE ( [Accidents], DimDate[Year] = MAX ( DimDate[Year] ) - 1 )
RETURN
    DIVIDE ( [Accidents] - Prev, Prev ) * 100
```

## Road-user involvement (FactInvolvement — multi-counted by design)

One accident can involve several road-user types, so involvement counts sum to
more than the accident total (3,055,312 involvements over 2,098,019 accidents).
Shares are therefore computed against `FactKreisYear` accidents, never against
the involvement total.

```dax
Bicycle-Involved Accidents =
CALCULATE (
    SUM ( FactInvolvement[AccidentCount] ),
    FactInvolvement[RoadUser] = "Bicycle"
)
```

```dax
Bicycle Share % =
DIVIDE ( [Bicycle-Involved Accidents], [Accidents] ) * 100
```

```dax
Involved Accidents (selected road user) =
SUM ( FactInvolvement[AccidentCount] )
```

```dax
Fatal Rate of Involvement % =
DIVIDE (
    CALCULATE (
        SUM ( FactInvolvement[AccidentCount] ),
        DimSeverity[Severity] = "Fatal"
    ),
    [Involved Accidents (selected road user)]
) * 100
```

## When & under what conditions (FactTimePattern / FactConditions)

```dax
Darkness Accidents =
CALCULATE (
    SUM ( FactConditions[AccidentCount] ),
    DimLight[Light] = "Darkness"
)
```

```dax
Darkness Share % =
DIVIDE ( [Darkness Accidents], SUM ( FactConditions[AccidentCount] ) ) * 100
```

```dax
Night Accidents (22-05) =
CALCULATE (
    SUM ( FactTimePattern[AccidentCount] ),
    FactTimePattern[Hour] >= 22 || FactTimePattern[Hour] <= 5
)
```

```dax
Peak Hour Accidents =
MAXX ( VALUES ( FactTimePattern[Hour] ), SUM ( FactTimePattern[AccidentCount] ) )
```

## Display helpers

```dax
Selected Year Label =
"Focus: " & SELECTEDVALUE ( DimDate[Year], "2016–2024 (coverage grows by year)" )
```

---

Notes
- KPI cards on Page 1 use: Accidents, Fatal Accidents, Serious-Injury
  Accidents, Slight-Injury Accidents, Bicycle Share %, Darkness Share % —
  each with `Accidents YoY %`-style deltas where a single year is selected.
- The choropleth uses [Accidents per 100k Inhabitants (per Year)]; pool
  2020–2024 in the Year slicer to reproduce the web edition (full-coverage era).
- Coverage warning for report readers: pre-2020 totals cover only the Länder
  that had joined the geocoded atlas (8 in 2016 → 15 in 2019). The layout spec
  puts this note on Page 1.
- `DimWeekday` keeps the source coding (1 = Sunday … 7 = Saturday); sort the
  heatmap axis by a Mon-first sort column if you reorder it.
