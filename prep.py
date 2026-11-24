#!/usr/bin/env python
"""Prep for Germany's Accident Black Spots (Destatis Unfallatlas 2016-2024).

Loads the raw yearly Unfallatlas CSV/TXT files, verifies counts & coverage,
builds the star schema (powerbi/data/) and the pre-aggregated data.json that
drives the web dashboard. Run with the project venv (pandas).
"""
import glob, json, re
import pandas as pd
import numpy as np

BASE = '/home/hatch/workspace/germany-accident-blackspots'
RAW = f'{BASE}/data'
OUT_DATA = f'{BASE}/dashboard/powerbi/data'
OUT_JSON = f'{BASE}/dashboard/data.json'

LAND = {'01':'Schleswig-Holstein','02':'Hamburg','03':'Niedersachsen','04':'Bremen',
        '05':'Nordrhein-Westfalen','06':'Hessen','07':'Rheinland-Pfalz','08':'Baden-Württemberg',
        '09':'Bayern','10':'Saarland','11':'Berlin','12':'Brandenburg','13':'Mecklenburg-Vorpommern',
        '14':'Sachsen','15':'Sachsen-Anhalt','16':'Thüringen'}
SEV = {1:'Fatal',2:'Serious injury',3:'Slight injury'}
UART = {0:'Other kind',1:'Collision with starting/stopping vehicle',2:'Collision with vehicle ahead/waiting',
        3:'Collision with vehicle alongside (same direction)',4:'Collision with oncoming vehicle',
        5:'Collision with turning/crossing vehicle',6:'Collision between vehicle and pedestrian',
        7:'Impact with obstacle on carriageway',8:'Left carriageway to the right',9:'Left carriageway to the left'}
UTYP = {1:'Driving accident',2:'Turning off the road',3:'Turning into / crossing a road',
        4:'Crossing the road (pedestrian)',5:'Stationary traffic',6:'Vehicles in longitudinal traffic',
        7:'Other accident'}
ROADUSER = {'IstRad':'Bicycle','IstPKW':'Passenger car','IstFuss':'Pedestrian','IstKrad':'Motorcycle',
            'IstGkfz':'Goods vehicle','IstSonstige':'Other vehicle'}
LIGHT = {0:'Daylight',1:'Twilight',2:'Darkness'}
SURFACE = {0:'Dry',1:'Wet / damp',2:'Winter-slippery'}

# ---------------------------------------------------------------- load raw
import io, zipfile
zips = sorted(glob.glob(f'{RAW}/Unfallorte*_EPSG25832_CSV.zip'))
assert len(zips) == 9, zips
frames, verify = [], []
for z in zips:
    zf = zipfile.ZipFile(z)
    member = [n for n in zf.namelist() if 'LinRef' in n and n.endswith(('.csv', '.txt'))][0]
    df = pd.read_csv(io.BytesIO(zf.read(member)), sep=';', dtype=str, encoding='utf-8-sig', low_memory=False)
    df = df.rename(columns={'IstStrasse': 'IstStrassenzustand', 'STRZUSTAND': 'IstStrassenzustand',
                            'IstSonstig': 'IstSonstige', 'LICHT': 'ULICHTVERH'})
    if 'IstGkfz' not in df.columns: df['IstGkfz'] = '0'  # 2017: goods vehicles counted under "other"
    df['ULAND'] = df['ULAND'].str.zfill(2)
    df['UREGBEZ'] = df['UREGBEZ'].str.zfill(1)
    df['UKREIS'] = df['UKREIS'].str.zfill(2)
    for c in ['UJAHR','UMONAT','USTUNDE','UWOCHENTAG','UKATEGORIE','UART','UTYP1','ULICHTVERH',
              'IstStrassenzustand','IstRad','IstPKW','IstFuss','IstKrad','IstGkfz','IstSonstige']:
        df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')
    x = pd.to_numeric(df['XGCSWGS84'].str.replace(',', '.', regex=False), errors='coerce')
    y = pd.to_numeric(df['YGCSWGS84'].str.replace(',', '.', regex=False), errors='coerce')
    valid = ((x > 5) & (x < 16) & (y > 47) & (y < 56))
    yr = int(df['UJAHR'].iloc[0])
    verify.append({'year': yr, 'rows': int(len(df)), 'laender': int(df['ULAND'].nunique()),
                   'coord_valid_pct': round(float(valid.mean() * 100), 2)})
    df['AGS'] = df['ULAND'] + df['UREGBEZ'] + df['UKREIS']
    # City-states are coded below Kreis level in the police data (Hamburg
    # districts, Berlin boroughs) -> roll up to the Kreis-level AGS.
    df.loc[df['ULAND'] == '02', 'AGS'] = '02000'
    df.loc[df['ULAND'] == '11', 'AGS'] = '11000'
    df['coord_valid'] = valid
    frames.append(df[['AGS','ULAND','UJAHR','UMONAT','USTUNDE','UWOCHENTAG','UKATEGORIE','UART',
                      'UTYP1','ULICHTVERH','IstStrassenzustand','IstRad','IstPKW','IstFuss',
                      'IstKrad','IstGkfz','IstSonstige','coord_valid']])
all_df = pd.concat(frames, ignore_index=True)
total = len(all_df)
print('Per-year verification:')
for v in verify: print(' ', v)
print('TOTAL records:', total)
assert total == 2098019, total

# ---------------------------------------------------------------- population (Destatis Gemeindeverzeichnis, 31.12.2024)
import openpyxl
wb = openpyxl.load_workbook('/tmp/gv.xlsx', read_only=True, data_only=True)
ws = wb['Onlineprodukt_Gemeinden30062026']
pop_rows = []
for r in ws.iter_rows(min_row=6, values_only=True):
    # cols: 0 Satzart, 2 Land, 3 RB, 4 Kreis, 5 VB, 6 Gem, 9 pop total
    if r[6] not in (None, '') and r[9] not in (None, ''):
        try: pop = int(r[9])
        except (TypeError, ValueError): continue
        ags = f"{int(r[2]):02d}{int(r[3]):01d}{int(r[4]):02d}"
        pop_rows.append((ags, pop))
pop = pd.DataFrame(pop_rows, columns=['AGS','Population']).groupby('AGS', as_index=False).sum()
print('Kreise with population:', len(pop), 'total pop:', int(pop['Population'].sum()))
assert 82_000_000 < pop['Population'].sum() < 85_000_000

# Kreis names from GADM geometry properties
geo_raw = json.load(open('/tmp/gadm_deu2.geojson'))
name_by_ags = {}
for ft in geo_raw['features']:
    p = ft['properties']
    cc = p.get('CC_2')
    if cc and cc != 'NA':
        name_by_ags[cc] = re.sub(r'\(.*?\)', '', p['NAME_2']).strip()
name_by_ags['03159'] = 'Göttingen'  # GADM still carries the pre-2016 split (03152+03156)
kreise_in_data = sorted(all_df['AGS'].unique())
matched = [a for a in kreise_in_data if a in name_by_ags]
print(f'Kreise in accident data: {len(kreise_in_data)}, with GADM name/geometry: {len(matched)}')

# ---------------------------------------------------------------- star schema
fact1 = (all_df.groupby(['AGS','UJAHR','UKATEGORIE','UTYP1']).size().reset_index(name='AccidentCount'))
fact1.columns = ['KreisAGS','Year','SeverityCode','AccidentTypeCode','AccidentCount']
fact1.to_csv(f'{OUT_DATA}/FactKreisYear.csv', index=False)

inv = []
for col, label in ROADUSER.items():
    g = all_df[all_df[col] == 1].groupby(['AGS','UJAHR','UKATEGORIE']).size().reset_index(name='AccidentCount')
    g['RoadUser'] = label
    inv.append(g)
fact2 = pd.concat(inv, ignore_index=True)
fact2.columns = ['KreisAGS','Year','SeverityCode','AccidentCount','RoadUser']
fact2 = fact2[['KreisAGS','Year','RoadUser','SeverityCode','AccidentCount']]
fact2.to_csv(f'{OUT_DATA}/FactInvolvement.csv', index=False)

fact3 = (all_df.groupby(['ULAND','UJAHR','UMONAT','UKATEGORIE']).size().reset_index(name='AccidentCount'))
fact3.columns = ['LandCode','Year','Month','SeverityCode','AccidentCount']
fact3.to_csv(f'{OUT_DATA}/FactMonthlyLand.csv', index=False)

# When: weekday x hour pattern (weekday kept in source coding 1=Sun..7=Sat, documented)
fact4 = (all_df.groupby(['UJAHR','UWOCHENTAG','USTUNDE','UKATEGORIE']).size().reset_index(name='AccidentCount'))
fact4.columns = ['Year','WeekdayCode','Hour','SeverityCode','AccidentCount']
fact4.to_csv(f'{OUT_DATA}/FactTimePattern.csv', index=False)

# Conditions: light x road surface
fact5 = (all_df.groupby(['UJAHR','ULICHTVERH','IstStrassenzustand','UKATEGORIE']).size().reset_index(name='AccidentCount'))
fact5.columns = ['Year','LightCode','SurfaceCode','SeverityCode','AccidentCount']
fact5.to_csv(f'{OUT_DATA}/FactConditions.csv', index=False)

# Road-user seasonality (national, monthly)
inv_m = []
for col, label in ROADUSER.items():
    g = all_df[all_df[col] == 1].groupby(['UJAHR','UMONAT','UKATEGORIE']).size().reset_index(name='AccidentCount')
    g['RoadUser'] = label
    inv_m.append(g)
fact6 = pd.concat(inv_m, ignore_index=True)
fact6.columns = ['Year','Month','SeverityCode','AccidentCount','RoadUser']
fact6 = fact6[['Year','Month','RoadUser','SeverityCode','AccidentCount']]
fact6.to_csv(f'{OUT_DATA}/FactInvolvementMonthly.csv', index=False)

pd.DataFrame({'LightCode': list(LIGHT), 'Light': list(LIGHT.values())}).to_csv(f'{OUT_DATA}/DimLight.csv', index=False)
pd.DataFrame({'SurfaceCode': list(SURFACE), 'Surface': list(SURFACE.values())}).to_csv(f'{OUT_DATA}/DimSurface.csv', index=False)
pd.DataFrame({'WeekdayCode': [1,2,3,4,5,6,7], 'Weekday': ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']}).to_csv(f'{OUT_DATA}/DimWeekday.csv', index=False)

dim_kreis = pd.DataFrame({'KreisAGS': kreise_in_data})
dim_kreis['KreisName'] = dim_kreis['KreisAGS'].map(name_by_ags)
dim_kreis['LandCode'] = dim_kreis['KreisAGS'].str[:2]
dim_kreis['LandName'] = dim_kreis['LandCode'].map(LAND)
dim_kreis = dim_kreis.merge(pop, left_on='KreisAGS', right_on='AGS', how='left').drop(columns=['AGS']).rename(columns={'Population':'Population2024'})
dim_kreis.to_csv(f'{OUT_DATA}/DimKreis.csv', index=False)

pd.DataFrame({'LandCode': list(LAND), 'LandName': list(LAND.values())}).to_csv(f'{OUT_DATA}/DimLand.csv', index=False)
pd.DataFrame({'SeverityCode': list(SEV), 'Severity': list(SEV.values())}).to_csv(f'{OUT_DATA}/DimSeverity.csv', index=False)
pd.DataFrame({'AccidentTypeCode': list(UTYP), 'AccidentType': list(UTYP.values())}).to_csv(f'{OUT_DATA}/DimAccidentType.csv', index=False)
months = pd.DataFrame([(y, m) for y in range(2016, 2025) for m in range(1, 13)], columns=['Year','Month'])
months['YearMonth'] = months['Year'].astype(str) + '-' + months['Month'].astype(str).str.zfill(2)
months.to_csv(f'{OUT_DATA}/DimDate.csv', index=False)
print('Star schema rows:', {'FactKreisYear': len(fact1), 'FactInvolvement': len(fact2),
                           'FactMonthlyLand': len(fact3), 'FactTimePattern': len(fact4),
                           'FactConditions': len(fact5), 'FactInvolvementMonthly': len(fact6),
                           'DimKreis': len(dim_kreis)})

# ---------------------------------------------------------------- data.json aggregates
def agg_block(df):
    """Aggregates for one filter cell."""
    n = len(df)
    if n == 0: return None
    by_sev = df['UKATEGORIE'].value_counts()
    heat = np.zeros((7, 24), dtype=int)  # rows Mon..Sun
    wd_map = {2:0, 3:1, 4:2, 5:3, 6:4, 7:5, 1:6}
    for (wd, hr), c in df.groupby(['UWOCHENTAG','USTUNDE']).size().items():
        if pd.notna(wd) and pd.notna(hr): heat[wd_map[int(wd)], int(hr)] = c
    return {
        'n': int(n),
        'fatal': int(by_sev.get(1, 0)), 'serious': int(by_sev.get(2, 0)), 'slight': int(by_sev.get(3, 0)),
        'bikeShare': round(float((df['IstRad'] == 1).mean() * 100), 1),
        'darkShare': round(float((df['ULICHTVERH'] == 2).mean() * 100), 1),
        'monthly': [int(x) for x in df.groupby('UMONAT').size().reindex(range(1, 13), fill_value=0)],
        'heat': heat.flatten().tolist(),
        'uart': [int(df['UART'].eq(i).sum()) for i in range(10)],
        'utyp': [int(df['UTYP1'].eq(i).sum()) for i in range(1, 8)],
        'land': [int(df['ULAND'].eq(f'{i:02d}').sum()) for i in range(1, 17)],
        'light': [int(df['ULICHTVERH'].eq(i).sum()) for i in range(3)],
        'surface': [int(df['IstStrassenzustand'].eq(i).sum()) for i in range(3)],
        'hour': [int(df['USTUNDE'].eq(i).sum()) for i in range(24)],
        'involv': {label: int((df[col] == 1).sum()) for col, label in ROADUSER.items()},
    }

cells = {}
years = ['ALL'] + [str(y) for y in range(2016, 2025)]
sevs = ['ALL', '1', '2', '3']
rus = ['ALL'] + list(ROADUSER)
for y in years:
    dy = all_df if y == 'ALL' else all_df[all_df['UJAHR'] == int(y)]
    for s in sevs:
        ds = dy if s == 'ALL' else dy[dy['UKATEGORIE'] == int(s)]
        for ru in rus:
            d = ds if ru == 'ALL' else ds[ds[ru] == 1]
            b = agg_block(d)
            if b: cells[f'{y}|{s}|{ru}'] = b
print('filter cells:', len(cells))

# trend: monthly totals per year (for metric-switch trend, ALL severity/roaduser)
trend = {}
for y in range(2016, 2025):
    dy = all_df[all_df['UJAHR'] == y]
    trend[str(y)] = {
        'monthly': [int(x) for x in dy.groupby('UMONAT').size().reindex(range(1, 13), fill_value=0)],
        'fatalMonthly': [int(x) for x in dy[dy['UKATEGORIE'] == 1].groupby('UMONAT').size().reindex(range(1, 13), fill_value=0)],
    }

# choropleth: pooled 2020-2024 (full-coverage era) per Kreis.
# Eisenach (16056) joined Wartburgkreis (16063) in Jul 2021 -> map on current boundaries.
pool = all_df[all_df['UJAHR'] >= 2020].copy()
pool['AGS'] = pool['AGS'].replace({'16056': '16063'})
kmap = pool.groupby('AGS').size().rename('accidents')
kfatal = pool[pool['UKATEGORIE'] == 1].groupby('AGS').size().rename('fatal')
km = pd.concat([kmap, kfatal], axis=1).fillna(0).reset_index().merge(pop, on='AGS', how='left')
km['rate'] = (km['accidents'] / 5 / km['Population'] * 100000).round(1)  # avg per year, per 100k inhab.
km['name'] = km['AGS'].map(name_by_ags)
kreis_map = km[['AGS','name','accidents','fatal','Population','rate']].values.tolist()

# slope: Land totals 2019 vs 2024 (Länder present in both years; MV excluded - no 2019 data)
slope = []
for code, nm in LAND.items():
    a = int((all_df[(all_df['ULAND'] == code) & (all_df['UJAHR'] == 2019)]).shape[0])
    b = int((all_df[(all_df['ULAND'] == code) & (all_df['UJAHR'] == 2024)]).shape[0])
    if a > 0: slope.append({'land': nm, 'y2019': a, 'y2024': b, 'chg': round((b - a) / a * 100, 1)})

# COVID: monthly national 2019 vs 2020 vs 2021 (index, Jan=100 within year-pair comparison uses raw)
covid = {str(y): [int(x) for x in all_df[all_df['UJAHR'] == y].groupby('UMONAT').size().reindex(range(1, 13), fill_value=0)]
         for y in (2019, 2020, 2021)}

# top/bottom Kreise by rate (pooled 2020-2024, min 500 accidents for stability)
km_big = km[km['accidents'] >= 500].sort_values('rate', ascending=False)
top_rate = km_big.head(10)[['AGS','name','rate','accidents']].values.tolist()
bot_rate = km_big.tail(10).iloc[::-1][['AGS','name','rate','accidents']].values.tolist()
top_count = km.sort_values('accidents', ascending=False).head(10)[['AGS','name','accidents','rate']].values.tolist()

data = {
    'meta': {'total': total, 'verify': verify,
             'years': list(range(2016, 2025)),
             'landNames': [LAND[f'{i:02d}'] for i in range(1, 17)],
             'uartLabels': [UART[i] for i in range(10)],
             'utypLabels': [UTYP[i] for i in range(1, 8)],
             'lightLabels': [LIGHT[i] for i in range(3)],
             'surfaceLabels': [SURFACE[i] for i in range(3)]},
    'cells': cells, 'trend': trend, 'kreisMap': kreis_map, 'slope': slope, 'covid': covid,
    'topRate': top_rate, 'botRate': bot_rate, 'topCount': top_count,
}
with open(OUT_JSON, 'w') as f: json.dump(data, f, separators=(',', ':'))
print('data.json written')

# ---------------------------------------------------------------- simplified Kreis geometry
def _dp(pts, tol):
    """Douglas-Peucker on a list of [x, y] points."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i0, i1 = stack.pop()
        ax, ay = pts[i0]; bx, by = pts[i1]
        dx, dy = bx - ax, by - ay
        denom = (dx * dx + dy * dy) ** 0.5 or 1e-12
        dmax, imax = 0.0, -1
        for i in range(i0 + 1, i1):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / denom
            if d > dmax: dmax, imax = d, i
        if dmax > tol and imax > 0:
            keep[imax] = True; stack.append((i0, imax)); stack.append((imax, i1))
    return [p for p, k in zip(pts, keep) if k]

def simp_ring(ring, tol=0.004):
    pts = [[float(x), float(y)] for x, y in ring]
    if len(pts) > 1 and pts[0] == pts[-1]: pts = pts[:-1]  # unclose
    if len(pts) < 4: return None
    # anchor = farthest point from start; DP both arcs, then re-close
    a = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    out = _dp(pts[:a + 1], tol) + _dp(pts[a:] + [pts[0]], tol)[1:]
    out = [[round(x, 3), round(y, 3)] for x, y in out]
    ded = [out[0]]
    for p in out[1:]:
        if p != ded[-1]: ded.append(p)
    if ded[-1] != ded[0]: ded.append(ded[0])
    return ded if len(ded) >= 4 else None

# merge pre-2016 Göttingen split into today's 03159; drop Eisenach (now part of 16063)
merged = {}
for ft in geo_raw['features']:
    cc = ft['properties'].get('CC_2')
    if cc in ('03152', '03156'): cc = '03159'
    if not cc or cc == 'NA' or cc == '16056': continue
    g = ft['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    merged.setdefault(cc, []).extend(polys)

feats = []
for cc, polys in merged.items():
    new_polys = []
    for poly in polys:
        new_poly = []
        for i, ring in enumerate(poly):
            r = simp_ring(ring)
            if r and (i == 0 or len(r) >= 4): new_poly.append(r)
        if new_poly: new_polys.append(new_poly)
    if not new_polys: continue
    geom = {'type': 'MultiPolygon', 'coordinates': new_polys}
    feats.append({'type': 'Feature', 'properties': {'ags': cc, 'name': name_by_ags.get(cc, cc)}, 'geometry': geom})
geo_out = {'type': 'FeatureCollection', 'features': feats}
with open(f'{BASE}/dashboard/kreis_geo.json', 'w') as f: json.dump(geo_out, f, separators=(',', ':'))
import os
print('geo features:', len(feats), 'size KB:', os.path.getsize(f'{BASE}/dashboard/kreis_geo.json') // 1024)
