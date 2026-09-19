import re

from textnode import TextNode, TextType

IMAGE_PATTERN = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
LINK_PATTERN = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError(
                f"invalid markdown: unclosed delimiter {delimiter} in {old_node.text!r}"
            )

        split_nodes = []
        for i, section in enumerate(sections):
            if section == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(section, TextType.TEXT))
            else:
                split_nodes.append(TextNode(section, text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(IMAGE_PATTERN, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(LINK_PATTERN, text)


def _split_nodes_pattern(
    old_nodes: list[TextNode], pattern: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text = old_node.text
        cursor = 0
        for match in re.finditer(pattern, text):
            before = text[cursor : match.start()]
            if before != "":
                new_nodes.append(TextNode(before, TextType.TEXT))
            label, url = match.groups()
            new_nodes.append(TextNode(label, text_type, url))
            cursor = match.end()

        after = text[cursor:]
        if after != "":
            new_nodes.append(TextNode(after, TextType.TEXT))
    return new_nodes


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_pattern(old_nodes, IMAGE_PATTERN, TextType.IMAGE)


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_pattern(old_nodes, LINK_PATTERN, TextType.LINK)


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes
