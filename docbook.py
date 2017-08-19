import os
import re
import glob
import fnmatch

import markdown
import argparse

import time


class Docbook:
    TEMPLATE = '''
    ${body}
'''

    def __init__(self, src_pattern, out_pattern, src_exclude=None,
                 template_file=None, properties_file=None,
                 src_encoding='utf-8', out_encoding='utf-8', force_unix_path_style=True):
        """
        Init docbook engine
        :param src_pattern: source file or glob pattern,
        :param out_pattern: output file or filename with {n}-placeholders
        """
        self.src_path_pattern = src_pattern
        self.out_path_template = out_pattern
        self.src_exclude = src_exclude

        self.src_encoding = src_encoding
        self.out_encoding = out_encoding
        self.force_unix_path_style = force_unix_path_style

        self.template = self.load_template(template_file)
        self.properties = self.load_properties(properties_file)

        self.src_translate_pattern = None
        self.__parse_src_pattern()

    def list_source_files(self):
        """
        :return: List of filenames according to source pattern
        """
        paths = glob.glob(self.src_path_pattern)
        exclude_paths = []
        if self.src_exclude:
            exclude_paths = glob.glob(self.src_exclude)

        if self.force_unix_path_style:
            paths = [path.replace('\\', '/') for path in paths]
            exclude_paths = [path.replace('\\', '/') for path in exclude_paths]

        if exclude_paths:
            paths = [path for path in paths if path not in exclude_paths]

        return paths

    def __parse_src_pattern(self):
        """
        Search for glob symbols (? and *) in the source pattern and translate them to regex
        """
        if '*' in self.src_path_pattern or '?' in self.src_path_pattern:
            src_translate_pattern = fnmatch.translate(self.src_path_pattern)
            src_translate_pattern = src_translate_pattern.replace('.*', '(.*)')
            src_translate_pattern = src_translate_pattern.replace('.?', '(.?)')
            self.src_translate_pattern = src_translate_pattern

    def translate_file_path(self, src_path):
        """
        Translate source filename to output filename using source and output patterns.
        E.g.:
            source pattern    | output pattern       | source filename       | output filename
            ---------------------------------------------------------------------------------------------
            article-abc.md    | article-abc.html     | article-abc.md        | article-abc.html
            in/article-abc.md | out/article-abc.html | in/article-abc.md     | out/article-abc.html
            in/*.md           | out/{1}.html         | in/article-abc.md     | out/article-abc.html
            in/*/doc.md       | out/{1}.html         | in/article-abc/doc.md | out/article-abc.html
            in/*/doc.md       | out/{1}/index.html   | in/article-abc/doc.md | out/article-abc/index.html
            in/*/*.md         | out/{2}-{1}.html     | in/article/abc.md     | out/abc-article.html

        """
        if self.src_translate_pattern:
            m = re.match(self.src_translate_pattern, src_path)
            if m and m.groups():
                out_path = self.out_path_template
                for index, group in enumerate(m.groups()):
                    out_path = out_path.replace('{%d}' % (index + 1), group)
                return out_path
            else:
                print('Filename translation error')
                raise Exception()
        else:
            return self.out_path_template

    def load_file_as_string(self, filename):
        """
        Load file using docbook's encoding
        """
        with open(filename, 'r', encoding=self.src_encoding) as file:
            return file.read()

    def load_template(self, template_file):
        if template_file:
            return self.load_file_as_string(template_file)
        else:
            print('Using default template')
            return Docbook.TEMPLATE

    def load_properties(self, properties_file):
        """
        Load properties from file
        """
        props = {}
        if not properties_file or not os.path.isfile(properties_file):
            return props

        # print('Loading prperties: ' + properties_file)

        with open(properties_file, 'r', encoding=self.src_encoding) as f:
            for line in f:
                line = line.strip()
                if '=' not in line or line.startswith('#'):
                    continue
                k, v = line.split("=", 1)
                props[k] = v
        return props

    def merge_properties(self, properties_override):
        out = self.properties.copy()
        out.update(properties_override)
        return out

    def load_doc(self, doc_dir, doc_file):
        # print('Loading doc: %s/%s' % (doc_dir, doc_file))
        doc_text = self.load_file_as_string(doc_dir + '/' + doc_file)

        file_includes = re.findall('\$F\{([-.\w]+)\}', doc_text)
        if file_includes:
            for file_include in file_includes:
                # print('Loading include: ' + file_include)
                include_text = self.load_file_as_string(doc_dir + '/' + file_include)
                doc_text = doc_text.replace('$F{%s}' % file_include, include_text)

        return markdown.markdown(doc_text, extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.attr_list',
            'markdown.extensions.fenced_code'
        ])

    def render_template(self, props):
        template = self.template
        for key, value in props.items():
            template = template.replace('${%s}' % key, value)
        return template

    def write_file(self, path, content):
        # print('Writing doc: %s' % path)
        if os.path.isfile(path) and time.time() - os.path.getmtime(path) < 5:
            print('Trying to overwrite just modified file')
            raise Exception()

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding=self.out_encoding) as file:
            file.write(content)

    def process(self):
        sources = self.list_source_files()
        for source_path in sources:
            output_path = self.translate_file_path(source_path)
            print('%s -> %s' % (source_path, output_path))

            src_dir = os.path.dirname(source_path)
            src_filename = os.path.basename(source_path)

            doc_text = self.load_doc(src_dir, src_filename)

            doc_props_filename = os.path.splitext(src_filename)[0] + '.properties'

            doc_props = self.load_properties(src_dir + '/' + doc_props_filename)
            doc_props = self.merge_properties(doc_props)
            doc_props['body'] = doc_text
            doc_html = self.render_template(doc_props)
            self.write_file(output_path, doc_html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.description = '''Generate html book or static site from Markdown files.
Use-cases:
- generate single html from a .md file
- scan files using glob pattern and generate multiple output files     
'''

    parser.add_argument('--src', help='Source docs', required=True)
    parser.add_argument('--out', help='Output docs', required=True)
    parser.add_argument('--exclude', help='Subset of source files to exclude')
    parser.add_argument('--tpl', help='Template file. Default: docbook-template.html',
                        default='docbook-template.html')
    parser.add_argument('--props', help='Properties file. Default: "docbook.properties"',
                        default='docbook.properties')

    parser.epilog = '''Usage sample:
--src=docbook.md --out=docbook.html
--src=demo/source/page-*.md --out=demo/output/{1}.html --tpl=demo/docbook-template.html --props=demo/docbook.properties
'''

    args = parser.parse_args()

    docbook = Docbook(src_pattern=args.src, out_pattern=args.out, src_exclude=args.exclude,
                      template_file=args.tpl, properties_file=args.props)
    print('Processing')
    docbook.process()
    print('Done')
