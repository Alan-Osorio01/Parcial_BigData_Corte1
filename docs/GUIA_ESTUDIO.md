# Guía de estudio — Parcial 2 Big Data

Documento para entender **cómo funciona todo el proyecto** antes de la sustentación.  
Explica los 3 pipelines de CI/CD, las carpetas `etl/` e `infra/`, los tipos de ETLs y los tests.

---

## 1. Los 3 workflows de CI/CD

El proyecto tiene **tres pipelines diferentes** en `.github/workflows/`. Cada uno tiene un propósito distinto y se dispara en momentos diferentes.

### 1.1 `ci-cd.yml` — Tests antes de merge

**¿Para qué sirve?**  
Corre los tests del Parcial 1 (backend + frontend) **antes de que un Pull Request se haga merge**. Es la red de seguridad que evita que código roto entre a `main`.

**¿Cuándo se dispara?**  
Automático, cada vez que alguien **abre o actualiza un Pull Request hacia `main`**.

**¿Qué hace?**
1. Checkout del código
2. Instala Python 3.12 + dependencias del backend
3. Corre `pytest app/tests/ -v` (23 tests backend)
4. Instala Node 20 + dependencias del frontend
5. Corre `npm test` (14 tests frontend)

**¿Cómo disparo el pipeline?**  
No hay comando directo. Solo haz un Pull Request:
```bash
git checkout -b mi-rama
# hacer cambios
git add . && git commit -m "cambios"
git push origin mi-rama
# En GitHub: crear PR hacia main → el workflow se dispara solo
```

**¿Dónde veo el resultado?**  
GitHub → pestaña **Actions** → workflow "✅ CI — Tests"

---

### 1.2 `deploy.yml` — Desplegar la app (Parcial 1)

**¿Para qué sirve?**  
Despliega la aplicación (frontend + backend) a las EC2 cada vez que se hace push a `main`. Es el pipeline del **Parcial 1**.

**¿Cuándo se dispara?**  
Automático, cada `push` (o merge de PR) a la rama `main`.

**¿Qué hace?**
1. Corre los tests de backend y frontend (no despliega si fallan)
2. Si pasan, se conecta vía SSH a **EC2 Backend**:
   - `git pull origin main`
   - Reinstala dependencias Python
   - Reinicia servicio `chinook-backend` (systemd + FastAPI)
3. Luego se conecta vía SSH a **EC2 Frontend**:
   - `git pull origin main`
   - Construye el frontend (`npm run build`)
   - Copia los archivos a `/var/www/html/`
   - Reinicia Nginx

**¿Cómo disparo el pipeline?**  
Haciendo push a `main`:
```bash
git add .
git commit -m "cambios en la app"
git push origin main
```

**¿Qué secrets necesita?** (ya configurados en GitHub)
- `BACKEND_HOST` — IP pública de EC2 Backend
- `FRONTEND_HOST` — IP pública de EC2 Frontend
- `SSH_USER` — Usuario SSH (ubuntu)
- `SSH_PRIVATE_KEY` — Contenido del archivo `.pem`

---

### 1.3 `etl-deploy.yml` — Desplegar la capa analítica (Parcial 2)

**¿Para qué sirve?**  
Valida y despliega los scripts ETL (Glue Jobs) a AWS. Es el pipeline del **Parcial 2**.

**¿Cuándo se dispara?**
- **Automático** en cada push a `main` que modifique archivos de `etl/` o `infra/`
- **Manual** cuando necesites desplegar a AWS (porque los tokens de Academy rotan)

**¿Qué hace?**
1. **Job `test-etl`:** corre `pytest etl/tests/` (19 tests — DimDate + FactSales)
2. **Job `validate-scripts`:** verifica sintaxis Python + flake8 en `etl/` e `infra/`
3. **Job `deploy-and-update`** (solo manual): sube los scripts a S3 y actualiza los Glue Jobs

**¿Cómo disparo el pipeline?**

**Automático (solo tests y lint):**
```bash
# Modificar cualquier archivo en etl/ o infra/
git add etl/
git commit -m "actualizar ETL"
git push origin main
# → Los jobs 1 y 2 corren solos
```

**Manual (deploy real a AWS):**
1. **Actualizar secrets en GitHub** (porque las credenciales de Academy rotan cada 4h):
   - Ir a: `GitHub → Settings → Secrets and variables → Actions`
   - Actualizar: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
2. **Disparar el workflow manualmente:**
   - GitHub → pestaña **Actions** → workflow "ETL Analytics Pipeline"
   - Botón **Run workflow** → seleccionar rama `main`
   - En input `deploy`: escoger **`true`**
   - Click **Run workflow**

**¿Por qué el deploy es manual y no automático?**  
Las credenciales de AWS Academy expiran cada 4 horas. Si el deploy fuera automático a cada push, fallaría siempre que los tokens estén vencidos. Manual te da control de cuándo renovar secrets y disparar.

**Alternativa — ejecutar el deploy desde tu PC (sin GitHub Actions):**
```bash
cd "Parcial_BigData_Corte1"
.venv/bin/python infra/deploy_jobs.py
```

---

## 2. Carpeta `etl/` — Los jobs de transformación

```
etl/
├── glue_jobs/       ← Scripts PySpark (Glue ETL)
├── python_jobs/     ← Scripts Python puros (Glue Python Shell)
└── tests/           ← Pruebas unitarias
```

### 2.1 `etl/glue_jobs/` — Glue Spark Jobs

Son scripts que **usan PySpark** y corren en el motor distribuido de AWS Glue. Se usan cuando hay que procesar **grandes volúmenes de datos** o hacer **joins complejos**.

Archivos que viven aquí:

| Archivo | Tipo | ¿Qué hace? |
|---|---|---|
| `fact_sales_etl.py` | Spark ETL | Lee `invoice`, `invoice_line`, `customer` del RDS, hace joins, calcula `InvoiceDateKey` y `TotalAmount`, escribe Parquet particionado |
| `dim_customer_etl.py` | Glue Visual | Lee tabla `customer` del RDS, mapea columnas, guarda Parquet en `dim_customer/` |
| `dim_customer_history_etl.py` | Glue Visual | Snapshot diario de `customer` con `snapshot_date` |
| `dim_track_etl.py` | Glue Visual | Join `track + album + artist + genre + media_type`, guarda Parquet en `dim_track/` |
| `dim_employee_etl.py` | Glue Visual | Lee tabla `employee`, incluye campo `ReportsTo` (jerarquía) |
| `dim_employee_history_etl.py` | Glue Visual | Snapshot diario con `reports_to` |

**Configuración Glue:**
- `WorkerType: G.1X` (2 workers)
- `GlueVersion: 4.0` (Spark 3.3)
- `connection_type: postgresql` vía Glue Connection `chinook-rds` (menos `fact_sales_etl.py` que usa JDBC directo)

### 2.2 `etl/python_jobs/` — Python Shell Jobs

Son scripts **Python normales** (sin Spark) que corren en un worker ligero de Glue (`Python Shell`). Se usan cuando el dataset es **chiquito** y no necesitas paralelismo.

| Archivo | ¿Qué hace? |
|---|---|
| `dim_date_etl.py` | Genera un calendario 2009-2030 (8,035 fechas) con pandas + paquete `holidays` de Colombia, guarda Parquet local y lo sube a S3 con boto3 |

**¿Por qué DimDate va aquí y no en `glue_jobs/`?**  
Es un dataset de solo 8,035 filas. Usar Spark sería matar un mosquito con bazooka — y Python Shell es **10× más barato** que un Glue ETL worker.

### 2.3 ¿Cuáles ETLs son "full load" y cuáles son incrementales?

| ETL | Estrategia | ¿Por qué? |
|---|---|---|
| `dim_customer_etl` | **Overwrite** (full replace) | Pocos clientes, cambios raros |
| `dim_track_etl` | **Overwrite** (full replace) | Catálogo fijo |
| `dim_employee_etl` | **Overwrite** (full replace) | Muy pocos empleados |
| `dim_date_etl` | **Full replace** | Calendario estático |
| `dim_customer_history_etl` | **Append** (snapshot diario) | Para ver evolución histórica |
| `dim_employee_history_etl` | **Append** (snapshot diario) | Para rastrear cambios de `reports_to` |
| `fact_sales_etl` | **Overwrite** completo | Ver explicación abajo ⬇ |

---

## 3. Cómo funciona `fact_sales_etl.py` paso a paso

Es el ETL más complejo — te lo desgloso línea por línea.

### Paso 1: Configuración e inicialización
```python
JDBC_URL    = "jdbc:postgresql://chinook-db...:5432/chinook"
JDBC_PROPS  = {"user": "postgres", "password": "Parcial1", "driver": "org.postgresql.Driver"}
TARGET_PATH = "s3://chinook-datalake-academy/fact_sales/"
```

### Paso 2: Leer 3 tablas del RDS
```python
invoice_line_df = spark.read.jdbc(url, "invoice_line", props)  # ~2200 filas
invoice_df      = spark.read.jdbc(url, "invoice", props)       # facturas
customer_df     = spark.read.jdbc(url, "customer", props)      # clientes
```
Usamos **`spark.read.jdbc()` directo** (no `connection_type="postgresql"`) porque en AWS Academy, Glue no puede resolver conexiones VPC — este método bypasea ese sistema.

### Paso 3: Joins para armar los hechos
```python
# 1. invoice_line + invoice → trae invoice_date y customer_id
fact = invoice_line_df.join(invoice_df, on="invoice_id", how="inner")

# 2. Con customer → trae support_rep_id (que es el EmployeeKey)
fact = fact.join(customer_df, on="customer_id", how="left")
```

### Paso 4: Calcular columnas derivadas
```python
# InvoiceDateKey: convierte fecha a entero yyyymmdd
# Ej: 2026-04-21 → 20260421
InvoiceDateKey = year*10000 + month*100 + day

# TotalAmount: precio × cantidad
TotalAmount = unit_price * quantity

# year, month, day: para particionamiento físico en S3
year/month/day = componentes de invoice_date
```

### Paso 5: Seleccionar columnas finales con nombres del DW
```python
CustomerKey, TrackKey, InvoiceDateKey, EmployeeKey,
Quantity, UnitPrice, TotalAmount, year, month, day
```

### Paso 6: Escribir Parquet particionado en modo OVERWRITE
```python
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
fact.write.mode("overwrite").partitionBy("year", "month", "day").parquet(TARGET_PATH)
```

**¿Por qué OVERWRITE?**  
`spark.read.jdbc()` no soporta **Glue Job Bookmarks** (marcadores que dicen "solo procesa filas nuevas"). Si usáramos `append`, cada corrida duplicaría los datos. Con overwrite cada corrida regenera toda la tabla limpia — 2,246 filas se regeneran en segundos.

**Resultado en S3:**
```
fact_sales/year=2026/month=04/day=21/part-00000-xxx.snappy.parquet
fact_sales/year=2026/month=04/day=22/part-00000-xxx.snappy.parquet
fact_sales/year=2025/month=12/day=14/part-00000-xxx.snappy.parquet
...
```

---

## 4. Carpeta `infra/` — Automatización con boto3

Scripts Python que usan **boto3** (el SDK de AWS) para crear, desplegar y borrar toda la infraestructura analítica. El PDF del parcial dice literalmente _"Todo se puede crear utilizando boto3"_ — y estos scripts cumplen eso.

### 4.1 `provision_infra.py` — Crear todo desde cero

**Uso:**
```bash
.venv/bin/python infra/provision_infra.py
```

**Qué hace** (en orden):
1. Crea el bucket S3 `chinook-datalake-academy` con 9 carpetas
2. Crea el Security Group `glue-chinook-workers` con regla self-reference (requisito de Glue)
3. Abre el puerto 5432 en el SG del RDS para que Glue pueda conectarse
4. Crea la Glue Connection `chinook-rds` (JDBC PostgreSQL)
5. Crea la Glue Database `chinook_dw`
6. Crea el Athena Workgroup `chinook-wg`

**¿Es seguro correrlo dos veces?**  
Sí — es **idempotente**. Si un recurso ya existe, lo saltea sin error.

### 4.2 `deploy_jobs.py` — Subir ETLs a S3 y crear Glue Jobs

**Uso:**
```bash
.venv/bin/python infra/deploy_jobs.py
```

**Qué hace:**
1. Lee todos los `.py` de `etl/glue_jobs/` y `etl/python_jobs/`
2. Los sube a `s3://chinook-datalake-academy/scripts/`
3. Por cada script, crea (o actualiza) un Glue Job con la configuración correcta:
   - **glueetl** para los de `glue_jobs/` (WorkerType G.1X, 2 workers)
   - **pythonshell** para los de `python_jobs/` (MaxCapacity 0.0625)

### 4.3 `create_athena_tables.py` — Ejecutar los DDLs en Athena

**Uso:**
```bash
.venv/bin/python infra/create_athena_tables.py
```

**Qué hace:**  
Lee `infra/athena_ddls.sql` y ejecuta cada `CREATE EXTERNAL TABLE` en Athena (via el workgroup `chinook-wg`). Al final ejecuta `MSCK REPAIR TABLE fact_sales` para cargar las particiones.

### 4.4 `schedule_jobs.py` — Crear Glue Triggers horarios

**Uso:**
```bash
.venv/bin/python infra/schedule_jobs.py
```

**Qué hace:**  
Crea 5 Glue Triggers que ejecutan los ETLs cada hora, escalonados cada 5 minutos:
```
00 min → dim-date-etl
05 min → dim-customer-etl
10 min → dim-track-etl
15 min → dim-employee-etl
20 min → fact-sales-etl
```

**Importante:** los triggers se crean con `StartOnCreation=False` (apagados) para no gastar créditos de Academy. Para activarlos: Glue Console → Triggers → botón Enable.

### 4.5 `tear_down.py` — Borrar todo

**Uso:**
```bash
.venv/bin/python infra/tear_down.py
# Pide confirmación: escribir CONFIRMAR
```

**Qué hace:**  
Elimina **toda** la infraestructura analítica en orden correcto (primero los recursos que dependen de otros):
1. Triggers
2. Glue Jobs
3. Glue Connection
4. Glue Database
5. Athena Workgroup
6. Bucket S3 (con todos sus archivos)
7. Security Group de Glue

Útil para resetear cuando algo queda mal o para limpiar al final del curso.

### 4.6 `athena_ddls.sql` — Los CREATE TABLE

No es un script Python sino un archivo SQL con las 5 definiciones de tablas externas de Athena + el `MSCK REPAIR TABLE fact_sales`. Lo consume `create_athena_tables.py`.

---

## 5. Tests unitarios — Qué testean

Tenemos **19 tests** en `etl/tests/` dividido en 2 archivos.

### 5.1 `test_dim_date.py` — 10 tests (Ana)

Prueban que el ETL de DimDate genera un calendario correcto:

| Test | Qué verifica |
|---|---|
| `test_rango_fechas_correcto` | Genera al menos 8,000 días (2009-2030) |
| `test_datekey_formato_yyyymmdd` | El DateKey es un entero de 8 dígitos |
| `test_unicidad_datekey` | No hay fechas duplicadas |
| `test_navidad_es_festivo` | El 25-dic-2026 tiene `IsHoliday=True` |
| `test_dia_semana_correcto` | El 04-ene-2026 es Sunday |
| `test_quarter_correcto` | Enero está en Q1 |
| `test_rango_mes` | Meses entre 1 y 12 |
| `test_rango_dia` | Días entre 1 y 31 |
| `test_sin_nulos` | Ninguna celda es NULL |
| `test_columnas_correctas` | Las 8 columnas esperadas existen |

### 5.2 `test_fact_sales.py` — 9 tests (Alan)

Prueban las **transformaciones puras** del ETL de FactSales (sin depender de Spark ni AWS):

| Test | Qué verifica |
|---|---|
| `test_invoice_date_key_formato_yyyymmdd` | Fecha 2026-04-21 → 20260421 |
| `test_invoice_date_key_primer_dia_anio` | 2025-01-01 → 20250101 |
| `test_invoice_date_key_ultimo_dia_anio` | 2025-12-31 → 20251231 |
| `test_invoice_date_key_longitud` | Siempre retorna 8 dígitos |
| `test_total_amount_unitario` | 0.99 × 1 = 0.99 |
| `test_total_amount_multiples_cantidades` | 0.99 × 4 = 3.96 |
| `test_total_amount_precio_alto` | 1.99 × 10 = 19.90 |
| `test_total_amount_sin_overflow_decimal` | Redondeo a 2 decimales |
| `test_extraer_particiones_year_month_day` | Extracción correcta de year/month/day |

### 5.3 Cómo correrlos

```bash
# Localmente
cd "Parcial_BigData_Corte1"
.venv/bin/python -m pytest etl/tests/ -v

# En CI: se corren solos en cada push
```

### 5.4 ¿Por qué no hay tests para los ETLs de dimensiones (Daniela)?

Porque esos ETLs son **Glue Visual Studio** exportados — el código generado automáticamente es muy acoplado al runtime de Glue y testearlo localmente requiere Spark + todas las dependencias de Glue (complicado).

El PDF solo exige _"pruebas unitarias"_ en general, no una prueba por tabla. Con los 19 tests que tenemos, cubrimos lo crítico: la **lógica de transformación** de FactSales y DimDate.

---

## 6. Cómo funciona el flujo end-to-end

Para entender toda la cadena de un vistazo:

```
┌────────────────────────────────────────────────────────────────┐
│  Usuario compra canciones en http://<IP_FRONTEND>               │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│  Backend FastAPI (EC2) recibe POST /api/purchase                │
│  → INSERT en tabla invoice + invoice_line del RDS PostgreSQL    │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│  Glue Job fact-sales-etl (manual o trigger cada hora)           │
│  → Lee invoice + invoice_line + customer del RDS                │
│  → Joins + cálculo de InvoiceDateKey y TotalAmount              │
│  → Escribe Parquet en s3://.../fact_sales/year=.../month=.../   │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│  Glue Data Catalog registra la tabla fact_sales                 │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│  Athena (chinook-wg) consulta el Parquet de S3 con SQL          │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│  Power BI Desktop (ODBC Simba) refresca los 4 dashboards        │
└────────────────────────────────────────────────────────────────┘
```

Tiempo total: **~3 minutos** desde la compra hasta ver el dato en Power BI.

---

## 7. Cosas que conviene repasar antes de la sustentación

### Para la demo en vivo
1. **Tener credenciales de AWS Academy frescas** el día de la entrega
2. **Orden de demo sugerido (10-15 min):**
   - Mostrar la app Parcial 1 funcionando → hacer una compra
   - Mostrar el RDS con `psql` (verificar la compra nueva)
   - Correr `fact-sales-etl` en Glue Console
   - Hacer una query en Athena con el `MAX(InvoiceDateKey)`
   - Refrescar Power BI → mostrar el dato nuevo en el dashboard
   - Mostrar que `git push` dispara el CI/CD y corre los tests

### Conceptos que pueden preguntar
- **¿Qué es un modelo estrella?** — una tabla central de hechos (FactSales) rodeada de tablas de dimensiones (DimDate, DimCustomer, DimTrack, DimEmployee)
- **¿Qué es un DateKey?** — entero yyyymmdd que funciona como clave foránea a DimDate; ahorra espacio comparado con guardar la fecha completa y acelera joins
- **¿Por qué particionar por año/mes/día?** — Athena solo lee los archivos de las particiones que coincidan con el filtro (pruning), reduciendo datos escaneados y costo
- **¿Por qué Parquet y no CSV?** — Parquet es columnar, comprimido (Snappy), con esquema embebido y ~10x más rápido en queries analíticas
- **¿Qué es un Glue Bookmark?** — marcador que guarda qué filas ya procesó un job para solo leer lo nuevo en la próxima corrida. No lo usamos en FactSales porque `spark.read.jdbc` no lo soporta, por eso vamos con overwrite
- **¿Por qué hay dos dimensiones `_history`?** — para poder reconstruir la jerarquía `reports_to` o el estado de un cliente en una fecha pasada
- **¿Por qué Python Shell para DimDate y Spark para FactSales?** — DimDate son 8K filas, Spark sería ineficiente. FactSales involucra joins entre tablas, Spark optimiza joins distribuidos

### Troubleshooting común
- **"Unable to resolve any valid connection"** en Glue → eliminar la VPC/connection del job, usar `spark.read.jdbc()` directo
- **"Empty partitions"** → credenciales AWS expiradas o el JAR JDBC no está en S3
- **Duplicados en fact_sales** → verificar que el job use `mode("overwrite")`, no append
- **Tokens expirados en CI/CD** → actualizar los 3 secrets de AWS en GitHub Settings

---

## 8. Comandos de referencia rápida

```bash
# Ver estado del repo
git status
git log --oneline -10

# Correr tests ETL localmente
.venv/bin/python -m pytest etl/tests/ -v

# Verificar credenciales AWS
.venv/bin/python -c "import boto3; print(boto3.client('sts').get_caller_identity())"

# Listar tablas de Glue Catalog
.venv/bin/python -c "import boto3; print([t['Name'] for t in boto3.client('glue').get_tables(DatabaseName='chinook_dw')['TableList']])"

# Correr query rápida en Athena (desde boto3)
# Ver infra/create_athena_tables.py para patrón

# Levantar infra desde cero
.venv/bin/python infra/provision_infra.py
.venv/bin/python infra/deploy_jobs.py
.venv/bin/python infra/create_athena_tables.py

# Tear down
.venv/bin/python infra/tear_down.py
```
