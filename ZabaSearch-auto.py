from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import os
import re
from typing import List, Dict, Optional

# Constants
CHROME_DRIVER_PATH = '/usr/bin/chromedriver'
JUNK_FILE_SIZE = 2252  # 2.2 KiB
JUNK_PATTERNS = (
    "Status: 404, NOT FOUND",
    "Search Error",
    "Please try again",
    "No records found",
    "No matches found"
)
USER_AGENT = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,115)}.0.0.0 Safari/537.36"
BASE_URL = 'https://www.zabasearch.com/'

def human_delay(min_delay: float = 0.5, max_delay: float = 2.5) -> None:
    """Random delay to mimic human behavior."""
    time.sleep(random.uniform(min_delay, max_delay))

def is_junk_file(file_path: str) -> bool:
    """Check if file is junk based on size."""
    try:
        return os.path.getsize(file_path) == JUNK_FILE_SIZE
    except OSError:
        return False

def is_junk_content(content: str) -> bool:
    """Check if content contains junk patterns."""
    return any(pattern in content for pattern in JUNK_PATTERNS)

def check_and_remove_junk_files(filename: str) -> bool:
    """Check and remove junk files."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
                if is_junk_file(filename) or is_junk_content(content):
                    print(f"Removing junk file: {filename}")
                    os.remove(filename)
                    return True
        except OSError:
            pass
    return False

def extract_relevant_info(content: str) -> str:
    """Extract specified fields from Zabasearch results."""
    soup = BeautifulSoup(content, 'html.parser')
    relevant_info = []
    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
    
    for person in soup.find_all('div', class_='person'):
        # Extract name
        if name_tag := person.find('h2'):
            if name_a := name_tag.a:
                relevant_info.append(f"Name: {name_a.get_text(strip=True)}")
        
        # Extract age
        if age_tag := person.find('h3'):
            relevant_info.append(f"Age: {age_tag.get_text(strip=True)}")
        
        # Extract AKA/Aliases
        if aka_div := person.find('div', id='container-alt-names'):
            aliases = [li.get_text(strip=True) for li in aka_div.find_all('li')]
            if aliases:
                relevant_info.append("AKA: " + ", ".join(aliases))
        
        # Extract phone numbers
        if phones_div := person.find('h3', string='Associated Phone Numbers'):
            if phones_ul := phones_div.find_next('ul'):
                phones = [a.get_text(strip=True) for a in phones_ul.find_all('a')]
                if phones:
                    relevant_info.append("Associated Phone Numbers: " + ", ".join(phones))
        
        # Extract email addresses
        if emails_div := person.find('h3', string='Associated Email Addresses'):
            if emails_ul := emails_div.find_next('ul'):
                emails = [
                    email_match.group(0)
                    for li in emails_ul.find_all('li')
                    if '@' in (email_text := li.get_text(strip=True))
                    for email_match in [email_pattern.search(email_text)]
                    if email_match
                ]
                if emails:
                    relevant_info.append("Associated Email Addresses: " + ", ".join(emails))
        
        # Extract last known address
        if address_div := person.find('h3', string='Last Known Address'):
            if address_p := address_div.find_next('p'):
                address = address_p.get_text(" ", strip=True).replace("\n", "").replace("  ", " ")
                relevant_info.append("Last Known Address: " + address)
        
        # Extract past addresses
        if past_addresses_div := person.find('h3', string='Past Addresses'):
            if past_addresses_ul := past_addresses_div.find_next('ul'):
                past_addresses = [
                    li.get_text(" ", strip=True).replace("\n", " ").replace("  ", " ")
                    for li in past_addresses_ul.find_all('li')
                ]
                if past_addresses:
                    relevant_info.append("Past Addresses:\n" + "\n".join(past_addresses))
        
        relevant_info.append("\n" + "-"*50 + "\n")
    
    # Remove last separator if exists
    if relevant_info and relevant_info[-1].strip() == '-'*50:
        relevant_info = relevant_info[:-1]
    
    return '\n'.join(relevant_info)

def save_results(filename: str, content: str) -> bool:
    """Save filtered results to file."""
    if not content or is_junk_content(content):
        print(f"Not saving junk content to {filename}")
        return False
    
    try:
        filtered_content = extract_relevant_info(content)
        with open(filename, 'w') as f:
            f.write(filtered_content)
        
        if is_junk_file(filename) or is_junk_content(open(filename).read()):
            print(f"Removing junk file after verification: {filename}")
            os.remove(filename)
            return False
            
        return True
    except OSError as e:
        print(f"Error saving results: {e}")
        return False

def read_input_from_file(file_path: str) -> List[Dict[str, str]]:
    """Read input data from file."""
    with open(file_path, 'r') as file:
        return [
            {
                'first_name': parts[0],
                'last_name': parts[1],
                'city': parts[2] if len(parts) > 2 else "",
                'state': parts[3] if len(parts) > 3 else ""
            }
            for line in file
            if not line.startswith(("First Name", "first_name")) and line.strip()
            for delimiter in ('\t' if '\t' in line else ',')
            for parts in [line.strip().split(delimiter)]
            if len(parts) >= 2
        ]

def handle_consent_modal(driver: webdriver.Chrome) -> bool:
    """Handle consent modal if it appears."""
    try:
        # Try to find and close the modal using different approaches
        try:
            # First approach - click agree button directly
            agree_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".inside-copy")))
            driver.execute_script("arguments[0].click();", agree_button)
            human_delay()
            return True
        except TimeoutException:
            # Second approach - check checkbox then click agree
            checkbox = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#security-check .check-wrapper")))
            driver.execute_script("arguments[0].click();", checkbox)
            human_delay(0.5, 1)
            
            agree_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".inside-copy")))
            driver.execute_script("arguments[0].click();", agree_button)
            human_delay()
            return True
            
    except Exception as e:
        print(f"Error handling consent modal: {str(e)}")
        # Try refreshing the page as a fallback
        try:
            driver.refresh()
            human_delay(2, 3)
            return True
        except Exception as refresh_error:
            print(f"Failed to refresh page: {refresh_error}")
            return False

def perform_search(input_data: Dict[str, str], driver: webdriver.Chrome) -> Optional[str]:
    """Perform search with given input data."""
    def fill_field(selector: str, value: str) -> bool:
        for attempt in range(3):
            try:
                field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                field.clear()
                field.send_keys(value)
                human_delay(0.5, 1.5)
                return True
            except Exception as e:
                if attempt == 2:
                    print(f"Failed to fill {selector}: {e}")
                    return False
                time.sleep(1)
        return False
    
    try:
        if not fill_field(".search-first-name", input_data['first_name']):
            return None
        if not fill_field(".search-last-name", input_data['last_name']):
            return None
            
        if input_data['city']:
            fill_field(".search-city", input_data['city'])
            
        if input_data['state']:
            try:
                state_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-state")))
                Select(state_element).select_by_visible_text(input_data['state'])
                human_delay(1, 2)
            except Exception as e:
                print(f"Couldn't select state: {e}")

        for attempt in range(2):
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".button-search"))).click()
                break
            except:
                if attempt == 1:
                    print("Failed to submit search form")
                    return None
                time.sleep(2)

        try:
            WebDriverWait(driver, random.uniform(5, 10)).until(
                lambda d: "results" in d.current_url.lower() or 
                d.find_elements(By.CSS_SELECTOR, ".results-container"))
        except:
            pass

        return driver.page_source

    except Exception as e:
        print(f"Search error: {e}")
        driver.save_screenshot(f"search_error_{time.time()}.png")
        return None

def create_driver() -> webdriver.Chrome:
    """Create and configure Chrome WebDriver."""
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    
    # Headless mode settings
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-agent={USER_AGENT}")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": USER_AGENT})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def reset_browser(driver: webdriver.Chrome) -> bool:
    """Reset the browser by clearing cookies and refreshing."""
    try:
        driver.delete_all_cookies()
        driver.get(BASE_URL)
        human_delay(2, 3)
        return True
    except Exception as e:
        print(f"Error resetting browser: {e}")
        return False

def main() -> None:
    """Main execution function."""
    try:
        file_path = input("Enter input file path: ").strip()
        input_data_list = read_input_from_file(file_path)

        for i, input_data in enumerate(input_data_list):
            print(f"Searching for {input_data['first_name']} {input_data['last_name']}...")
            
            # Create new driver for each search to ensure clean state
            driver = create_driver()
            try:
                driver.get(BASE_URL)
                human_delay()
                
                if not handle_consent_modal(driver):
                    print("Failed to handle consent modal. Creating new browser session...")
                    if not reset_browser(driver):
                        print("Failed to reset browser. Skipping this search...")
                        continue

                filename = f"zaba_results_{input_data['first_name']}_{input_data['last_name']}.txt"
                check_and_remove_junk_files(filename)
                
                if results := perform_search(input_data, driver):
                    if save_results(filename, results):
                        print(f"Successfully saved valid results to {filename}")
                    else:
                        print(f"Results not saved - detected as junk")

                if i < len(input_data_list) - 1:
                    delay = random.randint(15, 45)
                    print(f"Waiting {delay} seconds before next search...")
                    time.sleep(delay)
            finally:
                # Always quit the driver after each search
                driver.quit()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
