import re

import pandas as pd


def airtable_to_dataframe(airtable, join_fields=[]):
    data = airtable.get_all()
    df = pd.DataFrame(
        index=[i["id"] for i in data],
        data=[i["fields"] for i in data],
    )
    df.index = df.index.rename("ID")
    for f in join_fields:
        df.loc[:, f] = df[f].apply(
            lambda x: ";".join(x) if isinstance(x, list) else None
        )
    return df


def regnumber_to_orgid(reg_number):
    if reg_number.startswith("N"):
        return "GB-NIC-{}".format(re.sub("[^0-9]", "", reg_number))
    if reg_number.startswith("S"):
        return "GB-SC-SC{}".format(re.sub("[^0-9]", "", reg_number).zfill(6))
    return "GB-CHC-{}".format(reg_number)
