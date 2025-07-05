from selenium.common.exceptions import NoSuchElementException
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

# Path to ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'

def human_delay(min=0.5, max=2.5):
    time.sleep(random.uniform(min, max))

def is_junk_file(file_path):
    try:
        return os.path.getsize(file_path) == 2252  # 2.2 KiB exact size
    except:
        return False

def is_junk_content(content):
    junk_patterns = [
        "Status: 404, NOT FOUND",
        "Search Error",
        "Please try again",
        "No records found",
        "No matches found"
    ]
    return any(pattern in content for pattern in junk_patterns)

def check_and_remove_junk_files(filename):
    if os.path.exists(filename):
        try:
            with open(filename) as f:
                content = f.read()
                if is_junk_file(filename) or is_junk_content(content):
                    print(f"Removing junk file: {filename}")
                    os.remove(filename)
                    return True
        except:
            pass
    return False

def extract_relevant_info(content):
    """Extract only the specified fields from the Zabasearch results page content"""
    relevant_info = []
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all person sections
    person_sections = soup.find_all('div', class_='person')
    
    for person in person_sections:
        # Extract name
        name_tag = person.find('h2')
        if name_tag and name_tag.a:
            relevant_info.append(f"Name: {name_tag.a.get_text(strip=True)}")
        
        # Extract age
        age_tag = person.find('h3')
        if age_tag:
            relevant_info.append(f"Age: {age_tag.get_text(strip=True)}")
        
        # Extract AKA/Aliases
        aka_div = person.find('div', id='container-alt-names')
        if aka_div:
            aliases = [li.get_text(strip=True) for li in aka_div.find_all('li')]
            if aliases:
                relevant_info.append("AKA: " + ", ".join(aliases))
        
        # Extract phone numbers
        phones_div = person.find('h3', string='Associated Phone Numbers')
        if phones_div:
            phones_ul = phones_div.find_next('ul')
            if phones_ul:
                phones = [a.get_text(strip=True) for a in phones_ul.find_all('a')]
                if phones:
                    relevant_info.append("Associated Phone Numbers: " + ", ".join(phones))
        
        # Extract email addresses - improved to get full domains
        emails_div = person.find('h3', string='Associated Email Addresses')
        if emails_div:
            emails_ul = emails_div.find_next('ul')
            if emails_ul:
                emails = []
                for li in emails_ul.find_all('li'):
                    # Handle both blurred and normal email formats
                    email_text = li.get_text(strip=True)
                    if '@' in email_text:
                        # Extract complete email address
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+', email_text)
                        if email_match:
                            emails.append(email_match.group(0))
                if emails:
                    relevant_info.append("Associated Email Addresses: " + ", ".join(emails))
        
        # Extract last known address
        address_div = person.find('h3', string='Last Known Address')
        if address_div:
            address_p = address_div.find_next('p')
            if address_p:
                address = address_p.get_text(" ", strip=True).replace("\n", "").replace("  ", " ")
                relevant_info.append("Last Known Address: " + address)
        
        # Extract past addresses
        past_addresses_div = person.find('h3', string='Past Addresses')
        if past_addresses_div:
            past_addresses_ul = past_addresses_div.find_next('ul')
            if past_addresses_ul:
                past_addresses = []
                for li in past_addresses_ul.find_all('li'):
                    address = li.get_text(" ", strip=True).replace("\n", " ").replace("  ", " ")
                    past_addresses.append(address)
                if past_addresses:
                    relevant_info.append("Past Addresses:\n" + "\n".join(past_addresses))
        
        # Add separator between people
        relevant_info.append("\n" + "-"*50 + "\n")
    
    # Remove the last separator if it exists
    if relevant_info and relevant_info[-1].strip() == '-'*50:
        relevant_info = relevant_info[:-1]
    
    return '\n'.join(relevant_info)

def save_results(filename, content):
    if not content or is_junk_content(content):
        print(f"Not saving junk content to {filename}")
        return False
    
    try:
        # Extract only the relevant information before saving
        filtered_content = extract_relevant_info(content)
        
        with open(filename, 'w') as f:
            f.write(filtered_content)
        
        if is_junk_file(filename) or is_junk_content(open(filename).read()):
            print(f"Removing junk file after verification: {filename}")
            os.remove(filename)
            return False
            
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

def read_input_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        data = []
        for line in lines:
            if line.startswith(("First Name", "first_name")) or not line.strip():
                continue
            delimiter = '\t' if '\t' in line else ','
            parts = line.strip().split(delimiter)
            if len(parts) >= 2:
                data.append({
                    'first_name': parts[0],
                    'last_name': parts[1],
                    'city': parts[2] if len(parts) > 2 else "",
                    'state': parts[3] if len(parts) > 3 else ""
                })
        return data

def handle_consent_modal(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-wrapper.open")))
        
        modal = driver.find_element(By.ID, "warning-modal")
        driver.execute_script("arguments[0].scrollIntoView(true);", modal)
        time.sleep(1)
        
        try:
            agree_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".inside-copy")))
            driver.execute_script("arguments[0].click();", agree_button)
        except:
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#security-check .check-wrapper")))
            driver.execute_script("arguments[0].click();", checkbox)
        
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay.open")))
        
        human_delay()
        return True
        
    except Exception as e:
        print(f"Error handling consent modal: {str(e)}")
        driver.save_screenshot("consent_modal_error.png")
        return False

def perform_search(input_data, driver):
    try:
        def fill_field(selector, value):
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

        try:
            return driver.page_source  # Return the full HTML source
        except NoSuchElementException:
            try:
                return driver.page_source
            except:
                return "No results found - page structure may have changed"

    except Exception as e:
        print(f"Search error: {e}")
        driver.save_screenshot(f"search_error_{time.time()}.png")
        return None

def create_driver():
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,115)}.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": options.arguments[-1].split('=')[1]})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def main():
    input_data_list = []
    try:
        use_file = input("Read from file? (yes/no): ").strip().lower()
        if use_file == 'yes':
            file_path = input("Enter file path: ").strip()
            input_data_list = read_input_from_file(file_path)
        else:
            input_data_list = [{
                'first_name': input("First Name: "),
                'last_name': input("Last Name: "),
                'city': input("City (optional): "),
                'state': input("State (optional): ")
            }]

        for i, input_data in enumerate(input_data_list):
            print(f"Searching for {input_data['first_name']} {input_data['last_name']}...")
            
            # Create new driver instance for each search
            driver = create_driver()
            try:
                driver.get('https://www.zabasearch.com/')
                human_delay()
                
                if not handle_consent_modal(driver):
                    print("Failed to handle consent modal. Skipping...")
                    continue

                filename = f"zaba_results_{input_data['first_name']}_{input_data['last_name']}.txt"
                check_and_remove_junk_files(filename)
                
                results = perform_search(input_data, driver)
                
                if results:
                    if save_results(filename, results):
                        print(f"Successfully saved valid results to {filename}")
                    else:
                        print(f"Results not saved - detected as junk")
            finally:
                # Always quit the driver after each search
                driver.quit()
                human_delay(1, 3)  # Small delay between driver restarts

            if i < len(input_data_list) - 1:
                delay = random.randint(15, 45)  # Longer delay between searches
                print(f"Waiting {delay} seconds before next search...")
                time.sleep(delay)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # No need to quit driver here since we quit after each search
        pass

if __name__ == "__main__":
    main()
