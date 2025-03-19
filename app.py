import os
from anthropic import Anthropic
import openai
from dotenv import load_dotenv
import random
import string
import re
import sys

# Load environment variables
load_dotenv()

# Initialize API clients
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')

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
    
    # Remove any markdown formatting
    code = re.sub(r'\*\*|__|\*|_|#', '', code)
    
    # Remove any explanatory text before or after the HTML
    code = re.sub(r'^.*?(?=<!DOCTYPE html>|<html)', '', code, flags=re.DOTALL)
    code = re.sub(r'</html>.*$', '</html>', code, flags=re.DOTALL)
    
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
    
    # Print the generated code
    print(generated_code)

if __name__ == "__main__":
    main() 