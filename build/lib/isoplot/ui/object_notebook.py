"""Module for controlling the Isoplot notebook"""

import io
import os
import logging
from pathlib import Path

import ipywidgets as widgets

mod_logger = logging.getLogger(f"isoplot.isoplot_notebook")

class IsoplotNb:

    def __init__(self, verbose=False):
        """ Initialize the widgets used in the dashboard and initial parameters """

        # Get home directory
        self.home = Path(os.getcwd())

        # Initiate child logger for class instances
        self.logger = logging.getLogger("isoplot.isoplot_notebook.IsoplotNb")
        handler = logging.StreamHandler()

        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        # Initiate all the widgets
        self.upload_data = widgets.FileUpload(
        accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
        multiple=False,  # True to accept multiple files upload else False
        description="Upload Datafile"
        )



        self.upload_template = widgets.FileUpload(accept="",
                                             multiple=False,
                                             description="Upload Template")

        self.generate_template_btn = widgets.Button(description='Create Template')

        self.submit_template_btn = widgets.Button(description='Submit Template')

        self.metabolite_selector = widgets.SelectMultiple(options=self.metabolite_list,
                                                          value=self.metabolite_list[0],
                                                          description="Metabolites",
                                                          disabled=False)

        self.condition_selector = widgets.SelectMultiple(options=self.condition_list,
                                                          value=self.condition_list[0],
                                                          description="Conditions",
                                                          disabled=False)

        self.time_selector = widgets.SelectMultiple(options=self.time_list,
                                                          value=self.time_list[0],
                                                          description="Times",
                                                          disabled=False)

        self.mode_selector = widgets.Dropdown(options=["Static", "Interactive"],
                                              value="Static",
                                              description="Mode",
                                              disabled=False)

        self.plot_selector = widgets.Dropdown(options=self.plot_list,
                                              value=self.plot_list[0],
                                              description="Plot Type",
                                              disabled=False)

        self.run_name = widgets.Text(value="",
                                     placeholder="Input run name",
                                     description="Run Name",
                                     disabled=False)

        self.log_console = widgets.Output()

        self.preview_window = widgets.Output()


    def make_gui(self):

        display(self.preview)

