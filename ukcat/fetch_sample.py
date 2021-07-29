import click
import pandas as pd
from airtable import Airtable

from ukcat.settings import SAMPLE_FILE
from ukcat.utils import airtable_to_dataframe, regnumber_to_orgid


@click.command()
@click.option("--base-id", type=str, envvar="AIRTABLE_BASE_ID")
@click.option("--airtable-api-key", type=str, envvar="AIRTABLE_API_KEY")
@click.option(
    "--table-name", default="Sample data", type=str, envvar="AIRTABLE_SAMPLE_TABLE_NAME"
)
@click.option(
    "--save-location",
    default=SAMPLE_FILE,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
def fetch_sample(
    base_id: str, airtable_api_key: str, table_name: str, save_location: str
) -> pd.DataFrame:
    """Fetch the completed sample from Airtable"""

    airtable = Airtable(
        base_id,
        table_name,
        airtable_api_key,
    )
    click.echo(f"Fetching records from table `{table_name}` in base `{base_id}`")
    sample = (
        airtable_to_dataframe(airtable, ["Tag Labels", "ICNPTSO code"])
        .drop(columns=["ICNPTSO"])
        .rename(
            columns={
                "Tag Labels": "UKCAT",
                "ICNPTSO code": "ICNPTSO",
            }
        )
    )
    for f in ["activities", "objects"]:
        sample.loc[:, f] = sample[f].fillna("").str.replace("\n", " ")
    sample.loc[:, "org_id"] = sample["reg_number"].apply(regnumber_to_orgid)
    columns_to_include = [
        "org_id",
        "reg_number",
        "name",
        "postcode",
        "active",
        "date_registered",
        "activities",
        "objects",
        "source",
        "income",
        "spending",
        "fye",
        "Batch ID",
        "web",
        "company_number",
        "UKCAT",
        "ICNPTSO",
    ]
    click.echo(f"Saving to CSV file `{save_location}`")
    sample = sample[columns_to_include].sort_values("org_id")

    if save_location:
        sample.to_csv(save_location, index=False)

    return sample


if __name__ == "__main__":
    fetch_sample()
