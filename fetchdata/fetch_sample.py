import click
from airtable import Airtable
from dotenv import load_dotenv

from .utils import airtable_to_dataframe, regnumber_to_orgid

load_dotenv()


@click.command()
@click.option("--base-id", envvar="AIRTABLE_BASE_ID")
@click.option("--airtable-api-key", envvar="AIRTABLE_API_KEY")
@click.option(
    "--table-name", default="Sample data", envvar="AIRTABLE_SAMPLE_TABLE_NAME"
)
@click.option("--save-location", default="./data/sample.csv")
def fetch_sample(base_id, airtable_api_key, table_name, save_location):
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
    sample[columns_to_include].sort_values("org_id").to_csv(save_location, index=False)


if __name__ == "__main__":
    fetch_sample()
