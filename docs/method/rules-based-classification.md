# Rules based classification

The manually classified entries provided a pool of baseline data from which to start developing the automated keyword searching. 

To assist with the creation of these keywords, we took all of the charities from the manual sample linked to each tag and ran frequencies on the most common words and pairs of words (bigrams). This provided an initial indication of the most common associated terms and allowed us to create a ‘regular expression’ of search terms. 

Secondly, using an online tool created for this purpose, we worked through each tag examining the ‘false negatives’. These were charities we had linked manually to a tag, but which were not yet being caught by our search terms. Examining the activities of these charities often revealed modifications or additions that needed to be made to the search terms. 

At the same time, we kept a close eye on those charities that were being included by the search terms, particularly those from the sample which we hadn’t manually linked. In many cases, these were entirely reasonable and had either been missed during the manual classification, or were just slightly wider in scope than the manual coders had operated. 

Unsurprisingly, the eventual search terms included for each tag was a balance between whether to prioritise avoiding false positives or false negatives, which had to be struck fairly intuitively by the research team.

The method for refining the tags allowed us to produce two measures of success: precision and recall, as well as the f1 score, which combines the two. Each measure was scored between 0 and 1. In our case, these measures are defined as follows:

- **Precision** shows how many of the charities selected by the tag keyword were correct. This is equivalent to true positives as a proportion of all selected elements. A high precision score shows that the keyword was good at minimising false positives - a high proportion of those selected were correct. A low precision score meant that the keyword selected lots of charities that shouldn’t have been (false positives).
- **Recall** shows how many of the charities that should be selected for this tag were. This is equivalent to true positives as a proportion of all relevant elements. A high recall score means that the keyword did well at finding a large proportion of the relevant charities. A low recall score means that the keyword found a small proportion of the relevant charities - lots of false negatives.
- The **F1 Score** combines these, using the harmonic mean. It generally reflects the lower of the two figures.

Figure X shows the distribution of tag results in bands using these three measures. It demonstrates that the current tags are better at maximising recall, and less so with precision. These means we would expect to see more false positives in the result, but fewer false negatives. This is reflected in the results when the tags are applied more widely, with a larger number of tags per charity than in the sample data.

Figure X: Distribution of tags across different measures of quality of the results

<div class="flourish-embed flourish-chart" data-src="visualisation/6706687"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

To complicate matters further, we continued to refine the UK-CAT throughout this process. Although it would have been a neater, more linear method to finish it first, we found that often the process of coming up with the key words made it logical to tweak the tags themselves. Sometimes this was to avoid duplication, clarify the difference between two tags, or in one or two cases because creating suitable search terms was simply not possible due to the inherent ambiguity that sometimes occurs in the English language. 

