from setuptools import setup

setup(
    install_requires=[
        "beautifulsoup4==4.12.2",
        "black==23.9.1",
        "boto3==1.28.57",
        "build==1.0.3",
        "isort==5.12.0",
        "pandas==2.1.1",
        "parsel==1.8.1",
        "pip-chill==1.0.3",
        "pysocks==1.7.1",
        "ruff==0.0.291",
    ],
    entry_points={
        "console_scripts": [
            "forex_scraper = exchange_rate_scraper:main",
        ]
    },
)
