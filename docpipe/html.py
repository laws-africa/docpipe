import re
import math

from lxml import html
from lxml.html.clean import Cleaner
import cssutils

from .pipeline import Stage, Pipeline
from .xmlutils import unwrap_element, merge_adjacent


class TextToHtmlText(Stage):
    """ Transform plain text into HTML-ready text.

    Reads: context.text
    Writes: context.html_text
    """
    def __call__(self, context):
        root = html.Element("div")

        for line in context.text.splitlines():
            p = html.Element("p")
            p.text = line
            root.append(p)

        context.html_text = html.tostring(root, pretty_print=True, encoding='unicode')


class ParseHtml(Stage):
    """ Parse html with lxml.html and ensure that context.html is a container and not a single element (eg. 'p').

    Fixing the root is necessary usually during tests when we might be passing in plain text or just a <p> tag.

    Reads: context.html_text
    Writes: context.html
    """
    def __call__(self, context):
        context.html = html.fromstring(context.html_text)
        self.ensure_container_root(context)

    def ensure_container_root(self, context):
        if context.html.tag not in ['div', 'body', 'html']:
            # lxml.html.fromstring ensures there's always html -> ...
            context.html = context.html.getroottree().getroot()


class NukeHiddenText(Stage):
    """ Identifies hidden spans like [PCh1s2] before section 2 and deletes them.

    Reads: context.html
    Writes: context.html
    """

    def __call__(self, context):
        for hidden_span in context.html.xpath('.//span[@style="display: none"]'):
            hidden_span.getparent().remove(hidden_span)


class SerialiseHtml(Stage):
    """ Serialise html into text.

    Reads: context.html
    Writes: context.html_text
    """
    def __call__(self, context):
        context.html_text = html.tostring(context.html, encoding='unicode')


class CleanHtml(Stage):
    """ Clean dangerous HTML.

    Reads: context.html
    Writes: context.html
    """
    cleaner = Cleaner(
        style=True,
        inline_style=False,
        safe_attrs=list(Cleaner.safe_attrs) + ['style']
    )

    def __call__(self, context):
        context.html = self.cleaner.clean_html(context.html)


class ExtractBody(Stage):
    """ Make html only the body element.

    Reads: context.html
    Writes: context.html
    """
    def __call__(self, context):
        body = context.html.find('body')
        if body is not None:
            context.html = body


class BodyToDiv(Stage):
    """ Change the top-level body element to a div.

    Reads: context.html
    Writes: context.html
    """
    def __call__(self, context):
        context.html.tag = 'div'


class NormaliseHtmlTextWhitespace(Stage):
    """ Strip and normalise whitespace in HTML text.

    Reads: context.html_text
    Writes: context.html_text
    """
    def __call__(self, context):
        # &nbsp; to space
        context.html_text = context.html_text.replace('&nbsp;', ' ')

        # tabs to spaces, multiple spaces and newlines to one
        context.html_text = re.sub(r'[\r\n\s]+', ' ', context.html_text)


class MergeUl(Stage):
    """ Merge consecutive UL lists together

    Reads: context.html
    Writes: context.html
    """
    def __call__(self, context):
        for ul in context.html.xpath('.//ul'):
            prev = ul.getprevious()
            if prev is not None and prev.tag == 'ul':
                # merge this ul into the previous one
                for kid in ul:
                    prev.append(kid)
                ul.getparent().remove(ul)


class CleanTables(Stage):
    """ Clean tables in the html as follows:

    - strip any width attributes on the table
    - normalize existing width attributes on table cells from absolutes into percentages
    - remove any padding styles on table cells
    - remove cell border styles that set a border to none

    Reads: context.html
    Writes: context.html
    """
    def __call__(self, context):
        for table in context.html.xpath('.//table'):
            # strip table width
            if table.attrib.get('width'):
                table.attrib.pop('width')

            if table.attrib.get('cellpadding'):
                table.attrib.pop('cellpadding')

            if table.attrib.get('cellspacing'):
                table.attrib.pop('cellspacing')

            for row in table.xpath('.//tr'):
                total_row_width = sum([int(c.attrib['width'].replace('%', '')) for c in row if c.attrib.get('width')])
                for cell in row:
                    style = cssutils.parseStyle(cell.attrib.get('style'))

                    # normalize cell width to % based on total row width
                    width = cell.attrib.get('width')
                    if width:
                        width = int(width.replace('%', ''))
                        w_pct = math.floor(width / total_row_width * 100)
                        style['width'] = f'{w_pct}%'
                        cell.attrib['style'] = style.cssText.replace('\n', ' ')
                        cell.attrib.pop('width')

                    if style and cell.attrib.get('style'):
                        # remove any padding
                        style.removeProperty('padding')
                        style.removeProperty('padding-top')
                        style.removeProperty('padding-bottom')
                        style.removeProperty('padding-left')
                        style.removeProperty('padding-right')

                        # remove cell border styles that set any border to none
                        if style.getPropertyValue('border') == 'none':
                            style.removeProperty('border')

                        if style.getPropertyValue('border-top') == 'none':
                            style.removeProperty('border-top')

                        if style.getPropertyValue('border-bottom') == 'none':
                            style.removeProperty('border-bottom')

                        if style.getPropertyValue('border-left') == 'none':
                            style.removeProperty('border-left')

                        if style.getPropertyValue('border-right') == 'none':
                            style.removeProperty('border-right')

                        if style.getCssText():
                            cell.attrib['style'] = style.cssText.replace('\n', ' ')
                        else:
                            cell.attrib.pop('style')

                    if cell.attrib.get('height'):
                        cell.attrib.pop('height')


class StripWhitespace(Stage):
    """ Strip whitespace at the start and end of major content tags.
    Doesn't strip whitespace within tags at the start or end, as it could be significant.

    Reads: context.html
    Writes: context.html
    """
    whitespace = '  '
    tags = "p h1 h2 h3 h4 h5 li td th".split()

    def __call__(self, context):
        xpath = "|".join(f'.//{x}' for x in self.tags)
        for elem in context.html.xpath(xpath):
            # strip start
            if elem.text:
                elem.text = elem.text.lstrip(self.whitespace)

            # strip end
            kids = list(elem)
            if kids:
                if kids[-1].tail:
                    kids[-1].tail = kids[-1].tail.rstrip(self.whitespace)
            elif elem.text:
                elem.text = elem.text.rstrip(self.whitespace)


class MergeAdjacentInlines(Stage):
    """ Merge matching tags that are directly adjacent.

    eg::

        <b>text</b><b>more</b>

    becomes::

        <b>textmore</b>

    Reads: context.html
    Writes: context.html
    """
    tags = 'b i sup sub'.split()

    def __call__(self, context):
        xpath = '|'.join(f'.//{x}' for x in self.tags)

        for e in context.html.xpath(xpath):
            nxt = e.getnext()
            while nxt is not None and nxt.tag == e.tag and not e.tail:
                merge_adjacent(e, nxt)
                nxt = e.getnext()


class RemoveEmptyInlines(Stage):
    """ Remove inline elements that are empty (no children, no text or just whitespace).

    Reads: context.html
    Writes: context.html
    """
    tags = 'a b i sup sub'.split()

    def __call__(self, context):
        xpath = '|'.join(f'.//{n}' for n in self.tags)

        for node in context.html.xpath(xpath):
            # node has no children, and either no text or just whitespace
            # in the case of whitespace, it is preserved
            if not list(node) and (not node.text or not node.text.strip()):
                unwrap_element(node)


class SplitPOnBr(Stage):
    """ Split p tags that contain <br>s.

    eg: <p>Some text.<br><br>Broken onto two lines.</p>
    ->  <p>Some text.</p>
        <p>Broken onto two lines.</p>

    Reads: context.html
    Writes: context.html
    """

    def __call__(self, context):
        for br in reversed(list(context.html.xpath('.//p//br'))):
            # everything after the br moves into a new p tag
            p = context.html.makeelement('p')
            # reverse order of elements to be created afresh before hitting the ancestor p
            # e.g. ['i', 'b'] in the case of <p><b><i>Text<br>text</i></b></p>
            ancestor_tags = []
            elements = []

            # parent should be the original p, but we want to track everything on the way up too
            parent = br.getparent()
            while parent.tag != 'p':
                ancestor_tags.append(parent.tag)
                parent = parent.getparent()

            for elem_tag in ancestor_tags:
                elem = context.html.makeelement(elem_tag)
                elements.append(elem)
            elements.append(p)
            # now we have e.g. [<i>, <b>, <p>]
            # the lowest-down, <i> in the example but at minimum <p>,
            # gets the text
            for i, elem in enumerate(elements):
                if i == 0:
                    elem.text = br.tail

                    # when the immediate sibling of br is a tag
                    # e.g. <p>Text<br><i>italics</i></p>
                    # -- make sure <italics> ends up in the right place
                    sibling = br.getnext()
                    while sibling is not None:
                        elem.append(sibling)
                        sibling = sibling.getnext()

                    # when the br falls inside an intervening tag, e.g.
                    # <p>Text 1 <b>bold 1<br>bold 2</b> text 2</p>
                    # make sure ' text 2' ends up in the right place.
                    #
                    # This is the case when i > 0 and there are intervening tags. The tail of the main p is handled
                    # at the end of the function.
                    if i < len(elements) - 1:
                        elem.tail = br.getparent().tail
                        br.getparent().tail = None

                    continue

                # for all but the first / only element, append the lower-down one
                # (if there's only one, <p>, nothing needs to be appended)
                elem.append(elements[i - 1])

            # e.g. <p><b>Text<br>text</b> <i>italics</i></p>
            # -- make sure ' plain <i>italics</i>' goes after '<b>text<b>'
            sibling = br.getparent().getnext()
            if sibling is not None and len(ancestor_tags):
                p.append(sibling)

            # parent is the original p
            # move tail text onto the new p
            p.tail = parent.tail
            parent.tail = None
            parent.addnext(p)
            br.getparent().remove(br)


class RemoveEmptyParagraphs(Stage):
    """ Remove p tags that have no content except whitespace.

    Reads: context.html
    Writes: context.html
    """

    # tags that indicate a non-empty p, even if there is no text
    content_tags = ['img']

    def __call__(self, context):
        xpath = '|'.join(f'.//{x}' for x in self.content_tags)

        for p in context.html.xpath('.//p'):
            text = (''.join(p.xpath('.//text()'))).strip()

            if not text and not p.xpath(xpath):
                parent = p.getparent()
                parent.remove(p)
                p = parent

                # remove empty ancestors
                while p is not None:
                    if any(x is not None for x in p.iterchildren()) or p.getparent() is None:
                        break
                    parent = p.getparent()
                    parent.remove(p)
                    p = parent


parse_and_clean = Pipeline([
    NormaliseHtmlTextWhitespace(),
    ParseHtml(),
    NukeHiddenText(),
    ExtractBody(),
    CleanHtml(),
    MergeUl(),
    CleanTables(),
    MergeAdjacentInlines(),
    RemoveEmptyInlines(),
    StripWhitespace(),
], name="Parse and clean", description="Parse HTML and do basic cleaning.")
