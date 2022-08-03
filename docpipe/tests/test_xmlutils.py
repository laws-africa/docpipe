from unittest import TestCase

from lxml import etree

from docpipe.xmlutils import wrap_text, unwrap_element


class WrapTextTestCase(TestCase):
    def wrap(self, text):
        e = self.xml.makeelement('wrap')
        e.text = text
        return e

    def test_wrap_text(self):
        self.xml = etree.fromstring("""
<root>
  <p>foo bar baz</p>
</root>""")

        wrap_text(self.xml.find('p'), False, self.wrap)
        self.assertMultiLineEqual("""<root>
  <p><wrap>foo bar baz</wrap></p>
</root>""", etree.tostring(self.xml, encoding='unicode').strip())

    def test_wrap_text_offsets(self):
        self.xml = etree.fromstring("""
<root>
  <p>foo bar baz</p>
</root>""")

        wrap_text(self.xml.find('p'), False, self.wrap, 5, 7)
        self.assertMultiLineEqual("""<root>
  <p>foo b<wrap>ar</wrap> baz</p>
</root>""", etree.tostring(self.xml, encoding='unicode').strip())

    def test_wrap_text_mixed(self):
        self.xml = etree.fromstring("""
<root>
  <p>foo <b>bar</b> baz</p>
</root>""")

        wrap_text(self.xml.find('p'), False, self.wrap)
        self.assertMultiLineEqual("""<root>
  <p><wrap>foo </wrap><b>bar</b> baz</p>
</root>""", etree.tostring(self.xml, encoding='unicode').strip())

    def test_wrap_text_offset_mixed(self):
        self.xml = etree.fromstring("""
<root>
  <p>foo <b>bar</b> baz</p>
</root>""")

        wrap_text(self.xml.find('p'), False, self.wrap, 0, 2)
        self.assertMultiLineEqual("""<root>
  <p><wrap>fo</wrap>o <b>bar</b> baz</p>
</root>""", etree.tostring(self.xml, encoding='unicode').strip())

    def test_wrap_text_tail(self):
        self.xml = etree.fromstring("""
<root>
  <p>foo <b>bar</b> baz</p>
</root>""")

        wrap_text(self.xml.find('p').find('b'), True, self.wrap)
        self.assertMultiLineEqual("""<root>
  <p>foo <b>bar</b><wrap> baz</wrap></p>
</root>""", etree.tostring(self.xml, encoding='unicode').strip())

    def test_wrap_text_tail_offset(self):
        self.xml = etree.fromstring("""
<root>
  <p>foo <b>bar</b> baz</p>
</root>""")

        wrap_text(self.xml.find('p').find('b'), True, self.wrap, 2, 3)
        self.assertMultiLineEqual("""<root>
  <p>foo <b>bar</b> b<wrap>a</wrap>z</p>
</root>""", etree.tostring(self.xml, encoding='unicode').strip())


class UnwrapElementTestCase(TestCase):
    def test_unwrap_elem_first_child_complex(self):
        root = etree.fromstring('<p>text <term>content <b>child1</b> <i>child2</i> endterm</term> tail</p>')
        term = root.find('term')
        unwrap_element(term)

        actual = etree.tostring(root, encoding='utf-8').decode('utf-8')
        self.assertMultiLineEqual(
            '<p>text content <b>child1</b> <i>child2</i> endterm tail</p>',
            actual,
        )

    def test_unwrap_elem_first_child_simple(self):
        root = etree.fromstring('<p>text <term>content</term> tail</p>')
        term = root.find('term')
        unwrap_element(term)

        actual = etree.tostring(root, encoding='utf-8').decode('utf-8')
        self.assertMultiLineEqual(
            '<p>text content tail</p>',
            actual,
        )

    def test_unwrap_elem_second_child_complex(self):
        root = etree.fromstring('<p>text <term>first</term> and <term>content <b>child1</b> <i>child2</i> endterm</term> tail</p>')
        term = root.getchildren()[1]
        unwrap_element(term)

        actual = etree.tostring(root, encoding='utf-8').decode('utf-8')
        self.assertMultiLineEqual(
            '<p>text <term>first</term> and content <b>child1</b> <i>child2</i> endterm tail</p>',
            actual,
        )
