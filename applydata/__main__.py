import click
from dotenv import load_dotenv

from .apply_ukcat import apply_ukcat
from .apply_icnptso import apply_icnptso

load_dotenv()


@click.group()
def apply():
    pass


apply.add_command(apply_ukcat)
apply.add_command(apply_icnptso)

if __name__ == "__main__":
    apply()
