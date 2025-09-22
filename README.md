# Outlook Account Creation Backend (Python)

A structured Python backend project for automated Outlook account creation using SeleniumBase with stealth capabilities.

## Features

- Automated Outlook account creation
- Human-like browser behavior to avoid detection
- Email variation generation for availability checking
- Press-and-hold captcha handling using pyautogui
- Form filling with React-safe input methods
- Success detection and account saving
- Modular and maintainable code structure
- UV package management for dependency handling

## Project Structure

```
outlook-backend-python/
├── src/
│   ├── main.py              # Main entry point
│   ├── helpers/
│   │   ├── browser.py       # Browser configuration and frame helpers
│   │   └── input.py         # Input handling and form interaction
│   ├── handlers/
│   │   ├── captcha.py       # Captcha detection and handling
│   │   └── form.py          # Form filling logic
│   └── utils/
│       ├── constants.py     # Configuration constants
│       ├── helpers.py       # Utility functions
│       ├── detection.py     # Step and success detection
│       └── storage.py       # File system operations
├── pyproject.toml
└── README.md
```

## Installation

1. Navigate to the project directory:
```bash
cd outlook-backend-python
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Install Chrome browser if not already installed (required for SeleniumBase)

## Usage

### Command Line Usage

```bash
# Run with command line arguments
uv run outlook-create FirstName LastName

# Or run and enter details interactively
uv run outlook-create
```

### Development Mode

You can also run the script directly:
```bash
python src/main.py FirstName LastName
```

## Configuration

The project uses various timing constants and browser arguments defined in `src/utils/constants.py`:

- **Timings**: Navigation timeouts, action delays, and verification waits
- **Browser Arguments**: Stealth configuration and human-like behavior settings
- **URLs**: Outlook signup endpoints
- **Password**: Default account password

## How It Works

1. **Browser Setup**: Launches a stealth-configured Chrome browser using SeleniumBase
2. **Navigation**: Goes to Outlook signup page
3. **Email Selection**: Tries various email variations until an available one is found
4. **Form Filling**: Progresses through password, name, and date of birth forms
5. **Captcha Handling**: Detects and solves press-and-hold captcha challenges using pyautogui
6. **Success Detection**: Monitors for successful account creation
7. **Account Saving**: Stores successful accounts in `completed.txt`

## Dependencies

- `seleniumbase`: Enhanced Selenium with built-in stealth capabilities
- `selenium`: Web automation framework
- `pyautogui`: GUI automation for captcha handling
- `pillow`: Image processing support
- `webdriver-manager`: Automatic browser driver management

## Notes

- The browser runs in non-headless mode for debugging and captcha handling
- Accounts are saved to `completed.txt` in the project root
- The script includes extensive error handling and retry logic
- Human-like timing and behavior patterns are used throughout
- Press-and-hold captcha handling requires mouse control permissions

## Differences from Node.js Version

- Uses SeleniumBase instead of Puppeteer
- Implements pyautogui for mouse control in captcha handling
- Python async/await pattern instead of JavaScript promises
- UV package management instead of npm
- Different import/export syntax

## License

ISC
