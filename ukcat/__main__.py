import click
from dotenv import load_dotenv

from ukcat.apply_icnptso import apply_icnptso
from ukcat.apply_ukcat import apply_ukcat
from ukcat.fetch_charities import fetch_charities
from ukcat.fetch_sample import fetch_sample
from ukcat.fetch_tags import fetch_tags
from ukcat.ml_icnptso import create_ml_model

load_dotenv()


@click.group()
def cli():
    pass


@cli.group("fetch")
def fetch():
    pass


fetch.add_command(fetch_tags, name="tags")
fetch.add_command(fetch_sample, name="sample")
fetch.add_command(fetch_charities, name="charities")


@cli.group("apply")
def apply():
    pass


apply.add_command(apply_ukcat, name="ukcat")
apply.add_command(apply_icnptso, name="icnptso")


@cli.group("train")
def train():
    pass


train.add_command(create_ml_model, name="icnptso")

if __name__ == "__main__":
    cli()
