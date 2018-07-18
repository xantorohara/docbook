import argparse

from docbook.docbook import *

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

parser.description = 'Generate single html page from multiple Markdown files'

parser.add_argument('--src', help='Source files (source filename or glob pattern)',
                    required=True)
parser.add_argument('--out', help='Output filen',
                    required=True)

parser.add_argument('--exclude', help='Subset of source files to exclude')
parser.add_argument('--props', help='Properties file. Default: "docbook.properties"',
                    default='docbook.properties')

parser.add_argument('--item-tpl', help='Output template for the item',
                    default='docbook-item.html',
                    dest='item_template')
parser.add_argument('--list-tpl', help='Output template for the list',
                    default='docbook-list.html',
                    dest='list_template')

args = parser.parse_args()

src_path_pattern = args.src
out_filename = args.out
src_exclude = args.exclude
properties_file = args.props

properties = load_properties(properties_file)

src_translate_pattern = parse_pattern(src_path_pattern)

singlepage_item_template = load_file_as_string(args.singlepage_item_template)
singlepage_list_template = load_file_as_string(args.singlepage_list_template)

print('Processing')
sources = list_files(src_path_pattern, src_exclude)

singlepage_list = []
for source_path in sources:
    src_dir = os.path.dirname(source_path)
    src_dir = src_dir if src_dir else '.'
    src_filename = os.path.basename(source_path)

    doc_text = load_doc(src_dir, src_filename)

    doc_props_filename = os.path.splitext(src_filename)[0] + '.properties'

    doc_props = load_properties(src_dir + '/' + doc_props_filename)
    doc_props = merge_properties(properties, doc_props)
    doc_props['body'] = doc_text
    doc_html = render_template(doc_props, singlepage_item_template)
    singlepage_list.append(doc_html)

doc_props = merge_properties(properties, {'body': '\n'.join(singlepage_list)})
doc_html = render_template(doc_props, singlepage_list_template)
write_file(out_filename, doc_html)

print('Done')
