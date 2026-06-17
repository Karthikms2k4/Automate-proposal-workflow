import os
import markdown

def save_proposal_markdown(markdown_content: str, output_path: str):
    """
    Saves the proposal in Markdown format to the specified path.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error saving Markdown proposal: {e}")

def convert_markdown_to_html(markdown_content: str, output_path: str, client_name: str):
    """
    Converts a Markdown proposal into a premium, styled HTML document.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Enable table extensions and lists extensions for Markdown
        html_body = markdown.markdown(
            markdown_content, 
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Wrap HTML in a premium template
        html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Software Solutions - Proposal for {client_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #4F46E5;         /* Indigo */
            --primary-hover: #4338CA;
            --primary-light: #EEF2FF;
            --secondary: #06B6D4;       /* Cyan */
            --success: #10B981;
            --text-main: #1F2937;
            --text-muted: #4B5563;
            --bg-main: #F3F4F6;
            --bg-card: #FFFFFF;
            --border: #E5E7EB;
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            line-height: 1.6;
            padding: 40px 20px;
        }}

        .proposal-container {{
            max-width: 850px;
            margin: 0 auto;
            background: var(--bg-card);
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        .brand-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            padding: 40px 48px;
            color: white;
            position: relative;
        }}

        .brand-logo {{
            font-weight: 800;
            font-size: 1.5rem;
            letter-spacing: -0.5px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .brand-logo-icon {{
            width: 24px;
            height: 24px;
            background: white;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-weight: 900;
            font-size: 0.95rem;
        }}

        .brand-header h1 {{
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 8px;
            color: white;
        }}

        .brand-header p {{
            color: rgba(255, 255, 255, 0.85);
            font-weight: 500;
            font-size: 1rem;
        }}

        .proposal-body {{
            padding: 48px;
        }}

        /* Typography overrides for markdown rendering */
        .proposal-body h1 {{
            display: none; /* Hide top header from markdown since we have custom header */
        }}

        .proposal-body h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #111827;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--primary-light);
            display: flex;
            align-items: center;
        }}
        
        .proposal-body h2::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 1.25rem;
            background-color: var(--primary);
            margin-right: 10px;
            border-radius: 2px;
        }}

        .proposal-body h3 {{
            font-size: 1.15rem;
            font-weight: 600;
            color: #374151;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .proposal-body p {{
            margin-bottom: 1.25rem;
            color: var(--text-muted);
            font-size: 0.975rem;
        }}

        .proposal-body hr {{
            margin: 2.5rem 0;
            border: 0;
            border-top: 1px solid var(--border);
        }}

        .proposal-body ul, .proposal-body ol {{
            margin-bottom: 1.5rem;
            padding-left: 24px;
            color: var(--text-muted);
            font-size: 0.975rem;
        }}

        .proposal-body li {{
            margin-bottom: 0.5rem;
        }}

        .proposal-body strong {{
            color: #111827;
            font-weight: 600;
        }}

        /* Interactive custom components */
        .proposal-body blockquote {{
            background: var(--primary-light);
            border-left: 4px solid var(--primary);
            padding: 16px 24px;
            border-radius: 0 8px 8px 0;
            margin: 1.5rem 0;
        }}

        .proposal-body blockquote p {{
            color: var(--primary);
            font-weight: 500;
            margin-bottom: 0;
        }}

        /* Table design */
        .proposal-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            font-size: 0.95rem;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }}

        .proposal-body th {{
            background-color: var(--primary-light);
            color: var(--primary);
            font-weight: 600;
            text-align: left;
            padding: 14px 18px;
            border-bottom: 2px solid var(--border);
        }}

        .proposal-body td {{
            padding: 14px 18px;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
        }}

        .proposal-body tr:last-child td {{
            border-bottom: none;
        }}

        .proposal-body tr:nth-child(even) {{
            background-color: #F9FAFB;
        }}

        /* Interactive Footer buttons */
        .no-print {{
            max-width: 850px;
            margin: 0 auto 20px auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 10px;
        }}

        .btn {{
            text-decoration: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            border: none;
        }}

        .btn-primary {{
            background-color: var(--primary);
            color: white;
        }}

        .btn-primary:hover {{
            background-color: var(--primary-hover);
        }}

        .btn-outline {{
            background-color: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border);
        }}

        .btn-outline:hover {{
            background-color: #F9FAFB;
            color: var(--text-main);
        }}

        @media print {{
            .no-print {{
                display: none;
            }}
            body {{
                background-color: white;
                padding: 0;
            }}
            .proposal-container {{
                box-shadow: none;
                border: none;
                max-width: 100%;
            }}
            .brand-header {{
                background: white !important;
                color: black !important;
                border-bottom: 2px solid black;
                padding: 20px 0;
            }}
            .brand-logo-icon {{
                border: 1px solid black;
                color: black;
            }}
            .brand-header h1 {{
                color: black !important;
            }}
            .brand-header p {{
                color: black !important;
            }}
            .proposal-body {{
                padding: 20px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <a href="#" class="btn btn-outline" onclick="window.history.back(); return false;">← Back to App</a>
        <button class="btn btn-primary" onclick="window.print();">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5 1a2 2 0 0 0-2 2v2H2a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1v1a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-1h1a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-1V3a2 2 0 0 0-2-2H5zM4 3a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2H4V3zm1 5a2.5 2.5 0 1 1 5 0 2.5 2.5 0 0 1-5 0z"/>
            </svg>
            Export / Print Proposal
        </button>
    </div>

    <div class="proposal-container">
        <div class="brand-header">
            <div class="brand-logo">
                <span class="brand-logo-icon">A</span> Apex Software Solutions
            </div>
            <h1>B2B Services Proposal</h1>
            <p>Tailored Solutions. Engineered for Growth.</p>
        </div>
        <div class="proposal-body">
            {html_body}
        </div>
    </div>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_document)
    except Exception as e:
        print(f"Error converting Markdown to HTML: {e}")
