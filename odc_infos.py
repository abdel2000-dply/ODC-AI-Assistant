import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options  # For headless mode

# Set up Chrome options to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Runs Chrome in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
chrome_options.add_argument("--no-sandbox")  # Optional: Necessary for some systems, especially on Linux

# Set up the Selenium WebDriver (Chrome in this case) with headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the website
driver.get("https://www.orangedigitalcenters.com/programs")

# Wait for the page to load
time.sleep(5)

# Create a dictionary to store scraped data
data = {}

# Scrape header information: title and subtitle
header = driver.find_element(By.CLASS_NAME, 'starter-page')
title = header.find_element(By.CLASS_NAME, 'title').text
subtitle = header.find_element(By.CLASS_NAME, 'sub-title').text

data["header"] = {
    "title": title,
    "subtitle": subtitle
}

# Scrape content from the "Coding School", "FabLab Solidaires", "Orange Fab" sections 
program_names = ["Coding School", "FabLab Solidaires", "Orange Fab"]  
programs = []

# A function to scrape details for each program section
def scrape_program_data(program_name):
    program = {}
    program["name"] = program_name
    
    # Navigate to the program page or element
    program_elem = driver.find_element(By.XPATH, f"//h1[contains(text(), '{program_name}')]")
    
    description_elem = program_elem.find_element(By.XPATH, "./following-sibling::h1")
    description = description_elem.text if description_elem else ""
    
    # Get about numbers (community, events, etc.)
    about_numbers = []
    numbers_elem = program_elem.find_elements(By.XPATH, ".//following-sibling::div[@class='ant-row about-numbers']//div")
    
    # Collect about numbers while avoiding duplicates
    seen = set()  # Keep track of (title, value) to remove duplicates
    for number_elem in numbers_elem:
        title = number_elem.find_element(By.CLASS_NAME, "about-numbers-title").text
        value = number_elem.find_element(By.CLASS_NAME, "about-numbers-value").text
        description = number_elem.find_element(By.CLASS_NAME, "about-numbers-description").text
        
        # Add the number only if it's not already in the 'seen' set
        if (title, value) not in seen:
            about_numbers.append({"title": title, "value": value, "description": description})
            seen.add((title, value))
    
    program["description"] = description
    program["about_numbers"] = about_numbers
    return program

# Loop through the program names to scrape their data
for program_name in program_names:
    program_data = scrape_program_data(program_name)
    programs.append(program_data)

data["programs"] = programs

# Save the data into a JSON file
with open("scraped_data.json", "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4)

# Close the WebDriver
driver.quit()
