import os
import re


# data directory
DATA_DIR = "./data"

# files to store data in
CHARITY_CSV = os.path.join(DATA_DIR, "charities_active.csv")
UKCAT_FILE = os.path.join(DATA_DIR, "ukcat.csv")
ICNPTSO_CSV = os.path.join(DATA_DIR, "icnptso.csv")
ICNPTSO_MODEL = os.path.join(DATA_DIR, "icnptso_ml_model.pkl")
SAMPLE_FILE = os.path.join(DATA_DIR, "sample.csv")
TOP2000_FILE = os.path.join(DATA_DIR, "top2000.csv")

# regexes for use in machine learning models and text cleaning
REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
ADDITIONAL_STOPWORDS = [
    "trust",
    "fund",
    "charitable",
    "charity",
]

# machine learning settings
ML_RANDOM_STATE=42
ML_TEST_TRAIN_SIZE=0.2

# location of charity download files
######################################

# Charity Commission for England and Wales
CCEW_CHARITY_FILE = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.charity.zip"
CCEW_GD_FILE = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.charity_governing_document.zip"
CCEW_PARTA_FILE = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.charity_annual_return_parta.zip"

# Office of Scottish Charity Regulator
OSCR_ACTIVE = "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload"
OSCR_INACTIVE = (
    "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityFormerRegDownload"
)

# Charity Commission for Northern Ireland
CCNI_DATA = "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?include=Linked&include=Removed"
CCNI_ACTIVITIES_CSV = "./data/ccni_activities.csv"
