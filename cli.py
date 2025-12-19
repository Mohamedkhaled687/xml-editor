"""Command line interface of Social network program"""

import argparse
import json
import re
import sys
import os
import shlex
import networkx as nx
import matplotlib.pyplot as plt
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.controllers import XMLController, GraphController
from src.utils import file_io

def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(description="use XML editor in CLI mode", exit_on_error=False)
    commands = parser.add_subparsers(dest='command', help='Available functionalities', required=False)

    verify_arg = commands.add_parser('verify', help='verify the structure of the XML provided')
    verify_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    verify_arg.add_argument('-o', '--output', required=False, type=str, help='Path to the output XML file')
    verify_arg.add_argument('-f', '--fix', required=False, action='store_true', help='fix the XML file...')

    format_arg = commands.add_parser('format', help='formatting the xml file to the standard format')
    format_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    format_arg.add_argument('-o', '--output', required=False, type=str, help='Path to the output XML file')

    json_arg = commands.add_parser('json', help='transform the XML file to a json format file')
    json_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    json_arg.add_argument('-o', '--output', required=False, type=str, help='Path to the output XML file')

    mini_arg = commands.add_parser('mini', help='strip spaces in XML file')
    mini_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    mini_arg.add_argument('-o', '--output', required=False, type=str, help='Path to the output XML file')

    compress_arg = commands.add_parser('compress', help='compressing XML file to specified destination')
    compress_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    compress_arg.add_argument('-o', '--output', required=True, type=str, help='Path to the output XML file')

    decompress_arg = commands.add_parser('decompress', help='decompressing XML file to specified destination')
    decompress_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    decompress_arg.add_argument('-o', '--output', required=False, type=str, help='Path to the output XML file')

    search_arg = commands.add_parser('search', help='search through XML file in it\'s posts')
    search_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    search_arg.add_argument('-w', '--word', required=False, type=str, help='search with the given word')
    search_arg.add_argument('-t', '--topic', required=False, type=str, help='search with the given topic')

    active_arg = commands.add_parser('most_active', help='returns the most active person in a given input xml file')
    active_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')

    influencer_arg = commands.add_parser('most_influencer', help='returns the most influential person in a given input xml file')
    influencer_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')

    mutual_arg = commands.add_parser('mutual', help='returns mutual followers in a given social network (defined by a xml file)')
    mutual_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    mutual_arg.add_argument('-ids', '--ids', required=True, type=str, help='ids for each of the users that\'s desired to get the mutual between them')

    suggest_arg = commands.add_parser('suggest', help='suggests a new friend based on a given social network (defined by a xml file)')
    suggest_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    suggest_arg.add_argument('-id', '--id', required=True, type=str, help='id of the user for suggesting to him')

    draw_arg = commands.add_parser('draw', help='saving an image of a drawn graph representing the social network')
    draw_arg.add_argument('-i', '--input', required=True, type=str, help='Path to the input XML file')
    draw_arg.add_argument('-o', '--output', required=True, type=str, help='Path to the output XML file')

    return parser

def execute_command(args, editor, graph):
    """Execute a CLI command with parsed arguments."""
    match args.command:
        case 'verify':
            if args.fix and args.output is None:
                print(f"{Fore.RED}invalid usage{Style.RESET_ALL}")

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
                    print(f"{Fore.RED}error while processing xml data{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}invalid file path{Style.RESET_ALL}")

        case 'format':
            if file_io.read_file(args.input)[0]:
                try:
                    editor.set_xml_string(file_io.read_file(args.input)[1])
                    ack = editor.format()
                    if args.output is not None:
                        file_io.write_file(args.output, ack)
                    print(ack)
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing xml data{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}invalid file path{Style.RESET_ALL}")

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
                        print(f"{Fore.RED}invalid argument{Style.RESET_ALL}")
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing xml data{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

        case 'mini':
            ack = file_io.read_file(args.input)
            if ack[0]:
                try:
                    editor.set_xml_string(file_io.read_file(args.input)[1])
                    minified = editor.minify()
                    if args.output is not None:
                        file_io.write_file(args.output, minified)
                    print(minified)
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing xml data{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

        case 'compress':
            ack = file_io.read_file(args.input)
            if ack[0]:
                editor.set_xml_string(file_io.read_file(args.input)[1])
                editor.compress_to_string(output_path=args.output)
                print(f"{Fore.GREEN}✓ saved to {args.output}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}failed to compress the file ... check input path{Style.RESET_ALL}")

        case 'decompress':
            if args.output is not None:
                try:
                    editor.decompress_from_string(input_path=args.input, output_path=args.output)
                    print(f"{Fore.GREEN}✓ saved to {args.output}{Style.RESET_ALL}")
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing the compressed string{Style.RESET_ALL}")
            else:
                try:
                    print(editor.decompress_from_string(input_path=args.input))
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing the compressed string{Style.RESET_ALL}")

        case 'search':
            ack = file_io.read_file(args.input)
            if ack[0]:
                try:
                    editor.set_xml_string(file_io.read_file(args.input)[1])
                    if args.word is not None:
                        print(editor.search_in_posts(word=args.word))
                    else:
                        print(editor.search_in_posts(topic=args.topic))
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing the xml data{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

        case 'most_active':
            ack = file_io.read_file(args.input)
            if ack[0]:
                try:
                    graph.set_xml_data(ack[1])
                    graph.build_graph()
                    metrics = graph.get_metrics()
                    print(f"{Fore.GREEN}the most active person is: {metrics['most_active']['name']}{Style.RESET_ALL} \n{Fore.CYAN}with an id of: {metrics['most_active']['id']}{Style.RESET_ALL}")
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing the graph{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

        case 'most_influencer':
            ack = file_io.read_file(args.input)
            if ack[0]:
                try:
                    graph.set_xml_data(ack[1])
                    graph.build_graph()
                    metrics = graph.get_metrics()
                    print(
                        f"{Fore.GREEN}the person that has the most influence is: {metrics['most_influential']['name']}{Style.RESET_ALL} \n{Fore.CYAN}with an id of: {metrics['most_influential']['id']}{Style.RESET_ALL}")
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing the graph{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

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
                        print(f"{Fore.YELLOW}we didn't find any mutual friend{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}we found some mutual friends you might wanna check out:{Style.RESET_ALL}\n   {out}")
                except RuntimeError as e:
                    print(f"{Fore.RED}error while processing the graph{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

        case 'suggest':
            ack = file_io.read_file(args.input)
            if ack[0]:
                try:
                    graph.set_xml_data(ack[1])
                    graph.build_graph()
                    users = graph.suggest_users_to_follow(user_id=args.id.strip(), limit=5)
                    out = ""
                    for i in range(len(users)):
                        out += f"{i + 1}.\n        name: {users[i]['name']} with an id of {users[i]['user_id']} \n"
                    if out == "":
                        print(f"{Fore.YELLOW}we couldn't suggest any new friend{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}we can suggest some new friends you might wanna check out:{Style.RESET_ALL}\n   {out}")
                except RuntimeError as e:
                    print(f"{Fore.RED}error while trying to build graph{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}error while opening the input file{Style.RESET_ALL}")

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
                    print(f"{Fore.GREEN}✓ saved to {args.output}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error saving graph image: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}invalid argument{Style.RESET_ALL}")

def print_help_commands():
    """Print a helpful guide showing how to use commands in REPL mode."""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Available Commands - How to Use{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    commands_help = [
        ("verify", "Verify XML structure", 
         "verify -i input.xml [-o output.xml] [-f]",
         "verify -i assets/samples/file.xml -o verified.xml"),
        ("format", "Format XML file", 
         "format -i input.xml [-o output.xml]",
         "format -i assets/samples/file.xml -o formatted.xml"),
        ("json", "Convert XML to JSON", 
         "json -i input.xml [-o output.json]",
         "json -i assets/samples/file.xml -o output.json"),
        ("mini", "Minify XML (remove spaces)", 
         "mini -i input.xml [-o output.xml]",
         "mini -i assets/samples/file.xml -o minified.xml"),
        ("compress", "Compress XML file", 
         "compress -i input.xml -o output.compressed",
         "compress -i assets/samples/file.xml -o compressed.xml"),
        ("decompress", "Decompress XML file", 
         "decompress -i input.compressed [-o output.xml]",
         "decompress -i compressed.xml -o decompressed.xml"),
        ("search", "Search in posts", 
         "search -i input.xml [-w word] [-t topic]",
         "search -i assets/samples/file.xml -w technology"),
        ("most_active", "Find most active user", 
         "most_active -i input.xml",
         "most_active -i assets/samples/file.xml"),
        ("most_influencer", "Find most influential user", 
         "most_influencer -i input.xml",
         "most_influencer -i assets/samples/file.xml"),
        ("mutual", "Find mutual followers", 
         "mutual -i input.xml -ids \"1,2,3\"",
         "mutual -i assets/samples/file.xml -ids \"1,2,3\""),
        ("suggest", "Suggest friends", 
         "suggest -i input.xml -id user_id",
         "suggest -i assets/samples/file.xml -id 1"),
        ("draw", "Draw social network graph", 
         "draw -i input.xml -o graph.png",
         "draw -i assets/samples/file.xml -o graph.png"),
    ]
    
    for cmd, desc, syntax, example in commands_help:
        print(f"{Fore.GREEN}{cmd:<15}{Style.RESET_ALL} - {desc}")
        print(f"  {Fore.CYAN}Syntax:{Style.RESET_ALL} {Fore.WHITE}{syntax}{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}Example:{Style.RESET_ALL} {Fore.WHITE}{example}{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Special Commands:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}help{Style.RESET_ALL}  - Show this help message")
    print(f"  {Fore.GREEN}exit{Style.RESET_ALL}  - Exit the REPL (also: quit, q)")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def get_prompt():
    """Generate a bash-style prompt showing the current directory."""
    cwd = os.getcwd()
    home = os.path.expanduser('~')
    
    # Replace home directory with ~
    if cwd.startswith(home):
        display_path = '~' + cwd[len(home):]
    else:
        display_path = cwd
    
    return f"{Fore.GREEN}{display_path}{Style.RESET_ALL} {Fore.CYAN}${Style.RESET_ALL} "

def run_repl():
    """Run CLI in REPL (Read-Eval-Print Loop) mode with bash-style prompt."""
    parser = create_parser()
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}XML Editor CLI - Interactive Mode (REPL){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Type {Fore.GREEN}'exit'{Style.RESET_ALL} to exit. Type {Fore.GREEN}'help'{Style.RESET_ALL} for command help.\n")
    
    while True:
        try:
            # Get user input with bash-style prompt
            user_input = input(get_prompt()).strip()
            
            # Skip empty input
            if not user_input:
                continue
            
            # Handle exit command
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"{Fore.LIGHTRED_EX}Exiting CLI mode. Goodbye!{Style.RESET_ALL}")
                break
            
            # Handle help command
            if user_input.lower() == 'help':
                print_help_commands()
                continue
            
            # Parse and execute command
            try:
                # Split input into arguments
                args_list = shlex.split(user_input)
                
                # Temporarily replace sys.argv to parse arguments
                old_argv = sys.argv
                sys.argv = ['cli.py'] + args_list
                
                try:
                    args = parser.parse_args(args_list)
                    
                    if args.command is None:
                        print(f"{Fore.RED}Error: No command specified.{Style.RESET_ALL} Type {Fore.GREEN}'help'{Style.RESET_ALL} for available commands.")
                        continue
                    
                    # Create fresh controller instances for each command
                    editor = XMLController()
                    graph_controller = GraphController()
                    
                    # Execute the command
                    execute_command(args, editor, graph_controller)
                    
                finally:
                    sys.argv = old_argv
                    
            except SystemExit:
                # argparse may call sys.exit, catch it
                pass
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                print(f"Type {Fore.GREEN}'help'{Style.RESET_ALL} for usage information.")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.LIGHTRED_EX}Exiting CLI mode. Goodbye!{Style.RESET_ALL}")
            break
        except EOFError:
            print(f"\n{Fore.LIGHTRED_EX}Exiting CLI mode. Goodbye!{Style.RESET_ALL}")
            break

# Main execution
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # REPL mode
        run_repl()
    else:
        # Normal CLI mode (backward compatible)
        parser = create_parser()
        # Make command required for direct CLI calls
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                action.required = True
                break
        
        try:
            args = parser.parse_args()
            
            if args.command is None:
                parser.print_help()
                sys.exit(1)
            
            editor = XMLController()
            graph = GraphController()
            execute_command(args, editor, graph)
            
        except SystemExit as e:
            # argparse may raise SystemExit even with exit_on_error=False in some cases
            # Re-raise to preserve exit codes (0 for help, 2 for errors)
            raise
        except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
            # Handle argument errors (e.g., invalid choice, missing required args, type errors)
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            parser.print_help()
            sys.exit(2)
        except Exception as e:
            # Handle any other parsing errors
            print(f"{Fore.RED}Error parsing arguments: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Use 'python cli.py <command> --help' for command-specific help.{Style.RESET_ALL}")
            parser.print_help()
            sys.exit(2)