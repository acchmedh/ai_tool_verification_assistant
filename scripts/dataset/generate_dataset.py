import argparse
import sys
from pathlib import Path

# Project root on path first so "scripts" and "src" resolve when run as script
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.utils.section_generator import generate_all_sections
from scripts.utils.toc_generator import generate_all_tocs
from scripts.utils.tool_generator import generate_tools


def main():
    parser = argparse.ArgumentParser(description="Dataset Generation Console App")

    parser.add_argument("--all", action="store_true", help="Generate all files for all tools")

    parser.add_argument(
        "--tools", action="store_true", help="Generate folder name and {tool_name}_info.json files"
    )

    parser.add_argument("--tocs", action="store_true", help="Generate TOC files for all tools")

    parser.add_argument(
        "--sections", action="store_true", help="Generate HTML files for all sections in TOCs"
    )

    args = parser.parse_args()

    if args.all:
        print("Generating complete dataset...")
        generate_tools()
        generate_all_tocs()
        generate_all_sections()
    else:
        if args.tools:
            generate_tools()
        if args.tocs:
            generate_all_tocs()
        if args.sections:
            generate_all_sections()

    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
