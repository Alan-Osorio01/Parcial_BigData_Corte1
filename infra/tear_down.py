import boto3
from botocore.exceptions import ClientError

# ── CONFIG ───────────────────────────────────────────────────────────────────
REGION          = "us-east-1"
BUCKET          = "chinook-datalake-academy"
GLUE_DB         = "chinook_dw"
GLUE_CONNECTION = "chinook-rds"
ATHENA_WG       = "chinook-wg"
GLUE_SG_NAME    = "glue-chinook-workers"
VPC_ID          = "vpc-0f2744cffdd612162"

JOB_NAMES = [
    "dim-customer-etl", "dim-customer-history-etl",
    "dim-track-etl", "dim-employee-etl", "dim-employee-history-etl",
    "fact-sales-etl", "dim-date-etl",
]
TRIGGER_NAMES = [
    "trigger-dim-date", "trigger-dim-customer", "trigger-dim-track",
    "trigger-dim-employee", "trigger-fact-sales",
]
# ─────────────────────────────────────────────────────────────────────────────

s3     = boto3.client("s3",     region_name=REGION)
glue   = boto3.client("glue",   region_name=REGION)
athena = boto3.client("athena", region_name=REGION)
ec2    = boto3.client("ec2",    region_name=REGION)


def delete_glue_resources():
    for name in TRIGGER_NAMES:
        try:
            glue.delete_trigger(Name=name)
            print(f"  [ok]   Trigger {name} eliminado")
        except ClientError:
            print(f"  [skip] Trigger {name} no existe")

    for name in JOB_NAMES:
        try:
            glue.delete_job(JobName=name)
            print(f"  [ok]   Job {name} eliminado")
        except ClientError:
            print(f"  [skip] Job {name} no existe")

    try:
        glue.delete_connection(ConnectionName=GLUE_CONNECTION)
        print(f"  [ok]   Connection {GLUE_CONNECTION} eliminada")
    except ClientError:
        print(f"  [skip] Connection {GLUE_CONNECTION} no existe")

    try:
        glue.delete_database(Name=GLUE_DB)
        print(f"  [ok]   Glue DB {GLUE_DB} eliminada")
    except ClientError:
        print(f"  [skip] Glue DB {GLUE_DB} no existe")


def delete_athena_workgroup():
    try:
        athena.delete_work_group(WorkGroup=ATHENA_WG, RecursiveDeleteOption=True)
        print(f"  [ok]   Workgroup {ATHENA_WG} eliminado")
    except ClientError:
        print(f"  [skip] Workgroup {ATHENA_WG} no existe")


def empty_and_delete_bucket():
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET):
            objects = page.get("Contents", [])
            if objects:
                s3.delete_objects(
                    Bucket=BUCKET,
                    Delete={"Objects": [{"Key": o["Key"]} for o in objects]},
                )
        s3.delete_bucket(Bucket=BUCKET)
        print(f"  [ok]   Bucket {BUCKET} vaciado y eliminado")
    except ClientError:
        print(f"  [skip] Bucket {BUCKET} no existe")


def delete_glue_sg():
    resp = ec2.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [GLUE_SG_NAME]},
            {"Name": "vpc-id",     "Values": [VPC_ID]},
        ]
    )
    if not resp["SecurityGroups"]:
        print(f"  [skip] SG {GLUE_SG_NAME} no existe")
        return
    sg_id = resp["SecurityGroups"][0]["GroupId"]
    try:
        ec2.delete_security_group(GroupId=sg_id)
        print(f"  [ok]   SG {sg_id} ({GLUE_SG_NAME}) eliminado")
    except ClientError as e:
        print(f"  [warn] No se pudo eliminar SG: {e}")


if __name__ == "__main__":
    print("\n⚠️   tear_down.py — ELIMINA TODA LA INFRAESTRUCTURA ANALÍTICA\n")
    confirm = input("Escribe CONFIRMAR para continuar: ").strip()
    if confirm != "CONFIRMAR":
        print("Cancelado.")
        raise SystemExit(0)

    print("\n")
    print("1/4  Glue (triggers, jobs, connection, DB)...")
    delete_glue_resources()
    print("2/4  Athena Workgroup...")
    delete_athena_workgroup()
    print("3/4  S3 Bucket...")
    empty_and_delete_bucket()
    print("4/4  Security Group Glue...")
    delete_glue_sg()
    print("\n✅  Tear down completo.\n")
