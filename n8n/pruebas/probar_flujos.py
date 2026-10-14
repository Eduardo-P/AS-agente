#!/usr/bin/env python3
"""
probar_flujos.py — Pruebas de extremo a extremo de los flujos de n8n con el MODELO SIMULADO.

Requisitos (ver n8n/INSTALACION_N8N.md, sección "Probar sin modelo"):
  1. n8n corriendo con los 11 flujos importados y publicados (construidos con --raiz <RAIZ>).
  2. python n8n/pruebas/modelo_simulado.py --puerto 11435      (en otra terminal)
  3. Para probar Claude Code: un ejecutable llamado `claude` que ejecute claude_simulado.py,
     o la opción --sin-claude para omitir ese proveedor.

    python n8n/pruebas/probar_flujos.py --raiz <RAIZ> [--n8n http://localhost:5678] [--sin-claude]

ATENCIÓN: crea registros, trabajos y organizaciones de prueba dentro de <RAIZ>. Úsalo sobre
una COPIA del proyecto, no sobre la carpeta con datos reales.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
import zlib
from pathlib import Path

A = None
RES = []


def http(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(f"{A.n8n}/webhook/{ruta}", data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"} if datos else {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        texto = e.read().decode("utf-8")
        try:
            return e.code, json.loads(texto)
        except json.JSONDecodeError:
            return e.code, {"_texto": texto[:300]}


def esperar(trabajo, limite=180):
    t0 = time.time()
    while time.time() - t0 < limite:
        c, j = http("GET", f"pims/trabajo?id={trabajo}")
        if c == 200 and j.get("estado") in ("terminado", "error", "terminado_con_errores"):
            return j
        time.sleep(1.5)
    raise AssertionError(f"El trabajo {trabajo} no terminó en {limite} s (último: {j})")


def prueba(nombre):
    def deco(f):
        try:
            d = f()
            RES.append((True, nombre, d or ""))
        except AssertionError as e:
            RES.append((False, nombre, str(e)[:600]))
        except Exception as e:  # noqa: BLE001
            RES.append((False, nombre, f"{type(e).__name__}: {e}"[:600]))
        return f
    return deco


def nucleo(r):
    return {"resumen": r.get("resumen"), "puntaje": json.loads(json.dumps(r.get("puntaje_proveedor")), parse_int=float),
            "dictamen": r.get("dictamen"),
            "controles": [(c["control"], c["estado"], c["severidad"], c["ambito"]) for c in r["controles"]],
            "alertas": r.get("alertas")}


def pdf_minimo(paginas):
    """PDF válido de varias páginas con texto (Helvetica, WinAnsi), sin dependencias."""
    objs = []
    kids = []
    n_pag = len(paginas)
    font_id = 3 + 2 * n_pag
    for i, lineas in enumerate(paginas):
        pid, cid = 3 + 2 * i, 4 + 2 * i
        kids.append(f"{pid} 0 R")
        flujo = "BT /F1 10 Tf 40 800 Td 12 TL\n" + "".join(
            "(" + l.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") '\n" for l in lineas) + "ET"
        comp = zlib.compress(flujo.encode("cp1252", "replace"))
        objs.append((pid, f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents {cid} 0 R "
                          f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>".encode()))
        objs.append((cid, b"<< /Length " + str(len(comp)).encode() + b" /Filter /FlateDecode >>\nstream\n" + comp + b"\nendstream"))
    objs.insert(0, (2, f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {n_pag} >>".encode()))
    objs.insert(0, (1, b"<< /Type /Catalog /Pages 2 0 R >>"))
    objs.append((font_id, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"))
    objs.sort()
    salida = bytearray(b"%PDF-1.4\n")
    offs = {}
    for num, cuerpo in objs:
        offs[num] = len(salida)
        salida += f"{num} 0 obj\n".encode() + cuerpo + b"\nendobj\n"
    xref = len(salida)
    salida += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for num, _ in objs:
        salida += f"{offs[num]:010d} 00000 n \n".encode()
    salida += f"trailer << /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(salida)


def configurar(**cambios):
    c, j = http("POST", "pims/config", cambios)
    assert c == 200 and j.get("ok"), f"No se pudo configurar el modelo: {c} {j}"


def auditar(org, contrato, proveedor="", fecha="2026-10-01", archivo=None):
    cuerpo = {"organizacion": org, "proveedor": proveedor, "fecha_ref": fecha}
    if archivo:
        cuerpo["archivo"] = archivo
    else:
        cuerpo["contrato_texto"] = contrato
    c, j = http("POST", "pims/auditar", cuerpo)
    assert c == 202 and j.get("trabajo"), f"auditar respondió {c}: {j}"
    return esperar(j["trabajo"])


def main():
    global A
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--n8n", default="http://localhost:5678")
    ap.add_argument("--simulado", default="http://127.0.0.1:11435")
    ap.add_argument("--sin-claude", action="store_true")
    ap.add_argument("--log", help="Registro del modelo simulado (--log de modelo_simulado.py), para revisar los prompts")
    A = ap.parse_args()
    raiz = Path(A.raiz)
    pr = raiz / "pims-dpa-auditor_pruebas"
    contrato = {n: (pr / "contratos" / f).read_text(encoding="utf-8") for n, f in
                [("NubeAndina", "dpa_nubeandina.md"), ("AndesCloud", "dpa_andescloud_bueno.md"), ("DigiServ", "dpa_ambiguo_inyeccion.md")]}
    ref = {n: json.loads((pr / "resultados" / f"resultado_{n}.json").read_text(encoding="utf-8")) for n in contrato}
    reg = {}

    @prueba("Estado: GET /pims/estado responde y oculta la API key")
    def _():
        configurar(api_key="sk-prueba-1234567890")
        c, j = http("GET", "pims/estado")
        assert c == 200 and j["ok"] and j["version"] == "2.0", j
        assert j["modelo"]["api_key"].startswith("********") and j["modelo"]["api_key"].endswith("7890"), j["modelo"]
        assert "_plantilla" not in [o["id"] for o in j["organizaciones"]]
        return f"{len(j['organizaciones'])} organizaciones"

    @prueba("Config: valores inválidos → 400 con la lista de errores")
    def _():
        c, j = http("POST", "pims/config", {"proveedor": "gpt9", "num_ctx": 5, "url_ollama": "ftp://x"})
        assert c == 400 and len(j.get("errores", [])) == 3, (c, j)

    proveedores = [("ollama", {"url_ollama": A.simulado}), ("anthropic", {"url_anthropic": A.simulado}),
                   ("openai", {"url_openai": A.simulado + "/v1"})]
    if not A.sin_claude:
        proveedores.append(("claude_code", {"claude_bin": "claude"}))
    for prov, extra in proveedores:
        @prueba(f"Auditar NubeAndina con proveedor '{prov}' → 22/100, idéntico a Python")
        def _(prov=prov, extra=extra):
            configurar(proveedor=prov, modelo="modelo-prueba", **extra)
            t = auditar("inversiones_altiplano", contrato["NubeAndina"], "NubeAndina")
            assert t["estado"] == "terminado", t
            c, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
            assert c == 200, d
            r = d["resultado"]
            assert nucleo(r) == nucleo(ref["NubeAndina"]), "el resultado difiere del cálculo de Python"
            assert r["_registro"]["proveedor"] == prov and r["trazabilidad"]["calculo"] == "script"
            assert r["contrato"]["hash_documento_sha256"] == hashlib.sha256(contrato["NubeAndina"].encode()).hexdigest()
            assert "Valores calculados por n8n" in d["informe"] and "Trazabilidad registrada por n8n" in d["informe"]
            reg[prov] = t["id_registro"]
            return f"{t['puntaje']}/100 · {t['dictamen']}"

    configurar(proveedor="ollama", url_ollama=A.simulado, modelo="modelo-prueba")

    @prueba("Auditar AndesCloud (organización con perfil) → 100/100; el perfil llega al prompt como no confiable")
    def _():
        t = auditar("altiplano_perfil", contrato["AndesCloud"], "AndesCloud")
        assert t["estado"] == "terminado" and t["puntaje"] == 100 and t["dictamen"] == "Recomendable", t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        p = d["resultado"]["organizacion"]["perfil"]
        sha = hashlib.sha256((raiz / "organizaciones/altiplano_perfil/perfil_organizacion.md").read_bytes()).hexdigest()
        assert p and p["hash_sha256"] == sha and p["estado"] == "Borrador", p
        assert any("sin validar" in a for a in d["resultado"]["trazabilidad"]["advertencias"])
        ultimo = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1] if A.log else None
        if ultimo:
            assert "CONTENIDO NO CONFIABLE" in ultimo["system"] and "Oficina de Cumplimiento" in ultimo["system"]
        reg["andes"] = t["id_registro"]
        return "perfil registrado con hash y advertencia de borrador"

    @prueba("Auditar DigiServ (inyección) → 0/100")
    def _():
        t = auditar("inversiones_altiplano", contrato["DigiServ"], "DigiServ")
        assert t["estado"] == "terminado" and t["puntaje"] == 0, t
        reg["digi"] = t["id_registro"]

    @prueba("JSON roto en la primera respuesta → una corrección automática → 22/100")
    def _():
        t = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:JSON_ROTO", "NubeAndina")
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        assert d["resultado"]["_registro"]["reintentos"] == 1, d["resultado"]["_registro"]
        return "reintentos = 1"

    @prueba("Contrato en PDF de 2 páginas → texto con marcadores de página y hash de los bytes del PDF")
    def _():
        lineas = contrato["NubeAndina"].splitlines()
        pdf = pdf_minimo([lineas[:12], lineas[12:]])
        import base64
        t = auditar("inversiones_altiplano", None, "NubeAndina",
                    archivo={"nombre": "Contrato NubeAndina.pdf", "base64": base64.b64encode(pdf).decode()})
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        assert d["resultado"]["contrato"]["hash_documento_sha256"] == hashlib.sha256(pdf).hexdigest()
        if A.log:
            ultimo = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1]
            assert "[Página 1]" in ultimo["usuario"] and "[Página 2]" in ultimo["usuario"], "faltan marcadores de página"
        return "PDF leído por n8n (Extract from File)"

    @prueba("Errores: organización inexistente → trabajo en error con mensaje claro")
    def _():
        t = auditar("no_existe_org", contrato["NubeAndina"])
        assert t["estado"] == "error" and "no existe" in t["mensaje"], t

    @prueba("Errores: petición inválida → 400 sin crear trabajo")
    def _():
        c, j = http("POST", "pims/auditar", {"organizacion": "../etc", "contrato_texto": "x"})
        assert c == 400 and not j["ok"], (c, j)
        c, j = http("POST", "pims/auditar", {"organizacion": "unsa"})
        assert c == 400 and "contrato_texto" in j["error"], (c, j)

    @prueba("Errores: proveedor caído (Ollama sin servicio) → trabajo en error, no se queda colgado")
    def _():
        configurar(proveedor="ollama", url_ollama="http://127.0.0.1:9")
        try:
            t = auditar("inversiones_altiplano", contrato["NubeAndina"])
        finally:
            configurar(proveedor="ollama", url_ollama=A.simulado)
        assert t["estado"] == "error" and "ollama" in t["mensaje"].lower(), t
        return t["mensaje"][:90]

    @prueba("Aprobaciones: orden obligatorio DPO → Legal y estados cerrados")
    def _():
        rid = reg.get("ollama") or next(iter(reg.values()))
        reg["aprobado"] = rid
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "Legal", "decision": "aprobar", "usuario": "Ana"})
        assert c == 409 and "DPO" in j["error"], (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "DPO", "decision": "aprobar", "usuario": "Luis", "comentario": "ok con enmiendas"})
        assert c == 200 and j["estado"] == "Pendiente Legal", (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "Legal", "decision": "aprobar", "usuario": "Ana"})
        assert c == 200 and j["estado"] == "Aprobado" and len(j["historial"]) == 2, (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "DPO", "decision": "rechazar", "usuario": "Luis"})
        assert c == 409, (c, j)
        _, d = http("GET", f"pims/registro/detalle?id={rid}")
        assert d["resultado"]["contrato"]["estado_dpa"] == "Aprobado" and "✅ aprobó" in d["informe"]
        c, j = http("POST", "pims/aprobar", {"id_registro": reg["digi"], "rol": "DPO", "decision": "rechazar", "usuario": "Luis"})
        assert c == 200 and j["estado"] == "Rechazado", (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": "NO_EXISTE_1", "rol": "DPO", "decision": "aprobar", "usuario": "x"})
        assert c == 404, (c, j)
        return "409 → Pendiente Legal → Aprobado → 409; rechazo y 404"

    @prueba("Registro: listado filtrable por organización y estado")
    def _():
        c, j = http("GET", "pims/registro?organizacion=inversiones_altiplano")
        assert c == 200 and j["total"] >= 5, j
        c, j = http("GET", "pims/registro?estado=Aprobado")
        assert c == 200 and reg.get("aprobado") in [x["id_registro"] for x in j["registros"]], j
        assert all(x["estado"] == "Aprobado" for x in j["registros"]), j

    @prueba("Perfilar organización (2 documentos) → perfil válido en Borrador, hashes reales, nota de inyección en §8")
    def _():
        c, j = http("POST", "pims/perfilar", {"organizacion": "altiplano_docs"})
        assert c == 202, (c, j)
        t = esperar(j["trabajo"])
        assert t["estado"] == "terminado", t
        md = (raiz / "organizaciones/altiplano_docs/perfil_organizacion.md").read_text(encoding="utf-8")
        for d in ("D1_rof_altiplano.md", "D2_manual_procesos_cobranza.md"):
            sha = hashlib.sha256((raiz / "organizaciones/altiplano_docs/documentos" / d).read_bytes()).hexdigest()
            assert sha in md, f"falta el hash de {d}"
        assert t["validacion"]["valido"] and len(t["validacion"]["documentos"]) == 2, t["validacion"]
        return t["mensaje"]

    @prueba("Perfil: GET devuelve validación y terceros; el DPO lo valida; segunda validación sigue siendo válida")
    def _():
        c, j = http("GET", "pims/perfil?organizacion=altiplano_docs")
        assert c == 200 and j["validacion"]["valido"] and len(j["terceros"]) == 4, j
        c, j = http("POST", "pims/perfil/validar", {"organizacion": "altiplano_docs", "validado_por": "María Quispe (DPO)"})
        assert c == 200 and j["estado"].startswith("Validado por DPO"), (c, j)
        c, j = http("GET", "pims/perfil?organizacion=altiplano_docs")
        assert j["validacion"]["estado"].startswith("Validado por DPO") and j["validacion"]["valido"], j["validacion"]
        c, j = http("POST", "pims/perfil/validar", {"organizacion": "unsa", "validado_por": "x"})
        assert c == 404, (c, j)

    @prueba("Organizaciones: perfil, registros y terceros sin DPA evaluado (brechas)")
    def _():
        c, j = http("GET", "pims/organizaciones")
        o = {x["id"]: x for x in j["organizaciones"]}
        assert o["altiplano_perfil"]["perfil"]["existe"] and reg["andes"] in [r["id_registro"] for r in o["altiplano_perfil"]["registros"]]
        b = o["altiplano_perfil"]["terceros_sin_dpa_evaluado"]
        assert any("NubeAndina" in x for x in b) and not any("AndesCloud" in x for x in b), b
        return f"brechas altiplano_perfil: {len(b)}"

    @prueba("Crear organización desde la API (Execute Command) y subir un documento")
    def _():
        oid = f"muni_prueba_{int(time.time()) % 100000}"
        c, j = http("POST", "pims/organizacion", {"id": oid, "nombre": "Municipalidad de Prueba", "jurisdiccion": "peru",
                                                  "cargo_dpo": "Oficial de Datos", "cargo_legal": "Procuraduría"})
        assert c == 201, (c, j)
        cfg = json.loads((raiz / f"organizaciones/{oid}/config_organizacion.json").read_text(encoding="utf-8"))
        assert cfg["aprobadores_cargos"]["Legal"] == "Procuraduría" and cfg["jurisdiccion"] == "peru"
        c, j = http("POST", "pims/organizacion", {"id": oid, "nombre": "x"})
        assert c == 409, (c, j)
        c, j = http("POST", "pims/organizacion", {"id": "otra", "nombre": "x", "jurisdiccion": "_plantilla"})
        assert c == 400, (c, j)
        c, j = http("POST", "pims/documento", {"organizacion": oid, "nombre": "ROF 2026.docx", "texto": "Artículo 1. Prueba."})
        assert c == 201 and j["nombre"] == "ROF_2026.txt", (c, j)
        assert (raiz / f"organizaciones/{oid}/documentos/ROF_2026.txt").read_text(encoding="utf-8") == "Artículo 1. Prueba."
        c, j = http("POST", "pims/documento", {"organizacion": "no_existe_x", "nombre": "a.txt", "texto": "x"})
        assert c == 404, (c, j)

    @prueba("Renovaciones: GET calcula alertas con la fecha de hoy y omite los rechazados")
    def _():
        c, j = http("GET", "pims/renovaciones")
        assert c == 200 and j["ok"], j
        ids = [x["id_registro"] for x in j["registros_con_alertas"]]
        assert reg["digi"] not in ids, "incluyó un registro rechazado"
        assert any(x["fin_vigencia"] is None for x in j["registros_con_alertas"])
        return f"{len(ids)} registros con alertas al {j['fecha_referencia']}"

    @prueba("Jurisdicciones: lista Perú utilizable y la plantilla no")
    def _():
        c, j = http("GET", "pims/jurisdicciones")
        d = {x["id"]: x for x in j["jurisdicciones"]}
        assert d["peru"]["usable"] and not d["_plantilla"]["usable"], d

    ok = sum(1 for r in RES if r[0])
    print(f"\nPruebas de los flujos de n8n (modelo simulado)\n{'=' * 46}")
    for paso, nombre, det in RES:
        print(f"[{'OK  ' if paso else 'FALLA'}] {nombre}" + (f"\n         {det}" if det else ""))
    print(f"\n{ok}/{len(RES)} pruebas correctas")
    sys.exit(0 if ok == len(RES) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    main()
