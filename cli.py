"""Command line interface of Social network program"""

import argparse
import json
import re
import sys
import os
import networkx as nx
import matplotlib.pyplot as plt

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

mutual_arg = commands.add_parser('mutual', help= 'returns mutual followers in a given social network (defined by a xml file)')
mutual_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
mutual_arg.add_argument('-ids',"--ids",required=True,type=str,help='ids for each of the users that\'s desired to get the mutual between them')

suggest_arg = commands.add_parser('suggest', help= 'suggests a new friend based on a given social network (defined by a xml file)')
suggest_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
suggest_arg.add_argument('-id',"--id",required=True,type=str,help='id of the user for suggesting to him')

draw_arg = commands.add_parser('draw', help= 'saving an image of a drawn graph representing the social network')
draw_arg.add_argument('-i',"--input",required=True,type=str,help='Path to the input XML file')
draw_arg.add_argument('-o',"--output",required=True,type=str,help='Path to the output XML file')


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
            try:
                editor.set_xml_string(file_io.read_file(args.input)[1])
                annotated_xml, error_counts = editor.validate()
                editor.set_xml_string(annotated_xml)
                ack = editor.format()
                if args.output is not None:
                    file_io.write_file(args.output, ack)
                print(ack)
            except RuntimeError as e:
                print("error while processing xml data")
        else:
            print("invalid file path")

    case  'format':
        if file_io.read_file(args.input)[0]:
            try:
                editor.set_xml_string(file_io.read_file(args.input)[1])
                ack = editor.format()
                if args.output is not None:
                    file_io.write_file(args.output,ack)
                print(ack)
            except RuntimeError as e:
                print("error while processing xml data")
        else:
            print("invalid file path")

    case 'json':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
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
            except RuntimeError as e:
                print("error while processing xml data")
        else:
            print("error while opening the input file")

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
            try:
                editor.decompress_from_string(input_path=args.input, output_path=args.output)
                print(f"saved to {args.output}")
            except RuntimeError as e:
                print("error while processing the compressed string")
        else:
            try:
                print(editor.decompress_from_string(input_path= args.input))
            except RuntimeError as e:
                print("error while processing the compressed string")

    case 'search':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
                editor.set_xml_string(file_io.read_file(args.input)[1])
                if args.word is not None:
                    print(editor.search_in_posts(word= args.word))
                else:
                    print(editor.search_in_posts(topic=args.topic))
            except RuntimeError as e:
                print("error while processing the xml data")
        else:
            print("error while opening the input file")

    case 'most_active':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
                graph.set_xml_data(ack[1])
                graph.build_graph()
                metrics = graph.get_metrics()
                print(f"the most active person is: {metrics['most_active']['name']} \nwith an id of: {metrics['most_active']['id']}")
            except RuntimeError as e:
                print("error while processing the graph")
        else:
            print("error while opening the input file")

    case 'most_influencer':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
                graph.set_xml_data(ack[1])
                graph.build_graph()
                metrics = graph.get_metrics()
                print(
                    f"the person that has the most influence is: {metrics['most_influential']['name']} \nwith an id of: {metrics['most_influential']['id']}")
            except RuntimeError as e:
                print("error while processing the graph")
        else:
            print("error while opening the input file")

    case 'mutual':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
                graph.set_xml_data(ack[1])
                graph.build_graph()
                result = re.findall(r'\d+', args.ids)
                mutual = graph.get_mutual_followers_between_many(result)
                out = ""
                for i in range(len(mutual)):
                    out += f"{i+1}.\n   name: {mutual[i]['name']} with an id of {mutual[i]['user_id']} \n"
                if out == "":
                    print("we didn't find any mutual friend")
                else:
                    print(f"we found some mutual friends you might wanna check out:\n   {out}")
            except RuntimeError as e:
                print("error while processing the graph")
        else:
            print("error while opening the input file")

    case 'suggest':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
                graph.set_xml_data(ack[1])
                graph.build_graph()
                users = graph.suggest_users_to_follow(user_id= args.id.strip(), limit = 5)
                out = ""
                for i in range(len(users)):
                    out += f"{i + 1}.\n        name: {users[i]['name']} with an id of {users[i]['user_id']} \n"
                if out == "":
                    print("we couldn't suggest any new friend")
                else:
                    print(f"we can suggest some new friends you might wanna check out:\n   {out}")
            except RuntimeError as e:
                print("error while trying to build graph")
        else:
            print("error while opening the input file")

    case 'draw':
        ack = file_io.read_file(args.input)
        if ack[0]:
            try:
                graph.set_xml_data(ack[1])
                graph.build_graph()
                plt.clf()
                nx.draw(graph.get_graph(), with_labels=True, node_color='skyblue',
                        edge_color='gray', node_size=1500, font_size=10,
                        arrows=True, arrowsize=20)
                plt.savefig(args.output, bbox_inches='tight')
                plt.close()
                print(f"saved to {args.output}")
            except Exception as e:
                print(f"Error saving graph image: {e}")
        else:
            print("invalid argument")