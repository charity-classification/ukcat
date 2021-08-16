# Machine Learning

To classify charities into ICNPTSO categories, the keyword/regular expression process used for UK-CAT would not work. This is because the keywords could indicate multiple ICNPTSO categories for a given charity, and we need to choose just one for each charity.

Instead, a machine learning approach was preferred. In this approach a set of training data (the names and activities description for our sample set of charities) is fed into a machine learning model along with the assigned ICNPTSO categories. You can then provide the model with a name and activities description for an unknown charity and it will predict the category that best applies (we can hold back part of the training dataset in order to test the accuracy of the model). This problem is generally known as text classification.

The approach to this task involved using various models provided by the [scikit-learn python package](https://scikit-learn.org/stable/). We selected eight different models that were suggested as potentially appropriate for performing text classification through machine learning. The nature of scikit-learn means it is possible to easily produce a set of pipelines that put the same data through each of the models and compare the results.

The pipeline for training the models consists of the following:

- Combine the name and activities description fields for each organisation into a single field
- Normalise the text in these fields. This includes removing special characters and putting the text into all lowercase.
- Remove "stopwords" from the text. Stopwords are common words used in English like "and", "a", "for", etc that are very common. A number of charity-specific stopwords were also removed, eg "trust", "fund", "charitable", "charity".
- Lemmatise all the words in the text. Lemmatisation converts words to a common root - so for example "better" and "good" are treated as the same.

For best results, this pipeline needs to also be applied to any text before the model can offer a prediction.

The sample data was split into "training" and "test" datasets. The sample dataset consisted of charities from both the manually classified random sample and the top 2000 charities that were manually classified. In total there were 6,203 charities, of which 4,962 (80%) were in the training set and 1,241 (20%) were in the test set.

## Model training results

Each model was then trained on the training data and used to predict categories for the test data. The accuracy of the model can then be computed. The accuracy of the model is the proportion of categories in the predicted values for the test data that were the same as the actual result from manual classification. The results across the eight models were as follows:


Model | Accuracy
----|----:
Linear Support Vector Classification | 56.7%
Logistic Regression | 55.8%
Linear model - Stochastic gradient descent | 54.6%
Support Vector Classification | 51.7%
Naive Bayesian | 37.1%
Decision Tree | 22.3%
Ada Boost | 14.2%
Random Forest | 9.7%


The results was a near tie between Linear Support Vector Classification, Logistic Regression and Linear model - Stochastic gradient descent, with accuracy of 57%, 56% and 55% respectively. Although it came a close second, Logistic Regression was chosen as the most appropriate model to take forward, primarily because it is possible to extract the probability assigned by the model to the results, which allows for further investigation of them.

Accuracy of 56% does mean that the model gets an incorrect result 11 times out of 20. However, this result is more impressive when compared to the fact that there are over 76 different categories for the model to choose from. A model that simply randomly assigned a category to each charity would have an accuracy of around 1%.

And while the final model had an accuracy of 56% for the lowest-level of ICNPTSO classification, it was correct for the "group" of the ICNPTSO category 70% of the time. This means that, for example, a charity may have been correctly identified as in the "Education" group (group B) but the exact sub-category may not have been right.

The probability scores given for the best match found by the model do give some insight into its confidence, although they are not especially helpful. 60% of the test results were given a confidence of 0.99 or higher. Out of those 72% were correct and 28% were incorrect - a higher accuracy than the model overall. The accuracy for matches with scores between 0.75-0.99 was around 35%, and for lower than 0.75 was around 25%. This does show that the confidence scores do reflect the accuracy of the results, but even for low confidence scores they are correct around one third of the time.

## Manual check

To further check the results of the machine learning model, a random sample of 300 charities was taken from the full results. This consisted of a weighted sample, based on taking 20 charities across 5 income bands, in each of the 3 regulatory jurisdictions. The sample included some manually classified results - these were ignored in the results shown below, with 236 of the results from the machine learning model. Each result was then checked and put into one of three categories:

- "Correct" - the ICNPTSO category assigned by the model was correct
- "Plausible" - the ICNPTSO category assigned was plausible, but a human looking at the charity might have chosen a different one
- "Incorrect" - the ICNPTSO category assigned did not look correct

The exercise produced a better result than found in the formal machine learning test - 85% of the matches overall were "correct", with a further 5% "plausible", leaving 11% that could be considered "incorrect". The results varied by regulator and by income band. CCEW had the lowest "correct" score, with 79%, followed by oscr (82% correct) and CCNI (91%). 

The score did not appear to very across income band for OSCR and CCNI, but for the CCEW results there was a pattern of smaller organisations being more likely to be incorrect - with 65% correct for the smallest band (under £10k, for CCEW) compared to 89% for £1m-£10m.

These results are encouraging, and suggest that the results are better than the formal machine learning test would suggest. If the "plausible" results are also accepted, the overall success rate from this exercise would be nearly 90%. 

## Refinements to models

There are ways that could improve the performance of the models for producing the correct ICNPTSO results. Two of these methods have been tried (and offer no significant improvement over the base model), while the others could be tried in future research.

### Refinement 1: combine with tag classification

This refinement involves using the keywords developed for the UK-CAT classification. As each UK-CAT tag has one or more "related" ICNPTSO categories, the method for this refinement was to first run the UK-CAT keywords against the charity text data (the name and activities). The unique set of related ICNPTSO categories found through these keywords could then be used to narrow down the set of allowed ICNPTSO categories from the machine learning model. The best result from the related ICNPTSO categories would be selected, using the probability from the machine learning model.

This method produced an accuracy of 52%, slightly less than the base model. In around 14% of cases only one related ICNPTSO category was found which was chosen by default. And in a small number of cases (<5%) no related categories were found. There was no difference in the accuracy of this technique across the number of different tags found - it performed worse than the base model no matter how many related tags were found.

The results of this refinement can be found in the `icnptso-ml-tag-test.ipynb` notebook.

### Refinement 2: classify by group first

A second potential refinement was to split the classification problem into two stages. The first stage would classify charities into ICNPTSO groups (e.g. Education), with the second stage then deciding on the subcategory within the group. This would involve one model to predict the group classification, then a series of models for the subcategories, one for each group. 

Applying this refinement did not produce any improvement in the accuracy generated. The accuracy of the group classification model was 69%, around the same as the accuracy at a group level for the classification as a whole. And once the individual models were run the overall accuracy of the process was 53%, slightly less than the base model.

### Potential further refinements

The two refinements tested did not produce any improvement in the accuracy of the result. There are other areas that could be tried though.

The first is parameter optimization. Currently the logistic regression model uses some default parameters chosen from the documentation. It is possible to tweak the parameters that the model uses to improve performance. This tweaking can be done manually, or by exploring a parameter space and optimising automatically based on results.

The second potential improvement would be to use another machine learning technique to get better results. An inspiration in this area might be Ma (2021), in which the author uses a number of advanced machine learning techniques in a similar space and produces improved results. In particular, the use of the BERT set of pre-trained word embeddings could help bring different words with similar meanings closer together within the model.

Finally, a larger sample dataset should result in increased accuracy, even for the existing model. There may be innovative ways of producing this increased sample - for example by "gamifying" the process of confirming potential tags for a charity using an interactive online tool. 
