import re
from enum import Enum

from htmlnode import HTMLNode, ParentNode
from inline_markdown import text_to_textnodes
from textnode import TextNode, TextType, text_node_to_html_node

HEADING_PATTERN = r"^#{1,6} ."


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []
    for raw_block in markdown.split("\n\n"):
        block = raw_block.strip()
        if block == "":
            continue
        blocks.append(block)
    return blocks


def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    if re.match(HEADING_PATTERN, block):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1] == "```":
        return BlockType.CODE
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    if all(line.startswith(f"{i}. ") for i, line in enumerate(lines, start=1)):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def text_to_children(text: str) -> list[HTMLNode]:
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]


def paragraph_to_html_node(block: str) -> ParentNode:
    paragraph = " ".join(block.split("\n"))
    return ParentNode("p", text_to_children(paragraph))


def heading_to_html_node(block: str) -> ParentNode:
    level = len(block) - len(block.lstrip("#"))
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading: {block!r}")
    text = block[level + 1 :]
    return ParentNode(f"h{level}", text_to_children(text))


def code_to_html_node(block: str) -> ParentNode:
    lines = block.split("\n")
    if len(lines) < 2 or not lines[0].startswith("```") or lines[-1] != "```":
        raise ValueError(f"invalid code block: {block!r}")
    inner_lines = lines[1:-1]
    text = "".join(f"{line}\n" for line in inner_lines)
    code = text_node_to_html_node(TextNode(text, TextType.TEXT))
    return ParentNode("pre", [ParentNode("code", [code])])


def quote_to_html_node(block: str) -> ParentNode:
    stripped_lines = []
    for line in block.split("\n"):
        if not line.startswith(">"):
            raise ValueError(f"invalid quote block: {block!r}")
        stripped_lines.append(line.lstrip(">").strip())
    return ParentNode("blockquote", text_to_children(" ".join(stripped_lines)))


def unordered_list_to_html_node(block: str) -> ParentNode:
    items = []
    for line in block.split("\n"):
        if not line.startswith("- "):
            raise ValueError(f"invalid unordered list block: {block!r}")
        items.append(ParentNode("li", text_to_children(line[2:])))
    return ParentNode("ul", items)


def ordered_list_to_html_node(block: str) -> ParentNode:
    items = []
    for i, line in enumerate(block.split("\n"), start=1):
        prefix = f"{i}. "
        if not line.startswith(prefix):
            raise ValueError(f"invalid ordered list block: {block!r}")
        items.append(ParentNode("li", text_to_children(line[len(prefix) :])))
    return ParentNode("ol", items)


def block_to_html_node(block: str) -> ParentNode:
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)
    raise ValueError(f"invalid block type: {block_type}")


def markdown_to_html_node(markdown: str) -> ParentNode:
    children = [block_to_html_node(block) for block in markdown_to_blocks(markdown)]
    return ParentNode("div", children)
