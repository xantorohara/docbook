import os
import re
import glob
import fnmatch

import markdown
import argparse

import time


def list_source_files(src_path_pattern, src_exclude):
    """
    :return: List of filenames according to source pattern
    """
    paths = glob.glob(src_path_pattern)
    exclude_paths = []
    if src_exclude:
        exclude_paths = glob.glob(src_exclude)

    paths = [path.replace('\\', '/') for path in paths]
    exclude_paths = [path.replace('\\', '/') for path in exclude_paths]

    if exclude_paths:
        paths = [path for path in paths if path not in exclude_paths]

    return paths


def parse_src_pattern(src_path_pattern):
    """
    Search for glob symbols (? and *) in the source pattern and translate them to regex
    """
    if '*' in src_path_pattern or '?' in src_path_pattern:
        src_translate_pattern = fnmatch.translate(src_path_pattern)
        src_translate_pattern = src_translate_pattern.replace('.*', '(.*)')
        src_translate_pattern = src_translate_pattern.replace('.?', '(.?)')
        return src_translate_pattern
    else:
        return None


def translate_file_path(src_path, src_translate_pattern, out_path_template):
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
    if src_translate_pattern:
        m = re.match(src_translate_pattern, src_path)
        if m and m.groups():
            out_path = out_path_template
            for index, group in enumerate(m.groups()):
                out_path = out_path.replace('{%d}' % (index + 1), group)
            return out_path
        else:
            print('Filename translation error')
            raise Exception()
    else:
        return out_path_template


def load_file_as_string(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def load_properties(properties_file):
    """
    Load properties from file
    """
    props = {}
    if not properties_file or not os.path.isfile(properties_file):
        return props

    # print('Loading properties: ' + properties_file)

    with open(properties_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' not in line or line.startswith("#"):
                continue
            k, v = line.split("=", 1)
            props[k] = v
    return props


def render_template(props, template):
    for key, value in props.items():
        template = template.replace('${%s}' % key, value)
    return template


def write_file(path, content):
    # print('Writing doc: %s' % path)
    if os.path.isfile(path) and time.time() - os.path.getmtime(path) < 5:
        print('Trying to overwrite just modified file')
        raise Exception()

    tmp_dir = os.path.dirname(path)
    tmp_dir = tmp_dir if tmp_dir else '.'
    os.makedirs(tmp_dir, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


def merge_properties(properties, properties_override):
    out = properties.copy()
    out.update(properties_override)
    return out


def load_template(template_file):
    if template_file:
        return load_file_as_string(template_file)
    else:
        print('Using default template')
        return '''${body}'''


def load_doc(doc_dir, doc_file):
    doc_dir = doc_dir if doc_dir else '.'
    doc_text = load_file_as_string(doc_dir + '/' + doc_file)

    file_includes = re.findall('\$F\{([-.\w\/\\\\]+)\}', doc_text)
    if file_includes:
        for file_include in file_includes:
            print('Loading include: ' + file_include)
            include_text = load_file_as_string(doc_dir + '/' + file_include)
            doc_text = doc_text.replace('$F{%s}' % file_include, include_text)

    return markdown.markdown(doc_text, extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.attr_list',
        'markdown.extensions.fenced_code'
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.description = '''Generate html pages from Markdown files.
Use-cases:
- generate single html from a .md file
- scan files using glob pattern and generate multiple output files     
'''

    parser.add_argument('--src', help='Source docs (source file or glob pattern)', required=True)
    parser.add_argument('--out', help='Output docs (output file or filename with {n}-placeholders)', required=True)
    parser.add_argument('--exclude', help='Subset of source files to exclude')
    parser.add_argument('--tpl', help='Template file. Default: docbook-template.html',
                        default='docbook-template.html')
    parser.add_argument('--props', help='Properties file. Default: "docbook.properties"',
                        default='docbook.properties')

    parser.add_argument('--sp', help='Output single page from multiple docs')
    parser.add_argument('--sp-item-tpl', help='', default='docbook-sp-item.html',
                        dest='singlepage_item_template')
    parser.add_argument('--sp-list-tpl', help='', default='docbook-sp-list.html',
                        dest='singlepage_list_template')

    parser.epilog = '''Usage sample:
--src=docbook.md --out=docbook.html
--src=demo/source/page-*.md --out=demo/output/{1}.html --tpl=demo/docbook-template.html --props=demo/docbook.properties
'''

    args = parser.parse_args()

    src_path_pattern = args.src
    out_path_template = args.out
    src_exclude = args.exclude
    template_file = args.tpl
    properties_file = args.props
    singlepage = args.sp

    template = load_template(template_file)

    properties = load_properties(properties_file)

    src_translate_pattern = parse_src_pattern(src_path_pattern)

    if singlepage:
        singlepage_item_template = load_template(args.singlepage_item_template)
        singlepage_list_template = load_template(args.singlepage_list_template)

    print('Processing')
    sources = list_source_files(src_path_pattern, src_exclude)

    singlepage_list = []
    for source_path in sources:
        output_path = translate_file_path(source_path, src_translate_pattern, out_path_template)
        print('%s -> %s' % (source_path, output_path))

        src_dir = os.path.dirname(source_path)
        src_dir = src_dir if src_dir else '.'
        src_filename = os.path.basename(source_path)

        doc_text = load_doc(src_dir, src_filename)

        doc_props_filename = os.path.splitext(src_filename)[0] + '.properties'

        doc_props = load_properties(src_dir + '/' + doc_props_filename)
        doc_props = merge_properties(properties, doc_props)
        doc_props['body'] = doc_text
        doc_html = render_template(doc_props, template)

        write_file(output_path, doc_html)

        if singlepage:
            doc_html = render_template(doc_props, singlepage_item_template)
            singlepage_list.append(doc_html)

    if singlepage:
        doc_props = merge_properties(properties, {'body': '\n'.join(singlepage_list)})
        doc_html = render_template(doc_props, singlepage_list_template)
        write_file(singlepage, doc_html)

    print('Done')
