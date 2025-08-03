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
- Required Python packages (install via `pip3 install -r requirements.txt`)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/airborne-commando/zabasearch-auto.git
   cd zabasearch-auto
   ```

2. Install dependencies:

   ```
   python3 -m venv venv && source /venv/bin/activate && pip3 install -r requirements.txt
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
..results/zaba_results_[firstname]_[lastname].txt
```

# **NEW TOOL**

`filter.py`
A tool that can filter results for you on county and will spit out information.

Example:

      Name: first last
      Age: AGE
      
      AKA: first last
      
      Phone Numbers:
        - xxx-xxx-xxxx
      
      Email Addresses:
        - email@email.com
      
      Current Address: 1111 street street New street, Pennsylvania 00000
      Current ZIP: 15068
      Current County: Westmoreland
      
      In Target County: YES
      
      Found 3 matches in zaba_results_dev_new.txt

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
- Website robots.txt restrictions

The maintainers of this project are not responsible for any misuse of this tool.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
