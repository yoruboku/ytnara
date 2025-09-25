"""
User Interface Module
Handles terminal UI with Rich library
"""

import logging
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from pyfiglet import figlet_format
from colorama import init

# Initialize colorama for Windows compatibility
init()

class TerminalUI:
    """Terminal UI with Rich library for beautiful interface"""
    
    def __init__(self):
        self.console = Console()
        self.progress = None
        self.current_task = None
    
    def show_banner(self):
        """Display the YT-Nara banner"""
        banner_text = figlet_format("YT-Nara", font="slant")
        banner_panel = Panel(
            f"[bold blue]{banner_text}[/bold blue]\n"
            "[bold green]Universal Content Automation Tool[/bold green]\n"
            "[dim]Discover • Download • Edit • Upload[/dim]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(banner_panel)
    
    def get_topic_input(self) -> str:
        """Get topic input from user with improved input handling"""
        topic_panel = Panel(
            "[bold cyan]📝 Topic Configuration[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(topic_panel)
        
        try:
            # Try Rich prompt first (supports backspace and editing)
            topic = Prompt.ask(
                "[bold cyan]Enter your topic[/bold cyan]",
                default="anime memes",
                show_default=True
            )
        except (KeyboardInterrupt, EOFError):
            # Fallback to basic input if Rich prompt fails
            self.console.print("[yellow]Using basic input mode...[/yellow]")
            topic = input("Enter your topic (anime memes): ").strip()
            if not topic:
                topic = "anime memes"
        
        self.console.print(f"[green]✅ Topic set: {topic}[/green]")
        return topic
    
    def get_cycles_input(self) -> int:
        """Get number of cycles from user with improved input handling"""
        cycles_panel = Panel(
            "[bold yellow]🔄 Cycle Configuration[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(cycles_panel)
        
        try:
            cycles = IntPrompt.ask(
                "[bold yellow]How many cycles to run?[/bold yellow]",
                default=3,
                show_default=True
            )
        except (KeyboardInterrupt, EOFError, ValueError):
            # Fallback to basic input if Rich prompt fails
            self.console.print("[yellow]Using basic input mode...[/yellow]")
            try:
                cycles = int(input("How many cycles to run? (3): ").strip() or "3")
            except ValueError:
                cycles = 3
        
        self.console.print(f"[green]✅ Cycles set: {cycles}[/green]")
        return cycles
    
    def get_daily_frequency_input(self) -> Optional[int]:
        """Get daily frequency input from user with improved input handling"""
        schedule_panel = Panel(
            "[bold magenta]📅 Schedule Configuration[/bold magenta]",
            border_style="magenta"
        )
        self.console.print(schedule_panel)
        
        try:
            use_scheduling = Confirm.ask(
                "[bold magenta]Do you want to schedule uploads throughout the day?[/bold magenta]",
                default=True
            )
        except (KeyboardInterrupt, EOFError):
            # Fallback to basic input
            self.console.print("[yellow]Using basic input mode...[/yellow]")
            response = input("Schedule uploads throughout the day? (y/n): ").strip().lower()
            use_scheduling = response in ['y', 'yes', '']
        
        if use_scheduling:
            try:
                frequency = IntPrompt.ask(
                    "[bold magenta]How many uploads per day?[/bold magenta]",
                    default=4,
                    show_default=True
                )
            except (KeyboardInterrupt, EOFError, ValueError):
                # Fallback to basic input
                try:
                    frequency = int(input("How many uploads per day? (4): ").strip() or "4")
                except ValueError:
                    frequency = 4
            self.console.print(f"[green]✅ Daily frequency set: {frequency}[/green]")
            return frequency
        else:
            self.console.print("[blue]ℹ️ All cycles will run immediately[/blue]")
            return None
    
    def show_confirmation(self, topic: str, cycles: int, daily_frequency: Optional[int]) -> bool:
        """Show configuration confirmation"""
        summary_panel = Panel(
            "[bold green]✅ Configuration Summary[/bold green]",
            border_style="green"
        )
        self.console.print(summary_panel)
        
        # Create summary table
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Topic", topic)
        table.add_row("Cycles", str(cycles))
        table.add_row("Videos per cycle", "4")
        table.add_row("Total videos", str(cycles * 4))
        
        if daily_frequency:
            table.add_row("Execution", f"Scheduled ({daily_frequency} per day)")
        else:
            table.add_row("Execution", "Immediate (all cycles)")
        
        summary_table_panel = Panel(table, title="Configuration", border_style="green")
        self.console.print(summary_table_panel)
        
        return Confirm.ask(
            "\n[bold green]Proceed with this configuration?[/bold green]",
            default=True
        )
    
    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"[blue]ℹ️ {message}[/blue]")
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"[yellow]⚠️ {message}[/yellow]")
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[red]❌ {message}[/red]")
    
    def print_step(self, message: str):
        """Print step message"""
        self.console.print(f"[bold blue]⚡ {message}[/bold blue]")
    
    def print_cycle_start(self, cycle_num: int, total_cycles: int):
        """Print cycle start message"""
        cycle_panel = Panel(
            f"[bold green]🚀 Starting Cycle {cycle_num}/{total_cycles}[/bold green]",
            border_style="green"
        )
        self.console.print(cycle_panel)
    
    def init_progress(self, tasks: list):
        """Initialize progress tracking"""
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        
        self.current_task = self.progress.add_task("Initializing...", total=100)
        self.progress.start()
    
    def update_progress(self, description: str, advance: int = 10):
        """Update progress"""
        if self.progress and self.current_task:
            self.progress.update(
                self.current_task,
                description=description,
                advance=advance
            )
    
    def complete_progress(self):
        """Complete progress tracking"""
        if self.progress:
            self.progress.stop()
    
    def show_statistics(self, stats: dict):
        """Show statistics"""
        stats_panel = Panel(
            "[bold green]📊 Statistics[/bold green]",
            border_style="green"
        )
        self.console.print(stats_panel)
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Processed", str(stats.get('total_processed', 0)))
        table.add_row("Completed", str(stats.get('completed', 0)))
        table.add_row("Failed", str(stats.get('failed', 0)))
        table.add_row("Average Relevance", str(stats.get('avg_relevance', 0)))
        
        stats_table_panel = Panel(table, title="Database Statistics", border_style="green")
        self.console.print(stats_table_panel)
    
    def run_setup(self):
        """Run setup mode"""
        setup_panel = Panel(
            "[bold yellow]🔧 YT-Nara Setup[/bold yellow]\n\n"
            "This will create necessary directories and configuration files.\n"
            "Make sure you have installed all dependencies from requirements.txt",
            border_style="yellow"
        )
        self.console.print(setup_panel)
        
        if Confirm.ask("Proceed with setup?", default=True):
            self.print_info("Creating directories...")
            # Create directories
            import os
            directories = ['downloads', 'edited_videos', 'logs', 'data', 'temp', 'sessions']
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                self.print_success(f"Created directory: {directory}")
            
            self.print_success("Setup completed successfully!")
        else:
            self.print_info("Setup cancelled.")