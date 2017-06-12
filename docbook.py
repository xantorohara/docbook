import os

import markdown
import argparse


def load_template(filename):
    print('Loading template: %s' % filename)
    with open(filename, 'r') as file:
        return file.read()


def render_template(template, props):
    print('Rendering template')
    for key, value in props.items():
        template = template.replace('${%s}' % key, value)
    return template


def load_doc(filename):
    print('Loading doc: %s' % filename)

    with open(filename, 'r') as file:
        text = file.read()
        return markdown.markdown(text, extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.attr_list',
            'markdown.extensions.fenced_code'
        ])


def load_props(filename):
    print('Loading properties: %s' % filename)
    props = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if '=' not in line or line.startswith('#'):
                continue
            k, v = line.split("=", 1)
            props[k] = v
    return props


def merge_props(props, props_override):
    props = props.copy()
    props.update(props_override)
    return props


def write_doc_html(filename, content):
    print('Writing doc: %s' % filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', help='Source docs directory', required=True)
    parser.add_argument('--out', help='Output docs directory', required=True)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--docs', help='Generate selected docs', nargs='+')
    group.add_argument('--all', help='Generate all docs', action='store_true')

    args = parser.parse_args()

    src_dir = args.src
    out_dir = args.out

    docs = []
    if args.docs:
        docs = args.docs
    elif args.all:
        print(os.listdir(src_dir))
        docs = [d for d in os.listdir(src_dir) if os.path.isdir(src_dir + '/' + d)]
        print(docs)
    else:
        print('No docs specified')

    global_template = load_template(src_dir + '/docbook-template.html')
    global_props = load_props(src_dir + '/docbook.properties')

    for doc in docs:
        doc_content = load_doc('%s/%s/doc.md' % (src_dir, doc))
        doc_props = load_props('%s/%s/doc.properties' % (src_dir, doc))
        doc_props = merge_props(global_props, doc_props)
        doc_props['body'] = doc_content

        doc_html = render_template(global_template, doc_props)

        if doc == 'index':
            outdir = out_dir + '/index.html'
        else:
            outdir = '%s/%s/index.html' % (out_dir, doc)
        write_doc_html(outdir, doc_html)
