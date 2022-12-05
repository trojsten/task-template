import jinja2
import os
import sys
import itertools

from core.utils import dicts, filters, colour as c


class CollectUndefined(jinja2.StrictUndefined):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.missing = []

    def __call__(self, *args, **kwargs):
        undefined = self.undefined_cls(*args, **kwargs)
        self.missing.append(undefined._undefined_name)
        return undefined

    def assert_no_missing(self):
        if len(self.missing) > 0:
            raise MissingVariablesError(self.missing)


class MissingVariablesError(Exception):
    def __init__(self, missing, *args):
        super().__init__(*args)
        self.missing = missing

    def __str__(self):
        return f"Missing variables: {self.missing}"


# Create a custom LaTeX Jinja2 environment, including filters
def environment(directory):
    env = jinja2.Environment(
        block_start_string='(@',
        block_end_string='@)',
        variable_start_string='(*',
        variable_end_string='*)',
        comment_start_string='(#',
        comment_end_string='#)',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        undefined=jinja2.StrictUndefined,
        loader=jinja2.FileSystemLoader(directory),
    )

    env.filters |= {
        'roman': filters.roman,
        'format_list': filters.render_list,
        'isotex': filters.isotex,
        'plural': filters.plural,
    }

    env.globals |= {
        'checkdigit': filters.check_digit,
        'plural': filters.plural,
        'textbf': filters.textbf,
    }

    return env


def print_template(root, template, context, output_directory=None, new_name=None):
    """ Print a Jinja2 template with provided context """
    template_path = f'{root}/{template}'
    output_path = sys.stdout if output_directory is None else open(os.path.join(output_directory, template if new_name is None else new_name), 'w')
    try:
        print(f"Rendering template {c.path(template_path)} to {c.path(output_path.name)}")
        print(
            environment(root).get_template(template).render(context),
            file=output_path,
        )
    except jinja2.exceptions.TemplateNotFound as e:
        print(f"{c.err('Template not found')}: {c.path(template_path)}, {c.err('aborting')}")
        sys.exit(41)
    except jinja2.exceptions.UndefinedError as e:
        print(f"Missing required variable from context in {c.path(template)}: {c.err(e)}")
        sys.exit(43)
