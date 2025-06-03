from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Selenium WebDriver
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

main_url = "https://www.moh.gov.my/index.php/pages/view/4378?mid=1501"
driver.get(main_url)
time.sleep(5)  # Wait for page to load

soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all accordion groups (states)
state_sections = soup.find_all("div", class_="accordion_header group")

all_data = []

for section in state_sections:
    state_name = section.find("h3").text.strip().replace('"', '').strip()

    # Find iframe inside section
    iframe = section.find_next("iframe")
    if iframe:
        iframe_url = "https://www.moh.gov.my" + iframe["src"]

        driver.get(iframe_url)
        time.sleep(3)

        while True:  # Loop to handle pagination
            # Parse the current page
            iframe_soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Parse table
            table = iframe_soup.find("table", id="DataTables_Table_0")
            if table:
                rows = table.find("tbody").find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 4:
                        no = cols[0].text.strip()
                        facility = cols[1].text.strip()
                        address = cols[2].text.strip()
                        phone = cols[3].text.strip()

                        all_data.append([state_name, no, facility, address, phone])

            # Check for "Next" button and navigate to the next page
            try:
                next_button = driver.find_element(By.XPATH, '//a[contains(text(), "Next")]')
                # Check if "Next" button is disabled (contains &nbsp; in HTML)
                if "&nbsp;" in next_button.get_attribute("innerHTML"):
                    break  # Exit loop if "Next" is disabled
                next_button.click()
                time.sleep(1)  # Wait for the next page to load
            except:
                break  # Exit loop if "Next" button is not found

# Convert to DataFrame
df = pd.DataFrame(all_data, columns=["State", "No.", "Facility Name", "Full Address", "Phone Number"])

# Save to CSV
df.to_csv("health_facilities_by_state.csv", index=False, encoding='utf-8-sig')

# Cleanup
driver.quit()