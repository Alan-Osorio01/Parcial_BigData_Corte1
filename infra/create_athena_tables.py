import boto3
import time
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────────────────
REGION    = "us-east-1"
BUCKET    = "chinook-datalake-academy"
ATHENA_WG = "chinook-wg"
DDL_FILE  = Path(__file__).parent / "athena_ddls.sql"
# ─────────────────────────────────────────────────────────────────────────────

athena = boto3.client("athena", region_name=REGION)


def run_query(sql: str, label: str):
    resp = athena.start_query_execution(
        QueryString=sql,
        WorkGroup=ATHENA_WG,
        ResultConfiguration={"OutputLocation": f"s3://{BUCKET}/athena-results/"},
    )
    qid = resp["QueryExecutionId"]

    for _ in range(60):
        status = athena.get_query_execution(QueryExecutionId=qid)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(2)

    if state == "SUCCEEDED":
        print(f"  [ok]   {label}")
    else:
        reason = status["QueryExecution"]["Status"].get("StateChangeReason", "")
        print(f"  [err]  {label}\n         → {state}: {reason}")


def load_statements():
    if not DDL_FILE.exists():
        print(f"  [warn] {DDL_FILE} no existe — esperar a que Ana entregue athena_ddls.sql")
        return []
    raw = DDL_FILE.read_text()
    return [s.strip() for s in raw.split(";") if s.strip()]


if __name__ == "__main__":
    print("\n=== create_athena_tables.py ===\n")

    statements = load_statements()
    if not statements:
        print("Sin DDLs que ejecutar.\n")
    else:
        print(f"Ejecutando {len(statements)} DDLs en Athena workgroup '{ATHENA_WG}'...\n")
        for i, sql in enumerate(statements, 1):
            label = f"[{i}/{len(statements)}] {sql.split(chr(10))[0][:70]}"
            run_query(sql, label)

    print("\n✅  Tablas Athena listas.\n")
