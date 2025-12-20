import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print the ASCII art banner for the application."""
    banner = f"""
{Fore.CYAN}███████╗ ██████╗  ██████╗██╗ █████╗ ██╗           ██╗    ██╗  ██╗    ██╗  
██╔════╝██╔═══██╗██╔════╝██║██╔══██╗██║          ██╔╝    ╚██╗██╔╝    ╚██╗ 
███████╗██║   ██║██║     ██║███████║██║         ██╔╝      ╚███╔╝      ╚██╗
╚════██║██║   ██║██║     ██║██╔══██║██║         ╚██╗      ██╔██╗      ██╔╝
███████║╚██████╔╝╚██████╗██║██║  ██║███████╗     ╚██╗    ██╔╝ ██╗    ██╔╝{Style.RESET_ALL}
"""
    print(banner)

def launch_gui():
    """Launch the graphical user interface."""
    from gui import AppManager
    manager = AppManager()
    manager.run()

def launch_cli():
    """Launch the command-line interface in REPL mode."""
    import cli
    cli.run_repl()

def print_help():
    help_text = f"""
{Fore.YELLOW}{"SocialX: An XML Editor and Visualizer".center(60)}{Style.RESET_ALL}

{Fore.CYAN}Usage:{Style.RESET_ALL}
    Select the desired mode by entering the corresponding number.

{Fore.CYAN}Modes:{Style.RESET_ALL}
    {Fore.GREEN}1.{Style.RESET_ALL} GUI  - Launch the graphical user interface.
    {Fore.GREEN}2.{Style.RESET_ALL} CLI  - Launch the command-line interface.
    {Fore.GREEN}3.{Style.RESET_ALL} Help - Show this help information.
    {Fore.GREEN}4.{Style.RESET_ALL} Exit - Exit the application.

{Fore.CYAN}Instructions:{Style.RESET_ALL}
    - Enter the number corresponding to your choice and press Enter.
    - For example, enter '1' to launch the GUI.
"""
    print(help_text)

def app():
    print_banner()
    print_help()
    
    while True:
        try:
            choice = input(f"{Fore.GREEN}Enter your choice (1/2/3/4): {Style.RESET_ALL}").strip()
            if choice == '1':
                print(f"{Fore.BLUE}Launching GUI...{Style.RESET_ALL}")
                launch_gui()
                print(f"{Fore.GREEN}Returned to main menu.{Style.RESET_ALL}\n")
            elif choice == '2':
                print(f"{Fore.BLUE}Launching CLI...{Style.RESET_ALL}")
                launch_cli()
                print(f"{Fore.GREEN}Returned to main menu.{Style.RESET_ALL}\n")
            elif choice == '3':
                print_help()
            elif choice == '4':
                print(f"{Fore.LIGHTRED_EX}Exiting application. Goodbye!{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1, 2, 3, or 4.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.LIGHTRED_EX}Exiting application. Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    app()