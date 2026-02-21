import json
import random
import sys
import time
from pathlib import Path
from typing import Any

from lxml import etree

from scripts.utils.generation_config import DATA_DIR, load_generator_config
from src.utils.openai_client import get_openai_client

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


client = get_openai_client()

config = load_generator_config("section_generation", "section_model")
SECTION_SYSTEM = config["system"]
SECTION_USER_TEMPLATE = config["user_template"]
MODEL_NAME = config["model_name"]
TEMPERATURE = config["temperature"]

# Number of data quality issues to place per document (2-3 total, one per chosen section).
ISSUES_MIN_PER_DOCUMENT = 2
ISSUES_MAX_PER_DOCUMENT = 3

# Rate limit: retry 429 after this many seconds; delay between section calls to avoid bursting.
RATE_LIMIT_WAIT_SECONDS = 90
DELAY_BETWEEN_SECTIONS_SECONDS = 2
MAX_RETRIES_ON_RATE_LIMIT = 5


def _flatten_toc_depth_first(sections: list[dict], depth: int = 0) -> list[tuple[dict, int]]:
    """Returns sections in depth-first order as (section_dict, depth) for indexing."""
    result: list[tuple[dict, int]] = []
    for s in sections:
        result.append((s, depth))
        if s.get("subsections"):
            result.extend(_flatten_toc_depth_first(s["subsections"], depth + 1))
    return result


def _pick_issue_section_indices(total_sections: int) -> set[int]:
    """Picks 2-3 section indices (0-based) that should each include one data quality issue."""
    if total_sections <= 0:
        return set()
    target = min(
        random.randint(ISSUES_MIN_PER_DOCUMENT, ISSUES_MAX_PER_DOCUMENT),
        total_sections,
    )
    return set(random.sample(range(total_sections), target))


def call_section_model(
    tool_info: dict,
    document_type: str,
    previous_html: list[str],
    section_title: str,
    heading_tag: str = "h2",
    include_issue_in_this_section: bool = False,
) -> str | None:
    """Calls the LLM API to generate HTML for a single section.

    Args:
        tool_info: Dictionary containing tool metadata
        document_type: Type of document being generated
        previous_html: List of previously generated HTML sections (for context)
        section_title: Title of the section to generate
        heading_tag: HTML heading tag to use (h2, h3, h4, etc.)
        include_issue_in_this_section: If True, this section must include exactly one data quality issue.

    Returns:
        str: Raw HTML content for the section
    """
    previous_html_str = "\n\n".join(previous_html) if previous_html else "(No previous sections)"
    data_quality_instruction = (
        "Include exactly one data quality issue in this section (one of: contradiction, ambiguity, minor typo, or inconsistent terminology). Make it subtle."
        if include_issue_in_this_section
        else "Do not include any data quality issues in this section; the document's 2-3 issues are placed in other sections."
    )

    user_prompt = SECTION_USER_TEMPLATE.format(
        tool_info_json=json.dumps(tool_info, ensure_ascii=False, indent=2),
        document_type=document_type,
        previous_html=previous_html_str,
        section_title=section_title,
        heading_tag=heading_tag,
        data_quality_instruction=data_quality_instruction,
    )

    print(f"  Generating section: {section_title}...", end=" ", flush=True)
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES_ON_RATE_LIMIT):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SECTION_SYSTEM},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=1500,
                timeout=120.0,
            )
            print("✓")
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_rate_limit = "429" in str(e) or "rate limit" in err_str
            if is_rate_limit and attempt < MAX_RETRIES_ON_RATE_LIMIT - 1:
                print(
                    f"\n  Rate limited, waiting {RATE_LIMIT_WAIT_SECONDS}s before retry ({attempt + 1}/{MAX_RETRIES_ON_RATE_LIMIT})...",
                    flush=True,
                )
                time.sleep(RATE_LIMIT_WAIT_SECONDS)
            else:
                print(f"✗ Error: {e}")
                raise
    if last_error is not None:
        raise last_error


def generate_section_html(
    tool_info: dict,
    document_type: str,
    previous_html: list[str],
    section_title: str,
    depth: int = 0,
    include_issue_in_this_section: bool = False,
) -> str:
    """Generates HTML for a single section using LLM.

    Args:
        tool_info: Dictionary containing tool metadata
        document_type: Type of document being generated
        previous_html: List of previously generated HTML sections
        section_title: Title of the section to generate
        depth: Nesting depth (0 = top-level, 1 = subsection, etc.)
        include_issue_in_this_section: If True, this section must include exactly one data quality issue.

    Returns:
        str: HTML content for the section
    """
    heading_tag = f"h{min(2 + depth, 6)}"

    return call_section_model(
        tool_info=tool_info,
        document_type=document_type,
        previous_html=previous_html,
        section_title=section_title,
        heading_tag=heading_tag,
        include_issue_in_this_section=include_issue_in_this_section,
    )


def traverse_toc_and_generate(
    toc: dict[str, Any],
    tool_info: dict,
    document_type: str,
    accumulated_html: list[str],
    section_index: list[int],
    issue_section_indices: set[int],
    depth: int = 0,
) -> None:
    """Recursively traverses TOC structure and generates HTML for all sections.
    Modifies accumulated_html in place. section_index is [current 0-based index];
    issue_section_indices are the indices that must each include one data quality issue (2-3 per document).
    """
    idx = section_index[0]
    include_issue = idx in issue_section_indices
    section_index[0] += 1

    section_html = generate_section_html(
        tool_info=tool_info,
        document_type=document_type,
        previous_html=accumulated_html.copy(),
        section_title=toc["title"],
        depth=depth,
        include_issue_in_this_section=include_issue,
    )

    accumulated_html.append(section_html)
    time.sleep(DELAY_BETWEEN_SECTIONS_SECONDS)

    if "subsections" in toc and toc["subsections"]:
        for subsection in toc["subsections"]:
            traverse_toc_and_generate(
                toc=subsection,
                tool_info=tool_info,
                document_type=document_type,
                accumulated_html=accumulated_html,
                section_index=section_index,
                issue_section_indices=issue_section_indices,
                depth=depth + 1,
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
    """Validates that HTML is well-formed, including correct tag nesting.

    Uses lxml's strict HTML parser (recover=False) so malformed nesting
    (e.g. <div><span></div></span>) or unclosed tags raise and are reported.
    The stdlib HTMLParser is fault-tolerant by design and does not catch these.
    """
    try:
        parser = etree.HTMLParser(recover=False)
        etree.fromstring(html_content.encode("utf-8"), parser=parser)
        return True
    except (etree.LxmlError, etree.XMLSyntaxError):
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

    flattened = _flatten_toc_depth_first(toc["sections"])
    total_sections = len(flattened)
    issue_section_indices = _pick_issue_section_indices(total_sections)

    print(
        f"Generating HTML for {tool_folder.name} / {document_type} ... ({total_sections} sections, {len(issue_section_indices)} with data quality issues)"
    )

    sections_html = []
    section_index = [0]
    for section in toc["sections"]:
        traverse_toc_and_generate(
            toc=section,
            tool_info=tool_info["description"],
            document_type=document_type,
            accumulated_html=sections_html,
            section_index=section_index,
            issue_section_indices=issue_section_indices,
            depth=0,
        )

    html_document = assemble_html_document(toc["title"], sections_html)

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


if __name__ == "__main__":
    generate_all_sections()
