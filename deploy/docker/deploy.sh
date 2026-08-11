#!/usr/bin/env bash
set -euo pipefail

# Production deploy for NotenHaus on DigitalOcean Droplet.
# Usage on server: bash deploy/docker/deploy.sh
# Requires .env (from .env.docker.example). Always builds images.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

USE_HTTPS=false
if [[ -f .env ]]; then
  val="$(grep -E '^USE_HTTPS=' .env | tail -1 | cut -d= -f2- | tr -d ' "\r' || true)"
  if [[ -n "${val:-}" ]]; then
    USE_HTTPS="$val"
  fi
fi

if [[ "${USE_HTTPS}" =~ ^[Tt]rue$ ]]; then
  export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml:docker-compose.ssl.yml"
  echo "==> Mode: HTTPS (docker.prod.conf + :443)"
else
  export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
  echo "==> Mode: HTTP only (docker.conf, до certbot / домену)"
fi

COMPOSE=(docker compose)

free_host_ports() {
  if command -v systemctl >/dev/null 2>&1; then
    systemctl stop nginx 2>/dev/null || true
    systemctl disable nginx 2>/dev/null || true
    for svc in $(systemctl list-units --type=service --all 2>/dev/null | grep -oE 'gunicorn[^ ]*' || true); do
      systemctl stop "$svc" 2>/dev/null || true
      systemctl disable "$svc" 2>/dev/null || true
    done
  fi
}

if [[ ! -f .env ]]; then
  echo "FATAL: .env not found. cp .env.docker.example .env && nano .env"
  exit 1
fi

echo "==> Freeing host ports 80/443"
free_host_ports

echo "==> Building web image (--build обов'язково)"
"${COMPOSE[@]}" build web

echo "==> Starting stack"
"${COMPOSE[@]}" up -d || echo "WARN: initial up -d non-zero (slow healthcheck?) — retry after wait"

echo "==> Waiting for web /healthz/ (up to ~4 min)"
WEB_OK=false
for _ in $(seq 1 120); do
  if "${COMPOSE[@]}" exec -T web python3 -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=5)" \
    2>/dev/null; then
    echo "web healthy"
    WEB_OK=true
    break
  fi
  sleep 2
done
if [[ "$WEB_OK" != "true" ]]; then
  echo "WARN: web not healthy in time — ${COMPOSE[*]} logs web"
fi

echo "==> Final up -d (ensure nginx/db present)"
"${COMPOSE[@]}" up -d || echo "WARN: final up -d non-zero — inspect ps below"

if curl -sf http://127.0.0.1/healthz/ >/dev/null; then
  echo "HTTP /healthz/ OK"
else
  echo "WARN: HTTP /healthz/ failed — ${COMPOSE[*]} logs web nginx"
fi

if [[ "${USE_HTTPS}" =~ ^[Tt]rue$ ]]; then
  if curl -sfk https://127.0.0.1/healthz/ >/dev/null 2>&1; then
    echo "HTTPS /healthz/ OK"
  else
    echo "WARN: HTTPS /healthz/ failed — certbot + docker.prod.conf paths"
  fi
fi

"${COMPOSE[@]}" ps

EXPECTED_SERVICES=(db web nginx)
MISSING=0
for svc in "${EXPECTED_SERVICES[@]}"; do
  if ! "${COMPOSE[@]}" ps "$svc" 2>/dev/null | grep -qE "Up|running"; then
    echo "ERROR: service '$svc' is NOT running — ${COMPOSE[*]} logs $svc"
    MISSING=1
  fi
done
if [[ "$MISSING" == "0" ]]; then
  echo "All ${#EXPECTED_SERVICES[@]} services are running."
fi
