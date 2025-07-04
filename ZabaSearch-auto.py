from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os

# Path to ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'  # Adjust if necessary

# Function to simulate human-like delays
def human_delay(min=0.5, max=2.5):
    time.sleep(random.uniform(min, max))

# Function to read input from a text file
def read_input_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        data = []
        for line in lines:
            # Skip header row if exists
            if line.startswith("First Name") or line.startswith("first_name"):
                continue
            if not line.strip():
                continue
            
            # Detect delimiter
            delimiter = '\t' if '\t' in line else ','
            parts = line.strip().split(delimiter)
            
            if len(parts) < 2:
                print(f"Skipping invalid line: {line.strip()}")
                continue
                
            first_name = parts[0]
            last_name = parts[1]
            city = parts[2] if len(parts) > 2 else ""
            state = parts[3] if len(parts) > 3 else ""
            
            data.append({
                'first_name': first_name,
                'last_name': last_name,
                'city': city,
                'state': state
            })
    return data

# Function to handle the consent modal - UPDATED VERSION
def handle_consent_modal(driver):
    try:
        # Wait for modal to be fully visible and interactive
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-wrapper.open"))
        )
        
        # Scroll the modal into view
        modal = driver.find_element(By.ID, "warning-modal")
        driver.execute_script("arguments[0].scrollIntoView(true);", modal)
        time.sleep(1)
        
        # Try multiple ways to click the agreement
        try:
            # First try clicking the visible "I AGREE" text
            agree_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".inside-copy"))
            )
            driver.execute_script("arguments[0].click();", agree_button)
        except:
            # Fallback to clicking the checkbox wrapper using JavaScript
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#security-check .check-wrapper"))
            )
            driver.execute_script("arguments[0].click();", checkbox)
        
        # Wait for modal to disappear
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-overlay.open"))
        )
        
        human_delay()
        return True
        
    except Exception as e:
        print(f"Error handling consent modal: {str(e)}")
        driver.save_screenshot("consent_modal_error.png")
        return False

# Function to perform a search - UPDATED VERSION
def perform_search(input_data, driver):
    try:
        # Ensure we're on the search page
        if "zabasearch.com/people/" in driver.current_url:
            driver.get('https://www.zabasearch.com/')
            if not handle_consent_modal(driver):
                return None

        # Fill form fields with retries
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
        
        # Fill first name with retries
        if not fill_field(".search-first-name", input_data['first_name']):
            return None
            
        # Fill last name with retries
        if not fill_field(".search-last-name", input_data['last_name']):
            return None
            
        # Fill city if provided
        if input_data['city']:
            fill_field(".search-city", input_data['city'])
            
        # Select state if provided
        if input_data['state']:
            try:
                state_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-state")))
                state_dropdown = Select(state_element)
                state_dropdown.select_by_visible_text(input_data['state'])
                human_delay(1, 2)
            except Exception as e:
                print(f"Couldn't select state: {e}")

        # Submit with retry
        for attempt in range(2):
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".button-search")))
                submit_button.click()
                break
            except:
                if attempt == 1:
                    print("Failed to submit search form")
                    return None
                time.sleep(2)

        # Wait for results with dynamic timeout
        try:
            WebDriverWait(driver, random.uniform(5, 10)).until(
                lambda d: "results" in d.current_url.lower() or 
                d.find_elements(By.CSS_SELECTOR, ".results-container"))
        except:
            pass  # Continue even if timeout occurs

        # Capture results with multiple fallbacks
        try:
            results_container = driver.find_element(By.CSS_SELECTOR, ".results-container")
            return results_container.text
        except NoSuchElementException:
            try:
                return driver.find_element(By.TAG_NAME, 'body').text
            except:
                return "No results found - page structure may have changed"

    except Exception as e:
        print(f"Search error: {e}")
        driver.save_screenshot(f"search_error_{time.time()}.png")
        return None

def main():
    driver = None
    try:
        # Initialize WebDriver with Chrome options - ADD THIS SECTION
        service = Service(chrome_driver_path)
        
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,115)}.0.0.0 Safari/537.36")
        
        # Initialize the driver with options
        driver = webdriver.Chrome(service=service, options=options)
        
        # Additional stealth settings
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": options.arguments[-1].split('=')[1]})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Rest of your existing main() function continues here...
        # Navigate to ZabaSearch
        driver.get('https://www.zabasearch.com/')
        human_delay()
        
        # Handle consent modal
        if not handle_consent_modal(driver):
            print("Failed to handle consent modal. Exiting.")
            return

        # Get input data
        use_file = input("Read from file? (yes/no): ").strip().lower()
        if use_file == 'yes':
            file_path = input("Enter file path: ").strip()
            input_data_list = read_input_from_file(file_path)
        else:
            first_name = input("First Name: ")
            last_name = input("Last Name: ")
            city = input("City (optional): ")
            state = input("State (optional): ")
            input_data_list = [{
                'first_name': first_name,
                'last_name': last_name,
                'city': city,
                'state': state
            }]

        # Process searches
        for i, input_data in enumerate(input_data_list):
            print(f"Searching for {input_data['first_name']} {input_data['last_name']}...")
            
            # Return to search page if not there
            if "zabasearch.com/people/" in driver.current_url:
                driver.get('https://www.zabasearch.com/')
                human_delay()
                handle_consent_modal(driver)

            results = perform_search(input_data, driver)
            
            if results:
                filename = f"zaba_results_{input_data['first_name']}_{input_data['last_name']}.txt"
                with open(filename, 'w') as f:
                    f.write(results)
                print(f"Results saved to {filename}")

            # Random delay between searches
            if i < len(input_data_list) - 1:
                delay = random.randint(10, 30)
                print(f"Waiting {delay} seconds before next search...")
                time.sleep(delay)

    except Exception as e:
        print(f"Error: {e}")
        if driver:
            driver.save_screenshot('error.png')
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
