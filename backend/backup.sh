#!/usr/bin/env bash
# ==============================================================================
# Automated Hot Backup Script for Montazh SQLite Database
# Performs online WAL-safe hot snapshot, PRAGMA integrity verification,
# Gzip compression, and 14-day retention cleanup.
# ==============================================================================

set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="${BACKEND_DIR}/database.sqlite"
BACKUP_DIR="${BACKEND_DIR}/backups"
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sqlite"

mkdir -p "${BACKUP_DIR}"

if [ ! -f "${DB_PATH}" ]; then
    echo "[ERROR] Database file '${DB_PATH}' does not exist!" >&2
    exit 1
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting hot backup of SQLite database..."

# 1. Hot snapshot using SQLite native online backup API
sqlite3 "${DB_PATH}" ".backup '${BACKUP_FILE}'"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "[ERROR] Backup failed! Destination file '${BACKUP_FILE}' was not created." >&2
    exit 1
fi

# 2. Automated integrity check
INTEGRITY=$(sqlite3 "${BACKUP_FILE}" "PRAGMA quick_check;" 2>&1 || true)
if [ "${INTEGRITY}" != "ok" ]; then
    echo "[ERROR] Backup integrity check failed: ${INTEGRITY}" >&2
    rm -f "${BACKUP_FILE}"
    exit 1
fi

RAW_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Hot snapshot verified (PRAGMA quick_check: ok, size: ${RAW_SIZE})"

# 3. Compress backup to conserve disk space
gzip -f "${BACKUP_FILE}"
ARCHIVE_FILE="${BACKUP_FILE}.gz"
COMPRESSED_SIZE=$(du -h "${ARCHIVE_FILE}" | cut -f1)

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backup successfully compressed: ${ARCHIVE_FILE} (${COMPRESSED_SIZE})"

# 4. Retention policy: delete backups older than 14 days
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Cleaning up backups older than 14 days..."
find "${BACKUP_DIR}" -type f \( -name "backup_*.sqlite" -o -name "backup_*.sqlite.gz" \) -mtime +14 -exec rm -f {} +
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backup and retention cycle completed successfully."
