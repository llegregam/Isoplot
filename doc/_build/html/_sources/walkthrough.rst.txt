Walkthrough
-------------------------------------

This part will walk the user through the usage of Isoplot. There are 2 ways to use the tool: through a GUI hosted on a **Jupyter Notebook**
or through a **Command Line Interface (CLI)**.

Jupyter Notebook GUI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once Isoplot is installed and the interactive notebook file **isoplot.ipynb** is downloaded and placed in the desired directory, launch 
Jupyter Notebook through the **Anaconda Launcher** or through the command line.
 
.. note:: The Isoplot Notebook interface outputs the created directories and files in the directory where the notebook is contained
 
Once in the Notebook, navigate to the appropriate folder and open isoplot.ipynb
 
.. image:: _static/walkthrough/Image1.png
   :width: 100%
   :align: left


Next, select the first cell and execute it. 

.. image:: _static/walkthrough/Image2.png
   :width: 100%
   :align: left
   
Once the buttons have appeared, use the first one to select the **datafile** and then the second one to submit it.

.. image:: _static/walkthrough/Image3.png
   :width: 100%
   :align: left

In the file explorer, navigate to the generated **ModifyThis.xlsx** template file and open it.

.. image:: _static/walkthrough/Image4.png
   :width: 100%
   :align: left

Fill the file with your conditions, times, replicate numbers, etc… then save it.

.. warning:: What you input here will be used by Isoplot to generate the groups for plotting (ex: condition AB at T0 replicate 1). **If you have multiple replicates for one same time and condition, number them starting from 1**.

.. image:: _static/walkthrough/Image5.png
   :width: 100%
   :align: left
   
The ModifyThis.xlsx file contains a table with 5 columns. They are detailed in :ref:`Tutorial - Template file<Template File>`. Once 
you have finished modifying the template, save it.

.. note:: It is good practice to change the name of the template file because if you press the "create template" button once more Isoplot will overwrite the old ModifyThis.xlsx file.

Example of finished template file:

.. image:: _static/walkthrough/Image6.png
   :width: 100%
   :align: left
   
Next step is to launch the next cell to generate the buttons to upload and submit the template. Once this is done you can start plotting your figures!
 
.. image:: _static/walkthrough/Image7.png
   :width: 100%
   :align: left
   

   