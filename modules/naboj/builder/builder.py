import abc
import sys
from pathlib import Path

sys.path.append('.')

from core.builder import builder
import core.builder.jinja as jinja


class BuilderNaboj(builder.BaseBuilder, metaclass=abc.ABCMeta):
    module = 'naboj'
    i18n_templates: [str] = []

    def create_argument_parser(self):
        super().create_argument_parser()
        self.parser.add_argument('competition', choices=['phys', 'math', 'chem', 'junior', 'test'])
        self.parser.add_argument('volume', type=int)

    def build(self):
        super().build()
        for template in self.i18n_templates:
            jinja.print_template(
                Path(self.launch_directory, *self.path()), template, self.context.data,
                outdir=self.output_directory,
                new_name=Path(template).with_suffix('.tex'),
            )
