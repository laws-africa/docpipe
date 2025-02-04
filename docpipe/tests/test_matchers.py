# flake8: noqa
from unittest import TestCase

import lxml.html
from lxml import etree
from cobalt import FrbrUri

from docpipe.citations import AchprResolutionMatcher, ActMatcher
from docpipe.matchers import ExtractedCitation


class RefsAchprResolutionMatcherTest(TestCase):
    maxDiff = None

    def setUp(self):
        self.marker = AchprResolutionMatcher()
        self.frbr_uri = FrbrUri.parse("/akn/aa-au/statement/resolution/achpr/2021/509")

    def test_html_matches(self):
        html = lxml.html.fromstring(
            """
<div>
  <p><b>Recalling resolution</b> ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020, the Need to Prepare</p>
  <p><b>Recalling</b> its Resolution ACHPR/Res.79 (XXXVIII) 05 on the Composition and Operationalization</p>
  <p>No markup inside existing <a href="#foo">ACHPR/Res.79 (XXXVIII) 05</a> A tags.</p>
</div>
"""
        )
        self.marker.markup_html_matches(self.frbr_uri, html)

        self.assertMultiLineEqual(
            """<div>
  <p><b>Recalling resolution</b> <a href="/akn/aa-au/statement/resolution/achpr/2020/437">ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020</a>, the Need to Prepare</p>
  <p><b>Recalling</b> its Resolution <a href="/akn/aa-au/statement/resolution/achpr/2005/79">ACHPR/Res.79 (XXXVIII) 05</a> on the Composition and Operationalization</p>
  <p>No markup inside existing <a href="#foo">ACHPR/Res.79 (XXXVIII) 05</a> A tags.</p>
</div>""",
            lxml.html.tostring(html, encoding="unicode", pretty_print=True).strip(),
        )
        self.assertEqual(
            [
                ExtractedCitation(
                    "ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020",
                    1,
                    36,
                    "/akn/aa-au/statement/resolution/achpr/2020/437",
                    None,
                    None,
                    None
                ),
                ExtractedCitation(
                    "ACHPR/Res.79 (XXXVIII) 05",
                    16,
                    41,
                    "/akn/aa-au/statement/resolution/achpr/2005/79",
                    None,
                    None,
                    None
                ),
            ],
            self.marker.citations,
        )

    def test_xml_matches(self):
        xml = etree.fromstring(
            """<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <statement name="statement">
    <meta>
      <p>No markup outside of main content ACHPR/Res.79 (XXXVIII) 05.</p>
    </meta>
    <preamble>
      <p eId="preamble__p_1"><b>Recalling resolution</b> ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020, the Need to Prepare</p>
      <p eId="preamble__p_2"><b>Recalling</b> its Resolution ACHPR/Res.79 (XXXVIII) 05 on the Composition and Operationalization</p>
      <p eId="preamble__p_3">No markup inside existing <ref href="#foo">ACHPR/Res.79 (XXXVIII) 05</ref> ref tags.</p>
    </preamble>
  </statement>
</akomaNtoso>"""
        )
        self.marker.markup_xml_matches(self.frbr_uri, xml)

        self.assertMultiLineEqual("""<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <statement name="statement">
    <meta>
      <p>No markup outside of main content ACHPR/Res.79 (XXXVIII) 05.</p>
    </meta>
    <preamble>
      <p eId="preamble__p_1"><b>Recalling resolution</b> <ref href="/akn/aa-au/statement/resolution/achpr/2020/437">ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020</ref>, the Need to Prepare</p>
      <p eId="preamble__p_2"><b>Recalling</b> its Resolution <ref href="/akn/aa-au/statement/resolution/achpr/2005/79">ACHPR/Res.79 (XXXVIII) 05</ref> on the Composition and Operationalization</p>
      <p eId="preamble__p_3">No markup inside existing <ref href="#foo">ACHPR/Res.79 (XXXVIII) 05</ref> ref tags.</p>
    </preamble>
  </statement>
</akomaNtoso>""",
            etree.tostring(xml, encoding="unicode", pretty_print=True).strip(),
        )
        self.assertEqual(
            [
                ExtractedCitation(
                    "ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020",
                    1,
                    36,
                    "/akn/aa-au/statement/resolution/achpr/2020/437",
                    None,
                    None,
                    None,
                ),
                ExtractedCitation(
                    "ACHPR/Res.79 (XXXVIII) 05",
                    16,
                    41,
                    "/akn/aa-au/statement/resolution/achpr/2005/79",
                    None,
                    None,
                    None,
                ),
            ],
            self.marker.citations,
        )

    def test_text_matches(self):
        text = """
  Recalling resolution ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020, the Need to Prepare
  Recalling its Resolution ACHPR/Res.79 (XXXVIII) 05 on the Composition and Operationalization
"""
        self.marker.extract_text_matches(self.frbr_uri, text)

        self.assertEqual(
            [
                ExtractedCitation(
                    "ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020",
                    24,
                    59,
                    "/akn/aa-au/statement/resolution/achpr/2020/437",
                    0,
                    '\n  Recalling resolution ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "ACHPR/Res.79 (XXXVIII) 05",
                    108,
                    133,
                    "/akn/aa-au/statement/resolution/achpr/2005/79",
                    0,
                    're\n  Recalling its Resolution ',
                    ' on the Composition and Operat',
                ),
            ],
            self.marker.citations,
        )


class RefsActMatcherTest(TestCase):
    maxDiff = None

    def setUp(self):
        self.marker = ActMatcher()
        self.frbr_uri = FrbrUri.parse("/akn/za-wc/act/2021/509")

    def test_html_matches(self):
        html = lxml.html.fromstring(
            """
<div>
  <p><b>Recalling </b> Act 25 of 2020, the Need to Prepare</p>
  <p><b>Recalling</b> Act 1 of 92 on the Composition and Operationalization</p>
  <p><b>Recalling</b> Act 1 of 1992 on the Composition and Operationalization</p>
  <p>No markup inside existing <a href="#foo">Act 12 of 2021</a> A tags.</p>
  <p>Avoid weird years Act 11 of 19 and others.</p>
  <p>National Environment Management: Air Quality Act, 2004 (Act No. 39 of 2004);</p>
  <p>National Environment Management: Air Quality Act, 2004 (No. 39 of 2004);</p>
</div>
"""
        )
        self.marker.markup_html_matches(self.frbr_uri, html)

        self.assertMultiLineEqual(
            """<div>
  <p><b>Recalling </b> <a href="/akn/za/act/2020/25">Act 25 of 2020</a>, the Need to Prepare</p>
  <p><b>Recalling</b> Act 1 of 92 on the Composition and Operationalization</p>
  <p><b>Recalling</b> <a href="/akn/za/act/1992/1">Act 1 of 1992</a> on the Composition and Operationalization</p>
  <p>No markup inside existing <a href="#foo">Act 12 of 2021</a> A tags.</p>
  <p>Avoid weird years Act 11 of 19 and others.</p>
  <p>National Environment Management: Air Quality Act, 2004 (<a href="/akn/za/act/2004/39">Act No. 39 of 2004</a>);</p>
  <p>National Environment Management: Air Quality <a href="/akn/za/act/2004/39">Act, 2004 (No. 39 of 2004)</a>;</p>
</div>""",
            lxml.html.tostring(html, encoding="unicode", pretty_print=True).strip(),
        )
        self.assertEqual(
            [
                ExtractedCitation(
                    "Act 25 of 2020",
                    1,
                    15,
                    "/akn/za/act/2020/25",
                    None,
                    None,
                    None,
                ),
                ExtractedCitation(
                    "Act 1 of 1992",
                    1,
                    14,
                    "/akn/za/act/1992/1",
                    None,
                    None,
                    None,
                ),
                ExtractedCitation(
                    'Act No. 39 of 2004',
                    56,
                    74,
                    '/akn/za/act/2004/39',
                    None,
                    None,
                    None),
                ExtractedCitation(
                    'Act, 2004 (No. 39 of 2004)',
                    45,
                    71,
                    '/akn/za/act/2004/39',
                    None,
                    None,
                    None
                )
            ],
            self.marker.citations,
        )

    def test_xml_matches(self):
        xml = etree.fromstring(
            """<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <statement name="statement">
    <meta>
      <p>No markup outside of main content Act 15 on 2007</p>
    </meta>
    <preamble>
      <p eId="preamble__p_1"><b>Recalling </b> Act 25 of 2020, the Need to Prepare</p>
      <p eId="preamble__p_2"><b>Recalling</b> Act 1 of 92 on the Composition and Operationalization</p>
      <p eId="preamble__p_2"><b>Recalling</b> Act 1 of 1992 on the Composition and Operationalization</p>
      <p eId="preamble__p_3">No markup inside existing <ref href="#foo">Act 12 of 2021</ref> ref tags.</p>
      <p eId="preamble__p_4">Avoid weird years Act 11 of 19 and others.</p>
      <p eId="preamble__p_5">National Environment Management: Air Quality Act, 2004 (Act No. 39 of 2004);</p>
      <p eId="preamble__p_6">National Environment Management: Air Quality Act, 2004 (No. 39 of 2004);</p>
    </preamble>
  </statement>
</akomaNtoso>"""
        )
        self.marker.markup_xml_matches(self.frbr_uri, xml)

        self.assertMultiLineEqual("""<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <statement name="statement">
    <meta>
      <p>No markup outside of main content Act 15 on 2007</p>
    </meta>
    <preamble>
      <p eId="preamble__p_1"><b>Recalling </b> <ref href="/akn/za/act/2020/25">Act 25 of 2020</ref>, the Need to Prepare</p>
      <p eId="preamble__p_2"><b>Recalling</b> Act 1 of 92 on the Composition and Operationalization</p>
      <p eId="preamble__p_2"><b>Recalling</b> <ref href="/akn/za/act/1992/1">Act 1 of 1992</ref> on the Composition and Operationalization</p>
      <p eId="preamble__p_3">No markup inside existing <ref href="#foo">Act 12 of 2021</ref> ref tags.</p>
      <p eId="preamble__p_4">Avoid weird years Act 11 of 19 and others.</p>
      <p eId="preamble__p_5">National Environment Management: Air Quality Act, 2004 (<ref href="/akn/za/act/2004/39">Act No. 39 of 2004</ref>);</p>
      <p eId="preamble__p_6">National Environment Management: Air Quality <ref href="/akn/za/act/2004/39">Act, 2004 (No. 39 of 2004)</ref>;</p>
    </preamble>
  </statement>
</akomaNtoso>""",
            etree.tostring(xml, encoding="unicode", pretty_print=True).strip(),
        )
        self.assertEqual(
            [
                ExtractedCitation(
                    "Act 25 of 2020",
                    1,
                    15,
                    "/akn/za/act/2020/25",
                    None,
                    None,
                    None,
                ),
                ExtractedCitation(
                    "Act 1 of 1992",
                    1,
                    14,
                    "/akn/za/act/1992/1",
                    None,
                    None,
                    None,
                ),
                ExtractedCitation(
                    'Act No. 39 of 2004',
                    56,
                    74,
                    '/akn/za/act/2004/39',
                    None,
                    None,
                    None,
                ),
                ExtractedCitation(
                    'Act, 2004 (No. 39 of 2004)',
                    45,
                    71,
                    '/akn/za/act/2004/39',
                    None,
                    None,
                    None,
                )
            ],
            self.marker.citations,
        )

    def test_text_matches(self):
        text = """
  Recalling Act 25 of 2020, the Need to Prepare
  Recalling Income Tax Act, 1962 (No 58 of 1962) on the Composition and Operationalization
  Recalling Act 195 of 2021, the Need to Prepare
  Recalling Act no. 205 of 2021, the Need to Prepare
  Recalling Act no. 1 of 2021, the Need to Prepare
  Recalling Act no. 1994 of 2021, the Need to Prepare
  Recalling Act 1994 of 2021, the Need to Prepare
  Recalling Act no. 2022 of 2021, the Need to Prepare
  Recalling Act 2022 of 2021, the Need to Prepare
  Avoid weird years Act 11 of 19 and others.
"""
        self.marker.extract_text_matches(self.frbr_uri, text)

        self.assertEqual(
            [
                ExtractedCitation(
                    "Act 25 of 2020", 13, 27, "/akn/za/act/2020/25", 0,
                    '\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act, 1962 (No 58 of 1962)", 72, 97, "/akn/za/act/1962/58", 0,
                    'repare\n  Recalling Income Tax ',
                    ' on the Composition and Operat',
                ),
                ExtractedCitation(
                    "Act 195 of 2021", 152, 167, "/akn/za/act/2021/195", 0,
                    'perationalization\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act no. 205 of 2021", 201, 220, "/akn/za/act/2021/205", 0,
                    'e Need to Prepare\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act no. 1 of 2021", 254, 271, "/akn/za/act/2021/1", 0,
                    'e Need to Prepare\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act no. 1994 of 2021", 305, 325, "/akn/za/act/2021/1994", 0,
                    'e Need to Prepare\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act 1994 of 2021", 359, 375, "/akn/za/act/2021/1994", 0,
                    'e Need to Prepare\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act no. 2022 of 2021", 409, 429, "/akn/za/act/2021/2022", 0,
                    'e Need to Prepare\n  Recalling ',
                    ', the Need to Prepare\n  Recall',
                ),
                ExtractedCitation(
                    "Act 2022 of 2021", 463, 479, "/akn/za/act/2021/2022", 0,
                    'e Need to Prepare\n  Recalling ',
                    ', the Need to Prepare\n  Avoid ',
                ),
            ],
            self.marker.citations,
        )
