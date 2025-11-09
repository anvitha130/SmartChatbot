import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def test_homepage_loads_and_interacts():
    # Setup Chrome in headless mode (no visible window)
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # ✅ 1. Open your Streamlit app
        driver.get("http://localhost:8501")
        time.sleep(5)  # wait for Streamlit to load completely

        # ✅ 2. Verify that the app title or keyword exists
        assert "career counselor" in driver.page_source.lower()

        # ✅ 3. Find an input box (first input on the page)
        # Adjust the XPATH if your app has multiple input fields
        input_box = driver.find_element(By.TAG_NAME, "input")
        input_box.send_keys("John Doe")

        # ✅ 4. Find and click the Submit button
        # Adjust text if your button says something else
        submit_button = driver.find_element(By.XPATH, "//button[contains(., 'Submit')]")
        submit_button.click()

        # ✅ 5. Wait for the result to appear
        time.sleep(3)

        # ✅ 6. Check if result text is displayed
        page_source = driver.page_source.lower()
        assert "result" in page_source or "recommendation" in page_source

        print("✅ Test passed: Streamlit app loaded and interaction succeeded")

    finally:
        driver.quit()
