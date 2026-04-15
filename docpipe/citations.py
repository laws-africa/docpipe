import re
from typing import Match

from .matchers import CitationMatcher, ExtractedMatch


class AchprResolutionMatcher(CitationMatcher):
    """ Finds references to ACHPR resolutions in documents, of the form:

    ACHPR/Res.227 (LII) 2012
    ACHPR/Res. 437 (EXT.OS/ XXVI1) 2020
    ACHPR/Res.79 (XXXVIII) 05
    """

    pattern_re = re.compile(
        r"""\bACHPR/Res\.?\s*
            (?P<num>\d+)\s*
            \((EXT\.\s*OS\s*/\s*)?[XVILC1]+\)\s*
            (?P<year>\d{2,4})
        """,
        re.X | re.I,
        )
    href_pattern = "/akn/aa-au/statement/resolution/achpr/{year}/{num}"
    html_candidate_xpath = ".//text()[contains(., 'ACHPR') and not(ancestor::a)]"
    xml_candidate_xpath = ".//text()[contains(., 'ACHPR') and not(ancestor::ns:ref)]"

    def href_pattern_args(self, match):
        args = super().href_pattern_args(match)

        # adjust for short years
        year = int(args["year"])
        if year < 100:
            if year > 80:
                year = 1900 + year
            else:
                year = 2000 + year
            args["year"] = str(year)

        return args


class ActNoOfYearMatcher(CitationMatcher):
    """ Finds references to Acts in documents, of the form:
    Act 5 of 2019
    Act No. 3 of 92
    Income Tax Act, 1962 (No 58 of 1962)
    """
    pattern_re = re.compile(
        r"""\bAct,?\s*
            ((19|20)\d{2}\s*)?
            \(?
            (?P<ref>
              ([no\.]*\s*)?
              (?P<num>\d+)\s*
              of\s*
              (?P<year>\d{4})
            )\)?
        """,
        re.X | re.I)
    href_pattern = "/akn/{juri}/act/{year}/{num}"
    html_candidate_xpath = ".//text()[contains(., 'Act') and not(ancestor::a)]"
    xml_candidate_xpath = ".//text()[contains(., 'Act') and not(ancestor::ns:ref)]"

    def href_pattern_args(self, match):
        args = super().href_pattern_args(match)

        # use document's country
        args['juri'] = self.frbr_uri.country

        return args

    def make_extracted_match(self, match: Match) -> ExtractedMatch:
        em = super().make_extracted_match(match)
        # adjust the match so that if we don't have a '(' in the match, then we must exclude any trailing ')`
        if em.text.endswith(')') and '(' not in em.text:
            em.text = em.text[:-1]
            em.end -= 1
        return em


# legacy name for backwards compatibility
ActMatcher = ActNoOfYearMatcher


class ActYearNumberMatcher(ActNoOfYearMatcher):
    """Finds references to Acts of the form:

    - Foo Act, 1999 (Act 123)
    """
    pattern_re = re.compile(r"(?P<year>\d{4})\s*\(\s*(?P<ref>Act\s*(?P<num>\d+)\s*)\)", re.I)

    def make_extracted_match(self, match: Match) -> ExtractedMatch:
        match = super().make_extracted_match(match)
        # adjust the match so that it only covers the "ref" group
        match.text = match.groups["ref"]
        match.start = match.original_match.start("ref")
        match.end = match.original_match.end("ref")
        return match

    def make_href(self, match: ExtractedMatch):
        year = match.groups["year"]
        num = match.groups["num"]
        return f"/akn/gh/act/{year}/{num}"
