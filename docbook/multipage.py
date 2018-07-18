import argparse

from docbook.docbook import *

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

parser.description = 'Generate html pages from Markdown files'

parser.add_argument('--src', help='Source files (source filename or glob pattern)',
                    required=True)
parser.add_argument('--out', help='Output files (output filename or filename template with {n}-placeholders)',
                    required=True)

parser.add_argument('--exclude', help='Subset of source files to exclude')
parser.add_argument('--tpl', help='Output template file. Default: docbook-template.html',
                    default='docbook-template.html')
parser.add_argument('--props', help='Properties file. Default: "docbook.properties"',
                    default='docbook.properties')

args = parser.parse_args()

src_path_pattern = args.src
out_path_template = args.out
src_exclude = args.exclude
template_file = args.tpl
properties_file = args.props

template = load_file_as_string(template_file)

properties = load_properties(properties_file)

src_translate_pattern = parse_pattern(src_path_pattern)

print('Processing')
sources = list_files(src_path_pattern, src_exclude)

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

print('Done')
