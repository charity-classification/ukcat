import click
from dotenv import load_dotenv

from .fetch_charities import fetch_charities
from .fetch_sample import fetch_sample
from .fetch_tags import fetch_tags

load_dotenv()


@click.group()
def fetch():
    pass


fetch.add_command(fetch_tags)
fetch.add_command(fetch_sample)
fetch.add_command(fetch_charities)

if __name__ == "__main__":
    fetch()
