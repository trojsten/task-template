import pprint
import argparse
import argparsedirs
from pathlib import Path

from core.utilities import colour as c, jinja, crawler


def empty_if_none(string):
    return '' if string is None else string


class BaseBuilder():
    module = None

    def __init__(self):
        self.create_argument_parser()
        self.args = self.parser.parse_args()

        self.launch_directory = Path(self.args.launch)
        self.template_root = Path(self.args.template_root)
        self.output_directory = Path(self.args.output) if self.args.output else None
        self.create_context()

    def create_argument_parser(self):
        self.parser = argparse.ArgumentParser(description="Prepare a DGS input dataset from repository")
        self.parser.add_argument('launch', action=argparsedirs.ReadableDir)
        self.parser.add_argument('template_root', action=argparsedirs.ReadableDir)
        self.parser.add_argument('-o', '--output', action=argparsedirs.WriteableDir)
        self.parser.add_argument('-d', '--debug', action='store_true')
        self.parser.add_argument('-t', '--tree', action='store_true')
        return self.parser

    def create_context(self):
        self.context = self.root_context_class(self.launch_directory, *self.id())

    def full_name(self):
        return '/'.join(map(str, self.id()))

    def full_path(self):
        return Path(self.launch_directory, *self.path())

    def id(self):
        raise NotImplementedError("Child classes of BaseBuilder must implement `id`")

    def path(self):
        raise NotImplementedError("Child classes of BaseBuilder must implement `path`")

    def print_debug_info(self) -> None:
        """ Prints debug info """
        print(c.act("Content templates:"))
        pprint.pprint(self.templates)

        print(c.act("Context:"))
        self.context.print()

    def print_build_info(self) -> None:
        """ Prints build info """
        print(f"{c.act('Invoking')} {c.name(self.module)} {c.act('template builder on')} {c.name(self.target)} {c.path(self.full_path())}")

    def print_dir_info(self):
        """ Prints directory info """
        print(f"{c.act('Directory structure:')}")
        crawler.Crawler(Path(self.launch_directory, *self.path())).print_path()

    def build(self):
        self.print_build_info()

        if self.args.debug:
            self.print_debug_info()

        if self.args.tree:
            self.print_dir_info()

        for template in self.templates:
            jinja.print_template(self.template_root, template, self.context.data, self.output_directory)

        if self.args.debug:
            print(f"{c.ok('Template builder on')} {c.name(self.target)} {c.path(self.full_name())} {c.ok('successful')}")
