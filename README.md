# ZabaSearch Web Scraper

A Selenium-based web scraper for extracting people search results from ZabaSearch.com with human-like interaction patterns and error handling.

## Features

- Automated search on ZabaSearch.com with configurable inputs
- Human-like delays and interaction patterns to avoid detection
- Robust error handling with fallback mechanisms
- Consent modal handling with multiple interaction approaches
- Results saving to individual text files
- Configurable Chrome options for stealth browsing

## Prerequisites

- Python 3.6+
- Chrome browser installed
- ChromeDriver matching your Chrome version
- Required Python packages (install via `pip install -r requirements.txt`)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/airborne-commando/zabasearch-auto.git
   cd zabasearch-auto
   ```

2. Install dependencies:

   ```
   python3 -m venv venv && source /venv/bin/activate && pip install -r requirements.txt
   ```

3. Download ChromeDriver:
   - Get the appropriate version from https://chromedriver.chromium.org/
   - Place it in `/usr/bin/chromedriver` or update the path in the script

## Usage

### Single Search Mode
Run the script and choose manual input when prompted:
```
python ZabaSearch-auto.py
```

### Batch Search Mode
1. Prepare a CSV or tab-delimited text file with the following format:
   ```
   first_name,last_name,city,state
   John,Doe,New York,NY
   Jane,Smith,Los Angeles,CA
   ```

2. Run the script and choose file input when prompted:
``` 
python ZabaSearch-auto.py
```

### Input File Format
The script accepts both CSV and tab-delimited files with the following columns:
1. First Name (required)
2. Last Name (required)
3. City (optional)
4. State (optional)

## Configuration

You can modify the following parameters in the script:
- `chrome_driver_path`: Path to your ChromeDriver executable
- Human delay timing in the `human_delay()` function
- Chrome options in the `main()` function

## Output

Results are saved as individual text files named:
```
zaba_results_[firstname]_[lastname].txt
```

## Troubleshooting

      Error handling consent modal: Message: 
      Stacktrace:
      #0 0x558f1c59f26a <unknown>
      #1 0x558f1c049ab0 <unknown>
      #2 0x558f1c09b6f0 <unknown>
      #3 0x558f1c09b8e1 <unknown>
      #4 0x558f1c0e9b94 <unknown>
      #5 0x558f1c0c11cd <unknown>
      #6 0x558f1c0e6fee <unknown>
      #7 0x558f1c0c0f73 <unknown>
      #8 0x558f1c08daeb <unknown>
      #9 0x558f1c08e751 <unknown>
      #10 0x558f1c563b7b <unknown>
      #11 0x558f1c567959 <unknown>
      #12 0x558f1c54a959 <unknown>
      #13 0x558f1c568518 <unknown>
      #14 0x558f1c52f10f <unknown>
      #15 0x558f1c58c918 <unknown>
      #16 0x558f1c58caf6 <unknown>
      #17 0x558f1c59e586 <unknown>
      #18 0x7f54758a07eb <unknown>
      #19 0x7f547592418c <unknown>

If it's multiple items in a CSV file, you can safely ignore. It's just trying to find the consent button which no longer exists (it was already clicked).

## Anti-Detection Features

- Randomized user-agent strings
- Human-like typing delays and interaction patterns
- JavaScript-based element interaction
- Screenshot capture on errors
- Randomized delays between searches (10-30 seconds)

## Error Handling

The script includes:
- Multiple fallback mechanisms for element interaction
- Screenshot capture when errors occur
- Retry logic for form submission
- Graceful handling of missing elements

## Legal Notice

Please use this script responsibly and in compliance with:
- ZabaSearch's Terms of Service
- Applicable laws and regulations in your jurisdiction
- Computer Fraud and Abuse Act (CFAA)
- Website robots.txt restrictions

The maintainers of this project are not responsible for any misuse of this tool.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
