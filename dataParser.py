from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

def getData():
    driver = webdriver.Chrome()
    try:
        driver.get('https://rdeapps.stanford.edu/MyMealPlan/')

        # Wait for the nested table with specific header class to be present
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table table thead.clsTableHeader")))

        # Locate the nested table
        nested_table = driver.find_element(By.CSS_SELECTOR, "table table thead.clsTableHeader").find_element(By.XPATH,
                                                                                                             "./ancestor::table")

        # Find all rows in the nested table
        rows = nested_table.find_elements(By.TAG_NAME, "tr")

        currentData = {}

        for row in rows[2:]:  # Skip the header row
            columns = row.find_elements(By.TAG_NAME, "td")
            if columns:
                plan_name = columns[0].text.strip()
                plan_value = columns[-1].text.strip()  # Assuming the value is in the last column
                # Dictionary format: { plan name : balance }
                currentData[plan_name] = plan_value
                print(f"{plan_name}: {plan_value}")

        print("ending dict: ", currentData)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

def extract_table_data():
    driver = webdriver.Chrome()
    driver.get('https://rdeapp.stanford.edu/MyMealPlan/Transactions')

    # Wait for the dropdown to load
    WebDriverWait(driver, 900).until(EC.presence_of_element_located((By.ID, "MainContent_lstPlans")))

    # Find the dropdown element
    select_element = Select(driver.find_element(By.ID, "MainContent_lstPlans"))

    # Dictionary to hold the data
    data_dict = {}

    # Iterate over options in the dropdown
    for option in select_element.options:
        # Skip the default or placeholder option
        if option.text == "Select a plan...":
            continue

        # Select the option
        select_element.select_by_visible_text(option.text)
        time.sleep(5)  # Wait for the table to update, adjust time as needed

        # Scrape the table data
        table_data = []
        # Ensure that the table is located correctly after each selection
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tableID1")))
        table_rows = driver.find_elements(By.CSS_SELECTOR, "#tableID1 tbody tr")

        for row in table_rows:  # Including header row if needed
            cols = row.find_elements(By.TAG_NAME, "td")
            for i in range(0, len(cols), 3):
                table_data.append((cols[i].text, cols[i + 1].text, cols[i + 2].text))

        print("table data ", table_data)
        print("CUR OPTION ", option.text)
        data_dict[option.text] = table_data

    print(data_dict)
    driver.quit()

    # Print or process the data_dict as needed
    print(data_dict)


extract_table_data()