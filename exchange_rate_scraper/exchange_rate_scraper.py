"""
Exchange rate scraper
Author: Luca Mircea
Date started: 24 Sep 2023
Premise: Here we'll develop the code for getting exchange
    rate data from a few different national bank websites
"""

import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from exchange_rate_scraper.constants import SNB_MAIN_WEBSITE_URL


def set_up_driver(url_target_website: str) -> webdriver:
    """Here we set up the web driver"""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("start-maximized")  # ensure window is full-screen

    driver = webdriver.Chrome(options=options)

    driver.get(url_target_website)

    time.sleep(10)

    return driver


def get_data_from_snb_website(target_url: str, switch_off_driver: bool = True) -> dict:
    """Here we parse the exchange rates"""

    driver = set_up_driver(target_url)

    WebDriverWait(driver=driver, timeout=5).until(
        expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "publication-date")
        )
    )

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, features="html.parser")

    exchange_rate_table_html = soup.find_all(
        "ul", class_="rates-wrapper exchange-rates-wrapper"
    )

    snb_rates = {}

    for element in exchange_rate_table_html:
        lines = element.find_all("li")
        for line in lines:
            spans = line.find_all("span")

            try:
                currency_pair = line.find("span", class_="term").text.strip()
                exchange_rate_value = line.find("span", class_="value").text.strip()
            except AttributeError:
                try:
                    currency_pair = spans[0].text.strip()
                    exchange_rate_value = spans[1].text.strip()
                except:  # noqa: E722
                    pass

            if currency_pair is not None:
                snb_rates[currency_pair] = exchange_rate_value

    if switch_off_driver:
        driver.quit()

    return snb_rates


snb_rates = get_data_from_snb_website(SNB_MAIN_WEBSITE_URL)
