import pandas as pd

tags = pd.read_csv("./data/ukcat.csv", index_col="Code")

intro = """# UK Charity Activity Tags (UK-CAT) classification system

UK-CAT is a classification system designed to categorise the activites of charities in the UK.
More detail about how the system was designed can be found on [the main page](/).

The system is organised into {:,.0f} categories, with {:,.0f} subcategories and {:,.0f} tags in
total. It is designed to accomodate charities having more than tag applied.
""".format(
    len(tags[tags["Level"] == 1]),
    len(tags[tags["Level"] == 2]),
    len(tags[tags["Level"] >= 2]),
)
print(intro)

for index, row in tags.iterrows():
    if row["Level"] == 1:
        print()
        print("## {} [`{}`]".format(row["tag"], index))
        print()
        print("Code | Tag | Subcategory")
        print("-----|-----|-----")
    else:
        print(
            "`{}` | {} | {}".format(
                index,
                row["tag"],
                row["Subcategory"] if isinstance(row["Subcategory"], str) else "",
            )
        )
