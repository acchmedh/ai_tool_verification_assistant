from typing import Any


def flatten_toc_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Flattens a nested TOC structure into a linear list of sections
    preserving the original order.

    Each returned item contains at least:
    - id
    - title
    """

    flat_sections: list[dict[str, Any]] = []

    def traverse(nodes: list[dict[str, Any]]) -> None:
        for node in nodes:
            flat_sections.append({
                "id": node.get("id"),
                "title": node.get("title")
            })

            children = node.get("children", [])
            if children:
                traverse(children)

    traverse(sections)
    return flat_sections
