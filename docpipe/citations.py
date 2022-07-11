import re

from .matchers import CitationMatcher


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
