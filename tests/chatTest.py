import asyncio
import sys
import signal
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from typing import Dict
import logging

class AssistantCLI:
    SUPPORTED_LANGUAGES = {
        '1': {'code': 'en', 'name': 'English'},
        '2': {'code': 'fr', 'name': 'French'},
        '3': {'code': 'ar', 'name': 'Arabic/Darija'}
    }

    def __init__(self):
        self.console = Console()
        self.setup_signal_handlers()
        self.welcome_messages = {
            'en': "ODC AI Assistant (Enhanced RAG Edition)\nCommands:\n- 'quit' or 'exit': End session\n- 'clear': Reset memory\n- 'debug': Toggle debug mode\n- 'help': Show commands",
            'fr': "Assistant IA ODC (Édition RAG Améliorée)\nCommandes:\n- 'quit' ou 'exit': Terminer\n- 'clear': Réinitialiser\n- 'debug': Mode debug\n- 'help': Aide",
            'ar': "مساعد ODC الذكي (نسخة RAG محسنة)\nالأوامر:\n- 'quit' أو 'exit': إنهاء\n- 'clear': مسح الذاكرة\n- 'debug': وضع التصحيح\n- 'help': المساعدة"
        }

    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.handle_interrupt)

    def handle_interrupt(self, signum, frame):
        self.console.print("\n[yellow]Gracefully shutting down...[/yellow]")
        sys.exit(0)

    def display_welcome(self, language: str):
        self.console.print(Panel(
            self.welcome_messages.get(language, self.welcome_messages['en']),
            title="Welcome",
            border_style="blue"
        ))

    @classmethod
    def select_language(cls) -> str:
        console = Console()
        console.print(Panel("Please select your preferred language:", title="Language Selection"))
        
        for key, lang in cls.SUPPORTED_LANGUAGES.items():
            console.print(f"{key}. {lang['name']}")
        
        while True:
            choice = console.input("Enter your choice (1-3): ").strip()
            if choice in cls.SUPPORTED_LANGUAGES:
                return cls.SUPPORTED_LANGUAGES[choice]['code']
            console.print("[red]Invalid choice, please try again.[/red]")

    def format_response(self, response: Dict) -> None:
        if response.get('answer'):
            self.console.print(Panel(
                response['answer'],
                title="Assistant",
                border_style="green"
            ))
        
        if response.get('sources'):
            self.console.print("\n[blue]Sources:[/blue]")
            for source in response['sources']:
                self.console.print(f"- {source['source']} (Confidence: {source['score']:.2f})")
        
        if response.get('confidence'):
            self.console.print(f"\n[yellow]Overall Confidence: {response['confidence']:.2%}[/yellow]")

async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='assistant_chat.log'
    )
    logger = logging.getLogger(__name__)

    # Initialize CLI and get language preference
    cli = AssistantCLI()
    selected_language = cli.select_language()
    
    # Initialize the enhanced handler
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Initializing AI Assistant...", total=100)
            handler = EnhancedLangChainHandler(selected_language)
            progress.update(task, completed=100)
    except Exception as e:
        logger.error(f"Failed to initialize handler: {e}")
        cli.console.print("[red]Failed to initialize the AI Assistant. Please check your configuration.[/red]")
        return

    cli.display_welcome(selected_language)
    debug_mode = False

    while True:
        try:
            user_input = cli.console.input("\n[bold blue]You:[/bold blue] ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit']:
                cli.console.print("[yellow]Goodbye![/yellow]")
                break
            
            elif user_input.lower() == 'clear':
                handler.memory.clear()
                cli.console.print("[green]Memory cleared![/green]")
                continue
            
            elif user_input.lower() == 'debug':
                debug_mode = not debug_mode
                cli.console.print(f"[yellow]Debug mode: {'enabled' if debug_mode else 'disabled'}[/yellow]")
                continue
            
            elif user_input.lower() == 'help':
                cli.display_welcome(selected_language)
                continue

            # Process user input
            with Progress() as progress:
                task = progress.add_task("[cyan]Thinking...", total=100)
                response = await handler.get_response_async(user_input)
                progress.update(task, completed=100)

            # Display response
            cli.format_response(response)

            # Log interaction if debug mode is enabled
            if debug_mode:
                logger.info(f"User: {user_input}")
                logger.info(f"Assistant: {response['answer']}")
                cli.console.print("\n[dim]Debug info logged[/dim]")

        except Exception as e:
            logger.error(f"Error during conversation: {e}")
            cli.console.print(f"[red]An error occurred: {str(e)}[/red]")
            cli.console.print("[yellow]You can continue with your next question.[/yellow]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        Console().print("\n[yellow]Gracefully shutting down...[/yellow]")
    except Exception as e:
        Console().print(f"[red]Fatal error: {str(e)}[/red]")
        logging.error(f"Fatal error: {e}")