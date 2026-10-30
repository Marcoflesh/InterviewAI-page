#!/bin/sh
# Se ejecuta DENTRO del contenedor `db` (lo llaman iniciar.sh / iniciar.ps1).
# Alinea la contraseña guardada en el volumen de PostgreSQL con POSTGRES_PASSWORD del .env.
# No borra datos. Usa la conexión local del contenedor (no requiere la contraseña vieja).
set -eu
printf '%s\n' "ALTER USER \"${POSTGRES_USER}\" WITH PASSWORD :'pw';" \
  | psql -v ON_ERROR_STOP=1 -q -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -v pw="${POSTGRES_PASSWORD}"
echo "OK: contrasena de la base de datos sincronizada con .env"
exit 0
