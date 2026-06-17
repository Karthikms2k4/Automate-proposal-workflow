import os
import json
import re
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProposalEngine:
    def __init__(self, proposals_db_path: str, emails_db_path: str):
        self.proposals_db_path = proposals_db_path
        self.emails_db_path = emails_db_path
        self.past_proposals = self._load_json(proposals_db_path)
        self.client_emails = self._load_json(emails_db_path)
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return []

    def get_emails(self) -> List[Dict[str, Any]]:
        return self.client_emails

    def match_proposal(self, email_body: str) -> Tuple[Dict[str, Any], float]:
        """
        Calculates a similarity score between the client email requirements
        and each past proposal using tech stack overlap and keyword matches.
        Returns the best matching proposal and its score.
        """
        best_match = None
        best_score = -1.0
        
        email_lower = email_body.lower()
        
        for prop in self.past_proposals:
            score = 0.0
            
            # 1. Tech Stack overlaps
            tech_matches = 0
            for tech in prop["tech_stack"]:
                if tech.lower() in email_lower:
                    tech_matches += 1
                    score += 2.0  # High weight for matching technology
            
            # 2. Industry / Category keywords
            category_keywords = {
                "E-Commerce": ["retail", "ecommerce", "storefront", "shopify", "cart", "checkout", "stripe", "buy"],
                "Enterprise Integrations": ["crm", "erp", "salesforce", "middleware", "sync", "api integration", "integration"],
                "DevOps & Cloud Infrastructure": ["aws", "cloud", "migrate", "migration", "terraform", "kubernetes", "eks", "ci/cd", "pipeline", "docker"],
                "IoT & Telemetry": ["iot", "fleet", "telematics", "tracking", "mqtt", "telemetry", "real-time", "timescale", "sensor"]
            }
            
            category = prop["category"]
            if category in category_keywords:
                for kw in category_keywords[category]:
                    if kw in email_lower:
                        score += 1.0
            
            # Normalize score
            total_elements = len(prop["tech_stack"]) + len(category_keywords.get(category, []))
            normalized_score = (score / total_elements) if total_elements > 0 else 0.0
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_match = prop
                
        return best_match, best_score

    def parse_client_details(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts key client details from the email using simple regex rules.
        This provides structured context for both template fallback and LLM.
        """
        body = email["body"]
        
        # Extract budget (e.g., "$75k to $90k", "$45k-$55k")
        budget_match = re.search(r"(\$\d+\s*[kK]?\s*(?:to|-)\s*\$\d+\s*[kK]?|\$\d+\s*[kK]?)", body)
        budget = budget_match.group(0) if budget_match else "TBD (Targeting client expectations)"
        
        # Extract timeline (e.g., "4 months", "2-3 months", "5 months")
        timeline_match = re.search(r"(\d+\s*(?:to|-)?\s*\d*\s*(?:months|weeks|month|week))", body)
        timeline = timeline_match.group(0) if timeline_match else "TBD"

        return {
            "client_name": email.get("sender_name", "Valued Client"),
            "sender_email": email.get("sender"),
            "company_name": email.get("company", "Prospect Corporation"),
            "extracted_budget": budget,
            "extracted_timeline": timeline,
            "project_subject": email.get("subject", "Development Services Proposal")
        }

    def generate_proposal(self, email: Dict[str, Any], matched_proposal: Dict[str, Any], details: Dict[str, Any]) -> Tuple[str, bool]:
        """
        Generates the proposal. If a Gemini API key is configured, uses Gemini.
        Otherwise, falls back to a high-fidelity template simulator.
        Returns a tuple: (proposal_markdown, is_api_call).
        """
        if self.api_key:
            try:
                return self._generate_with_gemini(email, matched_proposal, details), True
            except Exception as e:
                print(f"\n[bold yellow]Warning: Gemini API call failed ({e}). Falling back to Template Simulator.[/bold yellow]")
                return self._generate_with_template(email, matched_proposal, details), False
        else:
            return self._generate_with_template(email, matched_proposal, details), False

    def _generate_with_gemini(self, email: Dict[str, Any], matched_proposal: Dict[str, Any], details: Dict[str, Any]) -> str:
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        
        # Set up model configuration
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
You are an expert Principal Solutions Architect and Sales Engineer at "Apex Software Solutions".
Your task is to write a highly professional, tailored B2B Sales Proposal for a new client based on their email inquiry and a reference historical proposal.

Here is the details of the incoming client email:
- Sender Name: {details['client_name']}
- Sender Email: {details['sender_email']}
- Client Company: {details['company_name']}
- Subject: {details['project_subject']}
- Email Body:
\"\"\"
{email['body']}
\"\"\"

Here is a reference historical proposal that is highly relevant to this project type:
- Reference Title: {matched_proposal['title']}
- Reference Tech Stack: {', '.join(matched_proposal['tech_stack'])}
- Reference Scope: {json.dumps(matched_proposal['scope'], indent=2)}
- Reference Deliverables: {json.dumps(matched_proposal['deliverables'], indent=2)}
- Reference Timeline: {matched_proposal['timeline_weeks']} weeks
- Reference Cost: ${matched_proposal['cost_usd']:,} USD
- Reference Resource Plan: {json.dumps(matched_proposal['resource_plan'], indent=2)}

INSTRUCTIONS FOR GENERATION:
1. Write a formal, comprehensive Sales Proposal in Markdown.
2. Personalize it for {details['company_name']} (addressed to {details['client_name']}).
3. Extract features requested in the client email that might not be in the reference proposal (e.g. if they requested integration with Salesforce CRM, add it to the tech stack and scope) and tailor the proposal specifically.
4. Scale the timeline and budget to be realistic and align with the client's stated expectation if possible (Stated Budget: {details['extracted_budget']}, Stated Timeline: {details['extracted_timeline']}). Break down the cost logically.
5. Do NOT include any place-holders (like [Client Name] or [Insert Date]). Use the provided values. Use 2026 for the date.
6. The proposal MUST contain the following sections:
   - Header with Date, Client Info, and Title
   - 1. Executive Summary: Personalized greeting, understanding of their business goals, and value proposition.
   - 2. Objectives & Scope of Work: Bullet points showing the tailored scope of work. Add the specific integration requested.
   - 3. Technology Stack: Bullet points of the proposed technologies (tailored to client's requirements).
   - 4. Key Deliverables: Standardized list of project outcomes.
   - 5. Team & Resource Allocation: Roles and levels of involvement.
   - 6. Project Timeline & Milestones: Structured phase timeline (e.g., Phase 1: Planning, Phase 2: Design, etc.) mapping to the timeline.
   - 7. Commercials & Cost Breakdown: A detailed cost breakdown matching the final estimated price.
7. Return ONLY the markdown text of the proposal. Do not wrap it in ```markdown blocks. Keep the formatting clean and elegant.
"""
        response = model.generate_content(prompt)
        return response.text

    def _generate_with_template(self, email: Dict[str, Any], matched_proposal: Dict[str, Any], details: Dict[str, Any]) -> str:
        """
        High-fidelity template simulator that constructs an outstanding,
        dynamically customized proposal when the Gemini API is not available.
        """
        # Tailor scope items based on email body
        tailored_scope = list(matched_proposal["scope"])
        
        # Check for specific integrations requested in email but not in matched proposal
        email_lower = email["body"].lower()
        if "salesforce" in email_lower and not any("salesforce" in item.lower() for item in tailored_scope):
            tailored_scope.append("Integrate Salesforce CRM to synchronize client accounts and automate sales handoffs.")
        if "crm" in email_lower and not any("crm" in item.lower() for item in tailored_scope) and not "salesforce" in email_lower:
            tailored_scope.append("Establish secure API syncing with client's active CRM platform.")
        
        # Adjust timeline and cost based on details
        timeline_str = details["extracted_timeline"]
        budget_str = details["extracted_budget"]
        
        # Clean pricing estimation from budget string
        # Default to matched proposal cost, or parse client budget
        cost_val = matched_proposal["cost_usd"]
        if "75" in budget_str or "90" in budget_str:
            cost_val = 82000
            timeline_str = "16 weeks (approx. 4 months)"
        elif "45" in budget_str or "55" in budget_str:
            cost_val = 48000
            timeline_str = "10 weeks (approx. 2.5 months)"
        elif "months" in timeline_str:
            # e.g., 5 months -> 20 weeks
            months = re.findall(r"\d+", timeline_str)
            if months:
                weeks = int(months[0]) * 4
                timeline_str = f"{weeks} weeks ({timeline_str})"
        
        # Format tech stack
        tech_list = list(matched_proposal["tech_stack"])
        if "salesforce" in email_lower and "salesforce api" not in [t.lower() for t in tech_list]:
            tech_list.append("Salesforce API / REST Connector")
            
        # Build tech stack markdown
        tech_md = ""
        for t in tech_list:
            tech_md += f"*   **{t}**: Industry standard implementation.\n"

        # Build resources markdown
        resources_md = ""
        for res in matched_proposal["resource_plan"]:
            resources_md += f"*   **{res['role']}**: {res['count']}x ({res['involvement']})\n"
            
        # Build deliverables markdown
        deliverables_md = ""
        for idx, item in enumerate(matched_proposal["deliverables"], 1):
            deliverables_md += f"{idx}.  **{item.split(' - ')[0]}**: {item}\n"
            
        # Build scope markdown
        scope_md = ""
        for item in tailored_scope:
            scope_md += f"*   {item}\n"

        markdown_proposal = f"""# B2B SERVICES PROPOSAL

**Prepared For:** {details['company_name']}
**Primary Contact:** {details['client_name']} ({details['sender_email']})
**Date:** June 17, 2026
**Prepared By:** Apex Software Solutions Sales & Architecture Team
**Project Name:** {matched_proposal['title']} for {details['company_name']}

---

## 1. Executive Summary
Dear {details['client_name']},

Thank you for reaching out to Apex Software Solutions. We are excited about the opportunity to partner with {details['company_name']} to execute the **{matched_proposal['title']}** initiative.

Based on your inquiry, we understand that your core objective is to deliver a robust, modern solution that solves your current operational bottlenecks. We have designed a project scope that specifically aligns with your expectations, utilizing a modern, proven architecture to ensure scalability, security, and fast loading speeds. 

We bring extensive expertise in developing B2B enterprise systems and consumer platforms, and we have successfully completed similar projects in the past. This proposal outlines our engineering approach, resource plan, milestone timeline, and investment breakdown.

---

## 2. Project Scope & Architecture
Our engineering team will build and deploy the solution according to the following key scopes:

{scope_md}
---

## 3. Technology Stack
We propose a modern, secure, and developer-friendly stack to ensure long-term maintainability:

{tech_md}
---

## 4. Key Deliverables
Upon completion of the project, {details['company_name']} will receive the following deliverables:

{deliverables_md}
---

## 5. Team & Resource Allocation
To ensure rapid execution and adherence to quality standards, we are allocating the following dedicated specialists to this project:

{resources_md}
---

## 6. Project Timeline & Milestones
We estimate the total project duration to be **{timeline_str}**, divided into distinct agile milestones:

*   **Milestone 1: Discovery & System Design (Weeks 1-2)**
    *   Requirement refinement, database schemas mapping, Figma wireframes finalization.
*   **Milestone 2: Core Infrastructure & Backend API Development (Weeks 3-6)**
    *   Database deployment, API design, middleware configuration, core backend setup.
*   **Milestone 3: UI Design & Integration (Weeks 7-12)**
    *   Frontend application build, API bindings, system integration, CRM/external data sync.
*   **Milestone 4: Testing & Hardening (Weeks 13-14)**
    *   Quality assurance scripts run, performance optimization, load testing.
*   **Milestone 5: Handoff & Launch (Weeks 15-16)**
    *   Production environment rollout, data seeding, credentials handoff.

---

## 7. Commercials & Cost Breakdown
The total investment for this project is estimated at **${cost_val:,} USD**, billed against milestone completions:

| Project Phase | Deliverable Link | Percentage | Amount (USD) |
| :--- | :--- | :---: | :---: |
| **Project Kickoff** | Signed contract & project setup | 20% | ${int(cost_val * 0.2):,} USD |
| **Milestone 2 Completion** | Backend database & API framework ready | 30% | ${int(cost_val * 0.3):,} USD |
| **Milestone 3 Completion** | Frontend integration & core features | 30% | ${int(cost_val * 0.3):,} USD |
| **Final Release** | QA approval, handoff & launch | 20% | ${int(cost_val * 0.2):,} USD |
| **Total Project Cost** | **Fully Managed Handoff** | **100%** | **${cost_val:,} USD** |

We look forward to working with the {details['company_name']} team. If you have any questions, please let us know.
"""
        return markdown_proposal.strip()
