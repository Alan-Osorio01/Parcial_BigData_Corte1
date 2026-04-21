# ONBOARDING — Chinook Music Store

Guía completa de contexto, arquitectura y re-despliegue del proyecto.  
Destinada a nuevos integrantes del equipo o para migrar la infraestructura a una nueva cuenta AWS.

**Autores:** Alan Osorio · Daniela López · Ana Amador  
**Materia:** Big Data — Semestre 8  
**Última actualización:** Abril 2026

---

## Tabla de Contenidos

1. [¿Qué es este proyecto?](#1-qué-es-este-proyecto)
2. [Arquitectura AWS](#2-arquitectura-aws)
3. [Stack tecnológico](#3-stack-tecnológico)
4. [Estructura del código](#4-estructura-del-código)
5. [Base de datos](#5-base-de-datos)
6. [API — Endpoints documentados](#6-api--endpoints-documentados)
7. [Autenticación y roles](#7-autenticación-y-roles)
8. [Flujos principales de la app](#8-flujos-principales-de-la-app)
9. [Variables de entorno](#9-variables-de-entorno)
10. [Pipeline CI/CD](#10-pipeline-cicd)
11. [Cómo correr los tests](#11-cómo-correr-los-tests)
12. [Guía de re-despliegue en nueva cuenta AWS](#12-guía-de-re-despliegue-en-nueva-cuenta-aws)
13. [Problemas conocidos y notas importantes](#13-problemas-conocidos-y-notas-importantes)
14. [Capa Analítica — ETL + Athena + Power BI](#14-capa-analítica--etl--athena--power-bi)

---

## 1. ¿Qué es este proyecto?

**Chinook Music Store** es una aplicación web Full Stack que simula una tienda de música en línea. Está construida sobre la base de datos pública **Chinook** (artistas, álbumes, canciones, clientes y facturas) y añade un sistema de autenticación con roles y un flujo de compra.

Funcionalidades principales:
- Explorar y buscar canciones por nombre, artista o género
- Registrarse e iniciar sesión con JWT
- Procesar compras (genera facturas en la base de datos)
- Panel de administración (rol `admin`)

La app corre en **AWS**: dos instancias EC2 (frontend y backend) y una base de datos RDS PostgreSQL en subred privada.

---

## 2. Arquitectura AWS

```
                        Internet
                           |
                    [ Usuario final ]
                           |
              ┌────────────▼────────────┐
              │   EC2 #1 — Frontend     │  (Public Subnet)
              │   Ubuntu + Nginx        │
              │   Sirve React build     │
              │   Puerto: 80            │
              └────────────┬────────────┘
                           │ HTTP (API calls)
              ┌────────────▼────────────┐
              │   EC2 #2 — Backend      │  (Public Subnet)
              │   Ubuntu + FastAPI      │
              │   Gunicorn + Uvicorn    │
              │   Puerto: 8000          │
              └────────────┬────────────┘
                           │ PostgreSQL (5432)
              ┌────────────▼────────────┐
              │   RDS PostgreSQL        │  (Private Subnet)
              │   Base de datos Chinook │
              │   No accesible desde    │
              │   internet              │
              └─────────────────────────┘
```

### Security Groups

| Recurso | Inbound permitido | Notas |
|---|---|---|
| EC2 Frontend | 80 (HTTP), 443 (HTTPS), 22 (SSH) | Desde anywhere |
| EC2 Backend | 8000 (API), 22 (SSH) | Puerto 8000 desde anywhere |
| RDS | 5432 (PostgreSQL) | Solo desde SG del Backend |

---

## 3. Stack tecnológico

### Backend

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.12 | Lenguaje |
| FastAPI | 0.135.1 | Framework REST API |
| Uvicorn | 0.41.0 | Servidor ASGI |
| SQLAlchemy | 2.0.48 | ORM |
| Psycopg2-binary | 2.9.11 | Driver PostgreSQL |
| Pydantic | 2.12.5 | Validación de schemas |
| PyJWT / Python-jose | 3.5.0 | Tokens JWT |
| Passlib + Bcrypt | 1.7.4 / 3.2.2 | Hash de contraseñas |
| Pytest | 9.0.2 | Tests unitarios |
| Python-dotenv | 1.2.2 | Variables de entorno |

### Frontend

| Tecnología | Versión | Propósito |
|---|---|---|
| React | 18.3.1 | Framework UI |
| React Router DOM | 6.22.0 | Routing |
| Vite | 7.3.1 | Build tool |
| Axios | 1.6.0 | HTTP client |
| Vitest | 2.0.0 | Tests unitarios |
| React Testing Library | 16.0.0 | Testing de componentes |

### Infraestructura

| Servicio | Uso |
|---|---|
| AWS EC2 (x2) | Hosting frontend y backend |
| AWS RDS PostgreSQL | Base de datos |
| GitHub Actions | CI/CD automatizado |

---

## 4. Estructura del código

```
Parcial_BigData_Corte1/
│
├── .github/workflows/
│   ├── deploy.yml          # Pipeline de despliegue automático a EC2s
│   └── ci-cd.yml           # (Vacío — placeholder para tests en CI)
│
├── backend/
│   └── app/
│       ├── main.py         # Entry point FastAPI: registra routers, CORS, exception handler
│       ├── database.py     # Conexión SQLAlchemy + función get_db() (dependency injection)
│       ├── auth.py         # JWT (crear/validar tokens), Bcrypt (hash contraseñas), decoradores de rol
│       ├── models/
│       │   └── __init__.py # 8 modelos ORM: Artist, Album, Genre, Track, Customer, Invoice, InvoiceLine, User
│       ├── schemas/
│       │   └── __init__.py # Schemas Pydantic: validación de requests y responses
│       ├── routers/
│       │   └── __init__.py # 12 endpoints agrupados: /auth, /tracks, /customers, /purchase
│       ├── services/
│       │   └── __init__.py # Lógica de negocio: search_tracks, purchase_tracks, etc.
│       └── tests/
│           ├── conftest.py       # Fixtures: BD SQLite en memoria, TestClient
│           ├── test_endpoints.py # 6 tests de endpoints HTTP
│           └── test_services.py  # 6 tests de servicios/lógica
│
├── frontend/
│   └── src/
│       ├── main.jsx              # Punto de entrada React
│       ├── App.jsx               # Rutas + AuthProvider wrapper
│       ├── components/
│       │   └── Navbar.jsx        # Barra de navegación con control de sesión
│       ├── pages/
│       │   ├── Home.jsx          # Landing page
│       │   ├── Tracks.jsx        # Catálogo con búsqueda
│       │   ├── Purchase.jsx      # Checkout (seleccionar cliente + canciones)
│       │   ├── Login.jsx         # Formulario de login
│       │   ├── Register.jsx      # Formulario de registro
│       │   └── Admin.jsx         # Panel admin (protegido por rol)
│       ├── services/
│       │   └── api.js            # Axios instance + 6 funciones de API
│       └── tests/
│           ├── setup.js          # Config Vitest (jsdom)
│           ├── api.test.js       # 5 tests del cliente API
│           ├── Navbar.test.jsx   # 9 tests del componente Navbar
│           └── Home.test.jsx     # Tests de Home
│
├── Chinook_PostgreSql.sql  # Schema completo de la BD con datos (~15,876 líneas)
├── README.md               # Overview del proyecto
└── ONBOARDING.md           # Este archivo
```

---

## 5. Base de datos

### Tablas Chinook (datos del negocio)

| Tabla | Descripción | Columnas principales |
|---|---|---|
| `artist` | Artistas musicales | artist_id, name |
| `album` | Álbumes | album_id, title, artist_id |
| `genre` | Géneros musicales | genre_id, name |
| `track` | Canciones | track_id, name, album_id, genre_id, unit_price |
| `customer` | Clientes de la tienda | customer_id, first_name, last_name, email |
| `invoice` | Facturas de compra | invoice_id, customer_id, invoice_date, total |
| `invoice_line` | Líneas de factura | invoice_line_id, invoice_id, track_id, unit_price, quantity |
| `media_type` | Tipos de archivo | media_type_id, name |
| `playlist` | Listas de reproducción | playlist_id, name |
| `playlist_track` | Relación playlist-track | playlist_id, track_id |
| `employee` | Empleados | employee_id, nombre, cargo, etc. |

### Tabla custom (autenticación)

| Tabla | Descripción | Columnas |
|---|---|---|
| `users` | Usuarios de la app | user_id, email, password (hashed), role, created_at |

**Roles disponibles:** `admin` / `usuario`

### Cargar la base de datos

```bash
# En el servidor de base de datos RDS (desde EC2 Backend)
psql -h <RDS_ENDPOINT> -U <DB_USER> -d postgres -c "CREATE DATABASE chinook;"
psql -h <RDS_ENDPOINT> -U <DB_USER> -d chinook -f Chinook_PostgreSql.sql
```

La tabla `users` se crea automáticamente al iniciar FastAPI por primera vez (SQLAlchemy `create_all`).

---

## 6. API — Endpoints documentados

**Base URL:** `http://<BACKEND_IP>:8000/api`

### Auth

| Método | Endpoint | Auth requerida | Descripción |
|---|---|---|---|
| POST | `/auth/register` | No | Registrar usuario (role: `usuario`) |
| POST | `/auth/register/admin` | Token admin | Registrar usuario admin |
| POST | `/auth/login` | No | Login — retorna JWT |
| GET | `/auth/me` | Token cualquier rol | Datos del usuario actual |

**Body de registro/login:**
```json
{ "email": "user@example.com", "password": "pass123" }
```

**Respuesta de login:**
```json
{ "access_token": "eyJ...", "token_type": "bearer", "role": "usuario" }
```

---

### Tracks

| Método | Endpoint | Auth requerida | Descripción |
|---|---|---|---|
| GET | `/tracks` | No | Listar canciones (paginado) |
| GET | `/tracks?limit=50&offset=0` | No | Paginación |
| GET | `/tracks/{id}` | No | Detalle de canción |
| GET | `/tracks/search?q=query` | No | Buscar por nombre, artista o género |

**Respuesta de `/tracks`:**
```json
[
  {
    "track_id": 1,
    "name": "For Those About To Rock",
    "album": "For Those About To Rock We Salute You",
    "genre": "Rock",
    "unit_price": 0.99
  }
]
```

---

### Customers

| Método | Endpoint | Auth requerida | Descripción |
|---|---|---|---|
| GET | `/customers` | No | Listar todos los clientes |
| GET | `/customers/{id}` | No | Detalle de cliente |

---

### Purchase

| Método | Endpoint | Auth requerida | Descripción |
|---|---|---|---|
| POST | `/purchase` | No | Procesar compra |

**Body:**
```json
{ "customer_id": 1, "track_ids": [1, 2, 3] }
```

**Respuesta:**
```json
{
  "invoice_id": 413,
  "customer": "Luís Gonçalves",
  "tracks": ["For Those About To Rock", "Balls to the Wall"],
  "total": 1.98,
  "date": "2026-04-14T10:30:00"
}
```

---

## 7. Autenticación y roles

El sistema usa **JWT (JSON Web Tokens)** con los siguientes parámetros:

- **Algoritmo:** HS256
- **Secret Key:** `chinook-secret-key-2026` (hardcodeada en `auth.py` — cambiar en prod)
- **Expiración:** 60 minutos
- **Header HTTP:** `Authorization: Bearer <token>`

### Flujo de autenticación

```
1. POST /auth/login con {email, password}
2. FastAPI verifica password con Bcrypt
3. Si correcto → genera JWT con {sub: email, role: "usuario"|"admin"}
4. Frontend guarda token en estado (AuthContext)
5. Requests protegidos envían header: Authorization: Bearer <token>
6. FastAPI decodifica JWT → obtiene usuario de DB
7. Si rol insuficiente → 403 Forbidden
```

### Crear primer usuario admin

Como el endpoint `/auth/register/admin` requiere un token admin, el primer admin debe crearse directamente en la base de datos:

```sql
-- Conectarse a RDS y ejecutar:
INSERT INTO users (email, password, role, created_at)
VALUES (
  'admin@chinook.com',
  '$2b$12$HASH_GENERADO_CON_BCRYPT',  -- ver nota abajo
  'admin',
  NOW()
);
```

Para generar el hash de la contraseña desde Python:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
print(pwd_context.hash("tu_contraseña_aqui"))
```

---

## 8. Flujos principales de la app

### Flujo de compra

```
Usuario → /tracks → Selecciona canciones → /purchase
  → Selecciona cliente del dropdown
  → Hace click en "Procesar Compra"
  → POST /api/purchase {customer_id, track_ids}
  → FastAPI crea Invoice + InvoiceLines en RDS
  → Muestra resumen de factura con total
```

### Flujo de búsqueda

```
Usuario escribe "Rolling" en buscador
  → GET /api/tracks/search?q=Rolling
  → FastAPI hace JOIN Artist+Album+Genre con ILIKE '%Rolling%'
  → Retorna canciones que coincidan en nombre, artista o género
  → Frontend actualiza tabla
```

### Rutas del frontend

| Ruta | Componente | Protección |
|---|---|---|
| `/` | Home.jsx | Pública |
| `/tracks` | Tracks.jsx | Pública |
| `/purchase` | Purchase.jsx | Pública |
| `/login` | Login.jsx | Pública |
| `/register` | Register.jsx | Pública |
| `/admin` | Admin.jsx | Solo rol `admin` |

---

## 9. Variables de entorno

### Backend — archivo `.env` en `backend/`

```env
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
DB_HOST=<RDS_ENDPOINT>.rds.amazonaws.com
DB_PORT=5432
DB_NAME=chinook
```

### Frontend — `frontend/src/services/api.js`

La IP del backend está **hardcodeada** en este archivo. Al migrar a una nueva cuenta AWS, actualizar esta línea:

```javascript
// frontend/src/services/api.js — línea 3
const API = axios.create({
  baseURL: 'http://<NUEVA_IP_BACKEND>:8000/api'  // <-- cambiar aqui
})
```

### GitHub Actions Secrets

Configurar en: `GitHub repo → Settings → Secrets and variables → Actions`

| Secret | Valor |
|---|---|
| `BACKEND_HOST` | IP pública de EC2 Backend |
| `FRONTEND_HOST` | IP pública de EC2 Frontend |
| `SSH_USER` | Usuario SSH (ej: `ubuntu` o `ec2-user`) |
| `SSH_PRIVATE_KEY` | Contenido del archivo `.pem` de AWS |

---

## 10. Pipeline CI/CD

El despliegue es **completamente automático** con cada `push` a la rama `main`.

```
push a main
    │
    ├── Job: deploy-backend
    │   ├── SSH a EC2 Backend
    │   ├── git pull origin main
    │   ├── pip install -r backend/requirements.txt
    │   └── systemctl restart chinook-backend
    │
    └── Job: deploy-frontend  (corre después de backend)
        ├── SSH a EC2 Frontend
        ├── git pull origin main
        ├── npm install && npm run build
        ├── cp dist/* /var/www/html/
        └── systemctl restart nginx
```

El archivo `deploy.yml` usa la acción `appleboy/ssh-action@v1.0.0` para conectarse a las instancias via SSH usando los secrets configurados.

---

## 11. Cómo correr los tests

### Backend

```bash
cd backend
source venv/bin/activate       # o: python -m venv venv && pip install -r requirements.txt
pytest app/tests/ -v           # correr todos los tests
pytest app/tests/ --cov=app    # con reporte de cobertura
```

Los tests usan SQLite en memoria (no necesitan conexión a RDS).

### Frontend

```bash
cd frontend
npm install
npm test                       # corre Vitest
npm run test -- --coverage     # con cobertura
```

### Resumen de tests

| Capa | Archivo | Tests | Estado |
|---|---|---|---|
| Backend Endpoints | test_endpoints.py | 6 | Pasa |
| Backend Services | test_services.py | 6 | Pasa |
| Frontend Navbar | Navbar.test.jsx | 9 | Pasa |
| Frontend API | api.test.js | 5 | Pasa |
| Frontend Home | Home.test.jsx | Varios | Pasa |
| **Total** | | **37+** | **100%** |

---

## 12. Guía de re-despliegue en nueva cuenta AWS

Esta sección cubre paso a paso cómo levantar todo el proyecto desde cero en una nueva cuenta AWS.

### Paso 1: Crear la infraestructura AWS

#### 1.1 — Crear VPC y Subnets (o usar la VPC por defecto)

Se puede usar la VPC default de AWS. Solo asegurarse de tener:
- Una **subnet pública** para las dos EC2
- Una **subnet privada** para RDS (opcional pero recomendado)

#### 1.2 — Crear Security Groups

**SG-Backend:**
- Inbound: TCP 8000 desde `0.0.0.0/0`
- Inbound: TCP 22 desde tu IP (para SSH)
- Outbound: Todo

**SG-Frontend:**
- Inbound: TCP 80 desde `0.0.0.0/0`
- Inbound: TCP 22 desde tu IP (para SSH)
- Outbound: Todo

**SG-RDS:**
- Inbound: TCP 5432 desde SG-Backend (solo)
- Outbound: Todo

#### 1.3 — Crear RDS PostgreSQL

1. Ir a RDS → Create database
2. Engine: PostgreSQL
3. Template: Free tier (para desarrollo)
4. DB identifier: `chinook-db`
5. Master username: `postgres`
6. Master password: (guardar bien)
7. VPC: la misma que las EC2
8. Security group: SG-RDS
9. **Initial database name:** `chinook`
10. Public access: **No**
11. Crear → esperar ~5 min → copiar el Endpoint

#### 1.4 — Crear EC2 Backend

1. Ir a EC2 → Launch Instance
2. AMI: Ubuntu Server 22.04 LTS
3. Instance type: t2.micro (free tier)
4. Key pair: crear o usar existente → descargar `.pem`
5. Security group: SG-Backend
6. Storage: 8 GB gp3
7. Lanzar → copiar IP pública

#### 1.5 — Crear EC2 Frontend

Igual que EC2 Backend pero con Security group: SG-Frontend.

---

### Paso 2: Configurar EC2 Backend

Conectarse via SSH:
```bash
chmod 400 tu-key.pem
ssh -i tu-key.pem ubuntu@<IP_EC2_BACKEND>
```

Instalar dependencias:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip git postgresql-client
```

Clonar el repositorio:
```bash
cd ~
git clone https://github.com/<tu-org>/Parcial_BigData_Corte1.git
cd Parcial_BigData_Corte1
```

Configurar el entorno virtual y dependencias:
```bash
python3.12 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

Crear archivo `.env`:
```bash
cat > backend/.env << EOF
DB_USER=postgres
DB_PASSWORD=<tu_password_rds>
DB_HOST=<endpoint_rds>.rds.amazonaws.com
DB_PORT=5432
DB_NAME=chinook
EOF
```

Cargar la base de datos Chinook:
```bash
# Instalar cliente psql si no está
sudo apt install -y postgresql-client

# Cargar schema y datos
psql -h <RDS_ENDPOINT> -U postgres -d chinook -f Chinook_PostgreSql.sql
```

Crear el servicio systemd para FastAPI:
```bash
sudo nano /etc/systemd/system/chinook-backend.service
```

Contenido del servicio:
```ini
[Unit]
Description=Chinook FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Parcial_BigData_Corte1/backend
Environment="PATH=/home/ubuntu/Parcial_BigData_Corte1/backend/venv/bin"
ExecStart=/home/ubuntu/Parcial_BigData_Corte1/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Habilitar y arrancar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chinook-backend
sudo systemctl start chinook-backend
sudo systemctl status chinook-backend

# Verificar que responde
curl http://localhost:8000/api/tracks?limit=1
```

---

### Paso 3: Configurar EC2 Frontend

Conectarse via SSH:
```bash
ssh -i tu-key.pem ubuntu@<IP_EC2_FRONTEND>
```

Instalar dependencias:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx git
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Clonar el repositorio:
```bash
cd ~
git clone https://github.com/<tu-org>/Parcial_BigData_Corte1.git
cd Parcial_BigData_Corte1/frontend
```

**IMPORTANTE — Actualizar IP del backend antes de compilar:**
```bash
nano src/services/api.js
# Cambiar la línea:
# baseURL: 'http://44.216.77.83:8000/api'
# Por:
# baseURL: 'http://<NUEVA_IP_EC2_BACKEND>:8000/api'
```

Build y despliegue:
```bash
npm install
npm run build
sudo rm -rf /var/www/html/*
sudo cp -r dist/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html/
```

Configurar Nginx:
```bash
sudo nano /etc/nginx/sites-available/chinook
```

Contenido:
```nginx
server {
    listen 80;
    server_name _;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Activar y reiniciar:
```bash
sudo ln -s /etc/nginx/sites-available/chinook /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

Verificar:
```bash
curl http://localhost/
# Debe retornar el HTML de React
```

---

### Paso 4: Actualizar GitHub Actions Secrets

Ir a: `GitHub repo → Settings → Secrets and variables → Actions → New repository secret`

| Secret | Valor |
|---|---|
| `BACKEND_HOST` | IP pública nueva de EC2 Backend |
| `FRONTEND_HOST` | IP pública nueva de EC2 Frontend |
| `SSH_USER` | `ubuntu` |
| `SSH_PRIVATE_KEY` | Contenido completo del archivo `.pem` |

### Paso 5: Verificar el pipeline

```bash
git commit --allow-empty -m "test: trigger deploy"
git push origin main
```

Ir a GitHub → Actions y verificar que ambos jobs pasan correctamente.

### Paso 6: Crear el primer usuario admin

```bash
# Desde EC2 Backend, activar venv y abrir Python
source ~/Parcial_BigData_Corte1/backend/venv/bin/activate
python3 -c "
from passlib.context import CryptContext
pwd = CryptContext(schemes=['bcrypt'])
print(pwd.hash('tu_password_admin'))
"
# Copiar el hash generado

# Insertar en RDS
psql -h <RDS_ENDPOINT> -U postgres -d chinook -c "
INSERT INTO users (email, password, role, created_at)
VALUES ('admin@chinook.com', '<HASH_COPIADO>', 'admin', NOW());
"
```

---

### Checklist de re-despliegue

```
[ ] RDS creada y endpoint copiado
[ ] EC2 Backend creada y configurada
[ ] .env con credenciales RDS creado en backend/
[ ] Schema Chinook cargado en RDS (Chinook_PostgreSql.sql)
[ ] Servicio chinook-backend corriendo (systemctl status)
[ ] EC2 Frontend creada y configurada
[ ] IP del backend actualizada en frontend/src/services/api.js
[ ] Build de React copiado a /var/www/html/
[ ] Nginx corriendo y sirviendo la app
[ ] GitHub Secrets actualizados (BACKEND_HOST, FRONTEND_HOST, SSH_USER, SSH_PRIVATE_KEY)
[ ] Pipeline CI/CD verificado con push de prueba
[ ] Usuario admin creado en la BD
[ ] App accesible en http://<IP_FRONTEND>/
```

---

## 13. Problemas conocidos y notas importantes

### IP hardcodeada en el frontend

**Archivo:** `frontend/src/services/api.js` línea 3  
**Problema:** La IP `44.216.77.83` es de la cuenta AWS anterior. Cada vez que se migre a nueva cuenta, esta línea debe actualizarse manualmente antes de hacer el build.  
**Solución futura recomendada:** Usar variable de entorno de Vite (`import.meta.env.VITE_API_URL`).

### AuthContext no existe como archivo

**Síntoma:** `App.jsx`, `Login.jsx` y `Admin.jsx` importan `AuthContext` pero el archivo `frontend/src/context/AuthContext.jsx` no existe como archivo separado.  
**Estado actual:** El contexto está implementado inline dentro de `App.jsx`. Funciona correctamente, solo la organización de archivos es atípica.

### ci-cd.yml vacío

**Archivo:** `.github/workflows/ci-cd.yml`  
**Estado:** Archivo vacío creado como placeholder. Los tests no corren automáticamente en CI actualmente. Solo el deploy está automatizado.

### JWT Secret Key hardcodeada

**Archivo:** `backend/app/auth.py`  
**Valor:** `"chinook-secret-key-2026"`  
**Riesgo:** En producción real, esta key debe venir de una variable de entorno.

### CORS completamente abierto

**Archivo:** `backend/app/main.py`  
**Configuración:** `allow_origins=["*"]`  
**Riesgo:** En producción real, restringir al dominio del frontend.

---

## 14. Capa Analítica — ETL + Athena + Power BI

Parcial 2 agrega una capa analítica sobre el OLTP del Parcial 1.  
Responde 4 preguntas: canciones vendidas por día, artista más vendido por mes, día de semana con más compras, mes con mayor número de ventas.

### Recursos AWS creados

| Recurso | Nombre | Descripción |
|---|---|---|
| S3 Bucket | `chinook-datalake-academy` | Almacena Parquet particionados |
| Glue Database | `chinook_dw` | Catálogo de tablas analíticas |
| Glue Connection | `chinook-rds` | Conexión JDBC al RDS |
| Glue Job | `fact-sales-etl` | ETL principal (+ jobs de Daniela y Ana) |
| Athena Workgroup | `chinook-wg` | Queries SQL sobre S3 |
| IAM Role | `LabRole` | Rol compartido de Academy (no se crea, ya existe) |

### Estructura de carpetas

```
infra/                    # Scripts boto3 de infraestructura (Alan)
  provision_infra.py      # Crea toda la infra — idempotente
  deploy_jobs.py          # Sube ETLs a S3 y crea/actualiza Glue Jobs
  create_athena_tables.py # Ejecuta DDLs en Athena
  schedule_jobs.py        # Crea Glue Triggers horarios
  tear_down.py            # Borra toda la infra analítica

etl/
  glue_jobs/              # Scripts Glue Spark (Daniela + Alan)
    fact_sales_etl.py
    dim_customer_etl.py   ...
  python_jobs/            # Scripts Python Shell (Ana)
    dim_date_etl.py
  tests/                  # pytest (Ana)
```

### Primera vez: levantar la infra desde cero

```bash
# 1. Ir al proyecto
cd Parcial_BigData_Corte1

# 2. Crear entorno virtual e instalar boto3
python3 -m venv .venv && .venv/bin/pip install boto3

# 3. Copiar credenciales de Academy a ~/.aws/credentials
#    (ver sección "Renovar credenciales" abajo)

# 4. Levantar toda la infraestructura
.venv/bin/python infra/provision_infra.py

# 5. Subir scripts ETL y crear Glue Jobs
.venv/bin/python infra/deploy_jobs.py

# 6. Crear tablas en Athena (una vez Ana entregue athena_ddls.sql)
.venv/bin/python infra/create_athena_tables.py
```

### Renovar credenciales de Academy (rotan cada 4h)

1. Abrir **AWS Academy Learner Lab** → **Start Lab** → esperar luz verde
2. Clic en **AWS Details** → **Show AWS CLI**
3. Copiar las 3 líneas y pegarlas en `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = ASIA...
aws_secret_access_key = ...
aws_session_token = ...
```

4. Avisar al equipo en el chat: _"credenciales rotadas — actualicen ~/.aws/credentials"_

> Las credenciales también se usan en GitHub Actions Secrets  
> (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`).  
> Actualizarlas manualmente antes de cada deploy manual.

### Correr ETLs manualmente desde Glue Console

1. Ir a **AWS Glue → Jobs**
2. Seleccionar el job deseado (ej: `fact-sales-etl`)
3. Clic en **Run**
4. Monitorear en **Runs** → esperar estado `Succeeded` (~3-5 min)
5. Verificar datos en **Athena Console** → workgroup `chinook-wg`:

```sql
SELECT COUNT(*) FROM chinook_dw.fact_sales;
SELECT year, COUNT(*) FROM chinook_dw.fact_sales GROUP BY year;
```

### Desplegar scripts actualizados

Cuando se modifica cualquier ETL, redesplegar con:

```bash
.venv/bin/python infra/deploy_jobs.py
```

O via GitHub Actions (trigger manual):  
`GitHub repo → Actions → ETL Analytics Pipeline → Run workflow → deploy: true`

### Activar scheduling automático

Los triggers están creados pero **apagados** por defecto (para ahorrar créditos Academy).  
Activarlos cuando todos los ETLs estén validados:

```bash
.venv/bin/python infra/schedule_jobs.py
# Luego activar cada trigger en Glue Console → Triggers → Enable
```

Cadencia configurada: cada hora, escalonados 5 min entre jobs.

### Tear down completo

```bash
.venv/bin/python infra/tear_down.py
# Pide confirmación: escribir CONFIRMAR
```

Elimina bucket S3, Glue Jobs, Conexión, DB, Athena WG y SG de Glue.
