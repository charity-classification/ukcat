import io
import os
import zipfile

import click
import pandas as pd
import requests

from ukcat.settings import CIC_DATA, DATA_DIR

CIC_FIELDS = [
    "beneficiaries",
    "surplus_use",
    "activity_1",
    "community_benefit_1",
    "activity_2",
    "community_benefit_2",
    "activity_3",
    "community_benefit_3",
    "activity_4",
    "community_benefit_4",
    "activity_5",
    "community_benefit_5",
    "activity_6",
    "community_benefit_6",
    "activity_7",
    "community_benefit_7",
    "activity_8",
    "community_benefit_8",
    "activity_9",
    "community_benefit_9",
    "activity_10",
    "community_benefit_10",
]


@click.command()
@click.option("--cic-data", default=CIC_DATA, type=str)
@click.option(
    "--save-location",
    default=DATA_DIR,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def fetch_cics(
    cic_data: str,
    save_location: str,
) -> pd.DataFrame:
    """Fetch data on Community Interest Companies"""

    with zipfile.ZipFile(io.BytesIO(requests.get(cic_data).content)) as z:
        for f in z.namelist():
            if f.endswith(".csv"):
                with z.open(f) as csvfile:
                    cics = pd.read_csv(csvfile)

    csv_config = dict(
        index=False,
        date_format="%Y-%m-%d",
        float_format="%d",
    )
    for f in CIC_FIELDS:
        cics.loc[:, f] = cics[f].fillna("").str.replace("\n", " ")

    cics = cics.rename(
        columns={
            "uid": "org_id",
        }
    )

    if save_location:
        # save active cics
        click.echo("Saving cics.csv")
        cics.to_csv(os.path.join(save_location, "cics.csv"), **csv_config)
        click.echo("Saved cics.csv")

    return cics


if __name__ == "__main__":
    fetch_cics()
