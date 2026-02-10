# AltarDocker - Quick Start for Docker Desktop Users

**No coding or terminal required!** This guide is for users who prefer Docker Desktop's graphical interface.

## Prerequisites

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Make sure Docker Desktop is running

## Simple Setup (3 Steps)

### 1. Download the File

Download `docker-compose.yml` from the [AltarDocker repository](https://github.com/DreamRepo/AltarDocker) to a folder on your computer.
Copy the full path of this folder. 

![image](https://github.com/DreamRepo/AltarDocker/compose_path.png)


### 2. Deploy with Docker Desktop

**Using Docker Desktop GUI - if you find the option**
1. Open Docker Desktop
2. Click the **"+"** button or **"Import"** in the Containers tab
3. Select your `docker-compose.yml` file
4. Click **"Run"**

**Using Terminal:**

Open a terminal in the folder containing `docker-compose.yml`, then run:

```bash
# Default deployment (without MinIO)
docker compose up -d

# With MinIO (for S3-compatible storage)
docker compose --profile minio up -d
```

> **When to use MinIO?** Only if you need S3-compatible storage for raw data files. For most local setups, you don't need it. See [DEPLOY.md](DEPLOY.md) for more details.

![video](https://github.com/DreamRepo/AltarDocker/install_altardocker.mp4)

### 3. Access Your Services

| Service | URL | Description |
|---------|-----|-------------|
| **Omniboard** | http://localhost:9004 | Visualize and compare Sacred experiments |
| **AltarExtractor** | http://localhost:8050 | Browse and filter experiment data |
| **MongoDB** | `mongodb://localhost:27017` | Database (credentials: `admin` / `changeme123`) |

That's it! Your services are running with sensible defaults.

> **Tip:** Omniboard is already configured to connect to MongoDB. Just open http://localhost:9004 and start exploring your experiments!

If you deployed with `--profile minio`, you also have:

| Service | URL | Credentials |
|---------|-----|-------------|
| **MinIO Console** | http://localhost:9001 | `minio_admin` / `changeme123` |
| **MinIO S3 API** | http://localhost:9000 | — |

## Want to Customize?

**Simple method** - Edit the compose file directly:
- Open `docker-compose.yml` in Notepad/VS Code
- Find lines with `:-` (e.g., `:-change_me`)
- Change the value after `:-` to customize

**Advanced method** - See [DEPLOY.md](DEPLOY.md) for:
- Using `.env` files
- Changing ports
- Custom data storage paths
- Authentication setup

## Managing Services

In Docker Desktop:
- **View status**: Go to "Containers" tab → see `mongo_altar`, `omniboard`, `altar_extractor`
- **Stop**: Click the Stop button
- **Restart**: Click the Start button
- **View logs**: Click the container name

## Troubleshooting

**Port conflict?**
- Edit compose file and change `:-27017` to `:-27077` (see customization above)

**Can't access services?**
- Check containers are "Running" in Docker Desktop
- See [DEPLOY.md](DEPLOY.md) for detailed troubleshooting

## Next Steps

- Open http://localhost:9004 to visualize experiments with **Omniboard**
- Open http://localhost:8050 to analyze experiments with **AltarExtractor**
- Download [AltarSender](https://github.com/DreamRepo/AltarSender/releases) to upload experiments
- See [MANAGE_USERS.md](MANAGE_USERS.md) to create additional MongoDB users
