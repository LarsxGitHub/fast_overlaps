# Fast NxN comparisons

When comparing thousands of BGP feeds, each with potentially up to a million prefixes, Python's set comparisons are rather slow. This projects looks at whether it is possible to substitute Python's sets for BloomFilters. BloomFilters are space-efficient, probabilistic data structures for membership tests. Their structure allows them to trade-off accuracy for better performance. <br>

[GeeksForGeeks](https://www.geeksforgeeks.org/bloom-filters-introduction-and-python-implementation/) has a great high-level introduction to BloomFilters. For those that want to dig deeper, [Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter) is a great link tree.<br>

# Caveats & Sideeffects

The jaccard distance sometimes produces very weird/unexpected results when testing sets for which the cardinalities differ by more than an order of magnitude. Hence, we restrict out comparions only to sets that have the same order of magnitude, i.e., |a|/|b| < 10 and |b|/|a| < 10.

While each BloomFilter for a given alpha has a guaranteed membership accuracy of 1-alpha, I couldn't find a source that particularily looked at the difference of jaccard distances for pairs of BloomFilters. Assuming that the entries in both BloomFilters come from independent and identically distributed random variables, the accuracy should be no worse than (1-alpha)^2. Hence, I used the following trick: If we receive an alpha of X, we create BloomFilters with an alpha of 1-(1-X)^(1/2). While this seems to work rather well in practice (-> Results), I saw one run where the accuracy was 0.05001 (i.e., very slightly above the requested 0.05). 

The BloomFilter implementation that I rely on uses mmap'ed files under the hood. Hence, if you run the script but abort it, you will have files remaining in scripts/tmp/. All files within scripts/tmp/ are removed at the end of a run. Be careful: This really removes *all* files in scripts/tmp/, even those that you potentially added manually. 

In case this hasn't become clear yet: Picking tighter accuracy guarantees leads to larger BloomFilters and hence decreases performance. Similarly, looser guarantees lead to higher performance. Notably, this follows the "diminishing returns" pattern. Based on some playing around, 0.05 looks like a good tradeoff to me. 

# How to run

Running the code is simple, just enter scripts/ and then run

~~~
python3 tester.py 0.05 10
~~~

0.05 is a rough upper bound for the difference between real jaccard distance and approximated jaccard distance. 10 is the number of IPv4 feeds for which we load prefix lists during the test, i.e., it is the N in the NxN comparison. You can also do IPv6 runs, just adept the glob.glob(...) call in the tester code. 

If you want to adpet the method for your own needs and don't care about the performance tests, you find all required functions in scripts/utils.py

# Results

As running the code for large numbers of pairs takes a while, here is a sample results for 100:

~~~
############ Statistics for alpha = 0.05 ############

Ran 1513 comparisons in total.

0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99 percentile for jaccard inaccuracy [numerical difference]:
 0.0 0.0007201125175808443 0.025004926413256127 0.03732148884966108 0.04263526345176422 0.04426216558581122 0.044740332930573466

0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99 percentile for time taken in comparison to actual set comparison [fraction]
 0.1849769823646063 0.21796204727390758 0.23244590188671607 0.23573467930768277 0.23916606271395244 0.2404222840153796 0.24105610124893442
~~~

We observe that the difference between a BloomFilter's jaccard distance and the real jaccard distance with an alpha of 0.05 is around 0.037 and generally stays below 0.045. At the same time, we save more than 75% of execution time. 
