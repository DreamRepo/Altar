# AltarDocker

Docker Compose stack for running Sacred experiment tracking infrastructure locally.

## What's Included

| Service | Description | Port |
|---------|-------------|------|
| **MongoDB** | Stores experiment metadata | 27017 |
| **MinIO** | S3-compatible object storage | 9000, 9001 |

**Default configuration:**
- MongoDB: `localhost:27017`, database: `sacred`
- MinIO: S3 API `localhost:9000`, Console `localhost:9001`
  - Credentials: `minio_admin` / `changeme123`

## Installation

Choose your guide based on your needs:

- **[QUICKSTART-GUI.md](QUICKSTART-GUI.md)** — Easy install with Docker Desktop (no command line)
- **[DEPLOY.md](DEPLOY.md)** — Complete deployment guide with customization options
- **[MANAGE_USERS.md](MANAGE_USERS.md)** — MongoDB and MinIO user management

## Access the Services

- **MongoDB**: `mongodb://localhost:27017`
- **MinIO Console**: http://localhost:9001
- **Use with:**
  - [AltarSender](../AltarSender) — Upload experiments
  - [AltarViewer](../AltarViewer) — View experiments with Omniboard
  - [AltarExtractor](../AltarExtractor) — Analyze and export data


## For developers: 

### Adding MongoDB Authentication

By default, MongoDB runs without authentication. To add authentication:

1. **Add to your `.env` file:**
   ```dotenv
   MONGO_ROOT_USER=admin
   MONGO_ROOT_PASSWORD=your_secure_password
   ```

2. **Update the mongo service in `docker-compose.yml`** to use these variables:
   ```yaml
   mongo:
     image: mongo:6
     container_name: mongo_altar
     restart: unless-stopped
     environment:
       MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER}
       MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
       MONGO_INITDB_DATABASE: ${MONGO_DB}
     ports:
       - "${MONGO_PORT}:27017"
     volumes:
       - ${MONGO_DATA_PATH}:/data/db
   ```

3. **Recreate the container:**
   ```bash
   docker compose down
   docker compose up -d
   ```

> **Note:** After enabling authentication, you'll need to update connection strings in AltarSender, AltarViewer, and AltarExtractor to include the username and password.

## Requirements

- Docker >= 24
- Docker Compose v2
- At least 2 GB free disk space

## Related

- [AltarExtractor](https://github.com/DreamRepo/AltarExtractor) — Browse and filter Sacred experiments (standalone deployment)
- [AltarSender](https://github.com/DreamRepo/AltarSender) — GUI to send experiments to Sacred and MinIO
- [AltarViewer](https://github.com/DreamRepo/AltarViewer) — Launch Omniboard configured for your database

## License

GNU General Public License v3.0

