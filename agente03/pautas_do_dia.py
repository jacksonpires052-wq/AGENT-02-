#!/usr/bin/env python3
"""Pautas prontas do Agente 07 para a rodada dos stories (Agente 03).

Uso:
  python3 agente03/pautas_do_dia.py                 # lista as pautas livres das últimas 72 h
  python3 agente03/pautas_do_dia.py --rascunho DIR  # grava um noticia.json de rascunho por pauta em DIR
  python3 agente03/pautas_do_dia.py --marcar ID PASTA  # marca a pauta ID como usada pelo story PASTA

Só lê e escreve pautas/pautas.json. Não publica nada.
Os rascunhos ainda precisam da conferência de sempre (ano do dado, texto que não
afirma mais que a fonte, fonte = veículo onde foi lido).
"""
import datetime
import glob
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ = os.path.join(RAIZ, "pautas", "pautas.json")


def carregar():
    with open(ARQ, encoding="utf-8") as f:
        return json.load(f)


def links_usados():
    usados = set()
    for p in glob.glob(os.path.join(RAIZ, "stories", "*", "noticia.json")):
        try:
            with open(p, encoding="utf-8") as f:
                n = json.load(f)
            if n.get("link"):
                usados.add(n["link"].strip())
        except Exception:
            pass
    return usados


def data(p):
    try:
        return datetime.date.fromisoformat(str(p.get("data_noticia", ""))[:10])
    except ValueError:
        return None


def livres(hoje=None, dias=3):
    hoje = hoje or datetime.date.today()
    usados = links_usados()
    out = []
    for p in carregar():
        if p.get("usada") not in (False, None, ""):
            continue
        d = data(p)
        if d is None or (hoje - d).days > dias:
            continue
        if (p.get("link") or "").strip() in usados:
            continue
        out.append(p)
    out.sort(key=lambda p: (data(p), p.get("coletada_em", "")), reverse=True)
    return out


def rascunho(p):
    return {
        "slug": p["id"].split("-", 1)[-1][:30],
        "categoria": (p.get("categoria") or "").upper(),
        "numero": p.get("numero", ""),
        "numero_legenda": "",
        "titulo": p.get("titulo", ""),
        "texto": p.get("fato", ""),
        "fonte": p.get("fonte", ""),
        "link": p.get("link", ""),
        "pauta_id": p["id"],
    }


def marcar(pid, pasta):
    lista = carregar()
    achou = False
    for p in lista:
        if p.get("id") == pid:
            p["usada"] = pasta
            achou = True
    if not achou:
        sys.exit(f"pauta {pid} não encontrada")
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"pauta {pid} marcada como usada por {pasta}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--marcar"] and len(a) == 3:
        marcar(a[1], a[2])
    elif a[:1] == ["--rascunho"] and len(a) == 2:
        os.makedirs(a[1], exist_ok=True)
        for p in livres():
            with open(os.path.join(a[1], p["id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(rascunho(p), f, ensure_ascii=False, indent=1)
        print(f"{len(livres())} rascunhos em {a[1]}")
    else:
        ps = livres()
        print(f"{len(ps)} pautas livres das últimas 72 h (mais novas primeiro):")
        for p in ps:
            print(f"- {p['id']} | {p.get('data_noticia')} | {p.get('titulo')} | {p.get('fonte')}")
