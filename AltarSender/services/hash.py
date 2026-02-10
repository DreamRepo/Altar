import hashlib
import re
from datetime import datetime

# Alphabet Crockford sans I/L/O/U
_ALPH = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _get_current_timestamp_str() -> str:
    """Return current timestamp in format YYYYMMDDTHHMMSS."""
    now = datetime.now()
    return now.strftime("%Y%m%dT%H%M%S")


def extract_timestamp_str(s: str):
    rx = re.compile(
        r'(?P<year>\d{4})[-_/](?P<month>\d{2})[-_/](?P<day>\d{2})\D+'
        r'(?P<hour>\d{2})[-_:](?P<minute>\d{2})(?:[-_:](?P<second>\d{2}))?'
    )
    m = rx.search(s)
    if not m:
        return _get_current_timestamp_str()
    y = int(m.group("year")); mo = int(m.group("month")); d = int(m.group("day"))
    h = int(m.group("hour")); mi = int(m.group("minute"))
    se = int(m.group("second")) if m.group("second") else 0
    return f"{y:04d}{mo:02d}{d:02d}T{h:02d}{mi:02d}{se:02d}"
    

def _to_base32_crockford(b: bytes) -> str:
    n = int.from_bytes(b, "big")
    s = []
    while n:
        s.append(_ALPH[n & 31])
        n >>= 5
    return "".join(reversed(s)) or "0"


def short_hash_b32(name: str, length=7) -> str:
    h = hashlib.blake2b(name.encode(), digest_size=8)  # 8 octets = 64 bits
    b32 = _to_base32_crockford(h.digest())
    return b32[:length]


def make_compact_uid_b32(name: str, length=7) -> str:
    rx = re.compile(
        r'(?P<year>\d{4})[-_/](?P<month>\d{2})[-_/](?P<day>\d{2})\D+'
        r'(?P<hour>\d{2})[-_:](?P<minute>\d{2})(?:[-_:](?P<second>\d{2}))?'
    )
    m = rx.search(name)
    if not m:
        ts = _get_current_timestamp_str()
    else:
        sec = m.group("second") or "00"
        ts = f"{m.group('year')}{m.group('month')}{m.group('day')}T{m.group('hour')}{m.group('minute')}{sec}"
    return f"{short_hash_b32(name, length)}-{ts}"


def verify_name_matches_uid(name: str, uid: str, length=7) -> bool:
    """
    Retourne True si le nom correspond bien à l'UID donné.
    """
    try:
        expected_uid = make_compact_uid_b32(name, length)
    except ValueError:
        return False
    return uid == expected_uid
