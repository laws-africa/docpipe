from unittest import TestCase

from lxml import etree

from docpipe.xmlutils import wrap_text


class XmlUtilsTestCase(TestCase):
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
