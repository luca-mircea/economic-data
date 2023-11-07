from dotenv import dotenv_values

config = dotenv_values(".env")

AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
AWS_ACCESS_SECRET_KEY = config["AWS_ACCESS_SECRET_KEY"]

AWS_UPLOAD_BUCKET_NAME = config["AWS_UPLOAD_BUCKET_NAME"]
AWS_UPLOAD_TABLE_NAME = "exchange_rate_data"

SNB_MAIN_WEBSITE_URL = "https://www.snb.ch/en/"

SNB_RATES_TO_KEEP = ["EUR / CHF", "USD / CHF", "100 JPY / CHF", "GBP / CHF"]
