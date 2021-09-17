# Classifying UK Charities

This project is the home of the *UK Charity Activity Tags*, a project to classify
every UK registered charity using two classification taxonomies.

The project was a collaboration between [NCVO Research](https://www.ncvo.org.uk/policy-and-research), Dr Christopher Damm at the [Centre for Regional Economic and Social Research (Sheffield Hallam University)](https://www4.shu.ac.uk/research/cresr/staff/christopher-damm) and [David Kane](https://dkane.net/), an independent freelance researcher. The project was funded by Esmée Fairbairn Foundation.

The project started in Autumn 2020 with the first draft release of data in Autumn 2021.

## The need for this project

Use of data on registered charities is growing, but is constrained by the availability and quality of the data. Classifications of the service areas that charities operate in are a particular gap within the current available data. Data on these service areas are used by:

- **Infrastructure bodies**, for example a local Council for Voluntary Service, to examine the characteristics of the charity sector in their local area
- **Funders** to look at charities meeting particular areas of need or to help them with due diligence.
- **Researchers** to analyse a discrete service area (for example looking at the impact of COVID-19 on hospices) or compare between service areas.
- **Researchers** to provide a sampling frame for further survey or qualitative work
- **Charity service providers** to look at the size of market for products and services aimed at charities.

In England and Wales the main source of data on charities is the [Register of Charities](https://beta.charitycommission.gov.uk/) in England and Wales, maintained by the Charity Commission. It is one of the most comprehensive and detailed sources of data on Voluntary Sector Organisations (VSOs) anywhere in the world. Similar registers exist for charities registered in Scotland and Northern Ireland. They provide the main data source for many quantitative research studies on the voluntary sector and are excellent starting points for answering some of the above questions. The existing tools for classifying the register into service areas, however, are currently limited. 

## Method

The project aims to apply two sets of classification schemes to every registered charity in the UK. The two schemes are:

 - The **International Classification of Non-profit and Third Sector Organizations** (ICNP/TSO), which is part of the UN Satellite Accounts for Non-profits. Each charity was assigned one of these categories.
 - A new classification system - **UK Charity Activity Tags (UK-CAT)**, created as part of the project. These are a collection of general tags describing the activities of charities, based on an examination of the way that charities describe themselves. Each charity could have one or more of these tags applied to it.

To achieve this, a sample of registered charities was created and manually classified by the project team. This sample was then used as the base for both machine-learning models and rules-based classification to assign ICNP/TSO categories and UK-CAT tags to each charity. In some cases, particularly for larger organisations, manual categories are applied to ensure the categories are correct.

**[Read more about the method used...](method/introduction.md)**

## Results and outputs

- [Project report](data/charity-classification-report.pdf), from September 2021
- [Presentation given at 2021 Voluntary Sector and Volunteering Research Conference](data/charity-classification-presentation.pdf), Aston University, September 2021
- [Classification schema used in the project](data/outputs.md#classification-schema)
- [Charities that were manually classified](data/outputs.md#manually-classified-charities)
- [Tags automatically applied to all categories](data/outputs.md#categories-for-all-charities)

You can also view [code and data](https://github.com/drkane/ukcat/) from the project on its Github repository. 

**[More outputs from the project are available to download](data/outputs.md)**

## Feedback and next steps

Given the nature of this work we do not consider the project complete. Our aim is for a system that is used and owned by the voluntary sector as a whole, which requires input from a wide range of people.

We are particularly conscious that the classification scheme we have created, and the method of applying it, reflect the backgrounds and biases of the project team.

We welcome feedback and corrections to our work, including in the following areas:

 - Suggesting changes or additions to UK-CAT itself
 - Improvements to the method of applying the rules, including the machine learning models
 - Changes to the tags & ICNP/TSO categories applied to individual charities

### Feedback form

Use this form to provide any feedback on the classification, or you can email [feedback@charityclassification.org.uk](mailto:feedback@charityclassification.org.uk).

<iframe class="airtable-embed" src="https://airtable.com/embed/shrrnNAznHlGeySmR?backgroundColor=cyan" frameborder="0" onmousewheel="" width="100%" height="1533" style="background: transparent; border: 0px solid #ccc;"></iframe>