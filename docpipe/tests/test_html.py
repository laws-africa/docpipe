from unittest import TestCase

import lxml.html
from lxml import etree

from docpipe.citations import AchprResolutionMatcher
from docpipe.html import TextToHtmlText
from docpipe.matchers import ExtractedCitation
from docpipe.pipeline import PipelineContext


class RefsAchprResolutionMatcherTest(TestCase):
    maxDiff = None

    def test_html_to_text(self):
        context = PipelineContext(pipeline=None)
        context.text = """
one
    two < three
  four & five
"""

        TextToHtmlText()(context)
        self.assertMultiLineEqual(
            """<div>
<p></p>
<p>one</p>
<p>    two &lt; three</p>
<p>  four &amp; five</p>
</div>""",
            context.html_text.strip())
