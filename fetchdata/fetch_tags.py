import click
from airtable import Airtable
from dotenv import load_dotenv

from .utils import airtable_to_dataframe

load_dotenv()


@click.command()
@click.option("--base-id", envvar="AIRTABLE_BASE_ID")
@click.option("--airtable-api-key", envvar="AIRTABLE_API_KEY")
@click.option(
    "--table-name", default="Tags - working", envvar="AIRTABLE_TAGS_TABLE_NAME"
)
@click.option("--save-location", default="./data/ukcat.csv")
def fetch_tags(base_id, airtable_api_key, table_name, save_location):
    """Fetch the list of tags from Airtable"""

    airtable = Airtable(
        base_id,
        table_name,
        airtable_api_key,
    )
    click.echo(f"Fetching records from table `{table_name}` in base `{base_id}`")
    tags = airtable_to_dataframe(airtable, ["Related ICNPTSO code"])

    tags = (
        tags.rename(columns={"Name": "tag"})
        .sort_values("Full name")
        .loc[
            tags["Not used (describe why)"].isnull(),
            [
                "Code",
                "tag",
                "Category",
                "Subcategory",
                "Level",
                "Notes",
                "Related ICNPTSO code",
                "Regular expression",
                "Exclude regular expression",
            ],
        ]
    ).set_index("Code")
    click.echo(f"Saving to CSV file `{save_location}`")
    tags.to_csv(save_location)


if __name__ == "__main__":
    fetch_tags()
