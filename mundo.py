"""Baixa todos os imóveis da Mundo House (parceria) e gera mundo.json compacto, sem repetidos.
uso: python3 mundo.py saida.json"""
import re, json, sys, time, urllib.request, concurrent.futures as cf

BASE = "https://cdn.vistahost.com.br/mundohou/vista.imobi/fotos/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}


def baixar(n, tent=3):
    for t in range(tent):
        try:
            req = urllib.request.Request(f"https://mundohouse.com.br/busca?page={n}", headers=UA)
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2 + 3 * t)
    return ""


def extrair(h):
    partes = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', h)
    s = "".join(json.loads('"' + p + '"') for p in partes)
    achados = []
    for m in re.finditer(r'"properties":\[', s):
        try:
            arr, _ = json.JSONDecoder().raw_decode(s, m.end() - 1)
            if arr and isinstance(arr[0], dict) and "Codigo" in arr[0]:
                achados = arr if len(arr) > len(achados) else achados
        except Exception:
            pass
    return achados, s


def curto(u):
    return u[len(BASE):] if u and u.startswith(BASE) else u


def compactar(p):
    num = lambda k: float(p.get(k) or 0)
    venda = num("ValorVendaPromocional") or num("ValorVenda")
    aluguel = num("ValorLocacaoPromocional") or num("ValorLocacao")
    area = num("AreaPrivativa") or num("AreaTotal")
    fotos = [curto(f) for f in (p.get("Vitrine") or []) if f] or ([curto(p["FotoDestaque"])] if p.get("FotoDestaque") else [])
    o = {"c": str(p.get("Codigo")), "t": p.get("Categoria") or "Imóvel", "v": round(venda), "l": round(aluguel),
         "d": int(p.get("Dormitorios") or 0), "s": int(p.get("Suites") or 0), "g": int(p.get("Vagas") or 0),
         "b": int(p.get("TotalBanheiros") or 0), "a": round(area, 2) if area % 1 else int(area),
         "br": (p.get("BairroComercial") or p.get("Bairro") or "").strip(), "ci": (p.get("Cidade") or "").strip(),
         "e": (p.get("Empreendimento") or "").strip(), "f": fotos[:12], "dt": (p.get("DataAtualizacao") or p.get("DataCadastro") or "")[:10]}
    return {k: v for k, v in o.items() if v not in ("", 0, None, [])} | {"c": o["c"], "t": o["t"]}


def main(saida):
    h1 = baixar(1)
    m = re.search(r"de\s*(?:<!-- -->)?\s*([\d.]+)", re.sub(r"<[^>]+>", " ", h1))
    _, s = extrair(h1)
    total = int(re.search(r'"total(?:Count|Properties|Items)?":\s*(\d+)', s).group(1)) if re.search(r'"total(?:Count|Properties|Items)?":\s*(\d+)', s) else None
    print("total no site:", total, "| texto:", m.group(1) if m else "?")
    paginas = (total // 12 + 2) if total else 260
    todos = {}
    with cf.ThreadPoolExecutor(6) as ex:
        for n, h in zip(range(1, paginas + 1), ex.map(baixar, range(1, paginas + 1))):
            arr, _ = extrair(h)
            for p in arr:
                todos[str(p.get("Codigo"))] = p
            if n % 25 == 0:
                print("página", n, "->", len(todos), "imóveis", flush=True)
    print("baixados:", len(todos))
    lista, vistos, rep = [], set(), 0
    for p in sorted(todos.values(), key=lambda x: (x.get("DataAtualizacao") or ""), reverse=True):
        o = compactar(p)
        if not (o.get("v") or o.get("l")):
            continue
        chave = (o["t"], slug(o.get("br", "")), o.get("a"), o.get("d"), o.get("v"), o.get("l"), slug(o.get("e", "")))
        foto = o["f"][0].split("/")[-1] if o.get("f") else None
        if chave in vistos or (foto and foto in vistos):
            rep += 1
            continue
        vistos.add(chave)
        if foto:
            vistos.add(foto)
        lista.append(o)
    json.dump(lista, open(saida, "w"), ensure_ascii=False, separators=(",", ":"))
    print("salvos:", len(lista), "| repetidos removidos:", rep)


def slug(t):
    import unicodedata
    t = unicodedata.normalize("NFD", t or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "mundo.json")
