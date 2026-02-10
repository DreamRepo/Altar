def mask_uri(uri: str) -> str:
    """Mask the password in a Mongo URI for display."""
    try:
        if "://" not in uri or "@" not in uri:
            return uri
        scheme, rest = uri.split("://", 1)
        creds, host = rest.split("@", 1)
        if ":" in creds:
            user, _pwd = creds.split(":", 1)
            return f"{scheme}://{user}:****@{host}"
        return uri
    except Exception:
        return uri
