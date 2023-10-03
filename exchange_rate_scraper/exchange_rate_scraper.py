"""
Exchange rate scraper
Author: Luca Mircea
Date started: 24 Sep 2023
Premise: Here we'll develop the code for getting exchange
    rate data from a few different national bank websites
"""

import os
import tempfile
import time
from datetime import datetime

import pandas as pd
from boto3 import Session
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from exchange_rate_scraper.constants import AWS_ACCESS_KEY_ID  # noqa: E402
from exchange_rate_scraper.constants import (AWS_ACCESS_SECRET_KEY,
                                             AWS_UPLOAD_BUCKET_NAME,
                                             AWS_UPLOAD_TABLE_NAME,
                                             SNB_MAIN_WEBSITE_URL)


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
                    currency_pair = "not_found"
                    exchange_rate_value = "not_found"

            if currency_pair is not None:
                snb_rates[currency_pair] = exchange_rate_value

    if switch_off_driver:
        driver.quit()

    return snb_rates


def upload_data_to_s3(
    aws_access_key: str,
    aws_secret: str,
    bucket_name: str,
    upload_path: str,
    upload_file_name: str,
    file_to_upload_name: str,
):
    """Function for uploading to the S3 bucket, file agnostic"""

    session = Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret,
        region_name="eu-north-1",
    )

    s3 = session.resource("s3")

    upload_key = f"{upload_path}/{upload_file_name}"

    s3.Bucket(bucket_name).upload_file(file_to_upload_name, upload_key)


def main():
    snb_rates = get_data_from_snb_website(SNB_MAIN_WEBSITE_URL)
    snb_rates_df = pd.DataFrame.from_dict(snb_rates, orient="index")
    snb_rates_df["currency_pair"] = snb_rates_df.index
    snb_rates_df.columns = ["exchange_rate", "currency_pair"]
    snb_rates_df.reset_index(drop=True, inplace=True)

    snb_rates_df["source"] = "swiss_national_bank"
    snb_rates_df["datetime_collected"] = str(datetime.now())

    upload_date = str(datetime.now().date())

    upload_path = f"{AWS_UPLOAD_TABLE_NAME}/date_uploaded={upload_date}"
    upload_file_name = f"exchange_rates_{upload_date}.csv"

    with tempfile.TemporaryFile() as temp_dir:  # noqa: F841
        file_path = os.path.join(os.getcwd(), f"exchange_rates_{upload_date}.csv")
        snb_rates_df.to_csv(file_path, index=False)

        upload_data_to_s3(
            AWS_ACCESS_KEY_ID,
            AWS_ACCESS_SECRET_KEY,
            AWS_UPLOAD_BUCKET_NAME,
            upload_path,
            upload_file_name,
            file_path,
        )
