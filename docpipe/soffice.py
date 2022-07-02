import subprocess
from os import listdir
from os.path import splitext, join, isfile, basename
from shutil import copyfileobj
from tempfile import TemporaryDirectory, NamedTemporaryFile
import logging
import mimetypes

from docpipe.pipeline import Stage, Attachment


SOFFICE_CMD = 'soffice'
log = logging.getLogger(__name__)


class DocToHtml(Stage):
    """ Converts a document file into HTML using soffice.

    Reads: source_file
    Writes: context.html_text, context.attachments
    """
    def __call__(self, context):
        suffix = splitext(context.source_file.name)[1].lstrip('.')
        primary, files = soffice_convert(context.source_file, suffix, 'html')
        try:
            context.html_text = primary.read().decode('utf-8', errors='replace')
        finally:
            primary.close()

        context.attachments = [
            Attachment(name, mimetypes.guess_type(name)[0], f)
            for name, f in files.items()
        ]


def soffice_convert(infile, insuffix, outsuffix):
    """ Convert a doc (.doc or .docx) file to a PDF file (or .docx for .doc).

    :param insuffix: suffix of the input file data, such as 'docx' or 'pdf'
    :param outsuffix: suffix of the desired output format, such as 'html' or 'pdf'
    :return: a tuple `(primary, files)`, where `primary` is an open file handle for the primary output file, and `files`
    is a dict from filename to open file handles for other files produced during the conversion (eg. images).
    """
    with TemporaryDirectory() as tmpdir:
        # write the source file into the temp directory
        with NamedTemporaryFile(suffix=f".{insuffix}", dir=tmpdir) as f:
            copyfileobj(infile, f)
            f.flush()

            outf_name = splitext(f.name)[0] + f".{outsuffix}"
            soffice(["--convert-to", outsuffix, "--outdir", tmpdir, f.name])

        # now open and return the generated file and all other files in the directory, which include
        # images extracted from the document.
        # the temporary directory will be deleted, but the file handles will still be valid
        files = {
            fname: open(join(tmpdir, fname), 'rb')
            for fname in listdir(tmpdir) if isfile(join(tmpdir, fname))
        }

        return files[basename(outf_name)], files


def soffice(args):
    args = [SOFFICE_CMD, "--headless"] + args

    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True,
                                encoding='utf-8', errors='backslashreplace')
        log.info(f"Output from soffice: {result.stdout}")
    except subprocess.CalledProcessError as e:
        log.error(f"Error calling soffice. Output: \n{e.output}", exc_info=e)
        raise
