from setuptools import setup

setup(
    entry_points={
        "console_scripts": [
            "forex_scraper = exchange_rate_scraper/main:main",
        ]
    }
)
