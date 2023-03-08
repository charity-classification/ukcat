import os
import pickle
from typing import Optional, Sequence

import click
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
@click.option(
    "--charity-csv",
    default=CHARITY_CSV,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--icnptso-model",
    default=ICNPTSO_MODEL,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--icnptso-csv",
    default=ICNPTSO_CSV,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option("--id-field", default="org_id", type=str)
@click.option("--name-field", default="name", type=str)
@click.option(
    "--fields-to-use", "-f", multiple=True, default=ML_DEFAULT_FIELDS, type=str
)
@click.option(
    "--save-location",
    default=None,
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
)
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
    type=str,
    help="Overwrite the values for the charities in the sample with the manually found ICNPTSO from these files",
)
def apply_icnptso(
    charity_csv: str,
    icnptso_model: str,
    icnptso_csv: str,
    id_field: str,
    name_field: str,
    fields_to_use: Sequence[str],
    save_location: Optional[str],
    sample: int,
    add_names: bool,
    manual_files: Sequence[str],
) -> pd.DataFrame:
    if not save_location:
        save_location = charity_csv.replace(".csv", "-icnptso.csv")

    # open the charity csv file
    charities = pd.read_csv(charity_csv, index_col=id_field)
    if sample > 0:
        charities = charities.sample(sample)

    # create the corpus
    corpus = get_text_corpus(charities, fields=list(fields_to_use), do_cleaning=False)

    # fetch the model
    if os.path.exists(icnptso_model):
        with open(icnptso_model, "rb") as model_file:
            nb = pickle.load(model_file)
    else:
        nb = create_ml_model(save_location=icnptso_model)

    # apply the model
    y_pred_proba = nb.predict_proba(corpus)
    y_pred_proba = pd.DataFrame([dict(zip(nb.classes_, row)) for row in y_pred_proba])

    # create the output dataframe
    results = pd.DataFrame.from_dict(
        {
            "icnptso_code": y_pred_proba.idxmax(axis=1),
            "icnptso_code_probability": y_pred_proba.max(axis=1).round(3),
            id_field: charities.index,
        }
    )
    results.loc[:, "icnptso_code_source"] = "ml_model"

    # convert data to dataframe
    results = results.sort_values([id_field, "icnptso_code"]).drop_duplicates()[
        [id_field, "icnptso_code", "icnptso_code_probability", "icnptso_code_source"]
    ]

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
            manual_data, on=id_field, how="left"
        )["manual_icnptso_code"].fillna(results["icnptso_code"])
        results.loc[
            results[id_field].isin(manual_data.index), "icnptso_code_source"
        ] = "manual"
        results.loc[
            results[id_field].isin(manual_data.index), "icnptso_code_probability"
        ] = pd.NA

    # add in name and code names
    if add_names:
        icnptso_codes = pd.read_csv(icnptso_csv)
        icnptso_codes.index = (
            icnptso_codes["Sub-group"]
            .fillna(icnptso_codes["Group"])
            .fillna(icnptso_codes["Section"])
            .rename()
        )

        results = results.join(charities[name_field], on=id_field)
        results = results.join(
            icnptso_codes["Title"].rename("icnptso_name"), on="icnptso_code"
        )

    results = results.drop_duplicates()

    # save the results
    if save_location:
        results.to_csv(save_location, index=False)

    return results
