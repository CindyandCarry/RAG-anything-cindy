"""
Prompt templates for multimodal content processing

Contains all prompt templates used in modal processors for analyzing
different types of content (images, tables, equations, etc.)
"""

from __future__ import annotations
from typing import Any


PROMPTS: dict[str, Any] = {}

# System prompts for different analysis types
PROMPTS["IMAGE_ANALYSIS_SYSTEM"] = (
    "You are an expert image analyst. Provide detailed, accurate descriptions."
)
PROMPTS["IMAGE_ANALYSIS_FALLBACK_SYSTEM"] = (
    "You are an expert image analyst. Provide detailed analysis based on available information."
)
PROMPTS["TABLE_ANALYSIS_SYSTEM"] = (
    "You are an expert data analyst. Provide detailed table analysis with specific insights."
)
PROMPTS["EQUATION_ANALYSIS_SYSTEM"] = (
    "You are an expert mathematician. Provide detailed mathematical analysis."
)
PROMPTS["GENERIC_ANALYSIS_SYSTEM"] = (
    "You are an expert content analyst specializing in {content_type} content."
)

# Image analysis prompt template
PROMPTS[
    "vision_prompt"
] = """You are extracting facts from an image for a retrieval system. The description you write is the ONLY text used to find this image later, so it must contain every fact a question about this image might ask for.

Return a JSON object with EXACTLY this structure:

{{
    "detailed_description": "A fact-dense description, written as a flat list of facts (NOT a narrative). First classify the image into ONE of: chart / table / diagram / photo / text. Then write ONLY the facts relevant to that type:
    - chart   -> the exact chart type, every axis label and unit, every data value, legend categories, the time period, and the direction + magnitude of each trend.
    - table   -> every row/column header and the key cell values, verbatim.
    - diagram -> every node and label, and the direction of each arrow/relationship.
    - photo   -> every object/person and any visible text, using proper names.
    - text    -> transcribe the visible text verbatim, in reading order.
    For EVERY type: transcribe verbatim any text, numbers, or labels printed in the image. Never mention colors, lighting, layout, or style.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "image",
        "summary": "One or two sentences (max 60 words) stating what this image shows and its key finding, using the same specific numbers and names."
    }}
}}

Image details:
- Image Path: {image_path}
- Captions: {captions}
- Footnotes: {footnotes}

Return ONLY the JSON object. Write all fields in English."""

# Image analysis prompt with context support
PROMPTS[
    "vision_prompt_with_context"
] = """You are extracting facts from an image for a retrieval system. The description you write is the ONLY text used to find this image later, so it must contain every fact a question about this image might ask for. Use the surrounding context to resolve what entities the image refers to (e.g., what "the company" or "the segment" means).

Return a JSON object with EXACTLY this structure:

{{
    "detailed_description": "A fact-dense description, written as a flat list of facts (NOT a narrative). First classify the image into ONE of: chart / table / diagram / photo / text. Then write ONLY the facts relevant to that type:
    - chart   -> the exact chart type, every axis label and unit, every data value, legend categories, the time period, and the direction + magnitude of each trend.
    - table   -> every row/column header and the key cell values, verbatim.
    - diagram -> every node and label, and the direction of each arrow/relationship.
    - photo   -> every object/person and any visible text, using proper names.
    - text    -> transcribe the visible text verbatim, in reading order.
    For EVERY type: transcribe verbatim any text, numbers, or labels printed in the image. Never mention colors, lighting, layout, or style.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "image",
        "summary": "One or two sentences (max 60 words) stating what this image shows and its key finding, using the same specific numbers and names."
    }}
}}

Context from surrounding content:
{context}

Image details:
- Image Path: {image_path}
- Captions: {captions}
- Footnotes: {footnotes}

Return ONLY the JSON object. Write all fields in English."""

# Image analysis prompt with text fallback
PROMPTS["text_prompt"] = """Based on the following image information, provide analysis:

Image Path: {image_path}
Captions: {captions}
Footnotes: {footnotes}

{vision_prompt}"""

# Table analysis prompt template
PROMPTS[
    "table_prompt"
] = """You are analyzing a table for a retrieval system. The table's raw data is already stored separately, so do NOT re-list every cell. Write only the interpretation that the raw cells alone do not show.

Return a JSON object with EXACTLY this structure:

{{
    "detailed_description": "A concise analytical summary, written as a flat list of facts (no narrative). Include:
    - What the table is about (one line, using the caption if present)
    - What the rows represent and what the columns represent
    - The key comparisons: highest / lowest values, largest gaps, and how the main rows differ
    - Any clear trend or pattern across the table (increase / decrease / anomaly)
    - For EVERY claim, state the exact number, its unit, and the row/column it belongs to
    Do NOT re-list the whole table and do NOT pad with generic commentary.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "table",
        "summary": "One or two sentences (max 60 words) stating the table's purpose and its single most important finding, with the specific number."
    }}
}}

Table Information:
Image Path: {table_img_path}
Caption: {table_caption}
Body: {table_body}
Footnotes: {table_footnote}

Return ONLY the JSON object. Write all fields in English."""

# Table analysis prompt with context support
PROMPTS[
    "table_prompt_with_context"
] = """You are analyzing a table for a retrieval system. The table's raw data is already stored separately, so do NOT re-list every cell. Write only the interpretation that the raw cells alone do not show. Use the surrounding context to resolve what the table refers to.

Return a JSON object with EXACTLY this structure:

{{
    "detailed_description": "A concise analytical summary, written as a flat list of facts (no narrative). Include:
    - What the table is about (one line, using the caption if present)
    - What the rows represent and what the columns represent
    - The key comparisons: highest / lowest values, largest gaps, and how the main rows differ
    - Any clear trend or pattern across the table (increase / decrease / anomaly)
    - For EVERY claim, state the exact number, its unit, and the row/column it belongs to
    Do NOT re-list the whole table and do NOT pad with generic commentary.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "table",
        "summary": "One or two sentences (max 60 words) stating the table's purpose and its single most important finding, with the specific number."
    }}
}}

Context from surrounding content:
{context}

Table Information:
Image Path: {table_img_path}
Caption: {table_caption}
Body: {table_body}
Footnotes: {table_footnote}

Return ONLY the JSON object. Write all fields in English."""

# Equation analysis prompt template
PROMPTS[
    "equation_prompt"
] = """Please analyze this mathematical equation and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive analysis of the equation including:
    - Mathematical meaning and interpretation
    - Variables and their definitions
    - Mathematical operations and functions used
    - Application domain and context
    - Physical or theoretical significance
    - Relationship to other mathematical concepts
    - Practical applications or use cases
    Always use specific mathematical terminology.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "equation",
        "summary": "concise summary of the equation's purpose and significance (max 100 words)"
    }}
}}

Equation Information:
Equation: {equation_text}
Format: {equation_format}

Focus on providing mathematical insights and explaining the equation's significance."""

# Equation analysis prompt with context support
PROMPTS[
    "equation_prompt_with_context"
] = """Please analyze this mathematical equation considering the surrounding context, and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive analysis of the equation including:
    - Mathematical meaning and interpretation
    - Variables and their definitions in the context of surrounding content
    - Mathematical operations and functions used
    - Application domain and context based on surrounding material
    - Physical or theoretical significance
    - Relationship to other mathematical concepts mentioned in the context
    - Practical applications or use cases
    - How the equation relates to the broader discussion or framework
    Always use specific mathematical terminology.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "equation",
        "summary": "concise summary of the equation's purpose, significance, and role in the surrounding context (max 100 words)"
    }}
}}

Context from surrounding content:
{context}

Equation Information:
Equation: {equation_text}
Format: {equation_format}

Focus on providing mathematical insights and explaining the equation's significance within the broader context."""

# Generic content analysis prompt template
PROMPTS[
    "generic_prompt"
] = """Please analyze this {content_type} content and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive analysis of the content including:
    - Content structure and organization
    - Key information and elements
    - Relationships between components
    - Context and significance
    - Relevant details for knowledge retrieval
    Always use specific terminology appropriate for {content_type} content.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "{content_type}",
        "summary": "concise summary of the content's purpose and key points (max 100 words)"
    }}
}}

Content: {content}

Focus on extracting meaningful information that would be useful for knowledge retrieval."""

# Generic content analysis prompt with context support
PROMPTS[
    "generic_prompt_with_context"
] = """Please analyze this {content_type} content considering the surrounding context, and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive analysis of the content including:
    - Content structure and organization
    - Key information and elements
    - Relationships between components
    - Context and significance in relation to surrounding content
    - How this content connects to or supports the broader discussion
    - Relevant details for knowledge retrieval
    Always use specific terminology appropriate for {content_type} content.",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "{content_type}",
        "summary": "concise summary of the content's purpose, key points, and relationship to surrounding context (max 100 words)"
    }}
}}

Context from surrounding content:
{context}

Content: {content}

Focus on extracting meaningful information that would be useful for knowledge retrieval and understanding the content's role in the broader context."""

# Modal chunk templates
PROMPTS["image_chunk"] = """
Image Content Analysis:
Image Path: {image_path}
Captions: {captions}
Footnotes: {footnotes}

Visual Analysis: {enhanced_caption}"""

PROMPTS["table_chunk"] = """Table Analysis:
Image Path: {table_img_path}
Caption: {table_caption}
Structure: {table_body}
Footnotes: {table_footnote}

Analysis: {enhanced_caption}"""

PROMPTS["equation_chunk"] = """Mathematical Equation Analysis:
Equation: {equation_text}
Format: {equation_format}

Mathematical Analysis: {enhanced_caption}"""

PROMPTS["generic_chunk"] = """{content_type} Content Analysis:
Content: {content}

Analysis: {enhanced_caption}"""

# Query-related prompts
PROMPTS["QUERY_IMAGE_DESCRIPTION"] = (
    "Please briefly describe the main content, key elements, and important information in this image."
)

PROMPTS["QUERY_IMAGE_ANALYST_SYSTEM"] = (
    "You are a professional image analyst who can accurately describe image content."
)

PROMPTS[
    "QUERY_TABLE_ANALYSIS"
] = """Please analyze the main content, structure, and key information of the following table data:

Table data:
{table_data}

Table caption: {table_caption}

Please briefly summarize the main content, data characteristics, and important findings of the table."""

PROMPTS["QUERY_TABLE_ANALYST_SYSTEM"] = (
    "You are a professional data analyst who can accurately analyze table data."
)

PROMPTS[
    "QUERY_EQUATION_ANALYSIS"
] = """Please explain the meaning and purpose of the following mathematical formula:

LaTeX formula: {latex}
Formula caption: {equation_caption}

Please briefly explain the mathematical meaning, application scenarios, and importance of this formula."""

PROMPTS["QUERY_EQUATION_ANALYST_SYSTEM"] = (
    "You are a mathematics expert who can clearly explain mathematical formulas."
)

PROMPTS[
    "QUERY_GENERIC_ANALYSIS"
] = """Please analyze the following {content_type} type content and extract its main information and key features:

Content: {content_str}

Please briefly summarize the main characteristics and important information of this content."""

PROMPTS["QUERY_GENERIC_ANALYST_SYSTEM"] = (
    "You are a professional content analyst who can accurately analyze {content_type} type content."
)

PROMPTS["QUERY_ENHANCEMENT_SUFFIX"] = (
    "\n\nPlease provide a comprehensive answer based on the user query and the provided multimodal content information."
)
