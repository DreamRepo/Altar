from __future__ import annotations
import sys
import os

# Check if running in PyInstaller bundle
_FROZEN = getattr(sys, 'frozen', False)

import sacred
# Disable source/dependency discovery globally for PyInstaller (no source files on disk)
sacred.SETTINGS["DISCOVER_SOURCES"] = "none"
sacred.SETTINGS["DISCOVER_DEPENDENCIES"] = "none"

# Monkey-patch Source.create and MongoObserver.save_sources to handle missing files in PyInstaller
if _FROZEN:
    from sacred import dependencies
    from sacred.observers import mongo as mongo_module
    
    # Patch Source.create
    _original_source_create = dependencies.Source.create
    
    def _patched_source_create(filename, save_git_info=True):
        if not filename or not os.path.exists(filename):
            # Return a dummy Source instead of raising an error
            return dependencies.Source(filename or "frozen_app", "frozen", None, None, False)
        return _original_source_create(filename, save_git_info)
    
    dependencies.Source.create = staticmethod(_patched_source_create)
    
    # Patch MongoObserver.save_sources to skip missing files
    def _patched_save_sources(self, ex_info):
        # Return empty list - no sources to save in frozen app
        return []
    
    mongo_module.MongoObserver.save_sources = _patched_save_sources

from sacred import Experiment
from sacred.observers import MongoObserver
import numpy as np
import os
import pandas as pd
import csv
from typing import Any, Dict
import services.format_content as fc
from services.raw_data_saver import save_raw_data
from services.mongo_conn import build_mongo_url_from_payload


def send_experiment(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Validate presence of top-level domains
    if not isinstance(payload, dict):
        return {"ok": False, "message": "Invalid payload"}

    data_payload = payload.get("experiment", {}) or {}
    mongo_payload = payload.get("mongo", {}) or {}
    # experiment_name = (data_payload.get("name") or "").strip()
    selectors = data_payload.get("selectors", {}) or {}
    config = selectors.get("config", {}) or {}
    metrics = selectors.get("metrics", {}) or {}
    results = selectors.get("results", {}) or {}
    raw_data = selectors.get("raw_data", {}) or {}
    artifacts = selectors.get("artifacts", {}) or {}
    folders = data_payload.get("folders", [])

    raw_data_save_options = raw_data.get("options", {}) or {}

    # --- Build Mongo connection using shared helper ---
    mongo_payload = payload.get("mongo", {}) or {}
    mongo_url, mongo_db = build_mongo_url_from_payload(mongo_payload)

    print(f"payload: {payload}\n")
    # Attach Mongo observer

    # Keep originals for per-folder formatting
    base_config = config
    base_results = results
    base_raw_data = raw_data
    base_artifacts = artifacts
    base_metrics = metrics
    results_messages = []

    if folders and len(folders) > 0:
        all_ok = True
        for folder in folders:
            experiment_name = folder.replace("\\", "/").split("/")[-1]
            cfg = {'experiment': experiment_name}
            cfg.update(fc.format_config(folder, base_config))
            mets = fc.format_metrics(folder, base_metrics)
            arts = fc.format_raw_data(folder, base_artifacts)
            res = fc.format_results(folder, base_results)
            rawda = fc.format_raw_data(folder, base_raw_data)
            ex = Experiment(experiment_name, save_git_info=False)
            try:
                ex.observers.append(MongoObserver(url=mongo_url, db_name=mongo_db))
            except Exception as e:
                import traceback
                print(f"ERROR connecting to MongoDB: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                raise RuntimeError(f"Failed to connect to MongoDB: {e}") from e

            @ex.main
            def run(_run, _mets=mets, _arts=arts, _folder=folder, _res=res):
                print(f"res: {_res}\n")
                data_files = {}
                if isinstance(_mets, dict) and 'columns' in _mets:
                    columns_dict = _mets.get('columns', {}) or {}
                    if 'x_axis' in _mets:
                        x_axis = _mets.get('x_axis', []) or []
                        for column, series in columns_dict.items():
                            # log up to the min length to avoid index errors
                            limit = min(len(series), len(x_axis))
                            for i in range(limit):
                                _run.log_scalar(column, series[i], step=x_axis[i])
                    else:
                        for column, series in columns_dict.items():
                            for value in series:
                                _run.log_scalar(column, value)
                config_arts = {}
                for a in _arts.values():
                    src = a.get('source_path') if isinstance(a, dict) else str(a)
                    name = a.get('new_name') if isinstance(a, dict) else None
                    if not src:
                        continue
                    if os.path.exists(src):
                        try:
                            _run.add_artifact(src, name=name)
                            config_arts[a.get('minio_folder')] = name
                        except Exception as e:
                            print(f"WARNING: Failed to add artifact {src}: {e}", file=sys.stderr)
                data_files['artifacts'] = config_arts

                if len(rawda) > 0:
                    try:
                        rd_result, rd_config = save_raw_data(rawda, raw_data_save_options, payload.get("minio", {}) or {})
                        cfg['raw_data'] = rd_config
                        print(f"raw_data save: {rd_result}")
                        data_files['raw_data'] = rd_config
                    except Exception as e:
                        import traceback
                        print(f"ERROR saving raw_data: {e}", file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)
                        # Re-raise with more context
                        raise RuntimeError(f"Failed to save raw_data: {e}") from e

                _run.info['dataFiles'] = data_files
                _run.info['result'] = _res
            

            ex.add_config(cfg)

            try:
                current_run = ex.run(options={'--capture': 'no'})
                current_run.result = res
                # After run, optionally save raw_data (if any) according to options
                results_messages.append(f"{experiment_name or 'TEST_EXPERIMENT'}, run {current_run._id} sent")
            except Exception as e:
                import traceback
                print("ERROR running experiment:", e)
                print(traceback.format_exc())
                all_ok = False
                results_messages.append(f"{experiment_name or 'TEST_EXPERIMENT'} failed: {e}")
        return {"ok": all_ok, "message": "; ".join(results_messages)}