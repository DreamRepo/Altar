#!/bin/bash

# Dumps root repository
BASE_DIR="/home/user/mongodumps/dump"

# Timestamp (ex: 2025-07-07)
DATE_STR=$(date +%Y-%m-%d)

# Destination folder
OUT_DIR="$BASE_DIR/$DATE_STR"

# Execute the dump
/usr/bin/mongodump --host 0.0.0.0 --port 27017 \
  --username "$MONGO_ROOT_USER" \
  --password "$MONGO_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  --out="$OUT_DIR"

# Keep only the last 3 dumps
cd "$BASE_DIR"
ls -dt */ | tail -n +4 | xargs -d '\n' rm -rf
