import os

import click
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

CHARITY_CSV = "./data/charities_active.csv"
UKCAT_FILE = "./data/ukcat.csv"


@click.command()
@click.option("--charity-csv", default=CHARITY_CSV)
@click.option("--ukcat-csv", default=UKCAT_FILE)
@click.option("--id-field", default="org_id")
@click.option("--fields-to-use", "-f", multiple=True, default=["name", "activities"])
@click.option("--save-location", default=None)
@click.option(
    "--sample",
    default=0,
    type=int,
    help="Only do a sample of the charities (for testing purposes)",
)
@click.option(
    "--add-names/--no-add-names",
    default=False,
    help="Add the charity and category names to the data",
)
@click.option(
    "--include-groups/--no-include-groups",
    default=False,
    help="Add codes for the intermediate groups to the results",
)
def apply_ukcat(
    charity_csv,
    ukcat_csv,
    id_field,
    fields_to_use,
    save_location,
    sample,
    add_names,
    include_groups,
):
    if not save_location:
        save_location = charity_csv.replace(".csv", "-ukcat.csv")

    # open the charity csv file
    charities = pd.read_csv(charity_csv, index_col=id_field)
    if sample > 0:
        charities = charities.sample(sample)

    # create the corpus
    corpus = (
        charities[list(fields_to_use)].fillna("").apply(lambda x: " ".join(x), axis=1)
    )

    # fetch the classification file
    ukcat = pd.read_csv(ukcat_csv, index_col="Code")

    # for each classification category go through and apply the regular expression
    results = []
    for index, row in tqdm(ukcat.iterrows(), total=len(ukcat)):
        if (
            not isinstance(row["Regular expression"], str)
            or row["Regular expression"] == r"\b()\b"
        ):
            continue
        criteria = corpus.str.contains(
            row["Regular expression"], case=False, regex=True
        )
        if (
            isinstance(row["Exclude regular expression"], str)
            and row["Exclude regular expression"] != r"\b()\b"
        ):
            criteria = criteria & ~corpus.str.contains(
                row["Exclude regular expression"], case=False, regex=True
            )

        results.append(
            pd.Series(
                data=index,
                index=charities[criteria].index,
                name="ukcat_code",
            )
        )

    results = pd.concat(results)

    # add 2-digit versions of the codes & mid-level codes
    if include_groups:
        results = pd.concat(
            [
                results,
                results.str[0:2],
                results[results.str[2].astype(int) > 1].apply(lambda x: x[0:3] + "00"),
            ]
        )

    # convert data to dataframe
    results = (
        results.to_frame()
        .reset_index()
        .sort_values(["org_id", "ukcat_code"])
        .drop_duplicates()
    )

    # add in name and code names
    if add_names:
        results = results.join(charities["name"], on="org_id")
        results = results.join(ukcat["tag"].rename("ukcat_name"), on="ukcat_code")

    # save the results
    results.to_csv(save_location, index=False)
