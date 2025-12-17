import argparse
import json
import sys
import os


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.controllers import XMLController, GraphController
from src.utils import file_io

parser = argparse.ArgumentParser(description="use XML editor in CLI mode")
commands =parser.add_subparsers(dest='command', help='Available functionalities',required=True)

verify_arg = commands.add_parser('verify', help= 'verify the structure of the XML provided')
verify_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
verify_arg.add_argument('-o',"--output",required=False,type=str,help='Path to the output XML file')
verify_arg.add_argument('-f', "--fix", required=False, action='store_true', help='fix the XML file...')

format_arg = commands.add_parser('format', help= 'formatting the xml file to the standard format')
format_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
format_arg.add_argument('-o',"--output",required=False,type=str,help='Path to the output XML file')

json_arg = commands.add_parser('json', help= 'transform the XMl file to a json format file')
json_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
json_arg.add_argument('-o',"--output",required=False,type=str,help='Path to the output XML file')

mini_arg = commands.add_parser('mini', help= 'strip spaces in XML file')
mini_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
mini_arg.add_argument('-o',"--output",required=False,type=str,help='Path to the output XML file')

compress_arg = commands.add_parser('compress', help= 'compressing XML file to specified destination')
compress_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
compress_arg.add_argument('-o',"--output",required=True,type=str,help='Path to the output XML file')

decompress_arg = commands.add_parser('decompress', help= 'decompressing XML file to specified destination')
decompress_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
decompress_arg.add_argument('-o',"--output",required=False,type=str,help='Path to the output XML file')

search_arg = commands.add_parser('search', help= 'search through XML file in it\'s posts')
search_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
search_arg.add_argument('-w',"--word",required=False,type=str,help='search with the given word')
search_arg.add_argument('-t',"--topic",required=False,type=str,help='search with the given topic')

active_arg = commands.add_parser('most_active', help= 'returns the most active person in a given input xml file')
active_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')

influencer_arg = commands.add_parser('most_influencer', help= 'returns the most influential person in a given input xml file')
influencer_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')


if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

editor = XMLController()
graph = GraphController()
args = parser.parse_args()
match args.command:

    case 'verify':
        if args.fix and args.output is None:
            print("invalid usage")

        if file_io.read_file(args.input)[0]:
            editor.set_xml_string(file_io.read_file(args.input)[1])
            annotated_xml, error_counts = editor.validate()
            editor.set_xml_string(annotated_xml)
            ack = editor.format()
            if args.output is not None:
                file_io.write_file(args.output, ack)
            print(ack)
        else:
            print("invalid path")

    case  'format':
        if file_io.read_file(args.input)[0]:
            editor.set_xml_string(file_io.read_file(args.input)[1])
            ack = editor.format()
            if args.output is not None:
                file_io.write_file(args.output,ack)
            print(ack)
        else:
            print("invalid file path")

    case 'json':
        ack = file_io.read_file(args.input)
        if ack[0]:
            editor.set_xml_string(file_io.read_file(args.input)[1])
            bool_mes, _, json_data = editor.export_to_json()
            if bool_mes:
                if args.output is not None:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                else:
                    print(f"json data format: \n\n{json_data}")
            else:
                print("invalid argument")

    case 'compress':
        ack = file_io.read_file(args.input)
        if ack[0]:
            editor.set_xml_string(file_io.read_file(args.input)[1])
            editor.compress_to_string(output_path= args.output)
            print(f"saved to {args.output}")
        else:
            print("failed to compress the file ... check input path")

    case 'decompress':
        if args.output is not None:
            editor.decompress_from_string(input_path=args.input, output_path=args.output)
            print(f"saved to {args.output}")
        else:
            print(editor.decompress_from_string(input_path= args.input))

    case 'search':
        ack = file_io.read_file(args.input)
        if ack[0]:
            editor.set_xml_string(file_io.read_file(args.input)[1])
            if args.word is not None:
                print(editor.search_in_posts(word= args.word))
            else:
                print(editor.search_in_posts(topic=args.topic))

    case 'most_active':
        ack = file_io.read_file(args.input)
        if ack[0]:
            graph.set_xml_data(ack[1])
            graph.build_graph()
            metrics = graph.get_metrics()
            print(f"the most active person is: {metrics['most_active']['name']} \nwith an id of: {metrics['most_active']['id']}")

    case 'most_influencer':
        ack = file_io.read_file(args.input)
        if ack[0]:
            graph.set_xml_data(ack[1])
            graph.build_graph()
            metrics = graph.get_metrics()
            print(
                f"the person that has the most influence is: {metrics['most_influential']['name']} \nwith an id of: {metrics['most_influential']['id']}")

    case 'draw':
