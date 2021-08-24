Quickstart
-----------

Installation
^^^^^^^^^^^^

Isoplot requires Python 3.7 or higher. If you do not have a Python environment configured on your computer, 
we recommend that you follow the instructions from `Anaconda <https://www.anaconda.com/products/individual>`_.
Then, open a terminal (e.g. run Anaconda Prompt if you have Anaconda installed) and type :

.. code-block:: bash

	pip install isoplot

You are now ready to start Isoplot.

There are two ways to use isoplot : through the dedicated jupyter notebook (recommended) or through the command line.

Jupyter Notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First install jupyter notebook through the Anaconda Navigator or through `the dedicated website <https://jupyter.org/install>`_
and launch the notebook.

Navigate to the **Isoplot.ipynb** file that you can download from the `Github <https://github.com/llegregam/Isoplot>`_.

Launch the first cell to initiate the **« upload data »** and **« submit data »** 
buttons and use them to load in the tsv or csv IsoCor output file and generate the **template file** (ModifyThis.xlsx)

Modify the template as needed, save it and load it into the notebook after launching the second cell and initiating the 
**« Upload template »** and **« Submit template »** buttons.

Launch the next cells and generate plots !

.. note:: For more information on how to setup a python tool in a specific environment (recommended) using jupyter
          notebooks, check out `this documentation <https://nmrquant.readthedocs.io/en/latest/quickstart.html#environment-installation>`_.

Command-line interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To process your data, type in a terminal :

.. code-block:: bash

	isoplot [command line options] 

Here after the available options are enumerated and detailed.

.. argparse::
   :module: isoplot.ui.isoplotcli
   :func: parse_args
   :prog: isoplot
   :nodescription:


