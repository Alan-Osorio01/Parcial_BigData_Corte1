import boto3
from botocore.exceptions import ClientError
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────────────────
REGION          = "us-east-1"
BUCKET          = "chinook-datalake-academy"
LAB_ROLE_ARN    = "arn:aws:iam::611318804612:role/LabRole"
GLUE_CONNECTION = "chinook-rds"

GLUE_JOBS_DIR   = Path(__file__).parent.parent / "etl" / "glue_jobs"
PYTHON_JOBS_DIR = Path(__file__).parent.parent / "etl" / "python_jobs"

# Configuración de cada job: type, glue_version, workers (None = pythonshell)
JOB_CONFIGS = {
    "dim_customer_etl":         {"type": "glueetl",     "glue_version": "4.0", "workers": 2},
    "dim_customer_history_etl": {"type": "glueetl",     "glue_version": "4.0", "workers": 2},
    "dim_track_etl":            {"type": "glueetl",     "glue_version": "4.0", "workers": 2},
    "dim_employee_etl":         {"type": "glueetl",     "glue_version": "4.0", "workers": 2},
    "dim_employee_history_etl": {"type": "glueetl",     "glue_version": "4.0", "workers": 2},
    "fact_sales_etl":           {"type": "glueetl",     "glue_version": "4.0", "workers": 2},
    "dim_date_etl":             {"type": "pythonshell", "glue_version": "3.0", "workers": None},
}
# ─────────────────────────────────────────────────────────────────────────────

s3   = boto3.client("s3",   region_name=REGION)
glue = boto3.client("glue", region_name=REGION)


def upload_script(local_path: Path) -> str:
    key = f"scripts/{local_path.name}"
    s3.upload_file(str(local_path), BUCKET, key)
    s3_path = f"s3://{BUCKET}/{key}"
    print(f"  [ok]   {local_path.name} → {s3_path}")
    return s3_path


def build_job_input(name: str, script_s3: str, config: dict) -> dict:
    job_input = {
        "Role": LAB_ROLE_ARN,
        "Command": {
            "Name": config["type"],
            "ScriptLocation": script_s3,
            "PythonVersion": "3",
        },
        "DefaultArguments": {
            "--job-bookmark-option": "job-bookmark-enable",
            "--enable-metrics": "true",
            "--enable-continuous-cloudwatch-log": "true",
        },
        "GlueVersion": config["glue_version"],
        "MaxRetries": 0,
        "Timeout": 60,
    }

    if config["type"] == "glueetl":
        job_input["NumberOfWorkers"] = config["workers"]
        job_input["WorkerType"] = "G.1X"
        job_input["Connections"] = {"Connections": [GLUE_CONNECTION]}
    else:
        # Python Shell no usa WorkerType — usa MaxCapacity
        job_input["MaxCapacity"] = 0.0625

    return job_input


def upsert_job(name: str, script_s3: str, config: dict):
    job_name = name.replace("_", "-")
    job_input = build_job_input(job_name, script_s3, config)

    try:
        glue.get_job(JobName=job_name)
        glue.update_job(JobName=job_name, JobUpdate=job_input)
        print(f"  [upd]  Job {job_name} actualizado")
    except ClientError:
        glue.create_job(Name=job_name, **job_input)
        print(f"  [ok]   Job {job_name} creado")


if __name__ == "__main__":
    print("\n=== deploy_jobs.py ===\n")

    script_map: dict[str, str] = {}

    print("Subiendo scripts a S3...")
    for directory in [GLUE_JOBS_DIR, PYTHON_JOBS_DIR]:
        if directory.exists():
            for f in sorted(directory.glob("*.py")):
                script_map[f.stem] = upload_script(f)
        else:
            print(f"  [warn] Carpeta {directory} no existe aún")

    if not script_map:
        print("\n  Sin scripts que desplegar — agrega ETLs en etl/glue_jobs/ o etl/python_jobs/")
    else:
        print("\nCreando/actualizando Glue Jobs...")
        for job_name, config in JOB_CONFIGS.items():
            if job_name in script_map:
                upsert_job(job_name, script_map[job_name], config)
            else:
                print(f"  [warn] {job_name}.py no encontrado, saltando")

    print("\n✅  Jobs desplegados.\n")
