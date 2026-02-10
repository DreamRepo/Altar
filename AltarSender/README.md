# AltarSender — Experiment Sender to Sacred


![Send from folder — overview](https://raw.githubusercontent.com/DreamRepo/AltarSender/refs/heads/main/assets/send_from_folder.png)


[➡️ Download the latest release](https://github.com/DreamRepo/AltarSender/releases) for Windows, macOS, or Linux.

A graphical user interface (GUI) built with Python and CustomTkinter to send experiment results to a MongoDB Sacred database. Optionally upload heavy files to MinIO or a local/network file path.

---

![AltarSender — app screenshot](https://raw.githubusercontent.com/DreamRepo/AltarSender/refs/heads/main/assets/snapshot_app.png)

## Quick guide: Sacred infrastructure (at a glance)

The simplest mapping to help you fill the app:

| Field | What it means | Accepted formats |
|---|---|---|
| Config | Experimental parameters | JSON, CSV, Excel, YAML, or extraction from folder name |
| Metrics | XY data points | CSV, Excel |
| Artifacts | Small files (approx. <25 MB) | Any file (PNG, JPG, CSV, PDF, etc.) |
| Raw data | Large files (approx. >25 MB) | Any file (PNG, JPG, CSV, PDF, etc.) |
| Results | Performance numbers | JSON, CSV, Excel |

Tip: MongoDB stores your metadata (config, results, metrics), while MinIO or your filesystem stores the large raw files.

---

## Features

- Send experiment metadata (config, results, metrics) to MongoDB Sacred
- Upload artifacts to MongoDB (files < 25 MB)
- Upload raw data (large files) to MinIO S3 or filesystem paths
- Batch send multiple experiments with the same folder structure
- Visual mapping of experiment files to Sacred data types

---

## Prerequisites

- **Required:** Python 3.x installed
- **Required:** MongoDB database running (locally or on a server)
- **Optional:** MinIO server for large file storage

> **Deployment instructions:** See [Altar](dreamrepo.github.io/Altar) for setting up MongoDB and MiniIO.

---

## Setup

1. Clone or download the repository:
   ```bash
   git clone https://github.com/DreamRepo/AltarSender.git
   cd AltarSender
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   ```
   
   **Windows:**
   ```bash
   .venv\Scripts\activate
   ```
   
   **Linux/macOS:**
   ```bash
   source .venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

---

## Run the app

```bash
python app.py
```

If you see `ModuleNotFoundError: No module named 'XXXX'`, run:
```bash
pip install XXXX
```

The app window should open.

---

## Configuration

### MongoDB connection

Enter your database credentials in the app. Use the **Test Connection** button to verify connectivity.

### MinIO connection (optional)

If uploading raw data to MinIO, enter your MinIO credentials (endpoint, access key, secret key, bucket name).

---

## Experiment File Configuration

### Select your experiment folder

Each experiment should have its own folder. The folder name becomes the experiment name.

### File categories

#### Config

The experiment configuration (name, conditions, instrument settings, etc.).

**Supported formats:** JSON, CSV, Excel

**JSON example:**
```json
{
    "experiment": {
        "name": "Experiment1",
        "duration": {
            "time": 3200,
            "unit": "seconds"
        }
    }
}
```

With "Flatten JSON" enabled, this becomes:
```json
{
    "experiment_name": "Experiment1",
    "experiment_duration_time": 3200,
    "experiment_duration_unit": "seconds"
}
```

**CSV/Excel format** (no header, key-value pairs):

| param1 | value1 |
|--------|--------|
| param2 | value2 |
| param3 | value3 |

#### Results

Experiment result values. Same format as Config (JSON, CSV, or Excel).

#### Metrics

Time series data for plotting. Supported formats: CSV, Excel.

- If columns have headers, enable **Column header**
- If there's an X-axis column, enable **X-axis column** and select it
- Select which columns to plot in the database

#### Raw data

Large files to upload to MinIO or a filesystem path.

- Select a single file or an entire folder
- Choose destination: local path, network drive, and/or MinIO
- Files are renamed with a hash and organized by type

**Naming convention:**
- `video.tiff` → `video/[hash]_[datetime]_video.tiff` (if folder name contains datetime)
- `video.tiff` → `video/[hash]_video.tiff` (otherwise)

The hash is generated from the experiment folder name (7 alphanumeric characters).

#### Artifacts

Small files (< 50MB) stored directly in MongoDB. Same organization as raw data. These files can be accessed directly from Omniboard.

> **Warning:** Storing large artifacts impacts database performance.

---

## Sending Experiments

### Single experiment

1. Select the experiment folder
2. Configure file mappings
3. Click **Send experiment**

### Batch send (multiple experiments)

For experiments with identical folder structures:

1. Select one experiment folder and configure it
2. Enable **Send multiple experiments**
3. All sibling folders with the same structure will be selected
4. Click **Send experiment**

**Example structure:**
```
Parent folder/
├── 2023-04-17_18_13_Experiment1/
│   ├── config.json
│   ├── results.csv
│   ├── metrics.xlsx
│   ├── capture.png
│   └── raw_data/
│       ├── frames.tiff
│       └── video.mp4
│
└── 2023-04-17_18_18_Experiment2/
    ├── config.json
    ├── results.csv
    ├── metrics.xlsx
    ├── capture.png
    └── raw_data/
        ├── frames.tiff
        └── video.mp4
```

Configure `Experiment1`, enable batch mode, and both experiments will be sent.

---

## Viewing Results

Access your experiments in **Omniboard**:

| Data type  | Location in Omniboard              |
|------------|------------------------------------|
| Config     | **Config** (last menu item)        |
| Results    | **Run Info** → root → result       |
| Metrics    | **Metrics plot**                   |
| Artifacts  | **Artifacts**                      |
| Raw data   | **Run Info** → dataFiles (paths)   |

---

## Building Standalone Executables

You can build a standalone executable that doesn't require Python to be installed. The executable will include all dependencies.

### Prerequisites

Ensure you have the development environment set up:

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### Windows

```bash
# Option 1: Use the build script (recommended)
python build_exe.py

# Option 2: Use PyInstaller directly with the spec file
pyinstaller AltarSender.spec

# Option 3: Build manually
pyinstaller --name=AltarSender --onefile --windowed --noconfirm ^
    --add-data=".venv\Lib\site-packages\customtkinter;customtkinter" ^
    --hidden-import=customtkinter --hidden-import=sacred ^
    --hidden-import=sacred.observers --hidden-import=pymongo ^
    --hidden-import=pandas --hidden-import=numpy --hidden-import=openpyxl ^
    --hidden-import=boto3 --hidden-import=botocore ^
    --collect-all=customtkinter --collect-all=sacred ^
    app.py
```

The executable will be in the `dist/` folder: `dist/AltarSender.exe`

### Linux

```bash
# Option 1: Use the build script (recommended)
python build_exe.py

# Option 2: Use PyInstaller directly with the spec file
pyinstaller AltarSender.spec

# Option 3: Build manually
pyinstaller --name=AltarSender --onefile --windowed --noconfirm \
    --add-data=".venv/lib/python3.*/site-packages/customtkinter:customtkinter" \
    --hidden-import=customtkinter --hidden-import=sacred \
    --hidden-import=sacred.observers --hidden-import=pymongo \
    --hidden-import=pandas --hidden-import=numpy --hidden-import=openpyxl \
    --hidden-import=boto3 --hidden-import=botocore \
    --collect-all=customtkinter --collect-all=sacred \
    app.py
```

The executable will be in the `dist/` folder: `dist/AltarSender`

Make it executable if needed:
```bash
chmod +x dist/AltarSender
```

### macOS

```bash
# Option 1: Use the build script (recommended)
python build_exe.py

# Option 2: Use PyInstaller directly with the spec file
pyinstaller AltarSender.spec

# Option 3: Build manually
pyinstaller --name=AltarSender --onefile --windowed --noconfirm \
    --add-data=".venv/lib/python3.*/site-packages/customtkinter:customtkinter" \
    --hidden-import=customtkinter --hidden-import=sacred \
    --hidden-import=sacred.observers --hidden-import=pymongo \
    --hidden-import=pandas --hidden-import=numpy --hidden-import=openpyxl \
    --hidden-import=boto3 --hidden-import=botocore \
    --collect-all=customtkinter --collect-all=sacred \
    app.py
```

The executable will be in the `dist/` folder: `dist/AltarSender.app` (or `dist/AltarSender` binary)

> **Note:** On macOS, you may need to right-click and select "Open" the first time to bypass Gatekeeper, or run `xattr -cr dist/AltarSender.app` to remove quarantine attributes.

### Build Output

| Platform | Output Location | Output Name |
|----------|----------------|-------------|
| Windows  | `dist/`        | `AltarSender.exe` |
| Linux    | `dist/`        | `AltarSender` |
| macOS    | `dist/`        | `AltarSender.app` or `AltarSender` |

### Troubleshooting

- **Missing module errors:** Add the module as a `--hidden-import` flag
- **Missing data files:** Use `--add-data` to include necessary files
- **Large executable size:** This is normal (~50-100MB) due to bundled Python and dependencies
- **Antivirus warnings:** False positives are common with PyInstaller; whitelist the executable if needed

---

## Automated Builds (GitHub Actions)

This repository includes a GitHub Actions workflow that automatically builds executables for **Windows**, **Linux**, and **macOS**.

### Downloading the Latest Build

1. Go to the [Actions tab](../../actions) in this repository
2. Click on the latest successful **Build Executables** workflow run
3. Scroll down to **Artifacts** and download the version for your platform:
   - **AltarSender-Windows.exe** — Windows executable
   - **AltarSender-Linux** — Linux executable
   - **AltarSender-macOS** — macOS executable
4. Extract the ZIP file to get the executable

> **Note:** On Linux/macOS, you may need to make the file executable:
> ```bash
> chmod +x AltarSender-Linux   # or AltarSender-macOS
> ```

### Creating a Release

To publish a versioned release with executables attached:

1. Go to the [Releases page](../../releases) and click **Draft a new release**
2. Create a new tag (e.g., `v1.0.0`) and give the release a title
3. Add release notes describing changes
4. Click **Publish release**

The GitHub Action will automatically:
- Build executables for all three platforms
- Attach all executables to the release

Users can then download the executable for their platform directly from the release page.

### Manual Workflow Trigger

You can also manually trigger a build:

1. Go to the [Actions tab](../../actions)
2. Select **Build Executables** workflow
3. Click **Run workflow** → **Run workflow**

---

## Related

- [AltarDocker](https://github.com/DreamRepo/AltarDocker) — Deploy MongoDB, MinIO, Omniboard, and AltarExtractor
- [AltarExtractor](https://github.com/DreamRepo/AltarExtractor) — Browse and filter Sacred experiments in a web UI
