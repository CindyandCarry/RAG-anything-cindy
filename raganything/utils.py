"""
Utility functions for RAGAnything

Contains helper functions for content separation, text insertion, and other utilities
"""

import base64
from typing import Dict, List, Any, Tuple
from pathlib import Path
from lightrag.utils import logger


SECTION_SPLIT_MARKER = "<<<SECTION>>>"


def separate_content(
    content_list: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Separate text content and multimodal content

    Args:
        content_list: Content list from MinerU parsing

    Returns:
        (text_content, multimodal_items): Pure text content and multimodal items list
    """
    text_parts = []
    multimodal_items = []
    have_text = False

    for item in content_list:
        content_type = item.get("type", "text")

        if content_type == "text":
            # Text content
            text = item.get("text", "")
            if text.strip():
                # Insert a section boundary before heading text (text_level is set)
                if item.get("text_level") is not None and have_text:
                    text_parts.append(SECTION_SPLIT_MARKER)
                text_parts.append(text)
                have_text = True
        else:
            # Multimodal content (image, table, equation, etc.)
            multimodal_items.append(item)

    # Merge all text content
    text_content = "\n\n".join(text_parts)

    logger.info("Content separation complete:")
    logger.info(f"  - Text content length: {len(text_content)} characters")
    logger.info(f"  - Multimodal items count: {len(multimodal_items)}")

    # Count multimodal types
    modal_types = {}
    for item in multimodal_items:
        modal_type = item.get("type", "unknown")
        modal_types[modal_type] = modal_types.get(modal_type, 0) + 1

    if modal_types:
        logger.info(f"  - Multimodal type distribution: {modal_types}")

    return text_content, multimodal_items


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string

    Args:
        image_path: Path to the image file

    Returns:
        str: Base64 encoded string, empty string if encoding fails
    """
    try:
        import io

        from PIL import Image

        with Image.open(image_path) as img:
            img = img.convert("RGB")
            width, height = img.size
            longest_side = max(width, height)
            if longest_side > 1568:
                scale = 1568 / longest_side
                img = img.resize(
                    (max(1, int(width * scale)), max(1, int(height * scale)))
                )
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            encoded_string = base64.b64encode(buf.getvalue()).decode("utf-8")
        return encoded_string
    except Exception as e:
        logger.error(f"Failed to encode image {image_path}: {e}")
        return ""


def validate_image_file(image_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate if a file is a valid image file

    Args:
        image_path: Path to the image file
        max_size_mb: Maximum file size in MB

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        path = Path(image_path)

        logger.debug(f"Validating image path: {image_path}")
        logger.debug(f"Resolved path object: {path}")
        logger.debug(f"Path exists check: {path.exists()}")

        # Check if file exists
        if not path.exists():
            logger.warning(f"Image file not found: {image_path}")
            return False

        # Check file extension
        image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
            ".tif",
        ]

        path_lower = str(path).lower()
        has_valid_extension = any(path_lower.endswith(ext) for ext in image_extensions)
        logger.debug(
            f"File extension check - path: {path_lower}, valid: {has_valid_extension}"
        )

        if not has_valid_extension:
            logger.warning(f"File does not appear to be an image: {image_path}")
            return False

        # Check file size
        file_size = path.stat().st_size
        max_size = max_size_mb * 1024 * 1024
        logger.debug(
            f"File size check - size: {file_size} bytes, max: {max_size} bytes"
        )

        if file_size > max_size:
            logger.warning(f"Image file too large ({file_size} bytes): {image_path}")
            return False

        logger.debug(f"Image validation successful: {image_path}")
        return True

    except Exception as e:
        logger.error(f"Error validating image file {image_path}: {e}")
        return False


def html_table_to_markdown(html: str) -> str:
    """Convert an HTML <table> into a markdown pipe table, expanding rowspan/colspan
    so the row-column correspondence is preserved. Returns the input unchanged if it
    is not an HTML table or parsing fails.
    """
    if not html or "<table" not in html.lower():
        return html

    try:
        from html.parser import HTMLParser

        rows = []

        class _TableParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self._row = None
                self._cell = None
                self._rs = 1
                self._cs = 1

            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == "tr":
                    self._row = []
                elif tag in ("td", "th") and self._row is not None:
                    self._cell = []
                    self._rs = max(1, int(d.get("rowspan", "1") or "1"))
                    self._cs = max(1, int(d.get("colspan", "1") or "1"))

            def handle_data(self, data):
                if self._cell is not None:
                    self._cell.append(data)

            def handle_endtag(self, tag):
                if tag in ("td", "th") and self._cell is not None:
                    text = " ".join("".join(self._cell).split())
                    self._row.append((text, self._rs, self._cs))
                    self._cell = None
                    self._rs = 1
                    self._cs = 1
                elif tag == "tr" and self._row is not None:
                    rows.append(self._row)
                    self._row = None

        parser = _TableParser()
        parser.feed(html)
    except Exception:
        return html

    if not rows:
        return html

    # Expand rowspan/colspan into a rectangular grid.
    grid = []
    occupied_until = []

    for r, row in enumerate(rows):
        while len(grid) < r + 1:
            grid.append([])
        col = 0
        for text, rs, cs in row:
            while col < len(occupied_until) and occupied_until[col] > r:
                col += 1
            while len(grid[r]) < col:
                grid[r].append("")
            for dc in range(cs):
                idx = col + dc
                while len(grid[r]) <= idx:
                    grid[r].append("")
                if dc == 0:
                    grid[r][idx] = text
                while len(occupied_until) <= idx:
                    occupied_until.append(0)
                occupied_until[idx] = r + rs
            col += cs

    width = max(len(row) for row in grid)
    for row in grid:
        while len(row) < width:
            row.append("")

    # Render markdown pipe table; single-cell title rows become plain lines.
    lines = []
    header_done = False
    for row in grid:
        nonempty = [cell for cell in row if cell]
        if len(nonempty) == 1:
            lines.append(nonempty[0])
            continue
        lines.append("| " + " | ".join(cell if cell else " " for cell in row) + " |")
        if not header_done:
            lines.append("| " + " | ".join("---" for _ in row) + " |")
            header_done = True

    return "\n".join(lines)


async def insert_text_content(
    lightrag,
    input: str | list[str],
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    ids: str | list[str] | None = None,
    file_paths: str | list[str] | None = None,
):
    """
    Insert pure text content into LightRAG

    Args:
        lightrag: LightRAG instance
        input: Single document string or list of document strings
        split_by_character: if split_by_character is not None, split the string by character, if chunk longer than
        chunk_token_size, it will be split again by token size.
        split_by_character_only: if split_by_character_only is True, split the string by character only, when
        split_by_character is None, this parameter is ignored.
        ids: single string of the document ID or list of unique document IDs, if not provided, MD5 hash IDs will be generated
        file_paths: single string of the file path or list of file paths, used for citation
    """
    logger.info("Starting text content insertion into LightRAG...")

    # Use LightRAG's insert method with all parameters
    await lightrag.ainsert(
        input=input,
        file_paths=file_paths,
        split_by_character=split_by_character,
        split_by_character_only=split_by_character_only,
        ids=ids,
    )

    logger.info("Text content insertion complete")


async def insert_text_content_with_multimodal_content(
    lightrag,
    input: str | list[str],
    multimodal_content: list[dict[str, any]] | None = None,
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    ids: str | list[str] | None = None,
    file_paths: str | list[str] | None = None,
    scheme_name: str | None = None,
):
    """
    Insert pure text content into LightRAG

    Args:
        lightrag: LightRAG instance
        input: Single document string or list of document strings
        multimodal_content: Multimodal content list (optional)
        split_by_character: if split_by_character is not None, split the string by character, if chunk longer than
        chunk_token_size, it will be split again by token size.
        split_by_character_only: if split_by_character_only is True, split the string by character only, when
        split_by_character is None, this parameter is ignored.
        ids: single string of the document ID or list of unique document IDs, if not provided, MD5 hash IDs will be generated
        file_paths: single string of the file path or list of file paths, used for citation
        scheme_name: scheme name (optional)
    """
    logger.info("Starting text content insertion into LightRAG...")

    # Use LightRAG's insert method with all parameters
    try:
        await lightrag.ainsert(
            input=input,
            multimodal_content=multimodal_content,
            file_paths=file_paths,
            split_by_character=split_by_character,
            split_by_character_only=split_by_character_only,
            ids=ids,
            scheme_name=scheme_name,
        )
    except Exception as e:
        logger.info(f"Error: {e}")
        logger.info(
            "If the error is caused by the ainsert function not having a multimodal content parameter, please update the raganything branch of lightrag"
        )

    logger.info("Text content insertion complete")


def get_processor_for_type(modal_processors: Dict[str, Any], content_type: str):
    """
    Get appropriate processor based on content type

    Args:
        modal_processors: Dictionary of available processors
        content_type: Content type

    Returns:
        Corresponding processor instance
    """
    # Direct mapping to corresponding processor
    if content_type == "image":
        return modal_processors.get("image")
    elif content_type == "table":
        return modal_processors.get("table")
    elif content_type == "equation":
        return modal_processors.get("equation")
    else:
        # For other types, use generic processor
        return modal_processors.get("generic")


def get_processor_supports(proc_type: str) -> List[str]:
    """Get processor supported features"""
    supports_map = {
        "image": [
            "Image content analysis",
            "Visual understanding",
            "Image description generation",
            "Image entity extraction",
        ],
        "table": [
            "Table structure analysis",
            "Data statistics",
            "Trend identification",
            "Table entity extraction",
        ],
        "equation": [
            "Mathematical formula parsing",
            "Variable identification",
            "Formula meaning explanation",
            "Formula entity extraction",
        ],
        "generic": [
            "General content analysis",
            "Structured processing",
            "Entity extraction",
        ],
    }
    return supports_map.get(proc_type, ["Basic processing"])
