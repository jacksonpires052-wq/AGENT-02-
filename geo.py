# Geocodifica bairro+cidade dos imoveis da Mundo House (Nominatim, 1 req/s). Saida: geo.json
import json, time, unicodedata, urllib.request, urllib.parse, os, sys
def slug(s): return unicodedata.normalize('NFD', s or '').encode('ascii','ignore').decode().lower().strip()
src = sys.argv[1] if len(sys.argv)>1 else os.path.expanduser('~/mundo.json')
out = os.path.expanduser('~/geo.json')
dados = json.load(open(src))
geo = json.load(open(out)) if os.path.exists(out) else {}
def busca(q):
    u = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({'q':q,'format':'json','limit':1,'countrycodes':'br'})
    r = urllib.request.Request(u, headers={'User-Agent':'jacksonpires-site/1.0 (jacksonpires.web.app)'})
    for t in range(3):
        try:
            j = json.load(urllib.request.urlopen(r, timeout=20)); time.sleep(1.1)
            return [round(float(j[0]['lat']),5), round(float(j[0]['lon']),5)] if j else None
        except Exception as e: time.sleep(3)
    return None
cidades = sorted({i.get('ci') or '' for i in dados if i.get('ci')})
for c in cidades:
    k = '|' + slug(c)
    if k not in geo: geo[k] = busca(f'{c}, São Paulo, Brasil')
pares = sorted({(i.get('br') or '', i.get('ci') or '') for i in dados if i.get('br')})
print('bairros:', len(pares), flush=True)
for n,(b,c) in enumerate(pares):
    k = slug(b) + '|' + slug(c)
    if k in geo: continue
    geo[k] = busca(f'{b}, {c}, São Paulo, Brasil')
    if n % 25 == 0:
        json.dump(geo, open(out,'w')); print(n, flush=True)
json.dump(geo, open(out,'w'), separators=(',',':'))
print('FIM_GEO', len(geo), 'achados', sum(1 for v in geo.values() if v))
