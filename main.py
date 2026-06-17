import os
import sys

# Configure stdout and stderr to use UTF-8 on Windows terminal
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.proposal_engine import ProposalEngine
from src.cli_view import CLIView

def example_proposal_automation():
    """
    Example method that showcases the B2B Sales Proposal Generator.
    Loads databases, matches inbound client requirements, generates proposals
    in Markdown & HTML, and displays them via a rich console dashboard.
    """
    # Define paths to mock databases
    proposals_db = "d:\\Project\\ai_sales_assessment\\data\\past_proposals.json"
    emails_db = "d:\\Project\\ai_sales_assessment\\data\\client_emails.json"

    # Initialize the core engine
    engine = ProposalEngine(
        proposals_db_path=proposals_db,
        emails_db_path=emails_db
    )

    # Initialize the CLI View and run the interactive dashboard
    view = CLIView(engine=engine)
    view.run()

def main():
    """
    Entry point to showcase the functionality of the system.
    """
    example_proposal_automation()

if __name__ == "__main__":
    main()
