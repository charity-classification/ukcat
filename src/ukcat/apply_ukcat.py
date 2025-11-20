from typing import Optional, Sequence

import click
import pandas as pd
from tqdm import tqdm

from ukcat.apply_icnptso import MANUAL_FILES
from ukcat.ml_icnptso import get_text_corpus
from ukcat.settings import CHARITY_CSV, UKCAT_FILE


@click.command()
@click.option(
    "--charity-csv",
    default=CHARITY_CSV,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--ukcat-csv",
    default=UKCAT_FILE,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option("--id-field", default="org_id", type=str)
@click.option("--name-field", default="name", type=str)
@click.option("--fields-to-use", "-f", multiple=True, default=["name", "activities"], type=str)
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
    "--include-groups/--no-include-groups",
    default=False,
    help="Add codes for the intermediate groups to the results",
)
@click.option(
    "--manual-files",
    "-m",
    multiple=True,
    default=MANUAL_FILES,
    type=str,
    help="Overwrite the values for the charities in the sample with the manually found ICNPTSO from these files",
)
def apply_ukcat(
    charity_csv: str,
    ukcat_csv: str,
    id_field: str,
    name_field: str,
    fields_to_use: Sequence[str],
    save_location: Optional[str],
    sample: int,
    add_names: bool,
    include_groups: bool,
    manual_files: Sequence[str],
) -> pd.DataFrame:
    if not save_location:
        save_location = charity_csv.replace(".csv", "-ukcat.csv")

    # open the charity csv file
    charities = pd.read_csv(charity_csv, index_col=id_field)
    if sample > 0:
        charities = charities.sample(sample)

    # create the corpus
    corpus = pd.Series(
        index=charities.index,
        data=get_text_corpus(charities, fields=list(fields_to_use), do_cleaning=False),
    )

    # fetch the classification file
    ukcat = pd.read_csv(ukcat_csv, index_col="Code")

    # for each classification category go through and apply the regular expression
    results_list = []
    for index, row in tqdm(ukcat.iterrows(), total=len(ukcat)):
        if not isinstance(row["Regular expression"], str) or row["Regular expression"] == r"\b()\b":
            continue
        criteria = corpus.str.contains(row["Regular expression"], case=False, regex=True)
        if isinstance(row["Exclude regular expression"], str) and row["Exclude regular expression"] != r"\b()\b":
            criteria = criteria & ~corpus.str.contains(row["Exclude regular expression"], case=False, regex=True)

        results_list.append(
            pd.Series(
                data=index,
                index=charities[criteria].index,
                name="ukcat_code",
            )
        )

    results = pd.concat(results_list)

    # open the manual files and find the codes to apply
    if manual_files:
        manual_data = (
            pd.concat([pd.read_csv(f) for f in manual_files])
            .groupby("org_id")
            .first()["UKCAT"]
            .rename("manual_icnptso_code")
        )
        manual_data = manual_data[manual_data.notnull()].apply(lambda x: x.split(";")).explode()
        # remove any existing codes and replace with manual ones
        results = results.drop(results.index.isin(manual_data.index), errors="ignore")
        results = pd.concat([results, manual_data.rename("ukcat_code")])

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
    results = results.to_frame().reset_index().sort_values([id_field, "ukcat_code"]).drop_duplicates()

    # add in name and code names
    if add_names:
        results = results.join(charities[name_field], on=id_field)
        results = results.join(ukcat["tag"].rename("ukcat_name"), on="ukcat_code")

    results = results.drop_duplicates()

    # save the results
    if save_location:
        results.to_csv(save_location, index=False)

    return results
