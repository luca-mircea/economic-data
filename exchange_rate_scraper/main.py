"""
Exchange rate scraper
Author: Luca Mircea
Date started: 24 Sep 2023
Premise: Here we'll develop the code for getting exchange
    rate data from a few different national bank websites
"""

import logging
import os
import sys
import tempfile
from datetime import datetime

import pandas as pd
import requests
from boto3 import Session
from bs4 import BeautifulSoup, ResultSet

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from exchange_rate_scraper.constants import (AWS_ACCESS_KEY_ID,  # noqa: E402
                                             AWS_ACCESS_SECRET_KEY,
                                             AWS_UPLOAD_BUCKET_NAME,
                                             AWS_UPLOAD_TABLE_NAME,
                                             SNB_MAIN_WEBSITE_URL,
                                             SNB_RATES_TO_KEEP)


def get_page_source(url_target_website: str) -> str:
    result = requests.get(url_target_website)

    return result.text


def get_rates_from_website_elements(
    exchange_rate_names: ResultSet, exchange_rates: ResultSet
) -> dict:
    """Here we parse the rates from the results"""
    snb_rates = {}

    for list_index in range(len(exchange_rate_names)):
        element_names = exchange_rate_names[list_index]
        element_rates = exchange_rates[list_index]

        try:
            currency_pair = element_names.find(
                "span", class_="h-typo-small"
            ).text.strip()
            exchange_rate_value = element_rates.find(
                "span", class_="h-typo-t3"
            ).text.strip()
        except Exception as e:
            currency_pair = "not_found"
            exchange_rate_value = "not_found"
            logging.warning(f"Error with getting the exchange rates: {e}")

        if currency_pair is not None and currency_pair in SNB_RATES_TO_KEEP:
            snb_rates[currency_pair] = exchange_rate_value

    return snb_rates


def get_data_from_snb_website(target_url: str) -> dict:
    """Here we parse the exchange rates"""

    page_source = get_page_source(target_url)

    soup = BeautifulSoup(page_source, features="html.parser")

    exchange_rate_names = soup.find_all(class_="cms-financial-rates-item__key")
    exchange_rates = soup.find_all(class_="cms-financial-rates-item__value")

    snb_rates = get_rates_from_website_elements(exchange_rate_names, exchange_rates)

    return snb_rates


def process_rates_dict_into_nice_df(snb_rates: dict) -> pd.DataFrame:
    """Turn the dict into a nice DF for uploading"""
    snb_rates = get_data_from_snb_website(SNB_MAIN_WEBSITE_URL)
    snb_rates_df = pd.DataFrame.from_dict(snb_rates, orient="index")
    snb_rates_df["currency_pair"] = snb_rates_df.index
    snb_rates_df.columns = ["exchange_rate", "currency_pair"]
    snb_rates_df.reset_index(drop=True, inplace=True)

    snb_rates_df["source"] = "swiss_national_bank"
    snb_rates_df["datetime_collected"] = str(datetime.now())

    return snb_rates_df


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


def get_snb_data():
    snb_rates = get_data_from_snb_website(SNB_MAIN_WEBSITE_URL)
    snb_rates_df = process_rates_dict_into_nice_df(snb_rates)

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
