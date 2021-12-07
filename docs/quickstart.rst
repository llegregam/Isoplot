Quickstart
-----------

Installation
^^^^^^^^^^^^

Isoplot requires Python 3.7 or higher. If you do not have a Python environment configured on your computer, 
we recommend that you follow the instructions from `Anaconda <https://www.anaconda.com/products/individual>`_.
Then, open a terminal (e.g. run Anaconda Prompt if you have Anaconda installed) and type :

.. code-block:: bash

	pip install isoplot

If you have an old version of the software installed, you can update to the latest using the following command:

.. code-block:: bash

    pip install -U isoplot

You are now ready to start Isoplot.

There are two ways to use isoplot : through the dedicated jupyter notebook (recommended) or through the command line.


Environment installation
------------------------

One of the advantages of the Anaconda Suite is that it gives access to a user-friendly GUI for the creation and
maintenance of python environments. Python environments give the user a way to separate different installations of
tools so that different package dependencies do not overlap  with each other. This is especially useful if packages
share the same dependencies but in different versions. The Anaconda Suite provides a quick and intuitive way of
separating these installations.

How to create an environment in Anaconda
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When the user opens up the Anaconda software, she/he ends up on the main menu:

.. image:: _static/Environment_installation/1.jpg
    :width: 100%
    :align: center

The main window shows all the tools available for installation in the Navigator. To get to the environments page, the
user must click on the "Environments" panel that is in the left-side menu.

.. image:: _static/Environment_installation/2.jpg
    :width: 100%
    :align: center

Once on the Environments page, the user can click on the "create" button that is present at the bottom left of the
screen. A pop up menu will then appear and allow the user to select a python version and a name for the environment.

.. image:: _static/Environment_installation/3.jpg
    :width: 100%
    :align: center

Once the user clicks on the "create" button the environment is created and ready for use!

Installing packages in the environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that the environment exists, it is time to populate it with the tools needed. The first thing to do is to open
up a command-line interface, preferably Anaconda Prompt (it is the one that will be used in this tutorial. Other
command-line interfaces might use different names for commands). Once the interface is open, the first thing to do
is to activate the desired environment. The command for this is as follows:

.. code-block:: bash

    conda activate <name-of-environment>

Once this is done the environment name should be seen on the left of the screen behind the name of the directory
the interface is open in.

.. image:: _static/Environment_installation/4.jpg
    :width: 100%
    :align: center

Once the environment is activated, the user can install using pip or conda any of the desired tools. The dependencies
and the tool itself will now be installed in a safe and separate set of folders which will ensure that other
installations are not affected by anything happening in the environment. Once the user is done, she/he can now
close the prompt.


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


