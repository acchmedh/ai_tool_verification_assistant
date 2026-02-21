import argparse
import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.utils.tool_generator import generate_tools

def main():
    parser = argparse.ArgumentParser(description="Dataset Generation Console App")

    parser.add_argument(
        "--tools",
        action="store_true",
        help="Generate folder name and {tool_name}_info.json files"
    )

    args = parser.parse_args()

    if args.tools:
        generate_tools()

    # if args.all:
    #     generate_tools()
    #     generate_all_tocs()
    # else:
    #     if args.tools:
    #         generate_tools()
    #     if args.tocs:
    #         generate_all_tocs()

    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
