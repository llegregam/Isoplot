Tutorial
-------------------------------------

Input data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Isoplot takes as input **IsoCor corrected MS data** from **labelling experiments** in **tabular form**. 
The tabular data must contain a few key columns for each row :

* **« sample »** : Name of the sample containing the analyzed metabolite
* **« metabolite »** : name of the metabolite
* **« isotopologue »** : number of the metabolite’s :ref:`Isotopologue<Isotopologue>`
* **« corrected area »** : area of the analyzed metabolite’s isotopologue after correction by Isocor
* **« isotopologue fraction »**: see :ref:`Isotopologue fraction<Isotopologue fraction>`. 
* **« mean enrichment »** : see :ref:`Mean enrichment <Mean enrichment>`.

The input data file is used by Isoplot to generate a **template file** that the user must modify with the 
desired names for each sample’s parameters .

.. _Template File:

Template file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the data has been loaded into Isoplot through the notebook or the command-line, the template is generated 
by either clicking on the **« submit data »** button in the notebook or by not giving the command-line the template 
option. The template is a xlsx document that can be opened with excel, and contains a number of columns :

* **Sample** : this colummn corresponds to **the names given to the samples in the original dataset** and **must not be modified**,
or else Isoplot will not be able to pair the template’s information with the data.

* **Condition** : The different conditions for each sample

* **Condition order** : Order in the plots of each condition+time. When different replicates are present, **they must be given the same condition order if meaned plots are to be created**. For default order leave 1 on all rows.

* **Time** : The different time points for each sample.

* **Replicate number** : Different replicate numbers for each sample. **They must be numbered starting from 1 to n (n being number of replicates)** for each condition+time.

.. note:: If for any reason one of the samples must not be plotted or taken into account by Isoplot, remove the associated line from the template file

.. warning:: It is important to properly fill the template table as it is what Isoplot will use to define which data to group together for the plots.

Output files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the template is loaded and submited to Isoplot, a Data Export.xlsx file is created with the merged data that is used 
for the generation of the plots.

If static plots are created, the plots are outputed in the format given by the user (jpeg, png, svg or pdf).

If interactive plots are created, plots are outputed in html format. 
