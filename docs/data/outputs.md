# Data

Data outputs from the project can be found in the [github repository](https://github.com/drkane/ukcat/tree/main/data). The following resources are available:

## Classification schema

- ICNP/TSO: [`icnptso.csv`](https://github.com/drkane/ukcat/blob/main/data/icnptso.csv)
- UK-CAT: [`ukcat.csv`](https://github.com/drkane/ukcat/blob/main/data/ukcat.csv)

You can also see a list of the [UK-CAT categories](tag_list.md) as an HTML page.

## Manually classified charities

These files show the charities that were [manually classified](method/manual-classification.md) as part of this project. 

- [`sample.csv`](https://github.com/drkane/ukcat/blob/main/data/sample.csv)
- [`top2000.csv`](https://github.com/drkane/ukcat/blob/main/data/top2000.csv)

## Results of running automated classification

These files show the results of running automatic classification for Uk-CAT and ICNP/TSO against
the latest lists of active and inactive charities in the UK.

The UK-CAT classification used a system of [rules-based classification](method/rules-based-classification.md) as described in the methodology. The ICNP/TSO classification uses a [machine-learning model](method/machine-learning.md) that is overwritten by any manual classifications found in the sample.

- [`charities_active-ukcat.csv`](https://github.com/drkane/ukcat/blob/main/data/charities_active-ukcat.csv)
- [`charities_inactive-ukcat.csv`](https://github.com/drkane/ukcat/blob/main/data/charities_inactive-icnptso.csv)
- [`charities_active-icnptso.csv`](https://github.com/drkane/ukcat/blob/main/data/charities_active-icnptso.csv)
- [`charities_inactive-icnptso.csv`](https://github.com/drkane/ukcat/blob/main/data/charities_inactive-icnptso.csv)
