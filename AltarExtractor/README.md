# AltarExtractor — Sacred Experiments Browser

A Dash web app to browse Sacred experiments stored in MongoDB. Features a clean Bootstrap UI, saved credentials, config filtering, metrics visualization, and CSV export.

## Features

- Connect to any MongoDB instance with Sacred data
- Browse experiments by name
- Filter runs by configuration keys (boolean, number, string filters)
- View and select metrics for detailed per-step analysis
- Export data as CSV
- Open datasets in Pygwalker for interactive exploration
- Credentials saved in browser local storage

---

## Requirements

- Python 3.9+ recommended
- pip

---

## Setup (Standalone)

1. Create and activate a virtual environment:

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Run the app

```bash
python main.py
```

Open your browser to http://127.0.0.1:8050/

---

## Usage

### Connecting to MongoDB

You can either:
- Paste a full MongoDB URI (e.g., `mongodb+srv://user:pass@cluster/yourdb?authSource=admin`), or
- Fill in individual fields: host, port, username, password, and auth source

Specify the database name (defaults to `sacred`) and click **Connect**.

### UI Features

- **Database credentials panel**: Toggle visibility with the "Database credentials" button
- **Save credentials**: Check to persist connection settings in browser localStorage
- **Config keys selection**: Choose which configuration keys to display and filter by
- **Experiments table**: View runs with selected config columns, sort and paginate
- **Metrics section**: Select metrics to view per-step data
- **Export**: Download as CSV or open in Pygwalker

---

## Deploy with AltarDocker (Recommended)

AltarExtractor is integrated into the [AltarDocker](../AltarDocker) stack and can be deployed alongside MongoDB and Omniboard.

### Start with AltarDocker

```bash
cd ../AltarDocker
docker compose --profile extractor up -d
```

Access at http://localhost:8050

### Connect to MongoDB in Docker

When running inside AltarDocker, use these connection settings:
- **Host**: `mongo` (Docker service name)
- **Port**: `27017`
- **Username**: your `MONGO_ROOT_USER`
- **Password**: your `MONGO_ROOT_PASSWORD`
- **Auth source**: `admin`

See [AltarDocker/DEPLOY.md](../AltarDocker/DEPLOY.md) for full deployment instructions.

---

## Docker Deployment (Standalone)

### Using Docker Compose

1. Build and run:
   ```bash
   docker-compose up -d --build
   ```

2. Access the app at http://localhost:8050

3. Stop:
   ```bash
   docker-compose down
   ```

> **⚠️ Docker Networking Note:**  
> If AltarExtractor and MongoDB are running in the **same Docker network** (e.g., via docker-compose), use the MongoDB **container/service name** (e.g., `mongo`) instead of `localhost` as the host.  
> `localhost` inside a container refers to the container itself, not the host machine or other containers.

### Using Docker directly

1. Build the image:
   ```bash
   docker build -t altar-extractor .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8050:8050 --name altar-extractor altar-extractor
   ```

3. Access at http://localhost:8050

4. Stop and remove:
   ```bash
   docker stop altar-extractor
   docker rm altar-extractor
   ```

---

## Environment Variables

| Variable         | Description                      | Default  |
|------------------|----------------------------------|----------|
| `PORT`           | Port the app listens on          | `8050`   |
| `SACRED_DB_NAME` | Default database name            | `sacred` |

Example:
```bash
docker run -d -p 8050:8050 -e SACRED_DB_NAME=my_db altar-extractor
```

Or in `docker-compose.yml`:
```yaml
environment:
  - SACRED_DB_NAME=my_sacred_db
```

---

## Customization

If your Sacred data uses a different structure than the standard `runs` collection with `experiment.name`, update the query logic in `altar_extractor/services/mongo.py` (see `fetch_sacred_experiment_names` function).

---

## Related

- [AltarDocker](https://github.com/DreamRepo/AltarDocker) — Deploy MongoDB, MinIO, Omniboard, and AltarExtractor
- [AltarSender](https://github.com/DreamRepo/AltarSender) — GUI to send experiments to Sacred