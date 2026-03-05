# 🎵 Chinook Music Store

Gestión y compra de canciones en línea, basada en la base de datos **Chinook**, desplegada en **AWS** con pipeline de CI/CD automatizado.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Funcionalidades](#-funcionalidades)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Variables de Entorno](#-variables-de-entorno)
- [Pruebas Unitarias](#-pruebas-unitarias)
- [Pipeline CI/CD](#-pipeline-cicd)
- [Despliegue en AWS](#-despliegue-en-aws)
- [Evidencias](#-evidencias)

---

## 📖 Descripción

**Chinook Music Store** es una aplicación web full-stack que permite a los usuarios explorar el catálogo musical de la base de datos Chinook, buscar canciones por nombre, artista o género, y realizar compras en línea. Incluye autenticación con roles (admin/usuario), validación de formularios y alertas de operaciones.

---

## 🏗️ Arquitectura
┌─────────────────────────────────────────────────────┐
│ AWS Cloud │
│ │
│ ┌──────────────┐ ┌──────────────────────┐ │
│ │ EC2 #1 │ │ EC2 #2 │ │
│ │ Frontend │◄──────►│ Backend │ │
│ │ React/Vite │ │ FastAPI + Python │ │
│ │ Port: 5173 │ │ Port: 8000 │ │
│ └──────────────┘ └──────────┬───────────┘ │
│ │ │
│ ┌──────────▼───────────┐ │
│ │ RDS PostgreSQL │ │
│ │ (Private Subnet) │ │
│ │ Base Chinook │ │
│ └──────────────────────┘ │
└─────────────────────────────────────────────────────┘


> ⚠️ La base de datos RDS **no es pública** — solo accesible desde la VPC interna.

---

## 🛠️ Tecnologías

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| React | 18.x | Framework UI |
| Vite | 5.x | Build tool |
| React Router DOM | 6.x | Navegación |
| Axios | 1.x | Consumo de API |
| Vitest | 2.1.9 | Pruebas unitarias |
| React Testing Library | 14.x | Testing de componentes |

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12 | Lenguaje base |
| FastAPI | 0.x | Framework API REST |
| SQLAlchemy | 2.x | ORM |
| Pydantic | 2.x | Validación de datos |
| PyJWT / Passlib | - | Autenticación JWT |
| PyTest | 9.0.2 | Pruebas unitarias |

### Infraestructura
| Servicio | Uso |
|---|---|
| AWS EC2 (x2) | Hosting Frontend y Backend |
| AWS RDS PostgreSQL | Base de datos (subred privada) |
| GitHub Actions | Pipeline CI/CD |

---

## 📁 Estructura del Proyecto

Parcial_BigData_Corte1/
│
├── .github/
│ └── workflows/
│ └── ci-cd.yml # Pipeline GitHub Actions
│
├── frontend/ # Aplicación React
│ ├── src/
│ │ ├── components/
│ │ │ ├── Navbar.jsx # Barra de navegación
│ │ │ └── ...
│ │ ├── pages/
│ │ │ ├── Home.jsx # Página principal
│ │ │ ├── Tracks.jsx # Catálogo de canciones
│ │ │ ├── Purchase.jsx # Página de compra
│ │ │ ├── Login.jsx # Autenticación
│ │ │ └── Register.jsx # Registro de usuario
│ │ ├── context/
│ │ │ └── AuthContext.jsx # Contexto de autenticación
│ │ ├── services/
│ │ │ └── api.js # Llamadas HTTP al backend
│ │ └── tests/
│ │ ├── Home.test.jsx # Tests componente Home
│ │ ├── Navbar.test.jsx # Tests componente Navbar
│ │ └── api.test.js # Tests servicios API
│ ├── package.json
│ └── vite.config.js
│
├── backend/ # API FastAPI
│ ├── app/
│ │ ├── routers/
│ │ │ └── init.py # Endpoints principales
│ │ ├── services/ # Lógica de negocio
│ │ ├── schemas/
│ │ │ └── init.py # Modelos Pydantic
│ │ ├── models/ # Modelos SQLAlchemy
│ │ ├── database.py # Configuración DB
│ │ └── tests/
│ │ ├── test_endpoints.py # Tests de endpoints HTTP
│ │ └── test_services.py # Tests de servicios
│ ├── requirements.txt
│ └── venv/
│
├── Chinook_PostgreSql.sql # Script base de datos Chinook
└── README.md



---

## ⚙️ Funcionalidades

### 👤 Autenticación
- Registro de nuevos usuarios
- Login con JWT
- Roles: `admin` y `usuario`
- Rutas protegidas según rol

### 🎵 Gestión de Canciones
- Listar catálogo completo de tracks
- Buscar por **nombre de canción**, **artista** o **género**
- Ver detalle de cada canción

### 🛒 Compras
- Realizar compra de canciones como cliente
- Generación de factura automática
- Validación de existencia de cliente

### 🖥️ UX / Interfaz
- Validación de formularios en frontend y backend
- Alertas de éxito y error en todas las operaciones
- Navegación con React Router


---

### pruebas (TESTS)

| Capa                 | Tests | Estado         |
| -------------------- | ----- | -------------- |
| Backend Endpoints    | 11    | ✅ 100% passing |
| Backend Services     | 12    | ✅ 100% passing |
| Frontend Components  | 9     | ✅ 100% passing |
| Frontend API Service | 5     | ✅ 100% passing |
| Total                | 37    | ✅ 37/37        |

### Pipeline CI/CD
El pipeline está implementado con GitHub Actions en .github/workflows/ci-cd.yml.

Flujo automatizado

Push a main
     │
     ▼
┌─────────────┐     ┌─────────────┐
│  CI Backend │     │ CI Frontend │
│  - pip install    │  - npm install
│  - pytest   │     │  - npm test │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │ (ambos pasan)
                 ▼
        ┌────────────────┐
        │   CD Deploy    │
        │                │
        │ SSH → EC2 #1   │
        │ git pull       │
        │ restart backend│
        │                │
        │ SSH → EC2 #2   │
        │ git pull       │
        │ npm build      │
        │ restart frontend│
        └────────────────┘
# 👨‍💻 Autor
Alan Osorio
Daniela Lopez
Ana Amador 