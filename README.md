# Chinook Music Store — Big Data

Proyecto completo del curso de Big Data (Semestre 8) que cubre dos parciales:

1. **Parcial 1 — Aplicación OLTP:** tienda de música Full Stack (React + FastAPI + RDS PostgreSQL) desplegada en AWS con CI/CD.
2. **Parcial 2 — Capa Analítica:** Data Warehouse con modelo estrella en S3 + AWS Glue + Athena + Power BI, alimentado desde el OLTP del Parcial 1.

**Autores:** Alan Osorio · Daniela López · Ana Amador  
**Curso:** Big Data — Semestre 8

---

## Arquitectura global

```
┌──────────────────────────────────────────────────────────────────────┐
│                            AWS Cloud                                  │
│                                                                       │
│  ┌─────────────── PARCIAL 1 — OLTP ─────────────────┐                │
│  │                                                    │                │
│  │   Usuario → EC2 Frontend (React+Nginx)            │                │
│  │                 │                                   │                │
│  │                 ▼                                   │                │
│  │         EC2 Backend (FastAPI)                      │                │
│  │                 │                                   │                │
│  │                 ▼                                   │                │
│  │       RDS PostgreSQL — Chinook DB                  │                │
│  │       (invoice, track, customer, employee...)      │                │
│  └─────────────────┬──────────────────────────────────┘                │
│                    │                                                   │
│                    │  (JDBC)                                           │
│                    ▼                                                   │
│  ┌──────────── PARCIAL 2 — ANALÍTICA ─────────────────┐                │
│  │                                                     │                │
│  │   AWS Glue                                          │                │
│  │     ├─ Visual ETL: DimCustomer, DimTrack, DimEmp.   │                │
│  │     ├─ Python Shell: DimDate (paquete holidays)     │                │
│  │     └─ Spark ETL: FactSales (joins + partitions)    │                │
│  │            │                                         │                │
│  │            ▼                                         │                │
│  │   S3 Data Lake (Parquet particionado y/m/d)         │                │
│  │            │                                         │                │
│  │            ▼                                         │                │
│  │   Glue Data Catalog (chinook_dw)                    │                │
│  │            │                                         │                │
│  │            ▼                                         │                │
│  │   Athena (workgroup chinook-wg)                     │                │
│  │            │                                         │                │
│  │            ▼                                         │                │
│  │   Power BI Desktop — 4 Dashboards                   │                │
│  └─────────────────────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
```

Diagrama editable: [`docs/arch.drawio`](./docs/arch.drawio)

---

## Preguntas de negocio que responde

La capa analítica contesta las 4 preguntas del parcial, consultables en Athena:

1. **Canciones vendidas por día** — `SUM(Quantity)` agrupado por `DimDate.FullDate`
2. **Artista más vendido por mes** — Join de `FactSales + DimDate + DimTrack`
3. **Día de la semana con más compras** — Agrupado por `DimDate.DayOfWeek`
4. **Mes con mayor número de ventas** — Agrupado por `DimDate.Year, Month`

Todas las queries validadas end-to-end contra datos reales (2,246+ filas en `fact_sales`).

---

## Estructura del repositorio

```
Parcial_BigData_Corte1/
│
├── backend/                     # Parcial 1 — API FastAPI
│   └── app/
│       ├── models/              # SQLAlchemy ORM (Chinook + users)
│       ├── schemas/             # Pydantic
│       ├── routers/             # Endpoints /auth /tracks /purchase
│       ├── services/            # Lógica de negocio
│       └── tests/               # pytest — 23 tests
│
├── frontend/                    # Parcial 1 — SPA React + Vite
│   └── src/
│       ├── pages/               # Home, Tracks, Purchase, Admin, etc.
│       ├── components/          # Navbar, Cart, etc.
│       ├── services/api.js      # Cliente Axios
│       └── tests/               # Vitest — 14 tests
│
├── infra/                       # Parcial 2 — Scripts boto3 de infraestructura
│   ├── provision_infra.py       # Crea bucket S3, SG, Glue Connection, DB, Athena WG
│   ├── deploy_jobs.py           # Sube ETLs a S3 y crea/actualiza Glue Jobs
│   ├── create_athena_tables.py  # Ejecuta los 5 DDLs en Athena
│   ├── schedule_jobs.py         # Crea Glue Triggers horarios
│   ├── tear_down.py             # Elimina toda la infra analítica
│   └── athena_ddls.sql          # CREATE EXTERNAL TABLE + MSCK REPAIR
│
├── etl/                         # Parcial 2 — Jobs ETL
│   ├── glue_jobs/               # Glue Spark
│   │   ├── fact_sales_etl.py
│   │   ├── dim_customer_etl.py
│   │   ├── dim_customer_history_etl.py
│   │   ├── dim_track_etl.py
│   │   ├── dim_employee_etl.py
│   │   └── dim_employee_history_etl.py
│   ├── python_jobs/             # Glue Python Shell
│   │   └── dim_date_etl.py
│   └── tests/                   # pytest — 19 tests de transformaciones
│       ├── test_dim_date.py     # 10 tests
│       └── test_fact_sales.py   # 9 tests
│
├── powerbi/                     # Parcial 2 — Dashboards
│   └── chinook_analytics.pbix
│
├── docs/                        # Documentación
│   └── arch.drawio              # Diagrama de arquitectura
│
├── .github/workflows/           # CI/CD
│   ├── ci-cd.yml                # Tests en pull request
│   ├── deploy.yml               # Deploy app a EC2
│   └── etl-deploy.yml           # Deploy ETLs a Glue + S3
│
├── Chinook_PostgreSql.sql       # Schema + seed de la base Chinook
├── requirements.txt             # Dependencias Python
├── README.md                    # Este archivo
└── ONBOARDING.md                # Guía completa de onboarding y re-despliegue
```

---

## Stack tecnológico

### Parcial 1 — Aplicación

| Capa | Tecnologías |
|---|---|
| Frontend | React 18, Vite, React Router, Axios, Vitest |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Pydantic, JWT, pytest |
| Infra | AWS EC2 (x2), AWS RDS PostgreSQL, GitHub Actions |

### Parcial 2 — Analítica

| Capa | Tecnologías |
|---|---|
| ETL | AWS Glue (Visual + Spark + Python Shell), PySpark 3.3, paquete `holidays` |
| Storage | AWS S3 (Parquet Snappy particionado year/month/day) |
| Query | AWS Athena + Glue Data Catalog |
| Visualización | Power BI Desktop + driver ODBC Simba |
| Automatización | boto3 (provision, deploy, schedule, tear down), GitHub Actions |

---

## Recursos AWS desplegados

| Recurso | Nombre | Propósito |
|---|---|---|
| S3 Bucket | `chinook-datalake-academy` | Data Lake (Parquet) |
| Glue Database | `chinook_dw` | Catálogo de tablas analíticas |
| Glue Connection | `chinook-rds` | JDBC al RDS OLTP |
| Glue Jobs (x7) | `fact-sales-etl`, `dim-*-etl` | ETLs Spark + Python Shell |
| Athena Workgroup | `chinook-wg` | Motor SQL sobre S3 |
| IAM Role | `LabRole` | Rol compartido de AWS Academy |

---

## Modelo estrella

```
              ┌───────────────┐
              │  DimCustomer  │
              │  CustomerKey  │
              └───────┬───────┘
                      │
 ┌───────────────┐    │    ┌───────────────┐
 │   DimTrack    │────┤────│   DimDate     │
 │   TrackKey    │    │    │   DateKey     │
 └───────────────┘    │    └───────────────┘
                      │
             ┌────────▼──────────┐
             │    FactSales      │
             │    ───────────    │
             │    CustomerKey FK │
             │    TrackKey    FK │
             │    InvoiceDateKey │
             │    EmployeeKey FK │
             │    Quantity       │
             │    UnitPrice      │
             │    TotalAmount    │
             └────────┬──────────┘
                      │
              ┌───────▼───────┐
              │  DimEmployee  │
              │  EmployeeKey  │
              └───────────────┘
```

Las dimensiones `DimCustomer_History` y `DimEmployee_History` guardan snapshots diarios para análisis histórico.

---

## Testing

Pruebas unitarias en todas las capas:

| Capa | Archivo | Tests | Estado |
|---|---|---|---|
| Backend Endpoints | `backend/app/tests/test_endpoints.py` | 11 | ✅ |
| Backend Services | `backend/app/tests/test_services.py` | 12 | ✅ |
| Frontend Components | `frontend/src/tests/*.jsx` | 9 | ✅ |
| Frontend API | `frontend/src/tests/api.test.js` | 5 | ✅ |
| ETL DimDate | `etl/tests/test_dim_date.py` | 10 | ✅ |
| ETL FactSales | `etl/tests/test_fact_sales.py` | 9 | ✅ |
| **Total** | | **56** | **100%** |

### Correr tests localmente

```bash
# Backend
cd backend && pytest app/tests/ -v

# Frontend
cd frontend && npm test

# ETL
python -m venv .venv
.venv/bin/pip install pytest pandas pyarrow holidays
.venv/bin/python -m pytest etl/tests/ -v
```

---

## Pipeline CI/CD

Tres workflows independientes:

| Workflow | Trigger | Qué hace |
|---|---|---|
| `ci-cd.yml` | PR a `main` | Corre tests backend + frontend |
| `deploy.yml` | Push a `main` | SSH a EC2s → `git pull` → rebuild + restart |
| `etl-deploy.yml` | Push a `main` en `etl/` o `infra/` | Tests ETL + lint. Deploy manual con `workflow_dispatch` |

### Secrets requeridos en GitHub

```
# Parcial 1
BACKEND_HOST, FRONTEND_HOST, SSH_USER, SSH_PRIVATE_KEY

# Parcial 2 (AWS Academy — rotan cada 4h)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
AWS_REGION = us-east-1
```

---

## Flujo end-to-end validado

1. Usuario compra canciones en la app (frontend)
2. Backend genera `invoice` + `invoice_line` en RDS
3. Glue Job `fact-sales-etl` lee los cambios del RDS vía JDBC
4. Escribe Parquet en S3 particionado por year/month/day (modo overwrite)
5. Glue Catalog registra las particiones automáticamente
6. Athena queries retornan la compra nueva en segundos
7. Power BI refresca dashboards con los datos actualizados

Tiempo total: **~3 minutos** desde la compra hasta ver el dato en Power BI.

---

## Levantar la infraestructura analítica desde cero

```bash
# 1. Clonar y entrar al repo
git clone https://github.com/Alan-Osorio01/Parcial_BigData_Corte1.git
cd Parcial_BigData_Corte1

# 2. Crear venv e instalar deps
python3 -m venv .venv
.venv/bin/pip install boto3 pytest pandas pyarrow holidays

# 3. Configurar credenciales de AWS Academy en ~/.aws/credentials

# 4. Provisionar toda la infraestructura
.venv/bin/python infra/provision_infra.py

# 5. Desplegar los 7 ETLs a Glue
.venv/bin/python infra/deploy_jobs.py

# 6. Crear las tablas en Athena
.venv/bin/python infra/create_athena_tables.py

# 7. Correr los Glue Jobs en Console → Jobs → Run
#    Orden recomendado: DimDate → Dimensiones → FactSales

# 8. Abrir powerbi/chinook_analytics.pbix en Power BI Desktop
#    y refrescar los datos
```

Guía detallada paso a paso en [`ONBOARDING.md`](./ONBOARDING.md).

---

## Consideraciones de AWS Academy

- Credenciales temporales (rotan cada 4h) — actualizar `~/.aws/credentials` y GitHub Secrets cuando roten
- Usar siempre el rol `LabRole` — Academy no permite crear IAM roles nuevos
- `fact_sales_etl.py` usa `spark.read.jdbc()` directo (sin Glue Connection Catalog) para evitar errores de resolución de conexiones en Academy
- Modo de escritura OVERWRITE en FactSales para evitar duplicados, ya que `spark.read.jdbc` no soporta Glue Bookmarks

---

## Documentación adicional

- [ONBOARDING.md](./ONBOARDING.md) — guía completa de onboarding, re-despliegue en nueva cuenta AWS y troubleshooting
- [docs/arch.drawio](./docs/arch.drawio) — diagrama de arquitectura editable
- [infra/athena_ddls.sql](./infra/athena_ddls.sql) — DDLs de las 5 tablas de Athena

---

## Autores

- **Alan Osorio** — Infraestructura, FactSales ETL, CI/CD analítico, documentación
- **Daniela López** — Visual ETLs (DimCustomer, DimTrack, DimEmployee) + snapshots históricos
- **Ana Amador** — DimDate Python ETL, DDLs Athena, tests unitarios, Power BI dashboards
