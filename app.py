import os
from anthropic import Anthropic
import openai
from dotenv import load_dotenv
import random
import string
import re
import sys
import http.server
import socketserver
import webbrowser
import tempfile
import threading
import time

# Load environment variables
load_dotenv()

# Initialize API clients
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')

def run_local_server(html_content: str, port: int = 8888):
    """Run a local HTTP server to display the generated website"""
    # Create a temporary directory to store the HTML file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the HTML content to a file
        html_path = os.path.join(temp_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Change to the temporary directory
        os.chdir(temp_dir)
        
        # Create and start the server
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"\nStarting local server at http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            
            # Open the website in the default browser
            webbrowser.open(f'http://localhost:{port}')
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                httpd.shutdown()

def generate_app_name():
    """Generate a random app name"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(8))

def clean_generated_code(code: str) -> str:
    """Clean the generated code to remove any non-coding characters and extract only HTML"""
    # Remove code block markers if present
    code = re.sub(r'```html\s*', '', code)
    code = re.sub(r'```\s*$', '', code)
    
    # Remove any leading/trailing whitespace
    code = code.strip()
    
    # Find the HTML content
    html_match = re.search(r'(?:<!DOCTYPE html>|<html).*?</html>', code, re.DOTALL)
    if html_match:
        code = html_match.group(0)
    else:
        # If no HTML structure found, wrap the content in proper HTML structure
        code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Generated Website</title>
</head>
<body>
{code}
</body>
</html>"""
    
    # Remove any markdown formatting
    code = re.sub(r'\*\*|__|\*|_|#', '', code)
    
    # Remove any explanatory text before or after the HTML
    code = re.sub(r'^.*?(?=<!DOCTYPE html>|<html)', '', code, flags=re.DOTALL)
    code = re.sub(r'</html>.*$', '</html>', code, flags=re.DOTALL)
    
    # Ensure DOCTYPE is present at the very beginning
    if not code.strip().startswith('<!DOCTYPE html>'):
        code = '<!DOCTYPE html>\n' + code
    
    return code.strip()

def generate_website_code(prompt: str) -> str:
    """Generate website code based on the user prompt using Claude."""
    system_prompt = """You are a web development expert. Generate a simple website based on the user's prompt.
    The website should:
    1. Use HTML, CSS and basic JavaScript if needed
    2. Be self-contained in a single file
    3. Have a clean, modern design
    4. Include all necessary styling inline
    5. The code must be valid HTML5 and work when opened directly in a browser
    6. The website must run on host 0.0.0.0 and port 8888
    7. Return ONLY the HTML code, no explanations or markdown
    8. The code MUST include all required HTML elements: <!DOCTYPE html>, <html>, <head>, <body>, and </html>
    """
    
    try:
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Create a simple website that displays '{prompt}'. Return only the complete HTML code with inline CSS and JavaScript. The code must be valid HTML5 and work when opened directly in a browser."
            }]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a simple website that displays '{prompt}'. Return only the complete HTML code with inline CSS and JavaScript. The code must be valid HTML5 and work when opened directly in a browser."}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return None

def validate_html(html_code: str) -> bool:
    """Basic validation of HTML code"""
    required_elements = ['<!DOCTYPE html>', '<html', '<head', '<body', '</html>']
    print("Debug - Generated HTML code:")
    print(html_code)
    print("\nDebug - Checking required elements:")
    for element in required_elements:
        found = element in html_code
        print(f"{element}: {'Found' if found else 'Missing'}")
    return all(element in html_code for element in required_elements)

def run_prompt(prompt: str, **kwargs) -> str:
    """Main function that will be called by the platform"""
    # Generate app name
    app_name = generate_app_name()
    
    # Generate website code
    html_code = generate_website_code(prompt)
    
    if not html_code:
        return "Error: Failed to generate website code"
    
    # Clean the generated code
    html_code = clean_generated_code(html_code)
    
    # Validate the generated code
    if not validate_html(html_code):
        return "Error: Generated code validation failed"
    
    # Add APP_NAME to the beginning of the code
    final_code = f"APP_NAME='{app_name}'\n\n{html_code}"
    
    return final_code

def main():
    """CLI interface for the code generator"""
    # Check if prompt was provided as command line argument
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
    else:
        prompt = input("Enter what you want to display on the website: ")
    
    # Generate the code
    generated_code = run_prompt(prompt)
    
    if generated_code.startswith("Error:"):
        print(generated_code)
        return
    
    # Extract the HTML content (remove the APP_NAME line)
    html_content = '\n'.join(generated_code.split('\n')[2:])
    
    # Ask if user wants to run the website locally
    while True:
        choice = input("\nWould you like to run the website locally? (y/n): ").lower()
        if choice in ['y', 'n']:
            break
        print("Please enter 'y' for yes or 'n' for no.")
    
    if choice == 'y':
        # Run the website locally
        run_local_server(html_content)
    else:
        # Just print the generated code
        print("\nGenerated code:")
        print(generated_code)

if __name__ == "__main__":
    main() 