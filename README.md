## Altar — Experiment Data Management

A monorepo of small tools and deployment configs to manage experiment data end‑to‑end:
- Send (meta)data to a database (MongoDB - noSQL) following a flexible data model (Sacred model)
- Store raw/heavy files (MinIO - s3 compatible)
- Visualization of data online (AltarViewer)
- Browsing and filtering Sacred experiments, extract datasets (AltarExtractor)
- Sending experiments to MongoDB/MinIO (AltarSender)

**📚 Documentation Site**: [https://dreamrepo.github.io/Altar/](https://dreamrepo.github.io/Altar/)

**✏️ Editing Documentation**: See [DOCS.md](DOCS.md) for detailed instructions on editing the website content using Jekyll and YAML.

### Repository structure

```
Altar/
├─ AltarDocker/      # Docker Compose: MongoDB, MinIO, Omniboard, Extractor + docs
├─ AltarExtractor/   # Dash app to browse, filter, and export Sacred experiments
├─ AltarSender/      # GUI to send experiments to Sacred (+ MinIO artifacts/raw data)
├─ _data/            # Website content in YAML format (easy to edit!)
├─ _layouts/         # Jekyll page templates
├─ assets/           # Website assets (CSS, JS)
├─ index.html        # Landing page
├─ DOCS.md           # Documentation editing guide
└─ README.md
```

### Subprojects

- **AltarDocker**: Local stack for MongoDB + MinIO + Omniboard + AltarExtractor
  - What it provides: a reproducible local/dev environment to store and visualize experiments.
  - Start here if you need a database and storage running locally.
  - Docs:
    - Deployment: `AltarDocker/DEPLOY.md`
    - User management: `AltarDocker/MANAGE_USERS.md`
    - Compose file: `AltarDocker/docker-compose.yml`

- **AltarExtractor**: Dash web app for browsing Sacred experiments
  - What it does: connect to MongoDB, browse Sacred runs, filter by config keys, view metrics, and export data as CSV or explore in Pygwalker.
  - Can run standalone or as part of AltarDocker (via `--profile extractor`).
  - Get started: `pip install -r requirements.txt`, run `python app.py`, or use Docker.
  - Docs: `AltarExtractor/README.md`

- **AltarSender**: GUI to send experiments to Sacred (and MinIO)
  - What it does: select per-experiment folders, map files (config/results/metrics/artifacts/raw data), then send to MongoDB Sacred and optionally MinIO or a filesystem path.
  - Get started: create/activate a virtual env, `pip install -r requirements.txt`, run `python app.py`.
  - Docs: `AltarSender/README.md`

### Quick start

1. **Run the local stack** (MongoDB + Omniboard):
   ```bash
   cd AltarDocker
   # Edit .env with your credentials
   docker compose up -d
   ```

2. **Add the Extractor** (optional):
   ```bash
   docker compose --profile extractor up -d
   ```
   Then open http://localhost:8050 and connect to MongoDB (host: `mongo`, port: `27017`).

3. **Add MinIO** (optional):
   ```bash
   docker compose --profile minio up -d
   ```

4. **Send experiments**:
   Use `AltarSender` → `python app.py` and configure sources (config/results/metrics/artifacts/raw data).

### URLs (default)

| Service        | URL                      |
|----------------|--------------------------|
| MongoDB        | mongodb://localhost:27017 |
| Omniboard      | http://localhost:9004    |
| AltarExtractor | http://localhost:8050    |
| MinIO Console  | http://localhost:9001    |
| MinIO S3 API   | http://localhost:9000    |

### Requirements

- Python 3.x (recommended: use a virtual environment)
- pip for Python dependencies
- Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux) to run the local data stack

### Useful links

- Deployment: `AltarDocker/DEPLOY.md`
- Manage users and access: `AltarDocker/MANAGE_USERS.md`
- Experiment sender docs: `AltarSender/README.md`
- Extractor docs: `AltarExtractor/README.md`

### Notes

- Credentials and endpoints for MongoDB/MinIO are configured in the Docker `.env` file.
- Omniboard connects to your MongoDB to visualize runs and artifacts; ensure its connection string matches your database/auth setup.
- AltarExtractor can save MongoDB credentials in browser local storage for convenience.

### Related Projects

- [AltarDocker](https://github.com/DreamRepo/AltarDocker) — Docker Compose stack for MongoDB, MinIO, Omniboard, and AltarExtractor
- [AltarExtractor](https://github.com/DreamRepo/AltarExtractor) — Dash web app to browse and filter Sacred experiments
- [AltarSender](https://github.com/DreamRepo/AltarSender) — GUI to send experiments to Sacred and MinIO

### License

GNU General Public License v3.0. See `LICENSE` at the repository root.
