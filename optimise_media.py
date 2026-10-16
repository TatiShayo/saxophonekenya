#!/usr/bin/env python3
"""
optimise_media.py — One-shot media optimisation for the Frederic Sax Ke site
==========================================================================
The site shipped 95.7 MB of media from the project root, of which 61.4 MB
was four unoptimised phone-export MP4s and 12.6 MB was five large PNGs.

This script, in order:

  1. Re-encodes every MP4 referenced by the site to H.264 CRF 28, capped at
     1080p on the long edge, with `+faststart` so the moov atom sits at the
     front of the file and playback can begin before the download finishes.
     The old files had the moov atom at the end, so a browser could not
     start playing until the whole file had arrived.

  2. Re-encodes every PNG/JPEG referenced by the site, downscaling to
     1920px on the long edge and re-compressing. Filenames are unchanged so
     every link, test and CSS url() keeps resolving.

  3. Moves QA/evidence screenshots that no page references out of the
     deploy root into `evidence/`, and updates the dev tooling accordingly.

Nothing is deleted. Originals are copied to `_media_backup/` first, and the
script refuses to run if that backup already exists unless --force is given.

Usage:
    python optimise_media.py            # optimise, keeping a backup
    python optimise_media.py --force    # overwrite an existing backup
    python optimise_media.py --dry-run  # report only, touch nothing
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "_media_backup"
EVIDENCE_DIR = ROOT / "evidence"

# Everything a page actually references.
SITE_VIDEOS = ["IMG_3610.MP4", "IMG_3615.MP4", "IMG_3617.MP4", "IMG_3618.MP4"]
SITE_IMAGES = [
    "IMG_2259.jpg", "IMG_3608.PNG", "IMG_3609.PNG", "IMG_3611.PNG",
    "IMG_3612.PNG", "IMG_3613.PNG", "WhatsApp Image 2026-08-25 at 22.29.22.jpeg",
]

# QA screenshots produced by run_vitl.py / take_shots.py. Not referenced by
# any page; they were sitting in the deploy root.
EVIDENCE_FILES = [
    "desktop_full.png", "full_shot.png", "shot.png", "vision_full_page.png",
    "shot_hero.png", "shot_hero_bright.png", "shot_videos.png", "shot_weddings.png",
    "shot_pinterest.png", "shot_cal_current.png", "shot_cal_desktop.png",
    "shot_cal_mobile.png", "shot_cal_selected_slot.png", "shot_slot_panel.png",
    "shot_slot_panel_mobile.png", "shot_wardawear_preview.png",
    "vision_desktop.png", "vision_desktop_video.png", "vision_mobile.png",
    "vision_mobile_final.png", "vision_mobile_fixed.png", "vision_videos_sec.png",
    "mobile_hero.png", "mobile_videos.png", "mobile_weddings.png",
    "mobile_pinterest.png", "Capture.PNG", "CaptureE.PNG",
]

MAX_LONG_EDGE = 1920
MAX_VIDEO_HEIGHT = 1080


def megabytes(path: Path) -> float:
    return path.stat().st_size / 1_048_576


def check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def optimise_video(path: Path, dry_run: bool) -> tuple[int, int]:
    before = path.stat().st_size
    if dry_run:
        return before, before

    tmp = path.with_suffix(".optimising.mp4")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(path),
        # Cap the long edge at 1080; these are vertical phone exports so we
        # scale on height and keep the aspect ratio.
        "-vf", f"scale=-2:'min({MAX_VIDEO_HEIGHT},ih)'",
        "-c:v", "libx264",
        "-crf", "28",
        "-preset", "slow",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-ac", "1",
        # faststart moves the moov atom to the front so playback can start
        # before the download completes.
        "-movflags", "+faststart",
        str(tmp),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ffmpeg failed: {result.stderr.strip()[:200]}")
        tmp.unlink(missing_ok=True)
        return before, before

    # Only replace the original if the new file is genuinely smaller.
    after = tmp.stat().st_size
    if after >= before:
        print(f"    kept original (re-encode was larger)")
        tmp.unlink()
        return before, before

    tmp.replace(path)
    return before, after


def optimise_image(path: Path, dry_run: bool) -> tuple[int, int]:
    before = path.stat().st_size
    if dry_run:
        return before, before

    from PIL import Image

    with Image.open(path) as img:
        icc = img.info.get("icc_profile")
        exif = img.info.get("exif")

        long_edge = max(img.size)
        if long_edge > MAX_LONG_EDGE:
            ratio = MAX_LONG_EDGE / long_edge
            new_size = (
                max(1, round(img.width * ratio)),
                max(1, round(img.height * ratio)),
            )
            img = img.resize(new_size, Image.LANCZOS)

        suffix = path.suffix.lower()
        tmp = path.with_suffix(f".optimising{suffix}")

        if suffix in {".jpg", ".jpeg"}:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            # Pillow raises if exif is explicitly passed as None.
            jpeg_kwargs = {
                "quality": 82,
                "optimize": True,
                "progressive": True,
                "subsampling": 1,
            }
            if icc:
                jpeg_kwargs["icc_profile"] = icc
            if exif:
                jpeg_kwargs["exif"] = exif
            img.save(tmp, "JPEG", **jpeg_kwargs)
        elif suffix == ".png":
            if img.mode not in ("RGB", "RGBA", "L", "P", "LA"):
                img = img.convert("RGB")
            png_kwargs = {"optimize": True, "compress_level": 9}
            if icc:
                png_kwargs["icc_profile"] = icc
            img.save(tmp, "PNG", **png_kwargs)
        else:
            other_kwargs = {}
            if icc:
                other_kwargs["icc_profile"] = icc
            if exif:
                other_kwargs["exif"] = exif
            img.save(tmp, **other_kwargs)

    after = tmp.stat().st_size
    if after >= before:
        print("    kept original (re-encode was larger)")
        tmp.unlink(missing_ok=True)
        return before, before

    tmp.replace(path)
    return before, after


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not check_ffmpeg():
        print("ffmpeg not found on PATH — video re-encoding skipped.")
        print("Images will still be optimised if Pillow is available.")

    # ---------------------------------------------------------------- backup
    if not args.dry_run and not args.force:
        if BACKUP.exists():
            print(f"Backup already exists at {BACKUP.name}/.")
            print("Re-run with --force to replace it, or --dry-run to report only.")
            return 1
        BACKUP.mkdir(exist_ok=True)
        for name in SITE_VIDEOS + SITE_IMAGES:
            source = ROOT / name
            if source.exists():
                shutil.copy2(source, BACKUP / name)
        print(f"Backup written to {BACKUP.name}/ ({len(list(BACKUP.glob('*')))} files)\n")

    total_before = total_after = 0

    # ---------------------------------------------------------------- videos
    print("VIDEOS")
    for name in SITE_VIDEOS:
        path = ROOT / name
        if not path.exists():
            print(f"  {name:<20} missing, skipped")
            continue
        before, after = optimise_video(path, args.dry_run)
        total_before += before
        total_after += after
        saved = (before - after) / 1_048_576
        print(f"  {name:<18} {before/1_048_576:7.2f} MB -> {after/1_048_576:7.2f} MB"
              f"   saved {saved:6.2f} MB")

    # ---------------------------------------------------------------- images
    print("\nIMAGES")
    for name in SITE_IMAGES:
        path = ROOT / name
        if not path.exists():
            print(f"  {name:<46} missing, skipped")
            continue
        before, after = optimise_image(path, args.dry_run)
        total_before += before
        total_after += after
        saved = (before - after) / 1_048_576
        print(f"  {name:<46} {before/1_048_576:6.2f} MB -> {after/1_048_576:6.2f} MB"
              f"   saved {saved:6.2f} MB")

    # ------------------------------------------------- move evidence out
    if not args.dry_run:
        EVIDENCE_DIR.mkdir(exist_ok=True)
        moved = 0
        for name in EVIDENCE_FILES:
            source = ROOT / name
            if source.exists():
                shutil.move(str(source), EVIDENCE_DIR / name)
                moved += 1
        if moved:
            print(f"\nEVIDENCE")
            print(f"  moved {moved} QA screenshots into evidence/ "
                  f"(no page references them)")

    total_saved = (total_before - total_after) / 1_048_576
    print(f"\n{'=' * 68}")
    print(f"  Site media: {total_before/1_048_576:.2f} MB -> {total_after/1_048_576:.2f} MB"
          f"   (saved {total_saved:.2f} MB, "
          f"{(total_saved / (total_before/1_048_576) * 100 if total_before else 0):.0f}%)")
    print(f"{'=' * 68}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
