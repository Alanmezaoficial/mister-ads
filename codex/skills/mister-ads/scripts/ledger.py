#!/usr/bin/env python3
"""Mister ADS 1.0: private JSON ledger and manual report exchange. Python stdlib only."""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

VERSION = "mister-ads/1"
STATES = {"consulta", "lead_calificado", "seguimiento", "venta_acordada", "perdida", "cancelada"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def read(p):
    p = Path(p)
    require(p.stat().st_size <= 20_000_000, "Archivo mayor a 20 MB; dividir el reporte")
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "Clave JSON repetida")
            out[key] = value
        return out
    return json.loads(p.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Número JSON no finito")))

def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()

def ident(value):
    require(isinstance(value, str) and ID.fullmatch(value), "Identificador inválido")

def date(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), "Fecha debe ser YYYY-MM-DD")
    dt.date.fromisoformat(value)
    return value

def number(value, nullable=False, positive=False):
    if value is None and nullable:
        return
    require(type(value) is int and (1 if positive else 0) <= value <= 9_007_199_254_740_991,
            "Cantidad debe ser un entero válido en unidades menores, o null cuando se permita")

def fields(row, required, optional=()):
    require(isinstance(row, dict), "Se esperaba un objeto")
    require(set(required) <= row.keys(), "Faltan campos: " + ", ".join(sorted(set(required)-row.keys())))
    require(not (row.keys()-set(required)-set(optional)), "Campos no admitidos: " + ", ".join(sorted(row.keys()-set(required)-set(optional))))

def config_check(c):
    fields(c, ["business_id", "currency", "minor_unit", "timezone", "synthetic"])
    ident(c["business_id"])
    require(isinstance(c["currency"], str) and re.fullmatch(r"[A-Z]{3}", c["currency"]), "Moneda ISO requerida")
    require(type(c["minor_unit"]) is int and 0 <= c["minor_unit"] <= 4, "Escala monetaria inválida")
    require(isinstance(c["timezone"], str) and re.fullmatch(r"[A-Za-z0-9_+/-]{1,80}", c["timezone"]), "Zona horaria requerida")
    require(type(c["synthetic"]) is bool, "synthetic debe ser booleano")

def envelope(data, config, required, optional=()):
    fields(data, ["schema_version", "business_id", "synthetic", *required], optional)
    require(data["schema_version"] == VERSION, "Versión de esquema incompatible")
    require(data["business_id"] == config["business_id"], "Negocio incompatible")
    require(type(data["synthetic"]) is bool and data["synthetic"] == config["synthetic"], "No mezclar datos ficticios y reales")

def money_scope(row, config):
    require(row["currency"] == config["currency"] and type(row["minor_unit"]) is int and row["minor_unit"] == config["minor_unit"], "Moneda o escala incompatible")

def validate_ledger(db):
    c = db["config"]
    for o in db["opportunities"].values():
        fields(o, ["opportunity_id", "entry_date", "status", "status_date", "agreed_value_minor", "currency", "minor_unit", "platform", "account_id", "campaign_id", "ad_id", "association_method", "source"])
        ident(o["opportunity_id"]); money_scope(o, c)
        require(o["status"] in STATES, "Estado comercial inválido")
        require(date(o["status_date"]) >= date(o["entry_date"]), "Estado anterior a la entrada")
        number(o["agreed_value_minor"], nullable=True)
        require(isinstance(o["source"], str) and 0 < len(o["source"]) <= 500, "Fuente comercial requerida")
        require(o["association_method"] in {"ad_id_en_formulario", "campaign_id_documentado", "declarado_usuario", "origen_desconocido"}, "Método de asociación inválido")
        for key in ("platform", "account_id", "campaign_id", "ad_id"):
            if o[key] is not None: ident(o[key])
        if o["campaign_id"] is not None or o["ad_id"] is not None:
            require(o["platform"] in {"meta", "google", "tiktok"} and o["account_id"] is not None and o["campaign_id"] is not None, "Atribución requiere plataforma, cuenta y campaña")
        if o["association_method"] == "origen_desconocido":
            require(all(o[k] is None for k in ("platform", "account_id", "campaign_id", "ad_id")), "Origen desconocido no puede llevar atribución")
        if o["ad_id"] is not None:
            require(o["association_method"] in {"ad_id_en_formulario", "declarado_usuario"}, "Método incompatible con anuncio")
    refunds = {}
    for p in db["payments"].values():
        fields(p, ["payment_id", "opportunity_id", "type", "classification", "amount_minor", "payment_date", "linked_payment_id", "currency", "minor_unit", "source"])
        ident(p["payment_id"]); money_scope(p, c); number(p["amount_minor"], positive=True)
        require(p["type"] in {"cobro", "reembolso"}, "Tipo de movimiento inválido")
        require(p["classification"] in {"anticipo", "abono", "liquidacion", "reembolso"}, "Clasificación inválida")
        require(isinstance(p["source"], str) and 0 < len(p["source"]) <= 500, "Fuente de movimiento requerida")
        o = db["opportunities"].get(p["opportunity_id"])
        require(o is not None, "Movimiento sin oportunidad")
        require(date(p["payment_date"]) >= o["entry_date"], "Movimiento anterior a oportunidad")
        if p["type"] == "reembolso":
            require(p["classification"] == "reembolso", "Clasificación incompatible")
            original = db["payments"].get(p["linked_payment_id"])
            require(original is not None and original["type"] == "cobro", "Reembolso sin cobro original")
            require(original["opportunity_id"] == p["opportunity_id"] and p["payment_date"] >= original["payment_date"], "Reembolso incompatible con cobro")
            refunds[p["linked_payment_id"]] = refunds.get(p["linked_payment_id"], 0) + p["amount_minor"]
            require(refunds[p["linked_payment_id"]] <= original["amount_minor"], "Reembolsos exceden cobro original")
        else:
            require(p["linked_payment_id"] is None and p["classification"] != "reembolso", "Cobro incompatible")

def validate_report(r, c):
    envelope(r, c, ["report_id", "platform", "account_id", "currency", "minor_unit", "timezone", "period", "attribution_window", "action_report_time", "generated_at", "source", "limitations", "rows"])
    ident(r["report_id"]); ident(r["account_id"]); money_scope(r, c)
    require(r["platform"] in {"meta", "google", "tiktok"}, "Plataforma inválida")
    require(r["timezone"] == c["timezone"], "Zona de cuenta distinta al registro; crear registro separado o conciliar explícitamente")
    fields(r["period"], ["start_date", "end_date", "inclusive"])
    require(r["period"]["inclusive"] is True and date(r["period"]["start_date"]) <= date(r["period"]["end_date"]), "Periodo inválido")
    for key in ("attribution_window", "action_report_time", "generated_at"):
        require(r[key] is None or (isinstance(r[key], str) and 0 < len(r[key]) <= 200), "Metadato inválido")
    if r["generated_at"] is not None:
        stamp = dt.datetime.fromisoformat(r["generated_at"].replace("Z", "+00:00"))
        require(stamp.tzinfo is not None, "generated_at debe incluir zona horaria")
    require(isinstance(r["source"], str) and 0 < len(r["source"]) <= 500, "Fuente requerida")
    require(isinstance(r["limitations"], list) and all(isinstance(x, str) and len(x) <= 1000 for x in r["limitations"]), "Limitaciones inválidas")
    require(isinstance(r["rows"], list) and len(r["rows"]) <= 100_000, "Filas inválidas")
    seen = set()
    for row in r["rows"]:
        fields(row, ["campaign_id", "adset_id", "ad_id", "amount_spent_minor", "impressions", "link_clicks", "leads_reported", "result_definition"])
        for k in ("campaign_id", "adset_id", "ad_id"): ident(row[k])
        require(row["ad_id"] not in seen, "Reporte requiere una fila agregada por anuncio; no mezclar totales o días")
        seen.add(row["ad_id"])
        for k in ("amount_spent_minor", "impressions", "link_clicks", "leads_reported"): number(row[k], nullable=True)
        require(isinstance(row["result_definition"], str) and 0 < len(row["result_definition"]) <= 1000, "Definición de resultado requerida")

def record(db, bundle, revise=False):
    envelope(bundle, db["config"], ["opportunities", "payments"])
    changes = []
    for group, key in [("opportunities", "opportunity_id"), ("payments", "payment_id")]:
        require(isinstance(bundle[group], list), "Registros deben ser lista")
        batch = {}
        for row in bundle[group]:
            require(isinstance(row, dict) and key in row, "Registro sin ID")
            ident(row[key]); item_id = row[key]
            require(item_id not in batch or batch[item_id] == row, "ID contradictorio dentro del lote")
            batch[item_id] = row
        for item_id, row in batch.items():
            old = db[group].get(item_id)
            if old == row: continue
            require(old is None or revise, "ID existente diferente: revisar y usar --revise con revisión esperada")
            changes.append({"group": group, "id": item_id, "before": old, "after": row})
            db[group][item_id] = copy.deepcopy(row)
    validate_ledger(db)
    return changes

def report_add(db, report):
    validate_report(report, db["config"])
    key = report["report_id"]
    old = db["reports"].get(key)
    require(old is None or old["data"] == report, "report_id existente con contenido distinto; usar otro ID para corrección")
    if old is not None: return []
    db["reports"][key] = {"sha256": digest(report), "imported_at": now(), "data": report}
    return [{"group": "reports", "id": key, "sha256": digest(report)}]

def prototype(a, c, config):
    require(config["synthetic"] is True and a.get("synthetic") is True and c.get("synthetic") is True, "Conversor solo admite prototipo sintético")
    require(a.get("schema_version") == c.get("schema_version") == "mister-ads-prototype-0.1", "Prototipo incompatible")
    for source in (a["account"], c): money_scope(source, config)
    require(a["account"]["timezone"] == a["period"]["timezone"] == config["timezone"], "Zona incompatible")
    common = {"schema_version": VERSION, "business_id": config["business_id"], "synthetic": True}
    report = {**common, "report_id": "prototype-" + digest(a)[:20], "platform": "meta", "account_id": a["account"]["ad_account_id"], "currency": config["currency"], "minor_unit": config["minor_unit"], "timezone": config["timezone"], "period": {k: a["period"][k] for k in ("start_date", "end_date", "inclusive")}, "attribution_window": a["attribution_window_declared"], "action_report_time": None, "generated_at": None, "source": "muse_synthetic_prototype", "limitations": ["Datos ficticios; fecha de generación y criterio temporal de acciones no disponibles.", a["lead_definition"]], "rows": []}
    for row in a["rows"]:
        money_scope(row, config)
        report["rows"].append({**{k: row[k] for k in ("campaign_id", "adset_id", "ad_id", "amount_spent_minor", "impressions", "link_clicks", "leads_reported")}, "result_definition": a["lead_definition"]})
    bundle = {**common, "opportunities": [], "payments": []}
    for row in c["opportunities_input"]:
        money_scope(row, config)
        item = {k: row[k] for k in ("opportunity_id", "entry_date", "status", "status_date", "agreed_value_minor", "currency", "minor_unit", "campaign_id", "ad_id", "association_method")}
        item.update(platform="meta" if row["campaign_id"] else None, account_id=a["account"]["ad_account_id"] if row["campaign_id"] else None, source="muse_synthetic_prototype")
        bundle["opportunities"].append(item)
    for row in c["payments"]:
        require(row["type"] in {"anticipo", "cobro", "reembolso"}, "Tipo de prototipo inválido")
        item = {k: row[k] for k in ("payment_id", "opportunity_id", "amount_minor", "payment_date", "linked_payment_id", "currency", "minor_unit")}
        item.update(type="reembolso" if row["type"] == "reembolso" else "cobro", classification={"anticipo": "anticipo", "cobro": "abono", "reembolso": "reembolso"}[row["type"]], source="muse_synthetic_prototype")
        bundle["payments"].append(item)
    return report, bundle

def summary(db, report_id=None):
    opportunities = list(db["opportunities"].values()); payments = list(db["payments"].values())
    gross = sum(p["amount_minor"] for p in payments if p["type"] == "cobro")
    refunds = sum(p["amount_minor"] for p in payments if p["type"] == "reembolso")
    won = [o for o in opportunities if o["status"] == "venta_acordada"]
    result = {"schema_version": VERSION, "revision": db["revision"], "config": db["config"], "opportunities": len(opportunities), "won": len(won), "payments": len(payments), "agreed_won_minor": sum(o["agreed_value_minor"] for o in won) if won and all(o["agreed_value_minor"] is not None for o in won) else None,
              "gross_minor": gross if payments else None, "refunds_minor": refunds if payments else None, "net_minor": gross-refunds if payments else None,
              "unknown_origin": sum(o["association_method"] == "origen_desconocido" for o in opportunities),
              "commercial_scope": "Todos los registros disponibles; no acredita cobertura completa ni deuda pendiente.",
              "reports": list(db["reports"]), "warnings": ["Registro vacío o parcial no equivale a cero ventas reales.", "No se calcula ROAS, rentabilidad ni tasa de cierre sin confirmar cohorte y cobertura."]}
    if report_id:
        require(report_id in db["reports"], "Reporte no encontrado")
        r = db["reports"][report_id]["data"]
        rows = {row["ad_id"]: row for row in r["rows"]}
        matches = []
        conflicts = []
        for o in opportunities:
            if o["platform"] != r["platform"] or o["account_id"] != r["account_id"]: continue
            if o["ad_id"] in rows:
                if o["campaign_id"] != rows[o["ad_id"]]["campaign_id"]: conflicts.append(o["opportunity_id"])
                elif r["period"]["start_date"] <= o["entry_date"] <= r["period"]["end_date"]: matches.append(o["opportunity_id"])
        result["advertising"] = {"report_id": report_id, "period": r["period"], "account_id": r["account_id"], "attribution_window": r["attribution_window"], "amount_spent_minor": sum(row["amount_spent_minor"] for row in r["rows"]) if r["rows"] and all(row["amount_spent_minor"] is not None for row in r["rows"]) else None, "matched_cohort_opportunities": matches, "link_conflicts": conflicts, "limitations": r["limitations"]}
        result["warnings"].append("Se usa un solo snapshot publicitario; no se suman reportes solapados ni se mezcla su gasto con cobros de otro periodo.")
    return result

def atomic_write(path, data):
    handle, tmp = tempfile.mkstemp(prefix=".ledger-", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf8") as stream:
            stream.write(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+"\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, help="Carpeta privada del negocio, fuera del código público")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("--config", required=True)
    p = sub.add_parser("record"); p.add_argument("--input", required=True); p.add_argument("--revise", action="store_true"); p.add_argument("--expect-revision", type=int, required=True)
    p = sub.add_parser("import-report"); p.add_argument("--input", required=True); p.add_argument("--expect-revision", type=int, required=True)
    p = sub.add_parser("import-prototype"); p.add_argument("--ads", required=True); p.add_argument("--commercial", required=True); p.add_argument("--expect-revision", type=int, required=True)
    p = sub.add_parser("summary"); p.add_argument("--report")
    sub.add_parser("export")
    args = parser.parse_args()
    root = Path(args.data_dir).expanduser().resolve(); target = root/"ledger.json"
    if args.command in {"summary", "export"}:
        db = read(target); validate_ledger(db)
        print(json.dumps(summary(db, args.report) if args.command == "summary" else db, ensure_ascii=False, indent=2)); return
    root.mkdir(parents=True, exist_ok=True)
    lock = root/".ledger.lock"
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Registro ocupado. Si hubo interrupción, comprobar que no queda escritor activo antes de recuperar el bloqueo.")
    os.close(lock_fd)
    try:
        if args.command == "init":
            config = read(args.config); config_check(config)
            if target.exists():
                require(read(target)["config"] == config, "Ya existe otro registro en esta carpeta")
                print(json.dumps({"status": "already_initialized", "path": str(target)})); return
            db = {"schema_version": VERSION, "config": config, "revision": 0, "opportunities": {}, "payments": {}, "reports": {}, "history": []}
            atomic_write(target, db)
            print(json.dumps({"status": "initialized", "revision": 0, "path": str(target)})); return
        db = read(target)
        require(db["revision"] == args.expect_revision, "Revisión desactualizada: leer el resumen y revisar antes de reintentar")
        if args.command == "record": changes = record(db, read(args.input), args.revise)
        elif args.command == "import-report": changes = report_add(db, read(args.input))
        else:
            report, bundle = prototype(read(args.ads), read(args.commercial), db["config"])
            changes = record(db, bundle) + report_add(db, report)
        if changes:
            db["revision"] += 1
            db["history"].append({"revision": db["revision"], "at": now(), "changes": changes})
            atomic_write(target, db)
        print(json.dumps({"status": "saved" if changes else "unchanged", "revision": db["revision"], "changes": len(changes), "path": str(target)}))
    finally:
        lock.unlink()

if __name__ == "__main__":
    try: main()
    except (ValueError, OSError, KeyError, TypeError, OverflowError) as error:
        # No payloads/credentials are printed on failure.
        print(json.dumps({"error": str(error) if isinstance(error, ValueError) else type(error).__name__}, ensure_ascii=False))
        raise SystemExit(2)
