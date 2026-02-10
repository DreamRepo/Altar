from __future__ import annotations

from typing import Any, Dict, List, Tuple
from pathlib import Path
import shutil
import os


def _build_minio_endpoint_url(endpoint: str, use_tls: bool) -> str:
    ep = (endpoint or "").strip()
    if ep.startswith("http://") or ep.startswith("https://"):
        return ep
    return ("https://" if use_tls else "http://") + ep


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} Ko"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.2f} Mo"
    else:
        return f"{size_bytes / 1024**3:.2f} Go"


def save_files_locally(files, target_dir) -> Dict[str, Any]:
    """Copy files to a local directory.

    Returns a result dict with counts and per-file status.
    """
    for file in files.values():
        target_dir = f"{target_dir}/{file['minio_folder']}"
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(file['source_path'], f"{target_dir}/{file['new_name']}")
    return {"ok": True, "message": f"Saved {len(files)} files locally to {target_dir}"}


def save_files_to_minio(files, minio_payload) -> Dict[str, Any]:
    """Upload files to a MinIO/S3 bucket using boto3.

    minio_payload must contain: endpoint, access_key, secret_key, bucket, tls (0/1 or bool)
    """
    try:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore
        from botocore.exceptions import ClientError  # type: ignore
    except Exception as e:
        return {"ok": False, "message": f"boto3 not available: {e}", "uploaded": 0, "failed": len(files or []), "details": []}

    endpoint = _build_minio_endpoint_url(minio_payload.get("endpoint", ""), bool(minio_payload.get("tls", 0)))
    access_key = (minio_payload.get("access_key") or "").strip()
    secret_key = (minio_payload.get("secret_key") or "").strip()
    bucket = (minio_payload.get("bucket") or "").strip()

    if not endpoint or not access_key or not secret_key or not bucket:
        return {"ok": False, "message": "Missing MinIO credentials or bucket", "uploaded": 0, "failed": len(files or []), "details": []}

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
    # Verify bucket exists
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception as e:
        return {"ok": False, "message": f"Bucket not accessible: {e}", "uploaded": 0, "failed": len(files or []), "details": []}

    for file in files.values():
        s3.upload_file(file['source_path'], bucket, f"{file['minio_folder']}/{file['new_name']}")
    return {"ok": True, "message": f"Uploaded {len(files)} files to MinIO bucket {bucket}"}


def save_raw_data(files, raw_data_save_options, minio_payload):
    """High-level helper that saves raw data locally and/or to MinIO based on options.

    raw_data_save_options can include:
      - send_minio: bool
      - save_locally: bool
      - local_path: str
    Returns a combined status with sub-results under 'minio' and 'local'.
    """
    send_m = bool(raw_data_save_options.get("send_minio", False))
    save_l = bool(raw_data_save_options.get("save_locally", False))
    local_path = raw_data_save_options.get("local_path", "") or ""

    result = {"ok": True, "message": "", "minio": None, "local": None}
    messages = []
    config = {}

    if save_l:
        local_res = save_files_locally(files, local_path)
        result["local"] = local_res
        result["ok"] = result["ok"] and bool(local_res.get("ok", False))
        messages.append(local_res.get("message", ""))
        config["local"] = get_config(files, local_path=local_path)

    if send_m:
        minio_res = save_files_to_minio(files, minio_payload)
        result["minio"] = minio_res
        result["ok"] = result["ok"] and bool(minio_res.get("ok", False))
        messages.append(minio_res.get("message", ""))
        config["minio"] = get_config(files, minio_payload=minio_payload)

    if not send_m and not save_l:
        result["ok"] = True
        result["message"] = "No raw-data save requested"
        return result, config

    result["message"] = " | ".join(m for m in messages if m)
    return result, config


def get_config(files, minio_payload=None, local_path=None):
    config = {}
    for file in files.values():
        file_config = {
            "type": file['new_name'].split(".")[-1],
            "fileName": file['new_name'],
            "size": format_size(os.path.getsize(file['source_path'])),
        }

        if minio_payload:
            file_config["bucket"] = minio_payload.get("bucket", "")
            file_config["minio_folder"] = file['minio_folder']
        
        else:
            file_config["local_path"] = local_path + "/" + file['minio_folder']
        
        config[file['minio_folder']] = file_config
        
    return config


