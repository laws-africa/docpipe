# flake8: noqa
from unittest import TestCase

import lxml.html
from lxml import etree
from cobalt import FrbrUri

from docpipe.citations import AchprResolutionMatcher
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
                    None
                ),
                ExtractedCitation(
                    "ACHPR/Res.79 (XXXVIII) 05",
                    16,
                    41,
                    "/akn/aa-au/statement/resolution/achpr/2005/79",
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
                    None
                ),
                ExtractedCitation(
                    "ACHPR/Res.79 (XXXVIII) 05",
                    16,
                    41,
                    "/akn/aa-au/statement/resolution/achpr/2005/79",
                    None
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
                ),
                ExtractedCitation(
                    "ACHPR/Res.79 (XXXVIII) 05",
                    108,
                    133,
                    "/akn/aa-au/statement/resolution/achpr/2005/79",
                    0,
                ),
            ],
            self.marker.citations,
        )
