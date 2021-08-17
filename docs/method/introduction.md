# Method

The project aims to apply two sets of classification schemes to every registered charity in the UK. The two schemes are:

 - The **International Classification of Non-profit and Third Sector Organizations** (ICNP/TSO), which is part of the UN Satellite Accounts for Non-profits. Each charity was assigned one of these categories.
 - A new classification system - **UK Charity Activity Tags (UK-CAT)**, created as part of the project. These are a collection of general tags describing the activities of charities, based on an examination of the way that charities describe themselves. Each charity could have one or more of these tags applied to it.

To achieve this, a sample of registered charities was created and manually classified by the project team. This sample was then used as the base for both machine-learning models and rules-based classification to assign ICNP/TSO categories and UK-CAT tags to each charity. In some cases, particularly for larger organisations, manual categories are applied to ensure the categories are correct.

The process for producing the finished classification schemes involved five distinct steps.

1. The first step was to create a population of charities, using data from charity regulators, and then [**create a sample of charities**](sampling.md) from within the population. These sampled organisations could then be manually classified to create a base set of organisations to train and test different methods for automatic classification. Charities were selected using a stratified random sampling method.

2. We then [**designed the UK-CAT classification scheme**](designing-taxonomy.md). This was done in an iterative way, using the manually sampled charities from step 1. The researchers added tags as they went through each charity in turn, with frequent iterations to combine charities and refine the classification, as necessary.

3. Next, all charities in the sample were [**manually classified**](manual-classification.md) by a team of researchers, using the UK-CAT and ICNP/TSO classification schemes. There was some checking between different researchers to ensure inter-coder reliability.

4. A [**rules-based classification**](rules-based-classification.md) was developed that could apply the UK-CAT tags to every charity in the UK. The rules consist of regular expressions that can be checked against the names and activities of charities. The manually classified set of charities could be used to test the accuracy of these rules.

5. A [**machine learning**](machine-learning.md) model was developed to apply the ICNP/TSO classification to all charities. A variety of different models were trained and evaluated using the manually classified set of charities.
