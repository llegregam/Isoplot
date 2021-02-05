FAQ
===

**1. Why are my replicates not being meaned properly?**

The most frequent reason for this comes from the numbering of the replicates. Indeed,
for each group of same condition+time (example: Wild Type T0) the replicates must
be numbered *starting from 1 untill the last* (example: Wild Type T0 1, Wild Type T0 2,
Wild Type T0 3, etc...)

**2. There was a problem during the experiment for one of my samples. How do I tell
Isoplot not to take it into account?**

The easiest way to remove any samples from the dataset is not to modify the dataset itself,
but rather to remove the corresponding line from the :ref:`template file<Template File>`.

**3. Sometimes the generated directory for my plots has multiple sub-directories with the
same name. Why is this?**

This happens when we generate multiple times the directory by using the same name twice in a row
(in the case of an error for example on the first try, or a mistake when selecting data to be
plotted). A quick fix is to restart the Kernel or change the name of the directory to be created
before generating the plots.

**4. I am trying to create barplots with meaned data (so with error bars) for isotopologue_fractions,
but some of my bars seem abherrent. They have error bars that go until under 0 and the total of the
fractions is not equal to 1. Why is this?

This happens when data is missing for only some replicates of a given sample condition & time. An ulterior
version of Isoplot will fix this, and not mean with replicates that are equal to 0.