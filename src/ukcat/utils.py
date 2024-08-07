import re
from typing import Sequence

import pandas as pd
from airtable import Airtable


def airtable_to_dataframe(airtable: Airtable, join_fields: Sequence[str] = []):
    data = airtable.get_all()
    df = pd.DataFrame(
        index=[i["id"] for i in data],
        data=[i["fields"] for i in data],
    )
    df.index = df.index.rename("ID")
    for f in join_fields:
        df.loc[:, f] = df[f].apply(lambda x: ";".join(x) if isinstance(x, list) else None)
    return df


def regnumber_to_orgid(reg_number: str) -> str:
    if reg_number.startswith("N"):
        return "GB-NIC-{}".format(re.sub("[^0-9]", "", reg_number))
    if reg_number.startswith("S"):
        return "GB-SC-SC{}".format(re.sub("[^0-9]", "", reg_number).zfill(6))
    return "GB-CHC-{}".format(reg_number)
