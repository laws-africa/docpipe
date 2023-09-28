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

    def test_split_p_on_br_deep_mixed(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>2. </b>text 1 <b>bold 1</b></p>
<p><b>bold 2</b> text 2</p>
<p>text <i>3</i></p>
<p>text 4</p>
<p>text 5</p>
</div>""",
            self.run_html_stage("""
<div>
<p>
    <b>2. </b>text 1 <b>bold 1<br>
    bold 2</b> text 2<br>
    text <i>3</i><br>
    text 4<br>
    text 5</p>
</div>
""".replace('\n    ', ''), SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_bold(self):
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

    def test_split_p_on_br_nested_mixed(self):
        self.assertMultiLineEqual(
            """<div>
<p>text 1 <b>bold 1 <i>i 1</i></b></p>
<p><b>bold 2</b> text 2</p>
</div>""",
            self.run_html_stage("""
<div>
<p>text 1 <b>bold 1 <i>i 1</i><br>bold 2</b> text 2</p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_mixed(self):
        self.assertMultiLineEqual(
            """<div>
<p>text 1 <b>bold 1</b></p>
<p><b>bold 2</b> text 2 <i>italics 1</i></p>
<p><i>italics 2</i> text 3 <b>bold 3</b></p>
</div>""",
            self.run_html_stage("""
<div>
<p>text 1 <b>bold 1<br>bold 2</b> text 2 <i>italics 1<br>italics 2</i> text 3 <b>bold 3</b></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested_bold(self):
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

    def test_split_p_on_br_nested_bold_simple(self):
        self.assertMultiLineEqual(
            """<div>
<p>text 1 <b>bold 1</b></p>
<p><b>bold 2</b> text 2</p>
</div>""",
            self.run_html_stage("""
<div>
<p>text 1 <b>bold 1<br>bold 2</b> text 2</p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested_italics(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>[PCh1]</b><i>CHAPTER 1</i></p>
<p><i>THE INTERPRETATION OF LAWS ACT</i></p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>[PCh1]</b><i>CHAPTER 1<br>THE INTERPRETATION OF LAWS ACT</i></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested_bold_italics(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>[PCh1]</b><b><i>CHAPTER 1</i></b></p>
<p><b><i>THE INTERPRETATION OF LAWS ACT</i></b></p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>[PCh1]</b><b><i>CHAPTER 1<br>THE INTERPRETATION OF LAWS ACT</i></b></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested_italics_bold(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>[PCh1]</b><i><b>CHAPTER 1</b></i></p>
<p><i><b>THE INTERPRETATION OF LAWS ACT</b></i></p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>[PCh1]</b><i><b>CHAPTER 1<br>THE INTERPRETATION OF LAWS ACT</b></i></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested_bold_multi(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>[PCh1]</b><b>CHAPTER 1</b></p>
<p><b>THE INTERPRETATION OF</b></p>
<p><b>LAWS</b></p>
<p><b>ACT</b></p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>[PCh1]</b><b>CHAPTER 1<br>THE INTERPRETATION OF<br>LAWS<br>ACT</b></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))

    def test_split_p_on_br_nested_italics_bold_multi(self):
        self.assertMultiLineEqual(
            """<div>
<p><b>[PCh1]</b><i><b>CHAPTER 1</b></i></p>
<p><i><b>THE INTERPRETATION OF</b></i></p>
<p><i><b>LAWS</b></i></p>
<p><i><b>ACT</b></i></p>
</div>""",
            self.run_html_stage("""
<div>
<p><b>[PCh1]</b><i><b>CHAPTER 1<br>THE INTERPRETATION OF<br>LAWS<br>ACT</b></i></p>
</div>
""", SplitPOnBr()).strip().replace('</p><p>', '</p>\n<p>'))
