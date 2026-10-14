#!/usr/bin/env python3
"""
modelo_simulado.py — Servidor que IMITA a un modelo de IA para probar los flujos de n8n
sin gastar cuota ni depender de la calidad de un modelo local.

    python n8n/pruebas/modelo_simulado.py [--puerto 11435] [--log modelo_simulado.log]

Expone las mismas rutas que los proveedores reales:
  POST /api/chat               (Ollama)
  POST /v1/messages            (Anthropic)
  POST /v1/chat/completions    (compatible con OpenAI)
  POST /claude                 (lo usa claude_simulado.py, que imita al CLI `claude -p`)

Respuestas deterministas, construidas con los archivos de referencia del proyecto:
  - Auditoría de NubeAndina / AndesCloud / DigiServ → informe de 11 secciones + el JSON de referencia
    (sin los campos que calcula n8n). Si el contrato contiene "MOCK:JSON_ROTO", la primera respuesta
    omite 'controles' para forzar la ruta de corrección.
  - Contratos supuestos de la UNSA (pims-dpa-auditor_pruebas/unsa/) → su evaluación de referencia.
  - Perfilador → notas por documento y, al final, el perfil de referencia de altiplano_con_perfil.

NO es un modelo: no "lee" el contrato. Sirve para comprobar el circuito (n8n, cálculo, archivos,
aprobaciones), no la calidad de la evaluación. Para eso, usa un modelo real.
"""
import argparse
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PRUEBAS = RAIZ / "pims-dpa-auditor_pruebas"
CALCULADOS = ("resumen", "puntaje_proveedor", "dictamen", "aprobacion", "organizacion", "jurisdiccion", "_registro")
LOG = None
_lock = threading.Lock()


def resultado_modelo(nombre):
    r = json.loads((PRUEBAS / "resultados" / f"resultado_{nombre}.json").read_text(encoding="utf-8"))
    for k in CALCULADOS:
        r.pop(k, None)
    r["alertas"] = [a for a in r["alertas"] if a.get("origen") != "script"]
    r["trazabilidad"] = {"version_skill": "2.0", "version_config": "2.0", "evaluador": "Modelo simulado", "calculo": "script"}
    return r


UNSA = {"Plataforma Aprende Andes": "unsa_01_aula_virtual", "Laboratorio Clínico Misti": "unsa_02_laboratorio_clinico",
        "Recaudo Sur Pagos": "unsa_03_pasarela_pagos", "Seguridad Integral Characato": "unsa_04_videovigilancia",
        "Ingeniería de Software Altoandino": "unsa_05_soporte_sistema_academico"}


def resultado_unsa(caso):
    r = json.loads((PRUEBAS / "unsa" / "referencia" / f"ref_{caso}.json").read_text(encoding="utf-8"))
    for c in r["controles"]:
        c.pop("_alternativas", None)
    return r


def informe(nombre):
    if nombre == "NubeAndina":
        return (PRUEBAS / "resultados" / "informe_DPA_NubeAndina.md").read_text(encoding="utf-8")
    titulos = ["Resumen ejecutivo", "Ficha del tercero, rol y vigencia del contrato", "Idoneidad: certificaciones y uso de IA",
               "Matriz de controles ISO/IEC 27701:2025", "Contraste con la ley aplicable y política interna",
               "Alertas (riesgo y renovación)", "Puntaje del proveedor (total y por dimensión)", "Plan de remediación",
               "Borrador de correo al proveedor", "Aprobaciones requeridas (DPO → Legal)", "Supuestos, limitaciones y trazabilidad"]
    cuerpo = "\n\n".join(f"## {i}. {t}\n\nTexto simulado de la sección {i}." for i, t in enumerate(titulos, 1))
    return f"# Informe de evaluación DPA — {nombre} (simulado)\n\n{cuerpo}\n"


def responder(system, usuario):
    if "Redacta el perfil completo" in usuario or "El perfil no pasa la validación" in usuario:
        return (PRUEBAS / "organizaciones_prueba" / "altiplano_con_perfil" / "perfil_organizacion.md").read_text(encoding="utf-8")
    m = re.search(r"\[DOCUMENTO (D\d+)", usuario)
    if m:
        d = m.group(1)
        return f"§1\n- Razón social y domicilio [{d}, art. 1]\n§6\n- Proveedores mencionados [{d}, p. 1]"
    if "[CONTRATO" in usuario:
        caso = next((v for k, v in UNSA.items() if k in usuario), None)
        if caso:
            r = resultado_unsa(caso)
            return f"{informe(r['tercero']['nombre'])}\n\n```json\n{json.dumps(r, ensure_ascii=False, indent=2)}\n```"
        nombre = ("NubeAndina" if "NubeAndina" in usuario else "AndesCloud" if "AndesCloud" in usuario
                  else "DigiServ" if "DigiServ" in usuario else None)
        if not nombre:
            return "No reconozco este contrato (modelo simulado)."
        r = resultado_modelo(nombre)
        if "no cumple el esquema" in usuario:      # petición de corrección
            return f"```json\n{json.dumps(r, ensure_ascii=False, indent=2)}\n```"
        if "MOCK:JSON_ROTO" in usuario:
            r.pop("controles")
        return f"{informe(nombre)}\n\n```json\n{json.dumps(r, ensure_ascii=False, indent=2)}\n```"
    return "Respuesta simulada genérica."


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        cuerpo = json.loads(self.rfile.read(n) or b"{}")
        ruta = self.path.rstrip("/")
        if ruta.endswith("/api/chat"):
            msgs = cuerpo.get("messages", [])
            system = next((m["content"] for m in msgs if m["role"] == "system"), "")
            usuario = next((m["content"] for m in msgs if m["role"] == "user"), "")
            texto = responder(system, usuario)
            salida = {"model": cuerpo.get("model"), "message": {"role": "assistant", "content": texto}, "done": True, "done_reason": "stop"}
            prov = "ollama"
        elif ruta.endswith("/v1/messages"):
            if not self.headers.get("x-api-key"):
                return self._enviar(401, {"type": "error", "error": {"type": "authentication_error", "message": "x-api-key header is required"}})
            system = cuerpo.get("system", "")
            usuario = cuerpo["messages"][0]["content"]
            texto = responder(system, usuario)
            salida = {"type": "message", "role": "assistant", "content": [{"type": "text", "text": texto}], "stop_reason": "end_turn",
                      "model": cuerpo.get("model")}
            prov = "anthropic"
        elif ruta.endswith("/chat/completions"):
            msgs = cuerpo.get("messages", [])
            system = next((m["content"] for m in msgs if m["role"] == "system"), "")
            usuario = next((m["content"] for m in msgs if m["role"] == "user"), "")
            texto = responder(system, usuario)
            salida = {"choices": [{"index": 0, "message": {"role": "assistant", "content": texto}, "finish_reason": "stop"}],
                      "model": cuerpo.get("model")}
            prov = "openai"
        elif ruta.endswith("/claude"):
            system, usuario = cuerpo.get("system", ""), cuerpo.get("mensaje", "")
            texto = responder(system, usuario)
            salida = {"type": "result", "subtype": "success", "is_error": False, "result": texto, "num_turns": 1}
            prov = "claude_code"
        else:
            return self._enviar(404, {"error": "ruta desconocida"})
        if LOG:
            with _lock, open(LOG, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"proveedor": prov, "modelo": cuerpo.get("model") or cuerpo.get("modelo"),
                                     "system_chars": len(system), "system": system, "usuario": usuario}, ensure_ascii=False) + "\n")
        self._enviar(200, salida)

    def _enviar(self, codigo, obj):
        datos = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)


def main():
    global LOG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--puerto", type=int, default=11435)
    ap.add_argument("--log", help="Archivo donde registrar cada petición (JSON por línea)")
    a = ap.parse_args()
    LOG = a.log
    print(f"Modelo simulado escuchando en http://127.0.0.1:{a.puerto} (Ollama: /api/chat · Anthropic: /v1/messages · OpenAI: /v1/chat/completions)")
    ThreadingHTTPServer(("127.0.0.1", a.puerto), H).serve_forever()


if __name__ == "__main__":
    main()
