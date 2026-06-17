import sys
import time
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Prompt, IntPrompt
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax

from src.proposal_engine import ProposalEngine
from src.utils import save_proposal_markdown

console = Console()

class CLIView:
    def __init__(self, engine: ProposalEngine):
        self.engine = engine

    def draw_header(self):
        console.clear()
        console.print(
            Panel.fit(
                "[bold white]  APEX SOFTWARE SOLUTIONS  [/bold white]\n"
                "[bold cyan]🤖 AI-Powered Sales Proposal Automation Assistant[/bold cyan]",
                border_style="cyan",
                padding=(1, 5)
            )
        )
        console.print("\n[dim]Workspace loaded successfully. Historical database connected.[/dim]\n")

    def show_emails_table(self, emails: List[Dict[str, Any]]) -> int:
        table = Table(title="Incoming Client Requirements (Inbound Emails)", expand=True)
        table.add_column("No.", style="cyan", width=4, justify="center")
        table.add_column("Sender", style="green", width=20)
        table.add_column("Company", style="bold yellow", width=18)
        table.add_column("Subject", style="white")
        table.add_column("Date", style="dim", width=12)

        for idx, email in enumerate(emails, 1):
            table.add_row(
                str(idx),
                email["sender_name"],
                email["company"],
                email["subject"],
                email["date"]
            )

        console.print(table)
        console.print()
        
        choice = IntPrompt.ask(
            "[bold white]Select an email number to review & generate proposal[/bold white]",
            choices=[str(i) for i in range(1, len(emails) + 1)],
            default=1
        )
        return choice - 1

    def display_email_contents(self, email: Dict[str, Any]):
        body_panel = Panel(
            email["body"],
            title=f"[bold green]{email['sender_name']} ({email['company']})[/bold green]",
            subtitle=f"[dim]{email['subject']} | {email['date']}[/dim]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(body_panel)
        console.print()

    def run_pipeline(self, email: Dict[str, Any]):
        console.print("[bold yellow]🚀 Initiating Automated Proposal Pipeline...[/bold yellow]\n")

        # Step 1: Parse details
        with console.status("[bold cyan]Step 1: AI Engine Parsing Requirements...[/bold cyan]") as status:
            time.sleep(1.5)
            details = self.engine.parse_client_details(email)
        
        parse_table = Table(title="Extracted Client Specifications", show_header=False, box=None)
        parse_table.add_row("[bold cyan]Client Contact:[/bold cyan]", details["client_name"])
        parse_table.add_row("[bold cyan]Company:[/bold cyan]", details["company_name"])
        parse_table.add_row("[bold cyan]Stated Budget:[/bold cyan]", f"[bold green]{details['extracted_budget']}[/bold green]")
        parse_table.add_row("[bold cyan]Expected Timeline:[/bold cyan]", f"[bold yellow]{details['extracted_timeline']}[/bold yellow]")
        
        console.print(Panel(parse_table, border_style="cyan", title="[bold cyan]1. Requirement Extraction[/bold cyan]"))
        console.print()

        # Step 2: Match Proposal
        with console.status("[bold magenta]Step 2: Searching Database for Historical Matches...[/bold magenta]") as status:
            time.sleep(1.5)
            matched_prop, match_score = self.engine.match_proposal(email["body"])

        if matched_prop:
            match_table = Table(show_header=False, box=None)
            match_table.add_row("[bold magenta]Reference Title:[/bold magenta]", matched_prop["title"])
            match_table.add_row("[bold magenta]Category:[/bold magenta]", matched_prop["category"])
            match_table.add_row("[bold magenta]Match Score:[/bold magenta]", f"[bold green]{match_score:.1%}[/bold green]")
            match_table.add_row("[bold magenta]Standard Pricing:[/bold magenta]", f"${matched_prop['cost_usd']:,} USD")
            match_table.add_row("[bold magenta]Standard Duration:[/bold magenta]", f"{matched_prop['timeline_weeks']} weeks")
            
            console.print(Panel(match_table, border_style="magenta", title="[bold magenta]2. Semantic Matching Result[/bold magenta]"))
        else:
            console.print("[bold red]No historical proposals matched this inquiry. Creating from scratch.[/bold red]")
            return
        console.print()

        # Step 3: Synthesis
        api_key_status = "[bold green]Active (Using Gemini API)[/bold green]" if self.engine.api_key else "[bold yellow]None Detected (Using Local Template Fallback)[/bold yellow]"
        console.print(f"GenAI Account Key: {api_key_status}")
        
        with console.status("[bold green]Step 3: Synthesizing Custom B2B Sales Proposal...[/bold green]") as status:
            time.sleep(2.5)
            proposal_md, used_api = self.engine.generate_proposal(email, matched_prop, details)

        source_tag = "[bold green]Gemini 1.5 Flash[/bold green]" if used_api else "[bold yellow]Local Proposal Synthesizer[/bold yellow]"
        console.print(f"\n[bold green]✓ Synthesis Complete![/bold green] (Generated via {source_tag})")
        
        # Save files
        client_clean = details["company_name"].lower().replace(" ", "_")
        md_filename = f"proposal_{client_clean}.md"
        
        md_path = f"d:\\Project\\ai_sales_assessment\\output\\{md_filename}"
        
        save_proposal_markdown(proposal_md, md_path)
        
        # Display output summary
        summary_table = Table(title="Generated Deliverables", box=None, show_header=False)
        summary_table.add_row("[bold white]Markdown Source:[/bold white]", f"[underline cyan]{md_path}[/underline cyan]")
        summary_table.add_row("[bold white]Status:[/bold white]", "[bold green]Saved & Ready[/bold green]")
        
        console.print(Panel(summary_table, border_style="green", title="[bold green]3. Proposal Generation Summary[/bold green]"))
        console.print()

        view_draft = Prompt.ask(
            "[bold white]Would you like to preview the generated proposal draft directly in the terminal?[/bold white] (y/n)",
            choices=["y", "n"],
            default="y"
        )
        
        if view_draft.lower() == "y":
            console.clear()
            console.print(Panel(f"[bold]Previewing: {md_filename}[/bold]\n", style="bold cyan"))
            
            # Syntax highlight
            syntax = Syntax(proposal_md, "markdown", theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print()
            Prompt.ask("[bold white]Press Enter to return to main dashboard[/bold white]")

    def run(self):
        while True:
            self.draw_header()
            emails = self.engine.get_emails()
            
            if not emails:
                console.print("[bold red]Error: No client emails found in database.[/bold red]")
                break
                
            email_idx = self.show_emails_table(emails)
            selected_email = emails[email_idx]
            
            self.draw_header()
            self.display_email_contents(selected_email)
            
            self.run_pipeline(selected_email)
            
            keep_running = Prompt.ask(
                "\n[bold white]Process another inquiry?[/bold white] (y/n)",
                choices=["y", "n"],
                default="y"
            )
            if keep_running.lower() != "y":
                break
                
        console.print("\n[bold green]Thank you for using Apex Sales Automation![/bold green] Exiting dashboard.\n")
