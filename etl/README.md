# ETL — Chinook Analytics

## Estructura

```
etl/
├── glue_jobs/      # Scripts Glue Spark (Daniela)
├── python_jobs/    # Scripts Python Shell (Ana)
└── tests/          # pytest (Ana)
```

## Jobs y estrategia de carga

| Job | Tipo | Incremental | Responsable |
|-----|------|-------------|-------------|
| dim_customer_etl | Glue ETL | Sí (bookmark) | Daniela |
| dim_customer_history_etl | Glue ETL | No (full copy) | Daniela |
| dim_track_etl | Glue ETL | Sí (bookmark) | Daniela |
| dim_employee_etl | Glue ETL | No (full copy) | Daniela |
| dim_employee_history_etl | Glue ETL | No (full copy + snapshot_date) | Daniela |
| fact_sales_etl | Glue ETL | Sí (bookmark en invoice_date) | Alan |
| dim_date_etl | Python Shell | No (full replace 2009-2030) | Ana |

## Desplegar jobs a AWS

```bash
cd infra
python deploy_jobs.py
```

## Correr tests localmente

```bash
pip install pytest pyspark pandas pyarrow holidays
pytest etl/tests/ -v
```
