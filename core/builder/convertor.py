import dotmap
import fileinput
import re
import subprocess
import sys
import tempfile

sys.path.append('.')

from core.utils import colour as c


class Convertor():
    languages = {
        'sk':   dict(name='slovak'      , locale='sk-SK', quotes=('„', '“'), figure='Obrázok'),
        'cs':   dict(name='czech'       , locale='cs-CZ', quotes=('„', '“'), figure='Obrázek'),
        'en':   dict(name='english'     , locale='en-US', quotes=('“', '”'), figure='Picture'),
        'ru':   dict(name='russian'     , locale='ru-RU', quotes=('«', '»')),
        'pl':   dict(name='polish'      , locale='pl-PL', quotes=('„', '“')),
        'hu':   dict(name='hungarian'   , locale='hu-HU', quotes=('„', '“')),
        'fr':   dict(name='french'      , locale='fr-FR', quotes=('«\u202F', '\u202F»')),
        'es':   dict(name='spanish'     , locale='es-ES', quotes=('«', '»')),
        'qq':   dict(name='test'        , locale='sk-SK', quotes=('(', ')')),
    }

    post_regexes = {
        'latex': [
            (r"``", r"“"),
            (r"''", r'”'),
            (r"\\includegraphics\[(.*)\]{(.*)\.(svg|gp)}", r"\\insertPicture[\g<1>]{\g<2>.pdf}"),
            (r"\\includegraphics\[(.*)\]{(.*)\.(png|jpg|pdf)}", r"\\insertPicture[\g<1>]{\g<2>.\g<3>}"),
            (r"^\\caption{}(\\label{.*})?\n", ""), # Remove empty labels and captions
        ],
        'html': [
            (
                r'<img src="(.*)" (.*)id="(.*)" style="height:([0-9.]*)mm" (.*)>',
                r'<img src="\g<1>" \g<2>id="\g<3>" style="max-width: 100%; max-height: calc(1.7 * \g<4>mm); margin: auto; display: block;" \g<5>>',
            ),
            (
                r'<figcaption>Figure (\d*): (.*)</figcaption>',
                r'<figcaption style="text-align: center;">Obrázok \g<1>: <span style="font-style: italic;">\g<2></span></figcaption>',
            ),
        ],
    }

    """ DeGeŠ hacks for shorter aligned math """
    math_regexes = [
        (r'^(\s*)\$\${$', r'\g<1>$$\n\\begin{aligned}'),
        (r'^(\s*)}\$\$', r'\g<1>\\end{aligned}\n$$'),
    ]

    replace_regexes = {
        'latex': [
            (r"^@E\s*(.*)$", r"\\errorMessage{\g<1>}"),
            (r"^@L\s*(.*)$", r"\g<1>"),
            (r"^@TODO\s*(.*)$", r"\\todoMessage{\g<1>}"),
        ],
        'html': [
            (r"^@E\s*(.*)$", r"Error: \g<1>"),
            (r"^@H\s*(.*)$", r"\g<1>"),
            (
                r"^!\[(?P<caption>.*)\]\((?P<filename>.*)\.(?P<extension>jpg|png|svg)\){(?P<extras>.*)}$",
                r"![\g<caption>](obrazky/\g<filename>.\g<extension>){\g<extras>}",
            ),
            (
                r"^!\[(?P<caption>.*)\]\((?P<filename>.*)\.(?P<extension>gp)\){(?P<extras>.*)}$",
                r"![\g<caption>](obrazky/\g<filename>.png){\g<extras>}",
            ),
        ],
    }

    @staticmethod
    def compile_regexes(regexes):
        return [(re.compile(regex), repl) for (regex, repl) in regexes]

    def __init__(self, format, locale_code, infile, outfile):
        self.locale_code = locale_code
        self.locale = dotmap.DotMap(self.languages[locale_code], _dynamic=False)
        self.format = format
        self.infile = infile
        self.outfile = outfile

        (self.quote_open, self.quote_close) = self.locale.quotes

        quotes_regexes = [
            (r'"(_)', self.quote_close + r'\g<1>'),
            (r'"(\b)', self.quote_open + r'\g<1>'),
            (r'(\b)"', r'\g<1>' + self.quote_close),
            (r'(\S)"', r'\g<1>' + self.quote_close),
            (r'"(\S)', self.quote_open + r'\g<1>'),
        ]

        self.quotes_regexes = self.compile_regexes(quotes_regexes)
        self.math_regexes = self.compile_regexes(self.math_regexes)
        self.replace_regexes = self.compile_regexes(self.replace_regexes[self.format])
        self.post_regexes = self.compile_regexes(self.post_regexes[self.format])

    def run(self):
        try:
            #fm, tm = frontmatter.parse(self.infile.read())
            #self.infile.seek(0)
            self.file = self.file_operation(self.preprocess)(self.infile)
            self.file = self.call_pandoc()
            self.file = self.file_operation(self.postprocess)(self.file)
            self.write()
        except IOError as e:
            print(f"{c.path(__file__)}: Could not create a temporary file: {e}")
        except AssertionError as e:
            print(f"{c.path(__file__)}: Calling pandoc failed")
        except Exception as e:
            print(f"Unexpected exception occurred:")
            raise e
            return -1
        else:
            return 0

    @staticmethod
    def file_operation(function):
        def inner(f):
            out = tempfile.SpooledTemporaryFile(mode='w+')

            for line in f:
                out.write(function(line))

            out.seek(0)
            return out

        return inner

    def write(self):
        for line in self.file:
            self.outfile.write(line)
        self.file.seek(0)

    def preprocess(self, line):
        if self.filter_tags(line):
            return self.chain_process(line, [self.replace_regexes, self.quotes_regexes, self.math_regexes])
        else:
            return ""

    @staticmethod
    def process_line(line, regexes):
        for regex, replacement in regexes:
            line = regex.sub(replacement, line)
        return line

    @staticmethod
    def chain_process(line, regex_sets):
        for regex_set in regex_sets:
            line = Convertor.process_line(line, regex_set)
        return line

    def postprocess(self, line):
        return self.chain_process(line, [self.post_regexes])

    def filter_tags(self, line):
        """
            Filter by customs tags:
            -   remove lines beginning with '%'
            -   remove lines beginning with '@H' if not converting for HTML
            -   remove lines beginning with '@L' if not converting for LaTeX
        """
        if re.match(r"^%", line) or \
            (re.match(r"^@H", line) and self.format != 'html') or \
            (re.match(r"^@L", line) and self.format != 'latex'):
            return ""
        return line

    def replace_tags(self, line):
        """
            Replace custom tags and pictures
        """
        for regex, replacement in self.replace_regexes:
            line = regex.sub(replacement, line)

        return line

    def call_pandoc(self):
        out = tempfile.SpooledTemporaryFile(mode='w+')

        self.file.seek(0)
        subprocess.run([
            "pandoc",
            "--mathjax",
            "--from", "markdown+smart",
            "--pdf-engine", "xelatex",
            "--to", self.format,
            "--filter", "pandoc-crossref", "-M", "'crossrefYaml=core/i18n/{self.language}/crossref.yaml'",
#            "--filter", "pandoc-fignos", "-M", f'fignos-caption-name="{self.locale.figure}"',
            "--filter", "pandoc-eqnos",
            "--metadata", f"lang={self.languages[self.locale_code]['locale']}",
        ], stdin=self.file, stdout=out)

        out.seek(0)
        return out
