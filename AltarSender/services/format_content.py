import pandas as pd
import numpy as np
import json
import os
from services.hash import make_compact_uid_b32
import re
try:
    import yaml
except ImportError:
    yaml = None


def coerce_bool_option(value):
    if value == 0:
        return None
    else:
        return 0


def _parse_folder_name_with_pattern(folder_path: str, pattern: str) -> dict:
    """Parse folder name using the given pattern and return extracted values.
    
    Pattern syntax:
    - $variable$ - matches any characters (greedy minimal)
    - $variable%N$ - matches exactly N characters
    """
    if not pattern or not folder_path:
        return {}
    
    folder_name = os.path.basename(folder_path.replace("\\", "/"))
    
    # Extract variable definitions from pattern
    # Format: $name$ or $name%length$
    var_pattern = r'\$([^$%]+)(?:%(\d+))?\$'
    variables = re.findall(var_pattern, pattern)
    
    if not variables:
        return {}
    
    # Build regex from pattern by replacing $var$ or $var%N$ with named groups
    regex_pattern = re.escape(pattern)
    for var_name, length in variables:
        if length:
            # Exact length: match exactly N characters
            escaped_var = re.escape(f"${var_name}%{length}$")
            regex_pattern = regex_pattern.replace(escaped_var, f"(?P<{var_name}>.{{{length}}})")
        else:
            # No length: match any characters (non-greedy)
            escaped_var = re.escape(f"${var_name}$")
            regex_pattern = regex_pattern.replace(escaped_var, f"(?P<{var_name}>.+?)")
    
    # Try to match
    try:
        match = re.match(f"^{regex_pattern}$", folder_name)
        if match:
            return match.groupdict()
    except re.error:
        pass
    
    return {}


def format_config(experiment_folder, config):
    """Format config from file and/or parsed folder values.
    
    Returns a dict that may include:
    - Values from config file (JSON, YAML, CSV, Excel)
    - Values parsed from folder name (if parse_from_folder is enabled)
    """
    data = {}
    
    config_name = config.get("name", "None") if isinstance(config, dict) else "None"
    use_custom_path = config.get("use_custom_path", False) if isinstance(config, dict) else False
    custom_path = config.get("custom_path", "") if isinstance(config, dict) else ""
    
    # Load config from file if specified
    file_path = None
    config_type = None
    
    if use_custom_path and custom_path:
        file_path = custom_path
        config_type = custom_path.split(".")[-1].lower()
    elif config_name and config_name != "None":
        file_path = os.path.join(experiment_folder, config_name)
        config_type = config_name.split(".")[-1].lower()
    
    if file_path and config_type:
        if config_type == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if config.get("options", {}).get("flatten"):
                data = pd.json_normalize(data, sep="_").to_dict(orient="records")[0]
        elif config_type in ("yaml", "yml"):
            if yaml is None:
                raise ValueError("PyYAML is not installed. Run: pip install pyyaml")
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if config.get("options", {}).get("flatten") and isinstance(data, dict):
                data = pd.json_normalize(data, sep="_").to_dict(orient="records")[0]
        elif config_type == "xlsx" or config_type == "xlsm":
            data = pd.read_excel(file_path, sheet_name=config.get("sheet")).to_dict(orient="records")
        elif config_type == "csv":
            sep = (config.get("options", {}) or {}).get("sep", ",")
            sep = "\t" if sep == "\\t" else sep
            data = pd.read_csv(file_path, sep=sep).to_dict(orient="records")
        else:
            raise ValueError(f"Unsupported config type: {config_type}")
    
    # Parse folder name if enabled (this is done per-folder for batch mode)
    if config.get("parse_from_folder") and config.get("folder_pattern"):
        parsed_values = _parse_folder_name_with_pattern(experiment_folder, config.get("folder_pattern", ""))
        if parsed_values:
            # Merge parsed values into data (parsed values take precedence)
            if isinstance(data, dict):
                data.update(parsed_values)
            elif isinstance(data, list):
                # If data is a list (from CSV/Excel), add parsed values to each record
                for record in data:
                    if isinstance(record, dict):
                        record.update(parsed_values)
            else:
                # data is empty or not a dict, just use parsed values
                data = parsed_values
    
    return data


def format_metrics(experiment_folder, metrics):
    metrics_data = {}
    metrics_name = metrics.get("name", "None") if isinstance(metrics, dict) else "None"
    if metrics_name and metrics_name != "None":
        file_path = os.path.join(experiment_folder, metrics_name)
        metrics_type = metrics_name.split(".")[-1]
        # determine header handling once
        header_arg = coerce_bool_option(metrics.get("options", {}).get("header", 0))
        if metrics_type == "xlsx" or metrics_type == "xlsm":
            df = pd.read_excel(
                file_path,
                sheet_name=metrics.get("sheet"),
                header=header_arg,
            )
        elif metrics_type == "csv":
            # respect configured separator for metrics CSV
            sep = (metrics.get("options", {}) or {}).get("sep", ",")
            # handle both escaped and real tab characters
            sep = "\t" if sep in ("\\t", "\t") else sep
            df = pd.read_csv(file_path, header=header_arg, sep=sep)
        else:
            raise ValueError(f"Unsupported metrics type: {metrics_type}")

        metrics_columns = {}

        options = metrics.get("options", {}) or {}
        selected_cols = options.get("selected_cols", []) or []
        has_time = 1 if options.get("has_time", 0) == 1 else 0
        time_col_name = options.get("time_col", "")

        # when no header, pandas will use integer column indices; UI sends strings
        def _normalize_col_key(name):
            if header_arg is None:  # no header
                try:
                    return int(name)
                except Exception:
                    return name
            return name

        # set x_axis if requested (do this regardless of it being in selected columns)
        if has_time and time_col_name != "":
            time_key = _normalize_col_key(time_col_name)
            if time_key in df.columns:
                metrics_data["x_axis"] = df[time_key].to_list()

        for col in selected_cols:
            col_key = _normalize_col_key(col)
            if col_key in df.columns:
                metrics_columns[col] = df[col_key].to_list()

        metrics_data["columns"] = metrics_columns

    return metrics_data


def format_results(experiment_folder, results):
    results_data = {}
    results_name = results.get("name", "None") if isinstance(results, dict) else "None"
    if results_name and results_name != "None":
        file_path = os.path.join(experiment_folder, results_name)
        results_type = results_name.split(".")[-1]
        if results_type == "xlsx" or results_type == "xlsm":
            data_ = pd.read_excel(file_path, sheet_name=results.get("sheet"), header=None).to_dict(orient="records")
            data = {e[0]: e[1] for e in data_}

        elif results_type == "csv":
            sep = (results.get("options", {}) or {}).get("sep", ",")
            sep = "\t" if sep == "\\t" else sep
            data_ = pd.read_csv(file_path, sep=sep, header=None).to_dict(orient="records")
            data = {e[0]: e[1] for e in data_}

        elif results_type == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported results type: {results_type}")
        
        results_data = {}

        for k, v in data.items():
            results_data[k] = v

    return results_data


def format_raw_data(experiment_folder, raw_data):
    files = {}
    raw_data_name = raw_data.get("name", "None") if isinstance(raw_data, dict) else "None"
    if raw_data_name and raw_data_name != "None":
        experiment_name = experiment_folder.split("/")[-1]
        file_path = os.path.join(experiment_folder, raw_data_name)
        if os.path.isfile(file_path):
            file = {
                'source_path': file_path,
                'new_name': make_compact_uid_b32(experiment_name) + "-" + raw_data_name,
                'minio_folder':  raw_data_name.split(".")[0],
            }
            files[raw_data_name] = file

        elif os.path.isdir(file_path):
            for f in raw_data.get("files", []):
                file = {
                    'source_path': os.path.join(file_path, f),
                    'new_name': make_compact_uid_b32(experiment_name) + "-" + f,
                    'minio_folder':  f.split(".")[0],
                }
                files[f] = file
        else:
            raise ValueError(f"Raw data file or folder not found: {file_path}")

    return files