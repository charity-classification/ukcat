import os
import pickle

import click
import nltk
import pandas as pd

from ukcat.ml_icnptso import create_ml_model, get_text_corpus
from ukcat.settings import (
    CHARITY_CSV,
    ICNPTSO_CSV,
    ICNPTSO_MODEL,
    ML_DEFAULT_FIELDS,
    SAMPLE_FILE,
    TOP2000_FILE,
)

MANUAL_FILES = [
    SAMPLE_FILE,
    TOP2000_FILE,
]


@click.command()
@click.option("--charity-csv", default=CHARITY_CSV)
@click.option("--icnptso-model", default=ICNPTSO_MODEL)
@click.option("--icnptso-csv", default=ICNPTSO_CSV)
@click.option("--id-field", default="org_id")
@click.option("--fields-to-use", "-f", multiple=True, default=ML_DEFAULT_FIELDS)
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
    "--manual-files",
    "-m",
    multiple=True,
    default=MANUAL_FILES,
    help="Overwrite the values for the charities in the sample with the manually found ICNPTSO from these files",
)
def apply_icnptso(
    charity_csv,
    icnptso_model,
    icnptso_csv,
    id_field,
    fields_to_use,
    save_location,
    sample,
    add_names,
    manual_files,
):
    if not save_location:
        save_location = charity_csv.replace(".csv", "-icnptso.csv")

    # open the charity csv file
    charities = pd.read_csv(charity_csv, index_col=id_field)
    if sample > 0:
        charities = charities.sample(sample)

    # create the corpus
    corpus = get_text_corpus(charities, fields=list(fields_to_use))

    # fetch the model
    if os.path.exists(icnptso_model):
        with open(icnptso_model, "rb") as model_file:
            nb = pickle.load(model_file)
    else:
        nb = create_ml_model(save_location=icnptso_model)

    # apply the model
    y_pred = nb.predict(corpus)

    # create the ouptut file
    results = pd.Series(index=charities.index, data=y_pred, name="icnptso_code")

    # convert data to dataframe
    results = (
        results.to_frame()
        .reset_index()
        .sort_values(["org_id", "icnptso_code"])
        .drop_duplicates()
    )

    # open the manual files and find the codes to apply
    if manual_files:
        manual_data = (
            pd.concat([pd.read_csv(f) for f in manual_files])
            .groupby("org_id")
            .first()["ICNPTSO"]
            .rename("manual_icnptso_code")
        )
        manual_data = manual_data[manual_data.notnull()]
        results.loc[:, "icnptso_code"] = results.join(
            manual_data, on="org_id", how="left"
        )["manual_icnptso_code"].fillna(results["icnptso_code"])

    # add in name and code names
    if add_names:

        icnptso_codes = pd.read_csv(icnptso_csv)
        icnptso_codes.index = (
            icnptso_codes["Sub-group"]
            .fillna(icnptso_codes["Group"])
            .fillna(icnptso_codes["Section"])
            .rename()
        )

        results = results.join(charities["name"], on="org_id")
        results = results.join(
            icnptso_codes["Title"].rename("icnptso_name"), on="icnptso_code"
        )

    # save the results
    results.to_csv(save_location, index=False)
