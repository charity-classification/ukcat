import pickle

import click
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ukcat.settings import (
    ADDITIONAL_STOPWORDS,
    BAD_SYMBOLS_RE,
    ICNPTSO_MODEL,
    ML_CATEGORY_FIELD,
    ML_DEFAULT_FIELDS,
    ML_RANDOM_STATE,
    ML_TEST_TRAIN_SIZE,
    REPLACE_BY_SPACE_RE,
    SAMPLE_FILE,
    TOP2000_FILE,
)

lemma = WordNetLemmatizer()

STOPWORDS = set(stopwords.words("english") + ADDITIONAL_STOPWORDS)


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


def get_text_corpus(df, fields=ML_DEFAULT_FIELDS, fill_activities=True):
    nltk.download("stopwords")
    nltk.download("wordnet")

    # if available then fill the activities field with objects if it's not available
    if fill_activities and ("objects" in df.columns) and ("activities" in fields):
        df.loc[:, "activities"] = df["activities"].fillna(df["objects"].fillna(""))

    corpus = df[fields].fillna("").apply(lambda x: " ".join(x), axis=1)
    return corpus.apply(clean_text).values


@click.command()
@click.option(
    "--sample-files",
    "-s",
    multiple=True,
    default=[SAMPLE_FILE, TOP2000_FILE],
    help="CSV files used to construct the sample. The columns must contain the fields in `--fields` and the `--category-field`",
)
@click.option(
    "--fields",
    "-f",
    multiple=True,
    default=ML_DEFAULT_FIELDS,
    help="Fields from which to create a text corpus. They will be combined with a space",
)
@click.option(
    "--category-field",
    default=ML_CATEGORY_FIELD,
    help="The field containing the category we're building the model against",
)
@click.option(
    "--save-location",
    default=ICNPTSO_MODEL,
    help="Where the model will be saved as a pickle file",
)
def create_ml_model(sample_files, fields, category_field, save_location):

    # create the sample dataframe
    df = pd.concat([pd.read_csv(f) for f in sample_files]).reset_index()

    # select the rows where ICNPTSO is not null
    df = df[df[category_field].notnull()]

    click.echo("Loaded sample dataset [{:,.0f} rows]".format(len(df)))

    # `y` is the ICNPTSO code attached to the charity.
    y = df[category_field].values

    # `X` is the list of cleaned values
    X = get_text_corpus(df, list(fields))

    # Split the values into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ML_TEST_TRAIN_SIZE, random_state=ML_RANDOM_STATE
    )
    click.echo("Split into test and training data")
    click.echo(" - {:,.0f} test rows".format(len(X_test)))
    click.echo(" - {:,.0f} training rows".format(len(X_train)))

    # create the training pipeline
    click.echo("Creating training pipeline")
    nb = Pipeline(
        [
            ("vect", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ("clf", LogisticRegression(n_jobs=5, C=1e5, max_iter=1000)),
        ]
    )
    click.echo("Fitting training data")
    nb.fit(X_train, y_train)

    click.echo("Testing model accuracy")
    y_pred = nb.predict(X_test)

    click.echo("Accuracy: {:.4f}".format(accuracy_score(y_pred, y_test)))

    click.echo("Saving model to [{}]".format(save_location))
    with open(save_location, "wb") as model_file:
        pickle.dump(nb, model_file)


if __name__ == "__main__":
    create_ml_model()
