arregla este readme que queede bonito y bien 
# 🎵 Chinook Music Store

Gestión y compra de canciones en línea, basada en la base de datos **Chinook**, desplegada en **AWS** con pipeline de CI/CD automatizado.

---

## 📖 Descripción

**Chinook Music Store** es una aplicación web full-stack que permite a los usuarios explorar el catálogo musical de la base de datos Chinook, buscar canciones por nombre, artista o género, y realizar compras en línea. Incluye autenticación con roles (admin/usuario), validación de formularios y alertas de operaciones.

---

## 🏗️ Arquitectura

graph TD
    subgraph AWS_Cloud [AWS Cloud]
        direction TB
        subgraph Public_Subnet [Public Subnet]
            EC2_FE[EC2 #1: Frontend - React/Vite]
            EC2_BE[EC2 #2: Backend - FastAPI]
        end
        subgraph Private_Subnet [Private Subnet]
            RDS[(RDS PostgreSQL: Chinook DB)]
        end
    end
    
    User((Usuario)) --> EC2_FE
    EC2_FE <--> EC2_BE
    EC2_BE <--> RDS

[!IMPORTANT]
Seguridad: La base de datos RDS se encuentra en una subred privada, siendo accesible únicamente por la instancia del Backend mediante reglas de Security Groups.

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
├── .github/workflows/    # Automatización CI/CD
├── frontend/             # SPA en React
│   ├── src/
│   │   ├── components/   # UI Reutilizable
│   │   ├── pages/        # Vistas principales
│   │   ├── services/     # Clientes de API
│   │   └── tests/        # Pruebas de componentes
│   └── vite.config.js
├── backend/              # API RESTful
│   ├── app/
│   │   ├── models/       # Entidades DB
│   │   ├── schemas/      # Validaciones Pydantic
│   │   ├── routers/      # Endpoints
│   │   └── tests/        # Pruebas de integración
│   └── requirements.txt
└── Chinook_PostgreSql.sql # Esquema de datos

---

## ⚙️ Funcionalidades

Módulo,Descripción
🔐 Auth,Registro de usuarios y Login seguro con JWT. Manejo de roles admin y usuario.
🎵 Catálogo,"Buscador avanzado por Track, Artista o Género."
🛒 Checkout,Proceso de compra con validación de existencia de cliente y generación de factura.
🎨 UX/UI,Interfaz responsiva con notificaciones en tiempo real y rutas protegidas.

---

### 🧪 Calidad de Software (Testing)

Contamos con una suite de pruebas automatizadas que garantizan la estabilidad del sistema en cada cambio.

Capa,Casos de Prueba,Estado
Backend Endpoints,11,✅ 100% Pass
Backend Services,12,✅ 100% Pass
Frontend Components,9,✅ 100% Pass
Frontend API Service,5,✅ 100% Pass
TOTAL,37,🚀 Ready for Production

### Pipeline CI/CD

El flujo de despliegue es completamente automático al realizar un push a la rama main:

1. Continuous Integration (CI):

    - Instalación de dependencias (npm/pip).
    - Ejecución de Linter y Pruebas Unitarias.

2. Continuous Deployment (CD):
3. 
    - Conexión vía SSH a las instancias EC2.
    - Actualización del código fuente (git pull).
    - Build de producción para React.
    - Reinicio de servicios (FastAPI/Gunicorn).
    - 
# 👨‍💻 Autorres

- Alan Osorio

- Daniela Lopez

- Ana Amador 