import click
import pandas as pd
from airtable import Airtable

from ukcat.settings import UKCAT_FILE
from ukcat.utils import airtable_to_dataframe


@click.command()
@click.option("--base-id", type=str, envvar="AIRTABLE_BASE_ID")
@click.option("--airtable-api-key", type=str, envvar="AIRTABLE_API_KEY")
@click.option(
    "--table-name",
    type=str,
    default="Tags - working",
    envvar="AIRTABLE_TAGS_TABLE_NAME",
)
@click.option(
    "--save-location",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
    default=UKCAT_FILE,
)
def fetch_tags(base_id: str, airtable_api_key: str, table_name: str, save_location: str) -> pd.DataFrame:
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

    return tags


if __name__ == "__main__":
    fetch_tags()
