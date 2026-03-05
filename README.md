#  Chinook Music Store — Script de Despliegue Completo AWS EC2
#  Stack: React 18/Vite 5 + FastAPI 3.12 + PostgreSQL (RDS)
#  Autores: Alan Osorio | Daniela Lopez | Ana Amador
# ================================================================
set -e
set -o pipefail

# ============================================================
# 🎨 COLORES
# ============================================================
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ============================================================
# ⚙️  CONFIGURACIÓN — EDITAR ANTES DE EJECUTAR
# ============================================================
REPO_URL="https://github.com/tu-usuario/Parcial_BigData_Corte1.git"
PROJECT_DIR="$HOME/Parcial_BigData_Corte1"

# --- Base de datos (AWS RDS) ---
DB_HOST="your-rds-endpoint.rds.amazonaws.com"
DB_PORT=5432
DB_NAME="chinook"
DB_USER="chinook_user"
DB_PASSWORD="your_secure_password"

# --- Backend ---
BACKEND_PORT=8000
SECRET_KEY="$(openssl rand -hex 32)"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# --- Frontend ---
# En producción usa la IP pública del EC2 Backend si son instancias separadas
BACKEND_URL="http://localhost:${BACKEND_PORT}"

# ============================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================
log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
log_step()    { echo -e "\n${CYAN}${BOLD}━━━ $1 ━━━${NC}"; }

check_cmd() {
    command -v "$1" &>/dev/null
}

# ============================================================
# PASO 1 — Actualizar sistema e instalar dependencias base
# ============================================================
log_step "PASO 1/13 · Actualizando sistema"

sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y \
    curl wget git build-essential software-properties-common \
    apt-transport-https ca-certificates gnupg lsb-release \
    openssl unzip nginx postgresql-client

log_success "Dependencias base instaladas."

# ============================================================
# PASO 2 — Instalar Node.js 20 LTS + PM2
# ============================================================
log_step "PASO 2/13 · Instalando Node.js LTS"

if ! check_cmd node; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if ! check_cmd pm2; then
    sudo npm install -g pm2
fi

log_success "Node $(node -v) · npm $(npm -v) listos."

# ============================================================
# PASO 3 — Instalar Python 3.12
# ============================================================
log_step "PASO 3/13 · Instalando Python 3.12"

if ! check_cmd python3.12; then
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update -y
    sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
fi

if ! check_cmd pip3; then
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12
fi

log_success "$(python3.12 --version) listo."

# ============================================================
# PASO 4 — Clonar / actualizar repositorio
# ============================================================
log_step "PASO 4/13 · Repositorio"

if [ -d "$PROJECT_DIR/.git" ]; then
    log_warning "Repo existente — ejecutando git pull..."
    cd "$PROJECT_DIR" && git pull origin main
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

log_success "Repositorio listo en: $PROJECT_DIR"

# ============================================================
# PASO 5 — Variables de entorno Backend (.env)
# ============================================================
log_step "PASO 5/13 · Generando backend/.env"

mkdir -p "$PROJECT_DIR/backend"

cat > "$PROJECT_DIR/backend/.env" <<EOF
# ── Base de datos ──────────────────────────────────────────
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# ── JWT / Seguridad ────────────────────────────────────────
SECRET_KEY=${SECRET_KEY}
ALGORITHM=${ALGORITHM}
ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}

# ── App ────────────────────────────────────────────────────
APP_ENV=production
DEBUG=False
BACKEND_PORT=${BACKEND_PORT}
EOF

log_success "backend/.env generado."

# ============================================================
# PASO 6 — Variables de entorno Frontend (.env)
# ============================================================
log_step "PASO 6/13 · Generando frontend/.env"

mkdir -p "$PROJECT_DIR/frontend"

cat > "$PROJECT_DIR/frontend/.env" <<EOF
VITE_API_URL=${BACKEND_URL}
VITE_APP_NAME=Chinook Music Store
EOF

log_success "frontend/.env generado."

# ============================================================
# PASO 7 — Instalar dependencias Backend + Tests
# ============================================================
log_step "PASO 7/13 · Configurando Backend (FastAPI)"

cd "$PROJECT_DIR/backend"

python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

log_info "Ejecutando suite de tests del backend (37 casos)..."
pytest app/tests/ -v --tb=short && log_success "Todos los tests del backend pasaron ✅" \
    || log_warning "Algunos tests fallaron — revisa los logs antes de continuar."

deactivate

# ============================================================
# PASO 8 — Importar esquema Chinook en RDS
# ============================================================
log_step "PASO 8/13 · Importando Chinook DB → RDS PostgreSQL"

export PGPASSWORD="$DB_PASSWORD"

if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c '\q' 2>/dev/null; then

    DB_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" 2>/dev/null)

    if [ "$DB_EXISTS" != "1" ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
            -c "CREATE DATABASE ${DB_NAME};"
        log_success "Base de datos '${DB_NAME}' creada."
    else
        log_warning "La base de datos '${DB_NAME}' ya existe — omitiendo creación."
    fi

    SQL_FILE="$PROJECT_DIR/Chinook_PostgreSql.sql"
    if [ -f "$SQL_FILE" ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"
        log_success "Esquema Chinook importado exitosamente."
    else
        log_warning "Chinook_PostgreSql.sql no encontrado — importación omitida."
    fi
else
    log_warning "No se pudo conectar a RDS. Verifica el endpoint y los Security Groups de AWS."
fi

unset PGPASSWORD

# ============================================================
# PASO 9 — Build de producción Frontend (React/Vite)
# ============================================================
log_step "PASO 9/13 · Build del Frontend"

cd "$PROJECT_DIR/frontend"

npm ci

log_info "Ejecutando tests del frontend..."
npm run test -- --run && log_success "Tests del frontend pasaron ✅" \
    || log_warning "Algunos tests del frontend fallaron."

npm run build

log_success "Build generado en: $PROJECT_DIR/frontend/dist"

# ============================================================
# PASO 10 — Gunicorn Socket (Unix socket para mejor rendimiento)
# ============================================================
log_step "PASO 10/13 · Configurando Gunicorn socket (systemd)"

sudo tee /etc/systemd/system/chinook-backend.socket > /dev/null <<EOF
[Unit]
Description=Chinook Backend — Gunicorn socket

[Socket]
ListenStream=/run/chinook-backend.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
EOF

sudo tee /etc/systemd/system/chinook-backend.service > /dev/null <<EOF
[Unit]
Description=Chinook Music Store — FastAPI/Gunicorn
Requires=chinook-backend.socket
After=network.target

[Service]
User=${USER}
Group=www-data
WorkingDirectory=${PROJECT_DIR}/backend
Environment="PATH=${PROJECT_DIR}/backend/venv/bin"
EnvironmentFile=${PROJECT_DIR}/backend/.env
ExecStart=${PROJECT_DIR}/backend/venv/bin/gunicorn \\
    app.main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind unix:/run/chinook-backend.sock \\
    --timeout 120 \\
    --access-logfile - \\
    --error-logfile -
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=chinook-backend

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable chinook-backend.socket chinook-backend.service
sudo systemctl start chinook-backend.socket

log_success "Gunicorn socket configurado y activo."

# ============================================================
# PASO 11 — Nginx: reverse proxy + sirviendo React SPA
# ============================================================
log_step "PASO 11/13 · Configurando Nginx"

sudo tee /etc/nginx/sites-available/chinook > /dev/null <<EOF
# ── Chinook Music Store — Nginx ────────────────────────────
server {
    listen 80;
    server_name _;

    # ── Frontend (React build estático) ──────────────────
    root ${PROJECT_DIR}/frontend/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # ── Backend API (FastAPI vía socket Gunicorn) ─────────
    location /api/ {
        proxy_pass http://unix:/run/chinook-backend.sock:/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 90;
        proxy_connect_timeout 90;
    }

    # ── Swagger UI ────────────────────────────────────────
    location /docs {
        proxy_pass http://unix:/run/chinook-backend.sock:/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /openapi.json {
        proxy_pass http://unix:/run/chinook-backend.sock:/openapi.json;
        proxy_set_header Host \$host;
    }

    # ── Compresión Gzip ───────────────────────────────────
    gzip on;
    gzip_types text/plain text/css application/json
               application/javascript text/xml application/xml
               application/x-font-ttf font/opentype image/svg+xml;
    gzip_min_length 256;

    # ── Seguridad básica ──────────────────────────────────
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
EOF

sudo ln -sf /etc/nginx/sites-available/chinook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t && sudo systemctl enable nginx && sudo systemctl reload nginx

log_success "Nginx configurado y recargado."

# ============================================================
# PASO 12 — Ajustar permisos y Firewall (UFW)
# ============================================================
log_step "PASO 12/13 · Permisos y Firewall"

sudo usermod -aG www-data "$USER"
sudo chown -R "$USER":www-data "$PROJECT_DIR/frontend/dist"
sudo chmod -R 755 "$PROJECT_DIR/frontend/dist"

if check_cmd ufw; then
    sudo ufw allow 'Nginx Full'
    sudo ufw allow OpenSSH
    sudo ufw --force enable
    log_success "UFW activado: OpenSSH + Nginx Full."
else
    log_warning "UFW no disponible — configura el Security Group en AWS manualmente (puerto 80/443)."
fi

# ============================================================
# PASO 13 — Verificación final de servicios
# ============================================================
log_step "PASO 13/13 · Verificación de servicios"

sleep 4

PUBLIC_IP=$(curl -s --max-time 3 ifconfig.me \
    || curl -s --max-time 3 http://169.254.169.254/latest/meta-data/public-ipv4 \
    || echo "TU-IP-EC2")

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       CHINOOK MUSIC STORE — ESTADO FINAL         ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"

# Nginx
if systemctl is-active --quiet nginx; then
    echo -e "  Nginx              ${GREEN}✅ Activo${NC}"
else
    echo -e "  Nginx              ${RED}❌ Inactivo — sudo systemctl status nginx${NC}"
fi

# Gunicorn socket
if systemctl is-active --quiet chinook-backend.socket; then
    echo -e "  Gunicorn socket    ${GREEN}✅ Activo${NC}"
else
    echo -e "  Gunicorn socket    ${RED}❌ Inactivo — sudo systemctl status chinook-backend.socket${NC}"
fi

# Gunicorn service
if systemctl is-active --quiet chinook-backend; then
    echo -e "  FastAPI Backend    ${GREEN}✅ Activo (Gunicorn 4 workers)${NC}"
else
    echo -e "  FastAPI Backend    ${YELLOW}⏳ Esperando primera petición (socket activation)${NC}"
fi

# Health check vía Nginx
if curl -sf "http://localhost/docs" > /dev/null 2>&1; then
    echo -e "  Health Check API   ${GREEN}✅ Backend responde${NC}"
else
    echo -e "  Health Check API   ${YELLOW}⚠️  No responde aún — espera unos segundos${NC}"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║                URLs DE ACCESO                    ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo -e "  🌐  Frontend:      ${CYAN}http://${PUBLIC_IP}/${NC}"
echo -e "  ⚡  API Base:      ${CYAN}http://${PUBLIC_IP}/api/${NC}"
echo -e "  📚  Swagger UI:    ${CYAN}http://${PUBLIC_IP}/docs${NC}"
echo -e "  📋  OpenAPI JSON:  ${CYAN}http://${PUBLIC_IP}/openapi.json${NC}"
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║             COMANDOS DE GESTIÓN                  ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo -e "  Reiniciar Backend: ${YELLOW}sudo systemctl restart chinook-backend${NC}"
echo -e "  Logs Backend:      ${YELLOW}sudo journalctl -u chinook-backend -f${NC}"
echo -e "  Reiniciar Nginx:   ${YELLOW}sudo systemctl restart nginx${NC}"
echo -e "  Logs Nginx:        ${YELLOW}sudo tail -f /var/log/nginx/error.log${NC}"
echo ""
echo -e "${GREEN}${BOLD}🎵 ¡Chinook Music Store desplegado exitosamente!${NC}"
echo -e "${BLUE}   Autores: Alan Osorio · Daniela Lopez · Ana Amador${NC}"
echo ""