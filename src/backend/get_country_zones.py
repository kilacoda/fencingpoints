import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

driver = Chrome()
driver.get("https://fie.org/fie/structure/federations-map")

selects = lambda: driver.find_elements(By.CLASS_NAME,"Form-dropdown")
fed_countries = dict()

print(selects())
fed_select = Select(selects()[0])
for option in fed_select.options[1:]: ## skip the hidden default text
    print(option.text)
    fed_select.select_by_visible_text(option.text)

    time.sleep(10)

    select_elements = selects()
    fed_select = Select(select_elements[0])
    country_select = Select(select_elements[1])

    fed_countries[option.text] = [opt.text for opt in country_select.options[1:]]
    print([opt.text for opt in country_select.options])

print(fed_countries)

with open("federations.json","w") as f:
    json.dump(fed_countries,f)
