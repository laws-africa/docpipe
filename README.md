# docpipe

A simple document pipeline mechanism that makes it easier to process and clean up Word and other document types.

# Other dependencies

This has some other non-Python dependencies for certain functionality:

* soffice (open office) for handling DOC and DOCX files
* pdftotext (poppler-utils) for extracting text from PDFs

# Local development

1. Clone this repo
2. Setup a virtual environment
3. Install dependencies: `pip install -e '.[test]'`
4. Run tests: `nosetests`

# License

Copyright 2022 Laws.Africa.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
