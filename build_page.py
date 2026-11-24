#!/usr/bin/env python
"""Inject data.json + kreis_geo.json into template.html -> index.html."""
import pathlib
base = pathlib.Path('/home/hatch/workspace/germany-accident-blackspots/dashboard')
tpl = (base / 'template.html').read_text()
data = (base / 'data.json').read_text()
geo = (base / 'kreis_geo.json').read_text()
assert '/*__DATA__*/{}' in tpl and '/*__GEO__*/{}' in tpl
out = tpl.replace('/*__DATA__*/{}', data).replace('/*__GEO__*/{}', geo)
(base / 'index.html').write_text(out)
print('index.html bytes:', len(out))
