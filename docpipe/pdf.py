import subprocess


def pdf_to_text(fname, cropbox=None, extras=None):
    """ Extract text from a pdf.
    """
    cmd = ["pdftotext", "-enc", "UTF-8"] + (extras or [])

    if cropbox:
        # left, top, width, height
        cropbox = (str(int(float(i))) for i in cropbox)
        cropbox = list(zip("-x -y -W -H".split(), cropbox))
        # flatten
        cmd += [x for pair in cropbox for x in pair]

    cmd += [fname, '-']
    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout.decode('utf-8')
