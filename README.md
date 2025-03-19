# Website Generator

A Python application that generates websites based on user prompts using AI (Claude and GPT-4).

## Features

- Generate websites from text prompts
- Local preview server
- Support for both Claude and GPT-4
- Modern, clean website designs
- Self-contained HTML output

## Prerequisites

- Python 3.7+
- Anthropic API key (for Claude)
- OpenAI API key (for GPT-4)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Shresth0710/website_generator.git
cd website_generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

1. Run the application:
```bash
python app.py
```

2. Enter your prompt when asked, or provide it as a command-line argument:
```bash
python app.py "Your website prompt here"
```

3. Choose whether to run the website locally:
   - Enter 'y' to start a local server and view the website
   - Enter 'n' to just get the generated code

## Local Development

The application includes a local development server that runs on port 8888 by default. When you choose to run the website locally:
- The server will start automatically
- Your default browser will open to show the website
- Press Ctrl+C to stop the server

## Security Notes

- Never commit your `.env` file or expose your API keys
- The `.env` file is included in `.gitignore` to prevent accidental commits
- Use `.env.example` as a template for setting up your environment variables

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 