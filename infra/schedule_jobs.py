import boto3
from botocore.exceptions import ClientError

# ── CONFIG ───────────────────────────────────────────────────────────────────
REGION = "us-east-1"

# Orden escalonado cada hora — 5 min entre jobs para evitar solapamiento
TRIGGERS = [
    {
        "Name":        "trigger-dim-date",
        "JobName":     "dim-date-etl",
        "Schedule":    "cron(0 */1 * * ? *)",
        "Description": "DimDate cada hora",
    },
    {
        "Name":        "trigger-dim-customer",
        "JobName":     "dim-customer-etl",
        "Schedule":    "cron(5 */1 * * ? *)",
        "Description": "DimCustomer cada hora",
    },
    {
        "Name":        "trigger-dim-track",
        "JobName":     "dim-track-etl",
        "Schedule":    "cron(10 */1 * * ? *)",
        "Description": "DimTrack cada hora",
    },
    {
        "Name":        "trigger-dim-employee",
        "JobName":     "dim-employee-etl",
        "Schedule":    "cron(15 */1 * * ? *)",
        "Description": "DimEmployee cada hora",
    },
    {
        "Name":        "trigger-fact-sales",
        "JobName":     "fact-sales-etl",
        "Schedule":    "cron(20 */1 * * ? *)",
        "Description": "FactSales cada hora",
    },
]
# ─────────────────────────────────────────────────────────────────────────────

glue = boto3.client("glue", region_name=REGION)


def upsert_trigger(t: dict):
    actions = [{"JobName": t["JobName"]}]
    try:
        glue.get_trigger(Name=t["Name"])
        glue.update_trigger(
            Name=t["Name"],
            TriggerUpdate={
                "Description": t["Description"],
                "Schedule":    t["Schedule"],
                "Actions":     actions,
            },
        )
        print(f"  [upd]  {t['Name']} actualizado  ({t['Schedule']})")
    except ClientError:
        glue.create_trigger(
            Name=t["Name"],
            Type="SCHEDULED",
            Schedule=t["Schedule"],
            Description=t["Description"],
            Actions=actions,
            StartOnCreation=False,  # activar manualmente cuando los ETLs estén listos
        )
        print(f"  [ok]   {t['Name']} creado (apagado)  ({t['Schedule']})")


if __name__ == "__main__":
    print("\n=== schedule_jobs.py ===\n")
    print("Creando/actualizando Glue Triggers...\n")
    for trigger in TRIGGERS:
        upsert_trigger(trigger)
    print(
        "\n✅  Triggers creados con StartOnCreation=False."
        "\n    Actívalos desde Glue Console → Triggers cuando los ETLs estén validados.\n"
    )
