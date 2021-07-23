import pickle
import re

import click
import nltk
import pandas as pd
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer

load_dotenv()

CHARITY_CSV = "./data/charities_active.csv"
ICNPTSO_CSV = "./data/icnptso.csv"
ICNPTSO_MODEL = "./data/icnptso_ml_model.pkl"

REPLACE_BY_SPACE_RE = re.compile("[/(){}\[\]\|@,;]")
BAD_SYMBOLS_RE = re.compile("[^0-9a-z #+_]")
STOPWORDS = set(
    stopwords.words("english")
    + [
        "trust",
        "fund",
        "charitable",
        "charity",
    ]
)

stemmer = LancasterStemmer()
lemma = WordNetLemmatizer()


def clean_text(text):
    """
    text: a string

    return: modified initial string
    """
    text = text.lower()  # lowercase text
    text = REPLACE_BY_SPACE_RE.sub(
        " ", text
    )  # replace REPLACE_BY_SPACE_RE symbols by space in text
    text = BAD_SYMBOLS_RE.sub(
        "", text
    )  # delete symbols which are in BAD_SYMBOLS_RE from text
    text = " ".join(
        lemma.lemmatize(word) for word in text.split() if word not in STOPWORDS
    )  # delete stopwors from text
    return text


@click.command()
@click.option("--charity-csv", default=CHARITY_CSV)
@click.option("--icnptso-model", default=ICNPTSO_MODEL)
@click.option("--icnptso-csv", default=ICNPTSO_CSV)
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
def apply_icnptso(
    charity_csv,
    icnptso_model,
    icnptso_csv,
    id_field,
    fields_to_use,
    save_location,
    sample,
    add_names,
):
    if not save_location:
        save_location = charity_csv.replace(".csv", "-icnptso.csv")

    # open the charity csv file
    charities = pd.read_csv(charity_csv, index_col=id_field)
    if sample > 0:
        charities = charities.sample(sample)

    # create the corpus
    nltk.download("stopwords")
    corpus = (
        charities[list(fields_to_use)].fillna("").apply(lambda x: " ".join(x), axis=1)
    )
    corpus = corpus.apply(clean_text).values

    # fetch the model
    with open(icnptso_model, "rb") as model_file:
        nb = pickle.load(model_file)

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
