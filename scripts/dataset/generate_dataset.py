import argparse

from tool_generator import generate_tool_info
# from toc_generator import generate_all_tocs
# from utils.config import load_generator_config


def generate_tools():
    config = load_generator_config('tool_info_generation')
    number_of_tools = config["NUMBER_OF_TOOLS"]

    print(f"Generating {number_of_tools} tools...")

    for i in range(number_of_tools):
        generate_tool_info(i)
        print(f"Generated tool_info.json for Tool {i}")


def main():
    parser = argparse.ArgumentParser(description="Dataset Generation Console App")

    parser.add_argument(
        "--tools",
        action="store_true",
        help="Generate tool_info.json files"
    )

    # parser.add_argument(
    #     "--tocs",
    #     action="store_true",
    #     help="Generate TOC files for all tools"
    # )
    #
    # parser.add_argument(
    #     "--all",
    #     action="store_true",
    #     help="Generate tools and TOCs"
    # )

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
