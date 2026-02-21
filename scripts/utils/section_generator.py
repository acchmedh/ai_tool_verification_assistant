import sys
import json
from pathlib import Path
from html.parser import HTMLParser
from typing import Any

# Add project root to a path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.utils.openai_client import get_openai_client
from scripts.utils.generation_config import load_generator_config, DATA_DIR

client = get_openai_client()

config = load_generator_config('section_generation', 'section_model')
SECTION_SYSTEM = config['system']
SECTION_USER_TEMPLATE = config['user_template']
MODEL_NAME = config['model_name']
TEMPERATURE = config['temperature']


def call_section_model(
        tool_info: dict,
        document_type: str,
        previous_html: list[str],
        section_title: str,
        heading_tag: str = "h2"
) -> str:
    """Calls the LLM API to generate HTML for a single section.

    Args:
        tool_info: Dictionary containing tool metadata
        document_type: Type of document being generated
        previous_html: List of previously generated HTML sections (for context)
        section_title: Title of the section to generate
        heading_tag: HTML heading tag to use (h2, h3, h4, etc.)

    Returns:
        str: Raw HTML content for the section
    """
    previous_html_str = "\n\n".join(previous_html) if previous_html else "(No previous sections)"

    user_prompt = SECTION_USER_TEMPLATE.format(
        tool_info_json=json.dumps(tool_info, ensure_ascii=False, indent=2),
        document_type=document_type,
        previous_html=previous_html_str,
        section_title=section_title,
        heading_tag=heading_tag
    )

    print(f"  Generating section: {section_title}...", end=" ", flush=True)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SECTION_SYSTEM},
                {"role": "user", "content": user_prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=1500,
            timeout=120.0
        )
        print("✓")
        return response.choices[0].message.content
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def generate_section_html(
        tool_info: dict,
        document_type: str,
        previous_html: list[str],
        section_title: str,
        depth: int = 0
) -> str:
    """Generates HTML for a single section using LLM.

    Args:
        tool_info: Dictionary containing tool metadata
        document_type: Type of document being generated
        previous_html: List of previously generated HTML sections
        section_title: Title of the section to generate
        depth: Nesting depth (0 = top-level, 1 = subsection, etc.)

    Returns:
        str: HTML content for the section
    """
    heading_tag = f"h{min(2 + depth, 6)}"

    return call_section_model(
        tool_info=tool_info,
        document_type=document_type,
        previous_html=previous_html,
        section_title=section_title,
        heading_tag=heading_tag
    )


def traverse_toc_and_generate(
        toc: dict[str, Any],
        tool_info: dict,
        document_type: str,
        accumulated_html: list[str],
        depth: int = 0
) -> None:
    """Recursively traverses TOC structure and generates HTML for all sections.
    
    This function modifies the accumulated_html list in place, adding generated sections.

    Args:
        toc: TOC section dictionary with 'title' and optional 'subsections'
        tool_info: Dictionary containing tool metadata
        document_type: Type of document being generated
        accumulated_html: List to accumulate generated HTML sections (modified in place)
        depth: Current nesting depth
    """
    section_html = generate_section_html(
        tool_info=tool_info,
        document_type=document_type,
        previous_html=accumulated_html.copy(),
        section_title=toc['title'],
        depth=depth
    )

    accumulated_html.append(section_html)

    if 'subsections' in toc and toc['subsections']:
        for subsection in toc['subsections']:
            traverse_toc_and_generate(
                toc=subsection,
                tool_info=tool_info,
                document_type=document_type,
                accumulated_html=accumulated_html,
                depth=depth + 1
            )


def assemble_html_document(title: str, sections_html: list[str]) -> str:
    """Assembles individual section HTML into a complete valid HTML document.

    Args:
        title: Document title
        sections_html: List of HTML strings for each section

    Returns:
        str: Complete HTML document
    """
    sections_content = "\n\n".join(sections_html)

    html_doc = f"""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{title}</title>
                </head>
                <body>
                    <h1>{title}</h1>
                    {sections_content}
                </body>
                </html>"""

    return html_doc


def validate_html(html_content: str) -> bool:
    """Validates that HTML content is well-formed.

    Args:
        html_content: HTML content to validate

    Returns:
        bool: True if HTML appears valid, False otherwise
    """
    try:
        parser = HTMLParser()
        parser.feed(html_content)
        parser.close()
        return True
    except Exception:
        return False


def generate_document_html(tool_folder: Path, document_type: str) -> None:
    """Generates HTML document for a specific tool and document type.

    Args:
        tool_folder: Path to the tool's directory
        document_type: Type of document to generate
    """
    tool_info_path = tool_folder / "tool_info.json"
    if not tool_info_path.exists():
        print(f"Skipping {tool_folder.name} / {document_type} (no tool_info.json)")
        return

    tool_info = json.loads(tool_info_path.read_text(encoding="utf-8"))

    toc_path = tool_folder / f"toc_{document_type}.json"
    if not toc_path.exists():
        print(f"Skipping {tool_folder.name} / {document_type} (no TOC file)")
        return

    toc = json.loads(toc_path.read_text(encoding="utf-8"))

    print(f"Generating HTML for {tool_folder.name} / {document_type} ...")

    sections_html = []
    for section in toc['sections']:
        traverse_toc_and_generate(
            toc=section,
            tool_info=tool_info['description'],
            document_type=document_type,
            accumulated_html=sections_html,
            depth=0
        )

    html_document = assemble_html_document(toc['title'], sections_html)

    if not validate_html(html_document):
        print(f"Warning: Generated HTML for {tool_folder.name} / {document_type} may be malformed")

    html_path = tool_folder / f"{document_type}.html"
    html_path.write_text(html_document, encoding="utf-8")
    print(f"Saved HTML: {html_path}")


def generate_all_sections() -> None:
    """Main function that iterates through all tool folders and generates HTML files for each document type.
    
    Processes all tool directories in the data folder, reads their tool_info.json files and TOC files,
    and generates HTML documents section by section. The generated HTML files are validated before
    being saved.
    
    Generated HTML files are saved as `{document_type}.html` in each tool's directory.
    """
    for tool_folder in sorted(DATA_DIR.iterdir()):
        if not tool_folder.is_dir():
            continue

        tool_info_path = tool_folder / "tool_info.json"
        if not tool_info_path.exists():
            print(f"Skipping {tool_folder.name} (no tool_info.json)")
            continue

        tool_info = json.loads(tool_info_path.read_text(encoding="utf-8"))
        docs = tool_info.get("document_types") or []
        if not docs:
            print(f"No document_types for {tool_folder.name}, skipping")
            continue

        for doc in docs:
            try:
                generate_document_html(tool_folder, doc)
            except Exception as e:
                print(f"Failed to generate HTML for {tool_folder.name} / {doc}: {e}")


if __name__ == '__main__':
    generate_all_sections()
