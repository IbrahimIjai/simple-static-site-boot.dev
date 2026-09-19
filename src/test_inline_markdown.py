import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_bold_in_middle(self):
        node = TextNode(
            "This is text with a **bolded phrase** in the middle", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_code_in_middle(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_italic_in_middle(self):
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delimiter_at_start(self):
        node = TextNode("**bold** at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" at the start", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delimiter_at_end(self):
        node = TextNode("ends with **bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("ends with ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_whole_string_is_delimited(self):
        node = TextNode("`all code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual([TextNode("all code", TextType.CODE)], new_nodes)

    def test_multiple_delimited_sections(self):
        node = TextNode("**one** and **two** and **three**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("one", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("three", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_no_delimiter_returns_same_text(self):
        node = TextNode("plain text with no delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [TextNode("plain text with no delimiters", TextType.TEXT)], new_nodes
        )

    def test_non_text_nodes_pass_through(self):
        nodes = [
            TextNode("already bold", TextType.BOLD),
            TextNode("a `code` word", TextType.TEXT),
            TextNode("Click me!", TextType.LINK, "https://www.boot.dev"),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("already bold", TextType.BOLD),
                TextNode("a ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" word", TextType.TEXT),
                TextNode("Click me!", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )

    def test_multiple_old_nodes(self):
        nodes = [
            TextNode("first _italic_ here", TextType.TEXT),
            TextNode("second _italic_ there", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("first ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" here", TextType.TEXT),
                TextNode("second ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" there", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_chained_delimiters(self):
        node = TextNode("A **bold** and an _italic_ and a `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("A ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and a ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
            new_nodes,
        )

    def test_empty_list(self):
        self.assertListEqual([], split_nodes_delimiter([], "**", TextType.BOLD))

    def test_unclosed_delimiter_raises(self):
        node = TextNode("This is **unclosed bold", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_unclosed_code_delimiter_raises(self):
        node = TextNode("an `unclosed code block", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_images_empty_alt_text(self):
        self.assertListEqual(
            [("", "https://i.imgur.com/zjjcJKZ.png")],
            extract_markdown_images("![](https://i.imgur.com/zjjcJKZ.png)"),
        )

    def test_extract_images_no_images(self):
        self.assertListEqual(
            [], extract_markdown_images("This is text with a [link](https://boot.dev)")
        )

    def test_extract_images_ignores_links(self):
        text = "![img](https://i.imgur.com/a.png) and [link](https://www.boot.dev)"
        self.assertListEqual(
            [("img", "https://i.imgur.com/a.png")], extract_markdown_images(text)
        )


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_extract_links_does_not_match_images(self):
        text = (
            "![rick roll](https://i.imgur.com/aKaOqIh.gif) and [link](https://boot.dev)"
        )
        self.assertListEqual(
            [("link", "https://boot.dev")], extract_markdown_links(text)
        )

    def test_extract_links_no_links(self):
        self.assertListEqual(
            [], extract_markdown_links("This is text with an ![image](https://a.png)")
        )

    def test_extract_links_empty_anchor_text(self):
        self.assertListEqual(
            [("", "https://www.boot.dev")],
            extract_markdown_links("[](https://www.boot.dev)"),
        )

    def test_extract_links_empty_text(self):
        self.assertListEqual([], extract_markdown_links(""))


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another "
            "![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode("![image](https://i.imgur.com/zjjcJKZ.png)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")],
            split_nodes_image([node]),
        )

    def test_split_image_with_trailing_text(self):
        node = TextNode(
            "![image](https://i.imgur.com/a.png) at the start", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/a.png"),
                TextNode(" at the start", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_split_images_no_images(self):
        node = TextNode("This is plain text", TextType.TEXT)
        self.assertListEqual(
            [TextNode("This is plain text", TextType.TEXT)], split_nodes_image([node])
        )

    def test_split_images_ignores_links(self):
        node = TextNode("A [link](https://www.boot.dev) only", TextType.TEXT)
        self.assertListEqual(
            [TextNode("A [link](https://www.boot.dev) only", TextType.TEXT)],
            split_nodes_image([node]),
        )

    def test_split_images_non_text_nodes_pass_through(self):
        nodes = [
            TextNode("bold", TextType.BOLD),
            TextNode("an ![image](https://i.imgur.com/a.png) here", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "https://i.imgur.com/b.png"),
        ]
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode("an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/a.png"),
                TextNode(" here", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "https://i.imgur.com/b.png"),
            ],
            split_nodes_image(nodes),
        )

    def test_split_images_multiple_old_nodes(self):
        nodes = [
            TextNode("first ![a](https://a.png)", TextType.TEXT),
            TextNode("second ![b](https://b.png)", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("first ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "https://a.png"),
                TextNode("second ", TextType.TEXT),
                TextNode("b", TextType.IMAGE, "https://b.png"),
            ],
            split_nodes_image(nodes),
        )

    def test_split_images_empty_list(self):
        self.assertListEqual([], split_nodes_image([]))


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and "
            "[to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_single_link(self):
        node = TextNode("[to boot dev](https://www.boot.dev)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("to boot dev", TextType.LINK, "https://www.boot.dev")],
            split_nodes_link([node]),
        )

    def test_split_links_no_links(self):
        node = TextNode("This is plain text", TextType.TEXT)
        self.assertListEqual(
            [TextNode("This is plain text", TextType.TEXT)], split_nodes_link([node])
        )

    def test_split_links_leaves_images_alone(self):
        node = TextNode(
            "![image](https://i.imgur.com/a.png) and [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("![image](https://i.imgur.com/a.png) and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
            ],
            split_nodes_link([node]),
        )

    def test_split_links_non_text_nodes_pass_through(self):
        nodes = [
            TextNode("italic", TextType.ITALIC),
            TextNode("go [here](https://www.boot.dev) now", TextType.TEXT),
        ]
        self.assertListEqual(
            [
                TextNode("italic", TextType.ITALIC),
                TextNode("go ", TextType.TEXT),
                TextNode("here", TextType.LINK, "https://www.boot.dev"),
                TextNode(" now", TextType.TEXT),
            ],
            split_nodes_link(nodes),
        )

    def test_split_links_empty_list(self):
        self.assertListEqual([], split_nodes_link([]))

    def test_split_images_then_links(self):
        node = TextNode(
            "![img](https://i.imgur.com/a.png) then [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link(split_nodes_image([node]))
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "https://i.imgur.com/a.png"),
                TextNode(" then ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_all_types(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_plain_text(self):
        self.assertListEqual(
            [TextNode("just some plain text", TextType.TEXT)],
            text_to_textnodes("just some plain text"),
        )

    def test_empty_string(self):
        self.assertListEqual([], text_to_textnodes(""))

    def test_only_bold(self):
        self.assertListEqual(
            [TextNode("bold", TextType.BOLD)], text_to_textnodes("**bold**")
        )

    def test_adjacent_delimiters(self):
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode("italic", TextType.ITALIC),
            ],
            text_to_textnodes("**bold**_italic_"),
        )

    def test_image_and_link_next_to_each_other(self):
        text = "![alt](https://a.png)[anchor](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("alt", TextType.IMAGE, "https://a.png"),
                TextNode("anchor", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_url_with_underscores_is_not_italicized(self):
        text = "see ![my_cool_image](https://i.imgur.com/my_file_name.png) here"
        self.assertListEqual(
            [
                TextNode("see ", TextType.TEXT),
                TextNode(
                    "my_cool_image",
                    TextType.IMAGE,
                    "https://i.imgur.com/my_file_name.png",
                ),
                TextNode(" here", TextType.TEXT),
            ],
            text_to_textnodes(text),
        )

    def test_code_block_protects_its_contents(self):
        text = "run `pip install my_package` first"
        self.assertListEqual(
            [
                TextNode("run ", TextType.TEXT),
                TextNode("pip install my_package", TextType.CODE),
                TextNode(" first", TextType.TEXT),
            ],
            text_to_textnodes(text),
        )

    def test_multiple_of_each_type(self):
        text = "**a** and **b** with _c_ and _d_"
        self.assertListEqual(
            [
                TextNode("a", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
                TextNode(" with ", TextType.TEXT),
                TextNode("c", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("d", TextType.ITALIC),
            ],
            text_to_textnodes(text),
        )

    def test_unclosed_delimiter_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("this is **not closed")


if __name__ == "__main__":
    unittest.main()
