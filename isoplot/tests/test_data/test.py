from isoplot.base.data_handler import DataHandler
from isoplot.base.plotter import StaticPlot

test = DataHandler(True)
test.import_isocor_data(r"C:\Users\legregam\Documents\Projets\Isoplot_v2\isoplot\tests\test_data\isocor_data.tsv")
test.import_template(r"C:\Users\legregam\Documents\Projets\Isoplot_v2\isoplot\tests\test_data\template.xlsx")
test.compute_data()
plot = StaticPlot(test.final_data, "2-OHGLu", ["A", "B"], [0, 24, 48], "isotopologue_fraction", "jpeg", True, True)

fig = plot.barplot()
fig.show()
