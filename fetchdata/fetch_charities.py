import os

import click
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

CCEW_CHARITY_FILE = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.charity.zip"
CCEW_GD_FILE = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.charity_governing_document.zip"

OSCR_ACTIVE = "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload"
OSCR_INACTIVE = (
    "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityFormerRegDownload"
)

CCNI_DATA = "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?include=Linked&include=Removed"
CCNI_ACTIVITIES_CSV = "./data/ccni_activities.csv"

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
]


def fetch_ccew(ccew_charity_file, ccew_gd_file):

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
    )
    ccew.loc[:, "objects"] = ccew.join(
        ccew_gd[ccew_gd["linked_charity_number"] == 0].set_index(
            "registered_charity_number"
        )["charitable_objects"],
        on="reg_number",
        how="left",
    )["charitable_objects"].rename("objects")
    click.echo("Loaded CCEW charitable objects file")

    return ccew[FIELDS]


def fetch_oscr(oscr_active, oscr_inactive):
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

    return oscr[FIELDS]


def fetch_ccni(ccni_data, ccni_activities_csv):
    click.echo("Loading CCNI data file")
    ccni = pd.read_csv(
        ccni_data,
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
    ccni.loc[:, "postcode"] = ccni["Public address"].apply(lambda x: x.split(", ")[-1])
    ccni.loc[:, "last_updated"] = pd.to_datetime("today")
    ccni.loc[:, "org_id"] = ccni["reg_number"].apply(lambda x: f"GB-NIC-{x}")
    ccni.loc[:, "reg_number"] = ccni["reg_number"].apply(lambda x: f"NI{x}")

    return ccni[FIELDS]


@click.command()
@click.option("--ccew-charity-file", default=CCEW_CHARITY_FILE)
@click.option("--ccew-gd-file", default=CCEW_GD_FILE)
@click.option("--oscr-active", default=OSCR_ACTIVE)
@click.option("--oscr-inactive", default=OSCR_INACTIVE)
@click.option("--ccni-data", default=CCNI_DATA)
@click.option("--ccni-activities-csv", default=CCNI_ACTIVITIES_CSV)
@click.option("--save-location", default="./data/")
def fetch_charities(
    ccew_charity_file,
    ccew_gd_file,
    oscr_active,
    oscr_inactive,
    ccni_data,
    ccni_activities_csv,
    save_location,
):
    """Fetch data on charities"""

    charities = pd.concat(
        [
            fetch_ccew(ccew_charity_file, ccew_gd_file),
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


if __name__ == "__main__":
    fetch_charities()
