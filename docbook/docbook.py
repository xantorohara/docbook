import fnmatch
import glob
import os
import re
import time

import markdown


def list_files(includes, excludes, reverse=False):
    """
    :return: List of filenames matching the includes pattern minus excludes pattern
    """
    paths = glob.glob(includes)
    exclude_paths = []
    if excludes:
        exclude_paths = glob.glob(excludes)

    paths = [path.replace('\\', '/') for path in paths]
    exclude_paths = [path.replace('\\', '/') for path in exclude_paths]

    if exclude_paths:
        paths = [path for path in paths if path not in exclude_paths]

    if reverse:
        paths.sort(reverse=True)
    else:
        paths.sort()
    return paths


def parse_pattern(path_pattern):
    """
    Search for glob symbols (? and *) in the source pattern and translate them to regex
    """
    if '*' in path_pattern or '?' in path_pattern:
        translate_pattern = fnmatch.translate(path_pattern)
        translate_pattern = translate_pattern.replace('.*', '(.*)')
        translate_pattern = translate_pattern.replace('.?', '(.?)')
        return translate_pattern
    else:
        return None


def translate_file_path(src_path, source_pattern, output_template):
    """
    Translate source filename to output filename using source and output patterns.
    E.g.:
        source pattern    | output template      | source filename       | output filename
        ---------------------------------------------------------------------------------------------
        article-abc.md    | article-abc.html     | article-abc.md        | article-abc.html
        in/article-abc.md | out/article-abc.html | in/article-abc.md     | out/article-abc.html
        in/*.md           | out/{1}.html         | in/article-abc.md     | out/article-abc.html
        in/*/doc.md       | out/{1}.html         | in/article-abc/doc.md | out/article-abc.html
        in/*/doc.md       | out/{1}/index.html   | in/article-abc/doc.md | out/article-abc/index.html
        in/*/*.md         | out/{2}-{1}.html     | in/article/abc.md     | out/abc-article.html

    """
    if source_pattern:
        m = re.match(source_pattern, src_path)
        if m and m.groups():
            out_path = output_template
            for index, group in enumerate(m.groups()):
                out_path = out_path.replace('{%d}' % (index + 1), group)
            return out_path
        else:
            print('Filename translation error')
            raise Exception()
    else:
        return output_template


def load_file_as_string(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def load_properties(filename):
    """
    Load properties from file
    """
    props = {}
    if not filename or not os.path.isfile(filename):
        return props

    # print('Loading properties: ' + properties_file)

    with open(filename, 'r', encoding='utf-8') as f:
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


def write_file(filename, content):
    # print('Writing doc: %s' % path)
    if os.path.isfile(filename) and time.time() - os.path.getmtime(filename) < 5:
        print('Trying to overwrite just modified file')
        raise Exception()

    tmp_dir = os.path.dirname(filename)
    tmp_dir = tmp_dir if tmp_dir else '.'
    os.makedirs(tmp_dir, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


def merge_properties(properties, properties_override):
    out = properties.copy()
    out.update(properties_override)
    return out


def load_doc(doc_dir, doc_file):
    doc_dir = doc_dir if doc_dir else '.'
    doc_text = load_file_as_string(doc_dir + '/' + doc_file)

    file_includes = re.findall('\$F{([-.\w/\\\\]+)\}', doc_text)
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
