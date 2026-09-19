import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(
            "a",
            "Google",
            None,
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(), ' href="https://www.google.com" target="_blank"'
        )

    def test_props_to_html_single(self):
        node = HTMLNode("a", "Boot.dev", None, {"href": "https://www.boot.dev"})
        self.assertEqual(node.props_to_html(), ' href="https://www.boot.dev"')

    def test_props_to_html_none(self):
        node = HTMLNode("p", "This is a paragraph")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty(self):
        node = HTMLNode("p", "This is a paragraph", None, {})
        self.assertEqual(node.props_to_html(), "")

    def test_values_default_to_none(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_children(self):
        child = HTMLNode("span", "child text")
        node = HTMLNode("div", None, [child])
        self.assertEqual(node.children, [child])

    def test_to_html_raises(self):
        node = HTMLNode("p", "This is a paragraph")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        node = HTMLNode("p", "This is a paragraph", None, {"class": "intro"})
        self.assertEqual(
            repr(node),
            "HTMLNode(p, This is a paragraph, None, {'class': 'intro'})",
        )


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_span(self):
        node = LeafNode("span", "This is a span")
        self.assertEqual(node.to_html(), "<span>This is a span</span>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_leaf_to_html_multiple_props(self):
        node = LeafNode(
            "a",
            "Click me!",
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.google.com" target="_blank">Click me!</a>',
        )

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "This is raw text")
        self.assertEqual(node.to_html(), "This is raw text")

    def test_leaf_to_html_no_value_raises(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_has_no_children(self):
        node = LeafNode("p", "Hello, world!")
        self.assertIsNone(node.children)

    def test_leaf_repr(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.boot.dev"})
        self.assertEqual(
            repr(node), "LeafNode(a, Click me!, {'href': 'https://www.boot.dev'})"
        )


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        parent_node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            parent_node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_deeply_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "section",
                    [
                        ParentNode(
                            "ul", [LeafNode("li", "one"), LeafNode("li", "two")]
                        ),
                        LeafNode("p", "tail"),
                    ],
                )
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><section><ul><li>one</li><li>two</li></ul><p>tail</p></section></div>",
        )

    def test_to_html_with_props(self):
        parent_node = ParentNode(
            "div", [LeafNode("span", "child")], {"class": "wrapper"}
        )
        self.assertEqual(
            parent_node.to_html(),
            '<div class="wrapper"><span>child</span></div>',
        )

    def test_to_html_mixed_parent_and_leaf_children(self):
        parent_node = ParentNode(
            "div",
            [
                LeafNode(None, "before "),
                ParentNode("em", [LeafNode(None, "middle")]),
                LeafNode(None, " after"),
            ],
        )
        self.assertEqual(
            parent_node.to_html(), "<div>before <em>middle</em> after</div>"
        )

    def test_to_html_empty_children(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")

    def test_to_html_no_tag_raises(self):
        parent_node = ParentNode(None, [LeafNode("span", "child")])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_no_children_raises(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_no_tag_and_no_children_messages_differ(self):
        with self.assertRaises(ValueError) as no_tag:
            ParentNode(None, [LeafNode("span", "child")]).to_html()
        with self.assertRaises(ValueError) as no_children:
            ParentNode("div", None).to_html()
        self.assertNotEqual(str(no_tag.exception), str(no_children.exception))

    def test_parent_has_no_value(self):
        parent_node = ParentNode("div", [LeafNode("span", "child")])
        self.assertIsNone(parent_node.value)

    def test_invalid_leaf_child_propagates(self):
        parent_node = ParentNode("div", [LeafNode("span", None)])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_parent_repr(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            repr(parent_node), "ParentNode(div, [LeafNode(span, child, None)], None)"
        )


if __name__ == "__main__":
    unittest.main()
