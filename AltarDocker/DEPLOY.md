# AltarDocker — Deployment Guide

Complete guide for deploying the Altar infrastructure stack for Sacred experiment tracking.

**Services included:**
- MongoDB for experiment metadata
- Omniboard for visualizing and comparing Sacred experiments
- AltarExtractor for browsing and filtering Sacred experiments
- MinIO for S3-compatible object storage *(optional)*

### About MinIO

MinIO is **optional** and **not recommended for local-only deployments**. When running everything locally, storing raw data directly on disk is simpler and faster.

**When to enable MinIO:**
- You plan to host raw data on a **shared server** accessible by multiple machines
- You are deploying the solution on a **remote server** where S3-compatible storage is needed
- You want to prepare for a future migration to cloud or shared infrastructure

---

## Prerequisites
- Docker >= 24 and Docker Compose v2 installed
- At least 2 GB free disk space

---

## 1) (Optional) Customize Settings

**The compose file works without a `.env` file!** It has built-in defaults:
- MongoDB: `sacred` database on port `27017`
- AltarExtractor: port `8050`
- MinIO *(if enabled)*: `minio_admin` / `changeme123` on ports `9000` and `9001`

**To customize**, copy `.env.example` to `.env` and modify the values:

```bash
cp .env.example .env
# Edit .env with your preferred values
```

The `.env.example` file contains:

```dotenv
# MongoDB Configuration
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=changeme123
MONGO_DB=sacred
MONGO_PORT=27017

# Omniboard Configuration
OMNIBOARD_HOST_PORT=9004
OMNIBOARD_DB=sacred

# AltarExtractor Configuration
EXTRACTOR_PORT=8050

# Volume Paths
MONGO_DATA_PATH=./data/mongo/

# ---------------------------------------------------------
# MinIO Configuration (only needed with --profile minio)
# ---------------------------------------------------------
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=your_secure_password
MINIO_S3_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_DATA_PATH=./data/minio/
```

---

## 2) Start the Services

### Default (without MinIO — recommended for local use)

```bash
docker compose up -d
docker ps
```

This starts:
- MongoDB on port 27017
- Omniboard on port 9004
- AltarExtractor on port 8050

### With MinIO (for shared/server deployments)

```bash
docker compose --profile minio up -d
docker ps
```

This additionally starts:
- MinIO S3 API on port 9000
- MinIO Console on port 9001

> **Note:** On Linux, you may need to prefix commands with `sudo`.

### Access URLs

| Service         | URL                            | Profile    |
|-----------------|--------------------------------|------------|
| MongoDB         | `mongodb://localhost:27017`    | default    |
| Omniboard       | http://localhost:9004          | default    |
| AltarExtractor  | http://localhost:8050          | default    |
| MinIO S3 API    | http://localhost:9000          | `minio`    |
| MinIO Console   | http://localhost:9001          | `minio`    |

---

## 3) Connect AltarExtractor to MongoDB

When AltarExtractor runs inside the Docker stack, use these connection settings in the web UI:

| Field         | Value                        |
|---------------|------------------------------|
| Host          | `mongo`                      |
| Port          | `27017`                      |
| Database      | `sacred` (or your `MONGO_DB`)|
| Username      | (leave empty if no auth)     |
| Password      | (leave empty if no auth)     |
| Auth source   | `admin`                      |

> **Tip:** The Docker service name `mongo` is used as the host because both containers share the same Docker network.

---

## Backups

See [BACKUP.md](./BACKUP.md) for complete backup and restore instructions for MongoDB and MinIO.

---

## 4) Cleanup

```bash
docker compose down
# To also remove volumes (deletes data):
# docker compose down -v
```

---

## Troubleshooting

- **Omniboard shows "No experiments found"?** Check that you're connected to the correct database. The default is `sacred` — if your experiments are in a different database, update the `OMNIBOARD_DB` variable in your `.env` file.
- **Omniboard cannot connect to MongoDB?** Verify the MongoDB credentials match between the `mongo` and `omniboard` services. Check the container logs with `docker logs omniboard`.
- **AltarExtractor cannot connect to MongoDB?** Make sure to use `mongo` as the host (Docker service name), not `localhost`.
- **Port conflict?** Change `MONGO_PORT`, `EXTRACTOR_PORT`, `OMNIBOARD_HOST_PORT`, or MinIO port mappings in `.env` or `docker-compose.yml`.
- **MinIO not starting?** Make sure you used `docker compose --profile minio up -d` (MinIO is optional and requires the profile).
- **S3 SDKs:** Use endpoint `http://localhost:9000` with MinIO credentials (requires `--profile minio`).

---

## Related

- [BACKUP.md](./BACKUP.md) — Backup and restore guide for MongoDB and MinIO
- [MANAGE_USERS.md](./MANAGE_USERS.md) — Create and manage MongoDB and MinIO users
- [AltarExtractor](../AltarExtractor) — Browse and filter Sacred experiments (included in this stack)
- [AltarSender](https://github.com/DreamRepo/AltarSender) — GUI to send experiments to Sacred and MinIO
- [Omniboard](https://github.com/vivekratnavel/omniboard) — Web dashboard for Sacred experiments (included in this stack)
