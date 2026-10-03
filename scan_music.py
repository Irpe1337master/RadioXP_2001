#!/usr/bin/env python3
"""Scan music/<genre>/ folders and write tracks.json.

Usage:  python3 scan_music.py
Needs:  pip install mutagen   (or ffprobe from ffmpeg as a fallback)

Folder name = genre. Tracks are sorted by filename, so the order is stable.
Title/artist come from tags, else from a "Artist - Title.mp3" filename.
"""
import json, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import quote

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

EXTS = {".mp3", ".ogg", ".m4a", ".wav", ".flac", ".opus"}
ROOT = Path(__file__).resolve().parent
MUSIC = ROOT / "music"


def pretty(text):
    return text.replace("_", " ").replace("-", " ").strip().title()


def read_file(path):
    """Return (duration_seconds, title, artist). Any can be None."""
    duration = title = artist = None
    if MutagenFile:
        try:
            audio = MutagenFile(path, easy=True)
            if audio is not None:
                if audio.info and audio.info.length:
                    duration = round(audio.info.length, 3)
                tags = audio.tags or {}
                title = (tags.get("title") or [None])[0]
                artist = (tags.get("artist") or [None])[0]
        except Exception as e:
            print(f"  ! could not read tags of {path.name}: {e}")
    if duration is None and shutil.which("ffprobe"):
        try:
            out = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", str(path)],
                capture_output=True, text=True, check=True).stdout.strip()
            duration = round(float(out), 3)
        except Exception:
            pass
    return duration, title, artist


def guess_from_name(stem):
    if " - " in stem:
        artist, title = stem.split(" - ", 1)
        return title.strip(), artist.strip()
    return pretty(stem), None


def main():
    if not MUSIC.is_dir():
        sys.exit(f"No music folder found at {MUSIC}. Create music/<genre>/ and add files.")
    if not MutagenFile and not shutil.which("ffprobe"):
        print("Note: install mutagen (pip install mutagen) for exact durations.\n"
              "Without it, durations are left out and the page measures them in the browser.\n")

    result = {}
    for folder in sorted((p for p in MUSIC.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        files = sorted((f for f in folder.iterdir() if f.suffix.lower() in EXTS),
                       key=lambda f: f.name.lower())
        if not files:
            continue
        tracks = []
        for f in files:
            duration, title, artist = read_file(f)
            g_title, g_artist = guess_from_name(f.stem)
            track = {
                "title": title or g_title,
                "artist": artist or g_artist or "",
                "file": quote(f.relative_to(ROOT).as_posix()),
            }
            if duration:
                track["duration"] = duration
            else:
                print(f"  ! no duration for {f.name}")
            tracks.append(track)
        result[pretty(folder.name)] = {"tracks": tracks}
        print(f"{pretty(folder.name)}: {len(tracks)} tracks")

    if not result:
        sys.exit("No audio files found in music/<genre>/ folders.")
    (ROOT / "tracks.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nWrote tracks.json. Commit it together with your music.")
    print("Reminder: adding or removing tracks changes the schedule, so stations jump for everyone.")


if __name__ == "__main__":
    main()
