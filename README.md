# Altar — Developer Guide

Experiment data management tools based on Sacred infrastructure.

**🌐 User Documentation**: [https://dreamrepo.github.io/Altar/](https://dreamrepo.github.io/Altar/)

## Repository Structure

```
Altar/
├── AltarDocker/      # Docker stack: MongoDB, MinIO, Omniboard
├── AltarExtractor/   # Dash app to browse Sacred experiments
├── AltarSender/      # GUI to send experiments to MongoDB/MinIO
├── AltarViewer/      # Launch Omniboard instances
├── _data/            # Website YAML content
├── _layouts/         # Jekyll templates
└── assets/           # CSS/JS for docs site
```

## Development Setup

### Deploy Local Stack

```bash
cd AltarDocker
cp .env.example .env  # Edit with your credentials
docker compose up -d
```

Access: MongoDB (27017), MinIO Console (9001), Omniboard (9015)

### Run Components

```bash
# AltarExtractor
cd AltarExtractor
pip install -r requirements.txt
python app.py

# AltarSender
cd AltarSender
pip install -r requirements.txt
python app.py

# AltarViewer
cd AltarViewer
pip install -r requirements.txt
python src/main.py
```

## Documentation Website

### Local Preview

```bash
# Install Jekyll (requires Ruby)
gem install bundler jekyll

# Serve locally
bundle install
bundle exec jekyll serve
```

Visit: http://localhost:4000

### Edit Content

Edit YAML files in `_data/`:
- `_data/index.yml` - Home page
- `_data/docker.yml` - AltarDocker docs
- `_data/extractor.yml` - AltarExtractor docs
- `_data/sender.yml` - AltarSender docs
- `_data/viewer.yml` - AltarViewer docs

See [DOCS.md](DOCS.md) for detailed editing instructions.

### Deploy

Push to `main` branch - GitHub Pages auto-builds and deploys.

## Building Executables

```bash
# AltarSender
cd AltarSender
pip install -r requirements-dev.txt
pyinstaller AltarSender.spec

# AltarViewer
cd AltarViewer
pip install -r requirements-dev.txt
pyinstaller AltarViewer.spec
```

Outputs in `dist/` directory.

## Testing

```bash
# AltarViewer
cd AltarViewer
pip install -r requirements-dev.txt
pytest

# AltarExtractor (if tests exist)
cd AltarExtractor
pytest
```

## License

GPL v3
