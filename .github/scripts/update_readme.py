#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import os
import random
import subprocess


START = "<!-- QUOTE:START -->"
END = "<!-- QUOTE:END -->"


def get_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def repo_checksum() -> str:
    """
    Compute a stable-ish checksum from tracked files in the current git repo.
    Since README changes daily, this will also change daily. Good. Weird.
    """
    data = subprocess.check_output(
        "git ls-files -z | xargs -0 sha256sum",
        shell=True,
    )
    return hashlib.sha256(data).hexdigest()[:8].upper()


def moon_phase(now: datetime) -> str:
    known_new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    synodic_month = 29.53058867

    days = (now - known_new_moon).total_seconds() / 86400
    age = days % synodic_month

    if age < 1.84566:
        return "🌑 New Moon"
    if age < 5.53699:
        return "🌒 Waxing Crescent"
    if age < 9.22831:
        return "🌓 First Quarter"
    if age < 12.91963:
        return "🌔 Waxing Gibbous"
    if age < 16.61096:
        return "🌕 Full Moon"
    if age < 20.30228:
        return "🌖 Waning Gibbous"
    if age < 23.99361:
        return "🌗 Last Quarter"
    if age < 27.68493:
        return "🌘 Waning Crescent"
    return "🌑 New Moon"


def fake_telemetry(checksum: str) -> str:
    station_id = f"K-{checksum[:4]}"

    channel = random.choice([
        "LONG_FAST",
        "VOID_LAMBDA",
        "PKI_ORACLE",
        "BBS-7",
        "NUMBERS_STATION",
        "TELLY_NET",
        "LIMINAL_SPACE",
    ])

    signal = random.randint(70, 99)

    entropy = random.choice([
        "nominal",
        "elevated",
        "spicy",
        "haunted",
        "within acceptable weirdness",
        "ritually bounded",
    ])

    trust_anchors = random.choice([
        "valid",
        "rotated",
        "suspiciously quiet",
        "blessed",
        "held together by ritual",
        "cross-signed by a sketchy CA",
    ])

    cat_interference = random.choice([
        "low",
        "moderate",
        "elevated",
        "critical",
        "Telly-class event",
        "router button at risk",
    ])

    return f"""🛰️ Station ID: `{station_id}`  
📻 Channel: `{channel}`  
🔐 Profile checksum: `{checksum}`  

**Telemetry**
- Signal strength: `{signal}%`
- Entropy: `{entropy}`
- Trust anchors: `{trust_anchors}`
- Cat interference: `{cat_interference}`"""


def render_quote_block(quote: str, updated: str, checksum: str) -> str:
    now = datetime.now(timezone.utc)
    moon = moon_phase(now)
    telemetry = fake_telemetry(checksum)

    return f"""{START}
> {quote}

📡 Transmission received: {updated}  
🌙 Lunar condition: {moon}  
{telemetry}
{END}"""


def main() -> None:
    quote = get_env("QUOTE")
    updated = get_env("UPDATED")

    readme = Path("README.md")
    if not readme.exists():
        raise RuntimeError("README.md not found. Run this script from the profile repo root.")

    text = readme.read_text(encoding="utf-8")

    if START not in text:
        raise RuntimeError(f"Could not find start marker: {START}")
    if END not in text:
        raise RuntimeError(f"Could not find end marker: {END}")

    checksum = repo_checksum()

    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)

    new_block = render_quote_block(quote, updated, checksum)
    readme.write_text(before + new_block + after, encoding="utf-8")

    print(f"Updated README with quote: {quote}")
    print(f"Profile checksum: {checksum}")


if __name__ == "__main__":
    main()
