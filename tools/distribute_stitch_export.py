from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory


def safe_slug(name: str) -> str:
    chars: list[str] = []
    for ch in name.strip().lower():
        if ch.isalnum():
            chars.append(ch)
        elif ch in {" ", "-", "_"}:
            chars.append("_")
    slug = "".join(chars)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "unnamed"


def ensure_dirs(repo_root: Path) -> dict[str, Path]:
    design_dir = repo_root / "frontend" / "design"
    stitch_dir = design_dir / "stitch_exports"
    screenshots_dir = stitch_dir / "screenshots"
    html_dir = stitch_dir / "html_css_export"

    screenshots_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)

    return {
        "design_dir": design_dir,
        "stitch_dir": stitch_dir,
        "screenshots_dir": screenshots_dir,
        "html_dir": html_dir,
    }


def copy_design_md(source_root: Path, target_stitch_dir: Path) -> Path | None:
    design_files = list(source_root.rglob("DESIGN.md"))
    if not design_files:
        return None

    design_src = design_files[0]
    design_dst = target_stitch_dir / "DESIGN.md"
    shutil.copy2(design_src, design_dst)
    return design_dst


def collect_screen_dirs(source_root: Path) -> list[Path]:
    result: list[Path] = []

    for path in source_root.rglob("*"):
        if not path.is_dir():
            continue

        has_screen = (path / "screen.png").exists()
        has_html = (path / "code.html").exists()

        if has_screen or has_html:
            result.append(path)

    return sorted(set(result))


def distribute_assets(
    screen_dirs: list[Path],
    screenshots_dir: Path,
    html_dir: Path,
) -> list[dict[str, str]]:
    inventory: list[dict[str, str]] = []

    for screen_dir in screen_dirs:
        screen_name = safe_slug(screen_dir.name)
        screen_png = screen_dir / "screen.png"
        code_html = screen_dir / "code.html"

        screenshot_target = ""
        html_target = ""

        if screen_png.exists():
            dst = screenshots_dir / f"{screen_name}.png"
            shutil.copy2(screen_png, dst)
            screenshot_target = str(dst)

        if code_html.exists():
            dst = html_dir / f"{screen_name}.html"
            shutil.copy2(code_html, dst)
            html_target = str(dst)

        inventory.append(
            {
                "screen_name": screen_name,
                "source_dir": str(screen_dir),
                "screenshot": screenshot_target,
                "html": html_target,
            }
        )

    return inventory


def write_inventory(stitch_dir: Path, inventory: list[dict[str, str]]) -> Path:
    out_path = stitch_dir / "stitch_inventory.md"

    lines = [
        "# Stitch Export Inventory",
        "",
        "| Screen | Screenshot | HTML | Source Directory |",
        "|---|---|---|---|",
    ]

    for item in inventory:
        screenshot_name = Path(item["screenshot"]).name if item["screenshot"] else "-"
        html_name = Path(item["html"]).name if item["html"] else "-"
        lines.append(
            f"| {item['screen_name']} | {screenshot_name} | {html_name} | `{item['source_dir']}` |"
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def process_source_dir(source_dir: Path, repo_root: Path) -> None:
    dirs = ensure_dirs(repo_root)

    design_md = copy_design_md(source_dir, dirs["stitch_dir"])
    screen_dirs = collect_screen_dirs(source_dir)
    inventory = distribute_assets(
        screen_dirs=screen_dirs,
        screenshots_dir=dirs["screenshots_dir"],
        html_dir=dirs["html_dir"],
    )
    inventory_path = write_inventory(dirs["stitch_dir"], inventory)

    print("Stitch export distributed successfully.")
    print(f"Target directory: {dirs['stitch_dir']}")
    print(f"Detected screen folders: {len(screen_dirs)}")
    print(f"Inventory file: {inventory_path}")
    if design_md:
        print(f"Copied DESIGN.md: {design_md}")
    else:
        print("No DESIGN.md found in source export.")


def process_zip(zip_path: Path, repo_root: Path) -> None:
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)
        process_source_dir(tmp_path, repo_root)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Distribute Google Stitch export files into the frontend design folders."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Path to repository root. Default: current directory.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--zip",
        type=Path,
        help="Path to a Stitch export ZIP file.",
    )
    group.add_argument(
        "--source-dir",
        type=Path,
        help="Path to an already extracted Stitch export directory.",
    )

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    if args.zip:
        zip_path = args.zip.resolve()
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP not found: {zip_path}")
        process_zip(zip_path, repo_root)

    if args.source_dir:
        source_dir = args.source_dir.resolve()
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        process_source_dir(source_dir, repo_root)


if __name__ == "__main__":
    main()