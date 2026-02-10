# AltarDocker — Backup & Restore Guide

Complete guide for backing up and restoring MongoDB and MinIO data.

---

## MongoDB

### Install MongoDB Database Tools

`mongodump` and `mongorestore` are part of **MongoDB Database Tools**. They are not included in MongoDB by default and must be installed separately.

> **Note:** If you use the Docker container methods below, you don't need to install these tools locally — they're already available inside the `mongo` container.

**Ubuntu/Debian:**
```bash
# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install database tools
sudo apt update
sudo apt install mongodb-database-tools
```

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-database-tools
```

**Windows:**

1. Download from: https://www.mongodb.com/try/download/database-tools
2. Extract the ZIP file
3. Add the `bin` folder to your PATH, or copy the executables to a folder already in PATH

**Verify installation:**
```bash
mongodump --version
mongorestore --version
```

---

### Dump (Backup)

#### From Docker container

```bash
# Dump entire database to local folder
docker exec mongo_altar mongodump --db sacred --out /data/db/backup

# Copy backup from container to host
docker cp mongo_altar:/data/db/backup ./mongo_backup
```

#### From host (if mongodump is installed locally)

```bash
mongodump --host localhost --port 27017 --db sacred --out ./mongo_backup
```

#### With authentication

```bash
mongodump --host localhost --port 27017 \
  --username YOUR_USER \
  --password YOUR_PASSWORD \
  --authenticationDatabase admin \
  --db sacred \
  --out ./mongo_backup
```

### Restore

#### To Docker container

```bash
# Copy backup to container
docker cp ./mongo_backup mongo_altar:/data/db/backup

# Restore from backup
docker exec mongo_altar mongorestore --db sacred /data/db/backup/sacred
```

#### From host (if mongorestore is installed locally)

```bash
mongorestore --host localhost --port 27017 --db [database_name] [/path/to/backup]
```

#### With authentication

```bash
mongorestore --host localhost --port 27017 \
  --username YOUR_USER \
  --password YOUR_PASSWORD \
  --authenticationDatabase admin \
  --db sacred \
  ./mongo_backup/sacred
```

#### Drop existing data before restore

Add `--drop` to remove existing collections before restoring:

```bash
docker exec mongo_altar mongorestore --drop --db sacred /data/db/backup/sacred
```

---

## MinIO

MinIO stores data as files on disk. You can back up using standard file tools or the MinIO client (`mc`).

### Option 1: Direct file copy (simplest)

Since MinIO data is mounted to `./data/minio/` by default, you can simply copy the folder:

#### Backup

```bash
# Stop MinIO first to ensure consistency (optional but recommended)
docker compose --profile minio stop minio

# Copy data folder
cp -r ./data/minio ./minio_backup

# Restart MinIO
docker compose --profile minio start minio
```

#### Restore

```bash
# Stop MinIO
docker compose --profile minio stop minio

# Restore data folder
rm -rf ./data/minio
cp -r ./minio_backup ./data/minio

# Restart MinIO
docker compose --profile minio start minio
```

### Option 2: Using MinIO Client (`mc`)

The MinIO client provides more control and can sync between MinIO instances.

#### Install MinIO Client

**Linux/macOS:**
```bash
curl https://dl.min.io/client/mc/release/linux-amd64/mc -o mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://dl.min.io/client/mc/release/windows-amd64/mc.exe" -OutFile "mc.exe"
```

#### Configure alias

```bash
mc alias set altar http://localhost:9000 minio_admin changeme123
```

#### Backup (mirror to local folder)

```bash
# Mirror entire MinIO server to local backup
mc mirror altar/ ./minio_backup/
```

#### Restore (mirror from local folder)

```bash
# Mirror local backup to MinIO server
mc mirror ./minio_backup/ altar/
```

#### Sync specific bucket

```bash
# Backup single bucket
mc mirror altar/my-bucket ./minio_backup/my-bucket

# Restore single bucket
mc mirror ./minio_backup/my-bucket altar/my-bucket
```

---

## Automated Backup Script (Linux)

Create a script to back up both MongoDB and MinIO:

```bash
#!/bin/bash
# backup_altar.sh

set -e

BACKUP_DIR="/path/to/backups"
DATE_STR=$(date +%Y-%m-%d_%H-%M)
BACKUP_PATH="$BACKUP_DIR/$DATE_STR"

mkdir -p "$BACKUP_PATH"

echo "=== Backing up MongoDB ==="
docker exec mongo_altar mongodump --db sacred --out /data/db/backup
docker cp mongo_altar:/data/db/backup "$BACKUP_PATH/mongo"
docker exec mongo_altar rm -rf /data/db/backup

echo "=== Backing up MinIO ==="
# Option A: Direct copy (uncomment if using)
# cp -r ./data/minio "$BACKUP_PATH/minio"

# Option B: Using mc (uncomment if using)
# mc mirror altar/ "$BACKUP_PATH/minio/"

echo "=== Backup complete: $BACKUP_PATH ==="

# Keep only last 7 backups
cd "$BACKUP_DIR"
ls -dt */ | tail -n +8 | xargs -d '\n' rm -rf 2>/dev/null || true
```

Make executable and schedule:

```bash
chmod +x backup_altar.sh

# Add to crontab (daily at 3am)
crontab -e
```

Add this line:
```
0 3 * * * /path/to/backup_altar.sh >> /path/to/backup.log 2>&1
```

---

## Restore Script (Linux)

```bash
#!/bin/bash
# restore_altar.sh

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore_altar.sh /path/to/backup/2025-01-08_03-00"
    exit 1
fi

BACKUP_PATH="$1"

if [ ! -d "$BACKUP_PATH" ]; then
    echo "Error: Backup directory not found: $BACKUP_PATH"
    exit 1
fi

echo "=== Restoring from: $BACKUP_PATH ==="

if [ -d "$BACKUP_PATH/mongo" ]; then
    echo "=== Restoring MongoDB ==="
    docker cp "$BACKUP_PATH/mongo" mongo_altar:/data/db/restore
    docker exec mongo_altar mongorestore --drop --db sacred /data/db/restore/sacred
    docker exec mongo_altar rm -rf /data/db/restore
fi

if [ -d "$BACKUP_PATH/minio" ]; then
    echo "=== Restoring MinIO ==="
    # Option A: Direct copy
    # docker compose --profile minio stop minio
    # rm -rf ./data/minio
    # cp -r "$BACKUP_PATH/minio" ./data/minio
    # docker compose --profile minio start minio

    # Option B: Using mc
    # mc mirror "$BACKUP_PATH/minio/" altar/
    echo "MinIO restore: uncomment preferred method in script"
fi

echo "=== Restore complete ==="
```

---

## Tips

- **Test your backups** regularly by restoring to a test environment
- **Store backups off-site** (cloud storage, external drive, different server)
- **Document your backup schedule** and retention policy
- **MongoDB:** Use `--gzip` flag to compress dumps: `mongodump --gzip --db sacred --out ./backup`
- **MinIO:** The `mc mirror` command supports `--overwrite` and `--remove` flags for exact mirroring

