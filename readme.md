# Classifying UK Charities

This repository is the home of the *UK Charity Activity Tags*, a project to classify
every UK registered charity using two classification taxonomies.

The project was a collaboration between [NCVO Research](https://www.ncvo.org.uk/policy-and-research), Dr Christopher Damm at the [Centre for Regional Economic and Social Research (Sheffield Hallam University)](https://www4.shu.ac.uk/research/cresr/staff/christopher-damm) and [David Kane](https://dkane.net/), an independent freelance researcher. The project was funded by Esmée Fairbairn Foundation.

The project started in Autumn 2020 with the first draft release of data in Summer 2021.

## Using the python scripts

The scripts included in the repository were created using Python 3.9. They are likely to work with other versions of Python too.

### Installing dependencies

To use the python scripts, you'll need to install the required packages. The best way to do this is with a virtual environment:

```sh
python -m venv env  # creates a virtual environment in the ./env directory
# now activate the virtual environment
env\Scripts\activate  # (on windows)
source env/bin/activate   # (on unix/mac os)
pip -r requirements.txt  # installs the requirements 
```

You can then run the python scripts as described above - remember to activate the virtual environment every time you open a new terminal.

### Updating or adding additional dependencies

Dependencies are managed using [pip-tools](https://github.com/jazzband/pip-tools). First install it with:

```sh
python -m pip install pip-tools wheel setuptools
```

Then add any additional dependencies to `requirements.in`. Run `pip-compile` to create an updated `requirements.txt` file, and then run `pip-sync` to install the new requirements.

**!! Important - don't edit the `requirements.txt` file directly, it should only be edited with pip-compile**

## Repository contents

### `/docs`

This directory contains the project documentation, which is turned into a website using [mkdocs](https://www.mkdocs.org/).

You can run a local version of the docs using `mkdocs serve`.

The website is generated using Github actions.

### `/notebooks`

These notebooks contain code for processing the data, such as the machine learning model for ICNP/TSO classification.

To run the notebooks from with the virtual environment, use the following code ([from veekaybee.github.io](https://veekaybee.github.io/2020/02/18/running-jupyter-in-venv/)), after install the dependencies above

```sh
ipython kernel install --user --name=ukcat
jupyter notebook  # or `jupyter lab`
```

### `/fetchdata`

This is a series of Python commands for fetching the data used in the project. The commands are as follows:

#### Fetch all charities

```sh
python -m fetchdata fetch-charities
```

This will create two CSV files containing data on charities. The files will be created in the `./data/` folder, and are `./data/charities_active.csv` and `./data/charities_inactive.csv`. 

These files are based on data from the [Charity Commission for England and Wales](https://register-of-charities.charitycommission.gov.uk/register/full-register-download), the [Scottish Charity Regulator](https://www.oscr.org.uk/about-charities/search-the-register/charity-register-download/) and the [Charity Commission for Northern Ireland](https://www.charitycommissionni.org.uk/charity-search/?pageNumber=1). Data is used under the Open Government Licence.

#### Fetch tags and sample

These are project internal scripts that fetch data from the airtable bases used by the project. They are used to create the two files `./data/sample.csv` and `./data/ukcat.csv` that are already available in the repo. They can only be operated correctly with the correct airtable credentials.

To fetch data you need to set two environment variables containing the airtable base ID and API key. The easiest way is to create a file called `.env` in this directory, and add the following lines (with the correct values):

```
AIRTABLE_API_KEY=keyGOESHERE
AIRTABLE_BASE_ID=appGOESHERE
```

An example can be found in `.env-sample`.

The commands to fetch the data are:

```sh
python -m fetchdata fetch-tags
python -m fetchdata fetch-sample
python -m fetchdata fetch-sample --table-name="Top charities" --save-location="./data/top2000.csv"
```