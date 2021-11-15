import os

import click
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape
from tqdm import tqdm

from ukcat import settings


def distribution(df, field, category_charities):
    distribution_df = pd.DataFrame(
        {
            "all": df[field].value_counts(),
            "category": df.loc[category_charities, field].value_counts(),
        }
    )
    distribution_df.loc["Total", :] = distribution_df.sum()
    distribution_df.loc[:, "percentage"] = distribution_df["category"].divide(
        distribution_df["all"]
    )
    return distribution_df


@click.command()
@click.option(
    "--charity-csv",
    default=settings.CHARITY_CSV,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--ukcat-csv",
    default=settings.UKCAT_FILE,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option("--id-field", default="org_id", type=str)
@click.option("--template", "-t", default="ukcat.md.j2", type=str)
@click.option(
    "--save-location",
    default="./docs/data/ukcat",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
)
def make_ukcat_docs(charity_csv, ukcat_csv, id_field, template, save_location):
    charities = pd.read_csv(charity_csv, index_col=id_field)
    charities_ukcat = pd.read_csv(charity_csv.replace(".csv", "-ukcat.csv"))
    ukcat = pd.read_csv(ukcat_csv, index_col="Code")

    charities.loc[:, "income_band"] = pd.cut(
        charities["income"],
        bins=settings.INCOME_BINS,
        labels=settings.INCOME_BIN_LABELS,
    )

    env = Environment(
        # loader=PackageLoader("ukcat"),
        loader=FileSystemLoader("ukcat/templates"),
        autoescape=select_autoescape(),
    )

    tag_list_template = env.get_template("tag_list.md.j2")
    with open("./docs/data/tag_list.md", "w", encoding="utf-8") as f:
        f.write(
            tag_list_template.render(
                n_categories=len(ukcat[ukcat["Level"] == 1]),
                n_subcategories=len(ukcat[ukcat["Level"] == 2]),
                n_tags=len(ukcat[ukcat["Level"] >= 2]),
                tags=ukcat,
            )
        )

    template = env.get_template(template)

    if not os.path.exists(save_location):
        os.makedirs(save_location)

    for category in tqdm(ukcat.index.tolist()):
        category_charities = charities_ukcat.loc[
            charities_ukcat["ukcat_code"].str.startswith(category), id_field
        ].unique()

        top_charities = (
            charities.loc[category_charities, :]
            .sort_values("income", ascending=False)
            .head(10)
            .replace({np.nan: None})
            .reset_index()
            .to_dict(orient="records")
        )

        random_charities = []
        if len(charities.loc[category_charities, :]) > 10:
            random_charities = (
                charities.loc[category_charities, :]
                .sample(10)
                .replace({np.nan: None})
                .reset_index()
                .to_dict(orient="records")
            )

        result = template.render(
            category=category,
            details=ukcat.loc[category, :].replace({np.nan: None}).to_dict(),
            by_income=distribution(charities, "income_band", category_charities)
            .reset_index()
            .to_dict("records"),
            by_source=distribution(charities, "source", category_charities)
            .reset_index()
            .to_dict("records"),
            top_charities=top_charities,
            random_charities=random_charities,
        )
        with open(
            os.path.join(save_location, category + ".md"), "w", encoding="utf-8"
        ) as f:
            f.write(result)
