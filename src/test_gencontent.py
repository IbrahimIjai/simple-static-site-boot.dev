import os
import tempfile
import unittest

from gencontent import extract_title, generate_pages_recursive


class TestExtractTitle(unittest.TestCase):
    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_strips_whitespace(self):
        self.assertEqual(extract_title("#   Hello World   "), "Hello World")

    def test_title_not_on_first_line(self):
        md = """
Some intro paragraph

# The Real Title

More text
"""
        self.assertEqual(extract_title(md), "The Real Title")

    def test_ignores_lower_level_headings(self):
        md = """
## Not the title

### Also not the title

# Tolkien Fan Club
"""
        self.assertEqual(extract_title(md), "Tolkien Fan Club")

    def test_returns_first_h1(self):
        md = "# First\n\n# Second"
        self.assertEqual(extract_title(md), "First")

    def test_keeps_inline_markdown(self):
        self.assertEqual(extract_title("# Hello **world**"), "Hello **world**")

    def test_no_h1_raises(self):
        md = """
## Only an h2

Just a paragraph
"""
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_hash_without_space_raises(self):
        with self.assertRaises(ValueError):
            extract_title("#NotAHeading")

    def test_empty_markdown_raises(self):
        with self.assertRaises(ValueError):
            extract_title("")


class TestGeneratePagesRecursive(unittest.TestCase):
    def write(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def read(self, path):
        with open(path) as f:
            return f.read()

    def test_mirrors_content_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = os.path.join(tmp, "content")
            public = os.path.join(tmp, "public")
            template = os.path.join(tmp, "template.html")
            self.write(template, "<title>{{ Title }}</title><body>{{ Content }}</body>")
            self.write(os.path.join(content, "index.md"), "# Home\n\nHello **there**")
            self.write(os.path.join(content, "blog", "tom", "index.md"), "# Tom")
            self.write(os.path.join(content, "notes.txt"), "not markdown")

            generate_pages_recursive(content, template, public)

            self.assertEqual(
                self.read(os.path.join(public, "index.html")),
                "<title>Home</title><body><div><h1>Home</h1>"
                "<p>Hello <b>there</b></p></div></body>",
            )
            self.assertEqual(
                self.read(os.path.join(public, "blog", "tom", "index.html")),
                "<title>Tom</title><body><div><h1>Tom</h1></div></body>",
            )
            self.assertFalse(os.path.exists(os.path.join(public, "notes.txt")))
            self.assertFalse(os.path.exists(os.path.join(public, "notes.html")))


if __name__ == "__main__":
    unittest.main()
