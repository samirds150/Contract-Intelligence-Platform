#!/usr/bin/env python
"""
Convert Full_Project_Guide.md to HTML with proper styling and CSS.
Open the HTML file in a browser and press Ctrl+P to print/save as PDF.
No external dependencies required.
"""

from pathlib import Path
import re

def md_to_html(md_file, html_file):
    """Convert Markdown to HTML."""
    print(f"Converting {md_file} to {html_file}...")
    
    if not Path(md_file).exists():
        print(f"Error: {md_file} not found")
        return False
    
    md_content = Path(md_file).read_text(encoding='utf-8')
    html_content = markdown_to_html(md_content)
    
    Path(html_file).write_text(html_content, encoding='utf-8')
    print(f"✓ HTML created: {html_file}")
    print(f"  Open in browser: file:///{html_file}")
    print(f"  Print to PDF: Ctrl+P (Windows/Linux) or Cmd+P (Mac)")
    return True

def markdown_to_html(md_text):
    """Convert markdown to HTML."""
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    code_lang = ''
    code_buffer = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith('```'):
            if not in_code_block:
                code_lang = stripped[3:].strip() or 'text'
                in_code_block = True
                code_buffer = []
            else:
                # End code block
                code_content = '\n'.join(code_buffer)
                html_lines.append(f'<pre><code class="language-{code_lang}">{escape_html(code_content)}</code></pre>')
                in_code_block = False
                code_lang = ''
                code_buffer = []
            continue
        
        if in_code_block:
            code_buffer.append(line)
            continue
        
        # Close list if we hit a non-list line
        if in_list and not stripped.startswith('- '):
            html_lines.append('</ul>')
            in_list = False
        
        # Headers
        if stripped.startswith('# '):
            html_lines.append(f'<h1>{markdown_inline(stripped[2:])}</h1>')
            continue
        if stripped.startswith('## '):
            html_lines.append(f'<h2>{markdown_inline(stripped[3:])}</h2>')
            continue
        if stripped.startswith('### '):
            html_lines.append(f'<h3>{markdown_inline(stripped[4:])}</h3>')
            continue
        
        # Horizontal rules
        if stripped.startswith('--') or stripped == '---':
            html_lines.append('<hr>')
            continue
        
        # Lists
        if stripped.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            list_content = markdown_inline(stripped[2:])
            html_lines.append(f'<li>{list_content}</li>')
            continue
        
        # Empty lines
        if not stripped:
            html_lines.append('')
            continue
        
        # Paragraphs
        if stripped:
            para_content = markdown_inline(stripped)
            html_lines.append(f'<p>{para_content}</p>')
    
    # Close any open list
    if in_list:
        html_lines.append('</ul>')
    
    html_body = '\n'.join(html_lines)
    
    # Wrap in HTML template with proper CSS
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contract RAG - Full Project Guide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.7;
            color: #333;
            background: #fafbfc;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        @media print {{
            body {{
                padding: 0;
                background: white;
            }}
            .container {{
                max-width: 100%;
                padding: 30px;
                box-shadow: none;
                border-radius: 0;
            }}
        }}
        
        h1 {{
            font-size: 2.8em;
            font-weight: 700;
            margin: 0.3em 0 0.4em 0;
            color: #1a1a1a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 0.3em;
            letter-spacing: -0.5px;
        }}
        
        h2 {{
            font-size: 2em;
            font-weight: 600;
            margin: 1.3em 0 0.5em 0;
            color: #0066cc;
            padding-top: 0.5em;
        }}
        
        h3 {{
            font-size: 1.45em;
            font-weight: 600;
            margin: 1em 0 0.4em 0;
            color: #0088dd;
        }}
        
        p {{
            margin: 0.9em 0;
            text-align: left;
            word-wrap: break-word;
        }}
        
        code {{
            background-color: #f0f0f0;
            color: #d73a49;
            padding: 3px 8px;
            border-radius: 3px;
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            border: 1px solid #e1e4e8;
            display: inline-block;
            white-space: nowrap;
        }}
        
        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 18px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.2em 0;
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.5;
            border-left: 5px solid #0066cc;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }}
        
        pre code {{
            background-color: transparent;
            color: inherit;
            padding: 0;
            border-radius: 0;
            border: none;
            font-size: inherit;
            display: block;
            white-space: pre;
        }}
        
        ul {{
            margin: 1em 0;
            padding-left: 0;
        }}
        
        li {{
            margin: 0.6em 0 0.6em 2.5em;
            line-height: 1.7;
            text-align: left;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
            border-bottom: 1px dotted #0066cc;
            transition: color 0.2s;
        }}
        
        a:hover {{
            color: #0052a3;
            text-decoration: underline;
        }}
        
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, #0066cc, transparent);
            margin: 2.5em 0;
        }}
        
        strong {{
            font-weight: 700;
            color: #1a1a1a;
        }}
        
        em {{
            font-style: italic;
            color: #555;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 25px;
            }}
            
            h1 {{
                font-size: 2em;
                margin: 0.2em 0 0.3em 0;
            }}
            
            h2 {{
                font-size: 1.5em;
                margin: 1em 0 0.4em 0;
            }}
            
            h3 {{
                font-size: 1.2em;
                margin: 0.8em 0 0.3em 0;
            }}
            
            pre {{
                font-size: 0.75em;
                padding: 12px;
                margin: 1em 0;
            }}
            
            li {{
                margin-left: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>
"""
    
    return html_template

def markdown_inline(text):
    """Apply inline markdown formatting (bold, italic, inline code, links)."""
    text = escape_html(text)
    
    # Bold: **text** -> <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Italic: *text* -> <em>text</em> (but not **text**)
    text = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Inline code: `text` -> <code>text</code>
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Links: [text](url) -> <a href="url">text</a>
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    return text

def escape_html(text):
    """Escape HTML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

if __name__ == '__main__':
    script_dir = Path(__file__).parent
    md_file = script_dir / 'Full_Project_Guide.md'
    html_file = script_dir / 'Full_Project_Guide.html'
    
    if md_to_html(md_file, html_file):
        print(f"\n✓ Done! View at: file:///{html_file}")
