import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_heading_paragraph_and_list(self):
        md = """
# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item
"""
        self.assertListEqual(
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
            markdown_to_blocks(md),
        )

    def test_single_block(self):
        self.assertListEqual(
            ["just one paragraph"], markdown_to_blocks("just one paragraph")
        )

    def test_excessive_newlines_are_dropped(self):
        md = "first block\n\n\n\n\nsecond block\n\n\n\nthird block"
        self.assertListEqual(
            ["first block", "second block", "third block"], markdown_to_blocks(md)
        )

    def test_leading_and_trailing_whitespace_is_stripped(self):
        md = "\n\n   # heading with spaces   \n\n\t a paragraph \t\n\n"
        self.assertListEqual(
            ["# heading with spaces", "a paragraph"], markdown_to_blocks(md)
        )

    def test_empty_markdown(self):
        self.assertListEqual([], markdown_to_blocks(""))

    def test_only_whitespace(self):
        self.assertListEqual([], markdown_to_blocks("\n\n   \n\n  \n\n"))

    def test_newlines_inside_block_are_preserved(self):
        md = "line one\nline two\nline three"
        self.assertListEqual(["line one\nline two\nline three"], markdown_to_blocks(md))

    def test_code_block_stays_one_block(self):
        md = "```\ndef hi():\n    print('hi')\n```"
        self.assertListEqual([md], markdown_to_blocks(md))


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        self.assertEqual(
            BlockType.PARAGRAPH, block_to_block_type("this is a normal paragraph")
        )

    def test_multiline_paragraph(self):
        block = "this is a paragraph\nspanning two lines"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_headings_one_through_six(self):
        for level in range(1, 7):
            block = f"{'#' * level} heading text"
            with self.subTest(level=level):
                self.assertEqual(BlockType.HEADING, block_to_block_type(block))

    def test_seven_hashes_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("####### too many"))

    def test_hash_without_space_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("#nospace"))

    def test_hash_without_text_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("# "))

    def test_code_block(self):
        block = "```\ndef hi():\n    print('hi')\n```"
        self.assertEqual(BlockType.CODE, block_to_block_type(block))

    def test_code_block_with_language(self):
        block = "```python\nprint('hi')\n```"
        self.assertEqual(BlockType.CODE, block_to_block_type(block))

    def test_code_block_empty_body(self):
        self.assertEqual(BlockType.CODE, block_to_block_type("```\n```"))

    def test_single_line_backticks_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("```"))

    def test_unclosed_code_block_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("```\nprint('hi')"))

    def test_quote_block(self):
        block = "> line one\n> line two\n> line three"
        self.assertEqual(BlockType.QUOTE, block_to_block_type(block))

    def test_quote_block_without_space(self):
        self.assertEqual(BlockType.QUOTE, block_to_block_type(">no space needed"))

    def test_quote_with_one_bad_line_is_paragraph(self):
        block = "> line one\nline two is not quoted"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_unordered_list(self):
        block = "- item one\n- item two\n- item three"
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type(block))

    def test_unordered_list_single_item(self):
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type("- only item"))

    def test_dash_without_space_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("-nospace"))

    def test_unordered_list_with_one_bad_line_is_paragraph(self):
        block = "- item one\nnot an item"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_ordered_list(self):
        block = "1. item one\n2. item two\n3. item three"
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type(block))

    def test_ordered_list_single_item(self):
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type("1. only item"))

    def test_ordered_list_not_starting_at_one_is_paragraph(self):
        block = "2. item two\n3. item three"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_ordered_list_skipping_a_number_is_paragraph(self):
        block = "1. item one\n3. item three"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_ordered_list_out_of_order_is_paragraph(self):
        block = "1. item one\n3. item three\n2. item two"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_ordered_list_number_without_space_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("1.nospace"))

    def test_ordered_list_with_ten_items(self):
        block = "\n".join(f"{i}. item {i}" for i in range(1, 11))
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type(block))

    def test_types_for_each_block_in_a_document(self):
        md = """
# Heading

A paragraph.

> a quote

- unordered
- list

1. ordered
2. list

```
code
```
"""
        types = [block_to_block_type(block) for block in markdown_to_blocks(md)]
        self.assertListEqual(
            [
                BlockType.HEADING,
                BlockType.PARAGRAPH,
                BlockType.QUOTE,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.CODE,
            ],
            types,
        )


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_codeblock_with_language(self):
        md = "```python\nprint('hi')\n```"
        self.assertEqual(
            "<div><pre><code>print('hi')\n</code></pre></div>",
            markdown_to_html_node(md).to_html(),
        )

    def test_empty_codeblock(self):
        self.assertEqual(
            "<div><pre><code></code></pre></div>",
            markdown_to_html_node("```\n```").to_html(),
        )

    def test_headings(self):
        md = """
# Heading one with **bold**

###### Heading six with _italic_
"""
        self.assertEqual(
            "<div><h1>Heading one with <b>bold</b></h1><h6>Heading six with <i>italic</i></h6></div>",
            markdown_to_html_node(md).to_html(),
        )

    def test_all_heading_levels(self):
        for level in range(1, 7):
            md = f"{'#' * level} heading"
            with self.subTest(level=level):
                self.assertEqual(
                    f"<div><h{level}>heading</h{level}></div>",
                    markdown_to_html_node(md).to_html(),
                )

    def test_quote(self):
        md = """
> This is a quote
> that spans **two** lines
"""
        self.assertEqual(
            "<div><blockquote>This is a quote that spans <b>two</b> lines</blockquote></div>",
            markdown_to_html_node(md).to_html(),
        )

    def test_quote_without_space_after_marker(self):
        self.assertEqual(
            "<div><blockquote>tight quote</blockquote></div>",
            markdown_to_html_node(">tight quote").to_html(),
        )

    def test_unordered_list(self):
        md = """
- first item with **bold**
- second item with _italic_
- third item with `code`
"""
        self.assertEqual(
            "<div><ul><li>first item with <b>bold</b></li>"
            "<li>second item with <i>italic</i></li>"
            "<li>third item with <code>code</code></li></ul></div>",
            markdown_to_html_node(md).to_html(),
        )

    def test_ordered_list(self):
        md = """
1. first item
2. second item with **bold**
3. third item
"""
        self.assertEqual(
            "<div><ol><li>first item</li>"
            "<li>second item with <b>bold</b></li>"
            "<li>third item</li></ol></div>",
            markdown_to_html_node(md).to_html(),
        )

    def test_links_and_images(self):
        md = "This is a [link](https://boot.dev) and an ![image](https://boot.dev/img.png)"
        self.assertEqual(
            '<div><p>This is a <a href="https://boot.dev">link</a> and an '
            '<img src="https://boot.dev/img.png" alt="image"></img></p></div>',
            markdown_to_html_node(md).to_html(),
        )

    def test_empty_markdown(self):
        self.assertEqual("<div></div>", markdown_to_html_node("").to_html())

    def test_full_document(self):
        md = """
# Tolkien Fan Club

I like **Tolkien**. Here's why I like Tolkien:

1. It has more **bad guys** than you can shake a stick at
2. It's more meaningful than a _simple_ story

> "I am in fact a Hobbit in all but size."
>
> -- J.R.R. Tolkien

- Ambitious
- Complete

```
hobbit = "Frodo"
```
"""
        self.assertEqual(
            "<div>"
            "<h1>Tolkien Fan Club</h1>"
            "<p>I like <b>Tolkien</b>. Here's why I like Tolkien:</p>"
            "<ol><li>It has more <b>bad guys</b> than you can shake a stick at</li>"
            "<li>It's more meaningful than a <i>simple</i> story</li></ol>"
            '<blockquote>"I am in fact a Hobbit in all but size."  -- J.R.R. Tolkien</blockquote>'
            "<ul><li>Ambitious</li><li>Complete</li></ul>"
            '<pre><code>hobbit = "Frodo"\n</code></pre>'
            "</div>",
            markdown_to_html_node(md).to_html(),
        )


if __name__ == "__main__":
    unittest.main()
