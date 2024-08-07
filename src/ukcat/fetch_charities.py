import csv
import io
import os

import click
import pandas as pd
import requests

from ukcat.settings import (
    CCEW_CHARITY_FILE,
    CCEW_GD_FILE,
    CCEW_PARTA_FILE,
    CCNI_ACTIVITIES_CSV,
    CCNI_DATA,
    DATA_DIR,
    OSCR_ACTIVE,
    OSCR_INACTIVE,
)

FIELDS = [
    "org_id",
    "reg_number",
    "name",
    "postcode",
    "active",
    "date_registered",
    "date_removed",
    "web",
    "company_number",
    "activities",
    "objects",
    "source",
    "last_updated",
    "income",
    "spending",
    "fye",
    "grant_making_is_main_activity",
]


def fetch_ccew(ccew_charity_file: str, ccew_gd_file: str, ccew_parta_file: str) -> pd.DataFrame:
    ccew_date_fields = [
        "date_of_registration",
        "date_of_removal",
        "date_of_extract",
        "latest_acc_fin_period_end_date",
    ]

    click.echo("Loading CCEW data file")
    ccew = pd.read_csv(
        ccew_charity_file,
        sep="\t",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
        parse_dates=ccew_date_fields,
    )
    click.echo("Loaded CCEW data file")

    ccew = ccew[ccew["linked_charity_number"] == 0]
    ccew = ccew.rename(
        columns={
            "registered_charity_number": "reg_number",
            "charity_name": "name",
            "charity_contact_postcode": "postcode",
            #     "active",
            "date_of_registration": "date_registered",
            "date_of_removal": "date_removed",
            "charity_contact_web": "web",
            "charity_company_registration_number": "company_number",
            "charity_activities": "activities",
            #     "objects",
            #     "source",
            "date_of_extract": "last_updated",
            "latest_income": "income",
            "latest_expenditure": "spending",
            "latest_acc_fin_period_end_date": "fye",
        }
    )
    ccew.loc[:, "source"] = "ccew"
    ccew.loc[:, "active"] = ccew["charity_registration_status"] == "Registered"
    ccew.loc[:, "org_id"] = ccew["reg_number"].apply(lambda x: f"GB-CHC-{x}")

    # Get charitable objects
    click.echo("Loading CCEW charitable objects file")
    ccew_gd = pd.read_csv(
        ccew_gd_file,
        sep="\t",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
    )
    ccew.loc[:, "objects"] = ccew.join(
        ccew_gd[ccew_gd["linked_charity_number"] == 0].set_index("registered_charity_number")["charitable_objects"],
        on="reg_number",
        how="left",
    )["charitable_objects"].rename("objects")
    click.echo("Loaded CCEW charitable objects file")

    # Get whether they are mainly a grantmaker
    click.echo("Loading CCEW charitable objects file")
    ccew_parta = pd.read_csv(
        ccew_parta_file,
        sep="\t",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
    )

    ccew.loc[:, "grant_making_is_main_activity"] = ccew.join(
        ccew_parta[ccew_parta["latest_fin_period_submitted_ind"]].set_index("registered_charity_number")[
            "grant_making_is_main_activity"
        ],
        on="reg_number",
        how="left",
    )["grant_making_is_main_activity"].fillna(False)
    click.echo("Loaded CCEW charitable objects file")

    return ccew[FIELDS]


def fetch_oscr(oscr_active: str, oscr_inactive: str) -> pd.DataFrame:
    click.echo("Loading OSCR data files")
    oscr = pd.concat(
        [
            pd.read_csv(
                oscr_active,
                compression="zip",
            ),
            pd.read_csv(
                oscr_inactive,
                compression="zip",
            ),
        ]
    )
    click.echo("Loaded OSCR data files")
    for c in ["Registered Date", "Year End", "Ceased Date"]:
        oscr.loc[:, c] = pd.to_datetime(oscr[c], dayfirst=True)

    oscr = oscr.rename(
        columns={
            "Charity Number": "reg_number",
            "Charity Name": "name",
            "Postcode": "postcode",
            #     "active",
            "Registered Date": "date_registered",
            "Ceased Date": "date_removed",
            "Website": "web",
            #     "company_number",
            #     "activities",
            "Objectives": "objects",
            #     "source",
            #     "last_updated",
            "Most recent year income": "income",
            "Most recent year expenditure": "spending",
            "Year End": "fye",
        }
    )
    oscr.loc[:, "source"] = "oscr"
    oscr.loc[:, "active"] = oscr["date_removed"].isnull()
    oscr.loc[:, "company_number"] = None
    oscr.loc[:, "activities"] = None
    oscr.loc[:, "last_updated"] = pd.to_datetime("today")
    oscr.loc[:, "org_id"] = oscr["reg_number"].apply(lambda x: f"GB-SC-{x}")
    oscr.loc[:, "grant_making_is_main_activity"] = None

    return oscr[FIELDS]


def fetch_ccni(ccni_data: str, ccni_activities_csv: str) -> pd.DataFrame:
    click.echo("Loading CCNI data file")
    ccni_data_response = requests.get(ccni_data, verify=False)
    ccni = pd.read_csv(
        io.BytesIO(ccni_data_response.content),
        encoding="cp858",
        dayfirst=True,
        parse_dates=[
            "Date registered",
            "Date for financial year ending",
        ],
    )
    click.echo("Loaded CCNI data file")

    # get activities file
    ccni = ccni.join(
        pd.read_csv(ccni_activities_csv, index_col="regno"),
        on="Reg charity number",
        how="left",
    )

    ccni = ccni.rename(
        columns={
            "Reg charity number": "reg_number",
            "Charity name": "name",
            #     "postcode",
            #     "active",
            "Date registered": "date_registered",
            #     "date_removed",
            "Website": "web",
            "Company number": "company_number",
            "what your organisation does": "activities",
            "charitable purposes": "objects",
            #     "source",
            #     "last_updated",
            "Total income": "income",
            "Total spending": "spending",
            "Date for financial year ending": "fye",
        }
    )
    ccni.loc[:, "source"] = "ccni"
    ccni.loc[:, "active"] = ccni["Status"] != "Removed"
    ccni.loc[:, "date_removed"] = None
    ccni.loc[:, "postcode"] = ccni["Public address"].fillna("").apply(lambda x: x.split(", ")[-1])
    ccni.loc[:, "last_updated"] = pd.to_datetime("today")
    ccni.loc[:, "org_id"] = ccni["reg_number"].apply(lambda x: f"GB-NIC-{x}")
    ccni.loc[:, "reg_number"] = ccni["reg_number"].apply(lambda x: f"NI{x}")
    ccni.loc[:, "grant_making_is_main_activity"] = None

    return ccni[FIELDS]


@click.command()
@click.option("--ccew-charity-file", default=CCEW_CHARITY_FILE, type=str)
@click.option("--ccew-gd-file", default=CCEW_GD_FILE, type=str)
@click.option("--ccew-parta-file", default=CCEW_PARTA_FILE, type=str)
@click.option("--oscr-active", default=OSCR_ACTIVE, type=str)
@click.option("--oscr-inactive", default=OSCR_INACTIVE, type=str)
@click.option("--ccni-data", default=CCNI_DATA, type=str)
@click.option("--ccni-activities-csv", default=CCNI_ACTIVITIES_CSV)
@click.option(
    "--save-location",
    default=DATA_DIR,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def fetch_charities(
    ccew_charity_file: str,
    ccew_gd_file: str,
    ccew_parta_file: str,
    oscr_active: str,
    oscr_inactive: str,
    ccni_data: str,
    ccni_activities_csv: str,
    save_location: str,
) -> pd.DataFrame:
    """Fetch data on charities"""

    charities = pd.concat(
        [
            fetch_ccew(ccew_charity_file, ccew_gd_file, ccew_parta_file),
            fetch_oscr(oscr_active, oscr_inactive),
            fetch_ccni(ccni_data, ccni_activities_csv),
        ]
    )

    csv_config = dict(
        index=False,
        date_format="%Y-%m-%d",
        float_format="%d",
    )
    for f in ["activities", "objects"]:
        charities.loc[:, f] = charities[f].fillna("").str.replace("\n", " ")

    if save_location:
        # save active charities
        click.echo("Saving charities_active.csv")
        charities.loc[charities["active"], FIELDS].to_csv(
            os.path.join(save_location, "charities_active.csv"), **csv_config
        )
        click.echo("Saved charities_active.csv")

        # save inactive charities
        click.echo("Saving charities_inactive.csv")
        charities.loc[~charities["active"], FIELDS].to_csv(
            os.path.join(save_location, "charities_inactive.csv"), **csv_config
        )
        click.echo("Saved charities_inactive.csv")

    return charities


if __name__ == "__main__":
    fetch_charities()
