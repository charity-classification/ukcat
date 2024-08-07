import click
from dotenv import load_dotenv

from ukcat.__about__ import __version__
from ukcat.apply_icnptso import apply_icnptso
from ukcat.apply_ukcat import apply_ukcat
from ukcat.fetch_charities import fetch_charities
from ukcat.fetch_sample import fetch_sample
from ukcat.fetch_tags import fetch_tags
from ukcat.make_docs import make_ukcat_docs
from ukcat.ml_icnptso import create_ml_model

load_dotenv()


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="ukcat")
def ukcat():
    pass


@ukcat.group("fetch")
def fetch():
    pass


fetch.add_command(fetch_tags, name="tags")
fetch.add_command(fetch_sample, name="sample")
fetch.add_command(fetch_charities, name="charities")


@ukcat.group("apply")
def apply():
    pass


apply.add_command(apply_ukcat, name="ukcat")
apply.add_command(apply_icnptso, name="icnptso")


@ukcat.group("train")
def train():
    pass


train.add_command(create_ml_model, name="icnptso")


@ukcat.group("docs")
def docs():
    pass


docs.add_command(make_ukcat_docs, name="ukcat")
