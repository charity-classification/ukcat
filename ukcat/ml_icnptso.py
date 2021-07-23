import pickle

import click
import pandas as pd
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression

from ukcat.settings import (
    ADDITIONAL_STOPWORDS,
    SAMPLE_FILE,
    TOP2000_FILE,
    REPLACE_BY_SPACE_RE,
    BAD_SYMBOLS_RE,
    ML_RANDOM_STATE,
    ML_TEST_TRAIN_SIZE,
    ICNPTSO_MODEL,
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


def get_text_corpus(df, fields=["name", "activities"]):
    corpus = df[fields].fillna("").apply(lambda x: " ".join(x), axis=1)
    return corpus.apply(clean_text).values


@click.command()
@click.option("--save-location", default=ICNPTSO_MODEL)
def create_ml_model(save_location):
    nltk.download("stopwords")
    nltk.download("wordnet")

    # create the sample dataframe
    df = pd.concat(
        [
            pd.read_csv(SAMPLE_FILE),
            pd.read_csv(TOP2000_FILE),
        ]
    ).reset_index()

    # select the rows where ICNPTSO is not null
    df = df[df["ICNPTSO"].notnull()]

    click.echo("Loaded sample dataset [{:,.0f} rows]".format(len(df)))

    # `y` is the ICNPTSO code attached to the charity.
    y = df["ICNPTSO"].values

    # `X` is the list of cleaned values
    X = get_text_corpus(df, ["name", "activities"])

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
    with open(save_location, 'wb') as model_file:
        pickle.dump(nb, model_file)


if __name__ == "__main__":
    create_ml_model()
