from unittest import TestCase

from docpipe.html import TextToHtmlText, ParseHtml, SerialiseHtml, StripWhitespace, SplitPOnBr
from docpipe.pipeline import PipelineContext


class HtmlTestCase(TestCase):
    maxDiff = None

    def run_html_stage(self, html_text, stage):
        context = PipelineContext(pipeline=None)
        context.html_text = html_text
        # parse html
        ParseHtml()(context)
        stage(context)
        SerialiseHtml()(context)
        return context.html_text

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

    def test_strip_whitespace(self):
        self.assertMultiLineEqual(
            """<div>
<h1>text <sup>a </sup></h1>
<p>foo</p>
<p><b>bold</b></p>
</div>""",
            self.run_html_stage("""
<div>
<h1> text <sup>a </sup></h1>
<p> foo  </p>
<p> <b>bold</b>  </p>
</div>
""", StripWhitespace()).strip())

    def test_split_p_on_br(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>2. </b>(1) A judge or magistrate in chambers may, on application in the prescribed</p>
<p>manner by a party to a marriage (hereinafter called the applicant) or by any other</p>
<p>person who has a material interest in the matter on behalf of the applicant, grant</p>
<p>an interdict against the other party to the marriage (hereinafter called the</p>
<p>respondent) enjoining the respondent—</p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>2. </b>(1) A judge or magistrate in chambers may, on application in the prescribed<br>manner by a party to a marriage (hereinafter called the applicant) or by any other<br>person who has a material interest in the matter on behalf of the applicant, grant<br>an interdict against the other party to the marriage (hereinafter called the<br>respondent) enjoining the respondent—</p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>[PCh1]</b><b>CHAPTER 1</b></p>
<p><b>THE INTERPRETATION OF LAWS ACT</b></p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>[PCh1]</b><b>CHAPTER 1<br>THE INTERPRETATION OF LAWS ACT</b></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))
