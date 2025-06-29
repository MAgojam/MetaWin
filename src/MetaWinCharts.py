"""
Module for creating figures using the matplotlib backend for Qt
"""

import math
from numbers import Number
from typing import Optional, Union

import matplotlib.patches
from matplotlib import patches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.collections import QuadMesh
from matplotlib.lines import Line2D
# the following import is necessary to force pyinstaller to include these backends for vector output when packaging
from matplotlib.backends import backend_svg, backend_ps, backend_pgf, backend_pdf
from matplotlib.colors import XKCD_COLORS, hex2color, CSS4_COLORS
import numpy
import scipy.stats

from MetaWinUtils import exponential_label, get_citation, create_reference_list
from MetaWinLanguage import get_text
import MetaWinWidgets

color_name_space = "xkcd"


# weighting options for the histograms
WEIGHT_NONE = 0
WEIGHT_INVVAR = 1
WEIGHT_N = 2

# style options for forest plots
FP_STYLE_PLAIN = 0
FP_STYLE_SCALED = 1
FP_STYLE_THICK = 2
FP_STYLE_RAINFOREST = 3
FOREST_STEP = 10
MARC_STYLE_0 = 10  # this is for plotting studies only, without the mean
MARC_STYLE_1 = 11  # version 1, when the mean is included in y-axis scaling (i.e., y-axis ranges from 0 to 1)
MARC_STYLE_2 = 12  # version 2, when the mean is excluded from y-axis scaling

LINE_STYLES = ("solid", "dashed", "dotted", "dashdot")
# MARKER_STYLES = {"point": ".", "circle": "o", "downward triangle": "v", "upward triangle": "^",
#                  "left triangle": "<", "right triangle": ">", "downard tri": "1", "upward tri": "2", "left tri": "3",
#                  "right tri": "4", "octagon": "8", "square": "s", "pentagon": "p", "filled plus": "P",
#                  "star": "*", "upward hexagon": "h", "sideways hexagon": "H", "plus": "+", "X": "x", "filled X": "X",
#                  "diamond": "D", "thin diamond": "d", "vertical line": "|", "horizontal line": "_", "tick left": 0,
#                  "tick right": 1, "tick up": 2, "tick down": 3, "upward caret": 6, "downward caret": 7,
#                  "left caret": 4, "right caret": 5, "centered upward caret": 10, "centered downward caret": 11,
#                  "centered left caret": 8, "centered right caret": 9}
MARKER_STYLES = {"point": ".", "circle": "o", "downward triangle": "v", "upward triangle": "^",
                 "left triangle": "<", "right triangle": ">", "octagon": "8", "square": "s", "pentagon": "p",
                 "filled plus": "P", "star": "*", "upward hexagon": "h", "sideways hexagon": "H", "plus": "+",
                 "X": "x", "filled X": "X", "diamond": "D", "thin diamond": "d", "vertical line": "|",
                 "horizontal line": "_", "tick left": 0, "tick right": 1, "tick up": 2, "tick down": 3,
                 "upward caret": 6, "downward caret": 7, "left caret": 4, "right caret": 5,
                 "centered upward caret": 10, "centered downward caret": 11, "centered left caret": 8,
                 "centered right caret": 9}

UNFILLED_MARKERS = {"point", "plus", "X", "vertical line", "horizontal line", "tick left", "tick right", "tick up",
                    "tick down", "upward caret", "downward caret", "left caret", "right caret",
                    "centered upward caret", "centered downward caret", "centered left caret", "centered right caret"}

COLORMAPS = {  # perceptually uniform
             "viridis (uniform)": "viridis",
             "plasma (uniform)": "plasma",
             "inferno (uniform)": "inferno",
             "magma (uniform)": "magma",
             "cividis (uniform)": "cividis",
             # sequential
             "greys (sequential light-to-dark)": "Greys",
             "purples (sequential light-to-dark)": "Purples",
             "blues (sequential light-to-dark)": "Blues",
             "greens (sequential light-to-dark)": "Greens",
             "oranges (sequential light-to-dark)": "Oranges",
             "reds (sequential light-to-dark)": "Reds",
             "yellow-orange-brown (sequentia light-to-dark)": "YlOrBr",
             "yellow-orange-red (sequential light-to-dark)": "YlOrRd",
             "orange-red (sequential light-to-dark)": "OrRd",
             "purple-red (sequential light-to-dark)": "PuRd",
             "red-purple (sequential light-to-dark)": "RdPu",
             "blue-purple (sequential light-to-dark)": "BuPu",
             "green-blue (sequential light-to-dark)": "GnBu",
             "purple-blue (sequential light-to-dark)": "PuBu",
             "yellow-green-blue (sequential light-to-dark)": "YlGnBu",
             "purple-blue-green (sequential light-to-dark)": "PuBuGn",
             "blue-green (sequential light-to-dark)": "BuGn",
             "yellow-green (sequential light-to-dark)": "YlGn",
             # sequential 2
             # # "binary": "binary",  # identical to gray_r
             # # "gist_yarg": "gist_yarg",  # identical to gray_r
             # # "gist_gray": "gist_gray",  # identical to gray
             "gray (sequential)": "gray",
             "bone (sequential)": "bone",
             "pink (sequential)": "pink",
             "spring (sequential)": "spring",
             "summer (sequential)": "summer",
             "autumn (sequential)": "autumn",
             "winter (sequential)": "winter",
             "cool (sequential)": "cool",
             "wistia (sequential)": "Wistia",
             "hot (black-red-yellow-white) (sequential)": "hot",
             "hot (black-orange-white) (sequential)": "afmhot",
             "GIST/Yorick heat (sequential)": "gist_heat",
             "copper (sequential)": "copper",
             # diverging
             "pink-white-green (diverging)": "PiYG",
             "purple-white-green (diverging)": "PRGn",
             "brown-white-green (diverging)": "BrBG",
             "orange-white-purple (diverging)": "PuOr",
             "red-white-gray (diverging)": "RdGy",
             "red-white-blue (diverging)": "RdBu",
             "red-yellow-blue (diverging)": "RdYlBu",
             "red-yellow-green (diverging)": "RdYlGn",
             "spectral (diverging)": "Spectral",
             "cool-warm (diverging)": "coolwarm",
             "blue-white-red (diverging)": "bwr",
             "seismic (diverging)": "seismic",
             # cyclic
             "twilight (cyclic)": "twilight",
             "twilight (shifted) (cyclic)": "twilight_shifted",
             "HSV wheel (cyclic)": "hsv",
             # qualitative
             "ColorBrewer pastel 1 (qualitative)": "Pastel1",
             "ColorBrewer pastel 2 (qualitative)": "Pastel2",
             "ColorBrewer paired (qualitative)": "Paired",
             "ColorBrewer accent (qualitative)": "Accent",
             "ColorBrewer dark 2 (qualitative)": "Dark2",
             "ColorBrewer set 1 (qualitative)": "Set1",
             "ColorBrewer set 2 (qualitative)": "Set2",
             "ColorBrewer set 3 (qualitative)": "Set3",
             "Vega 10 color (qualitative)": "tab10",
             "Vega 20 color, v1 (qualitative)": "tab20",
             "Vega 20 color, v2 (qualitative)": "tab20b",
             "Vega 20 color, v3 (qualitative)": "tab20c",
             # miscellaneous
             # # "flag": "flag",  # repeating pattern
             # # "prism": "prism",  # repeating pattern
             "ocean": "ocean",
             "GIST/Yorick earth": "gist_earth",
             "terrain": "terrain",
             "GIST/Yorick stern": "gist_stern",
             "gnuplot": "gnuplot",
             "gnuplot2": "gnuplot2",
             "CMR map": "CMRmap",
             "cubehelix": "cubehelix",
             "blue-red-green": "brg",
             "GIST/Yorick rainbow": "gist_rainbow",
             "rainbow": "rainbow",
             "jet": "jet",
             "turbo": "turbo",
             "NiPy spectral": "nipy_spectral",
             # # "gist_ncar": "gist_ncar"
            }


# ---------- Chart Data Classes ---------- #
class BaseChartData:
    def __init__(self):
        self.name = ""
        self.visible = True
        self.alt_axes = None
        self.edit_panel = None


    @staticmethod
    def export_to_list(self) -> list:
        # default - overload when necessary
        return []

    @staticmethod
    def style_text() -> str:
        # default - overload when necessary
        return ""

    def create_edit_panel(self):
        # default - overload when necessary
        return self.edit_panel


class ScatterData(BaseChartData):
    """
    an object to contain scatter plot data
    """
    def __init__(self):
        super().__init__()
        self.x = []
        self.y = []
        # scatter point style
        self.marker = "o"
        self.color = "#1f77b4"
        self.alpha = 1
        self.edgecolors = "#1f77b4"
        self.size = 36
        self.single_size = True
        self.min_size = 1
        self.max_size = 100
        self.linewidths = 1.5
        self.linestyle = "dotted"
        self.label = ""
        self.alpha = 1
        self.zorder = 0
        self.edgecolor_button = None
        self.linewidth_box = None
        self.linestyle_box = None
        self.color_button = None
        self.size_box = None
        self.marker_box = None
        self.no_fill_box = None
        self.min_size_box = None
        self.max_size_box = None
        self.opacity_box = None
        self.weights = None
        self.max_weight, self.min_weight = 0, 0

    def export_to_list(self) -> list:
        outlist = ["Scatter Plot Data\n",
                   f"Name\t{self.name}\n",
                   "x\ty\n"]
        for i in range(len(self.x)):
            outlist.append(f"{self.x[i]}\t{self.y[i]}\n")
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)

        (self.color_button, color_label, self.no_fill_box, self.opacity_box,
         opacity_label) = MetaWinWidgets.add_chart_color_button(get_text("Color"), self.color, self.edgecolors,
                                                                self.alpha)
        self.no_fill_box.clicked.connect(self.no_fill_clicked)
        self.no_fill_clicked()
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(self.no_fill_box, 2, 0)
        self.marker_box, marker_label = MetaWinWidgets.add_chart_marker_style(get_text("Shape"), self.marker,
                                                                              MARKER_STYLES)
        edit_layout.addWidget(marker_label, 0, 1)
        edit_layout.addWidget(self.marker_box, 1, 1)

        if self.single_size:
            self.size_box, size_label = MetaWinWidgets.add_chart_marker_size(get_text("Size"), self.size)
            edit_layout.addWidget(size_label, 0, 2)
            edit_layout.addWidget(self.size_box, 1, 2)
            col_adj = 0
        else:
            self.min_size_box, min_size_label = MetaWinWidgets.add_chart_marker_size(get_text("Min Size"),
                                                                                     self.min_size)
            edit_layout.addWidget(min_size_label, 0, 2)
            edit_layout.addWidget(self.min_size_box, 1, 2)
            self.max_size_box, max_size_label = MetaWinWidgets.add_chart_marker_size(get_text("Max Size"),
                                                                                     self.max_size)
            edit_layout.addWidget(max_size_label, 0, 3)
            edit_layout.addWidget(self.max_size_box, 1, 3)
            col_adj = 1

        edit_layout.addWidget(opacity_label, 0, 3+col_adj)
        edit_layout.addWidget(self.opacity_box, 1, 3+col_adj)
        (self.edgecolor_button, edgecolor_label, self.linewidth_box, width_label, self.linestyle_box, style_label,
         _, _, _, _) = MetaWinWidgets.add_chart_line_edits(get_text("Edge Color"), self.edgecolors,
                                                           get_text("Edge Width"), self.linewidths,
                                                           get_text("Edge Style"), self.linestyle, LINE_STYLES)
        edit_layout.addWidget(edgecolor_label, 0, 4+col_adj)
        edit_layout.addWidget(self.edgecolor_button, 1, 4+col_adj)
        edit_layout.addWidget(width_label, 0, 5+col_adj)
        edit_layout.addWidget(self.linewidth_box, 1, 5+col_adj)
        edit_layout.addWidget(style_label, 0, 6+col_adj)
        edit_layout.addWidget(self.linestyle_box, 1, 6+col_adj)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def no_fill_clicked(self):
        if self.no_fill_box.isChecked():
            self.color_button.setEnabled(False)
        else:
            self.color_button.setEnabled(True)

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidths = float(self.linewidth_box.text())
        self.edgecolors = self.edgecolor_button.color
        if self.no_fill_box.isChecked():
            self.color = "none"
        else:
            self.color = self.color_button.color
        if self.single_size:
            self.size = float(self.size_box.text())
        else:
            self.min_size = float(self.min_size_box.text())
            self.max_size = float(self.max_size_box.text())
        self.alpha = float(self.opacity_box.text())
        self.marker = MARKER_STYLES[self.marker_box.currentText()]

    def style_text(self) -> str:
        marker_name = list(MARKER_STYLES.keys())[list(MARKER_STYLES.values()).index(self.marker)]
        if marker_name.endswith("s"):
            s = "ses"
        else:
            s = "s"
        if marker_name in UNFILLED_MARKERS:
            if self.color == "none":
                return get_text("nothing (marker is invisible)")
            else:
                return find_color_name(self.color) + " " + marker_name + s
        else:
            if self.color == self.edgecolors:
                return find_color_name(self.color) + " " + marker_name + s
            else:
                if self.color == "none":
                    return get_text("marker_style_open_text").format(marker_name, s, find_color_name(self.edgecolors))
                else:
                    return get_text("marker_style_text").format(find_color_name(self.color), marker_name, s,
                                                                find_color_name(self.edgecolors))


class HistogramData(BaseChartData):
    """
    an object to contain histogram bins
    """
    def __init__(self):
        super().__init__()
        self.counts = None
        self.bins = None
        # style
        self.color = "#1f77b4"
        self.linewidth = 1
        self.linestyle = "solid"
        self.edgecolor = "black"
        self.alpha = 1
        # style editing
        self.edgewidth_box = None
        self.edgestyle_box = None
        self.bar_color_button = None
        self.edge_color_button = None
        self.opacity_box = None

    def export_to_list(self) -> list:
        outlist = ["Histogram Data\n",
                   f"Name\t{self.name}\n",
                   "count\tlower\tupper\n"]
        for i in range(len(self.counts)):
            outlist.append(f"{self.counts[i]}\t{self.bins[i]}\t{self.bins[i+1]}\n")
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.bar_color_button, label, _, self.opacity_box,
         opacity_label) = MetaWinWidgets.add_chart_color_button(get_text("Bar Color"), self.color, alpha=self.alpha)
        edit_layout.addWidget(label, 0, 0)
        edit_layout.addWidget(self.bar_color_button, 1, 0)
        (self.edge_color_button, color_label, self.edgewidth_box, width_label, self.edgestyle_box, style_label,
         _, _, _, _) = MetaWinWidgets.add_chart_line_edits(get_text("Edge Color"), self.edgecolor,
                                                           get_text("Edge Width"), self.linewidth,
                                                           get_text("Edge Style"), self.linestyle, LINE_STYLES)
        edit_layout.addWidget(color_label, 0, 1)
        edit_layout.addWidget(self.edge_color_button, 1, 1)
        edit_layout.addWidget(width_label, 0, 2)
        edit_layout.addWidget(self.edgewidth_box, 1, 2)
        edit_layout.addWidget(style_label, 0, 3)
        edit_layout.addWidget(self.edgestyle_box, 1, 3)
        edit_layout.addWidget(opacity_label, 0, 4)
        edit_layout.addWidget(self.opacity_box, 1, 4)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.edgestyle_box.currentText()
        self.linewidth = float(self.edgewidth_box.text())
        self.color = self.bar_color_button.color
        self.edgecolor = self.edge_color_button.color
        self.alpha = float(self.opacity_box.text())


class LabelData(BaseChartData):
    """
    an object to contain a list of labels
    """
    def __init__(self):
        super().__init__()
        self.labels = None
        self.y_pos = None

    def export_to_list(self) -> list:
        outlist = ["Data Labels\n",
                   f"Name\t{self.name}\n",
                   "Y-position\tLabel\n"]
        for i in range(len(self.labels)):
            outlist.append(f"{self.y_pos[i]}\t{self.labels[i]}\n")
        return outlist


class ForestCIData(BaseChartData):
    """
    an object to contain confidence intervals for a forest plot
    """
    def __init__(self):
        super().__init__()
        self.min_x = None
        self.max_x = None
        self.y = None
        # style
        self.linestyle = "solid"
        self.color = "#1f77b4"
        self.linewidth = 1.5
        self.single_width = True
        self.min_width = 1
        self.max_width = 10
        self.weights = None
        self.zorder = 0
        self.color_button = None
        self.linestyle_box = None
        self.linewidth_box = None
        self.min_linewidth_box = None
        self.max_linewidth_box = None

    def export_to_list(self) -> list:
        outlist = ["Forest Plot CI Data\n",
                   f"Name\t{self.name}\n",
                   "lower\tupper\ty\n"]
        for i in range(len(self.y)):
            outlist.append(f"{self.min_x[i]}\t{self.max_x[i]}\t{self.y[i]}\n")
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.color_button, color_label, self.linewidth_box, width_label,
         self.linestyle_box, style_label, self.min_linewidth_box, min_width_label, self.max_linewidth_box,
         max_width_label) = MetaWinWidgets.add_chart_line_edits(get_text("Color"), self.color,
                                                                get_text("Width"), self.linewidth,
                                                                get_text("Style"), self.linestyle,
                                                                LINE_STYLES,
                                                                single_width=self.single_width,
                                                                min_text=get_text("Min Width"),
                                                                min_width=self.min_width,
                                                                max_text=get_text("Max Width"),
                                                                max_width=self.max_width)
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        if self.single_width:
            edit_layout.addWidget(width_label, 0, 1)
            edit_layout.addWidget(self.linewidth_box, 1, 1)
            adj = 0
        else:
            edit_layout.addWidget(min_width_label, 0, 1)
            edit_layout.addWidget(self.min_linewidth_box, 1, 1)
            edit_layout.addWidget(max_width_label, 0, 2)
            edit_layout.addWidget(self.max_linewidth_box, 1, 2)
            adj = 1
        edit_layout.addWidget(style_label, 0, 2+adj)
        edit_layout.addWidget(self.linestyle_box, 1, 2+adj)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        if self.single_width:
            self.linewidth = float(self.linewidth_box.text())
        else:
            self.min_width = float(self.min_linewidth_box.text())
            self.max_width = float(self.max_linewidth_box.text())
        self.color = self.color_button.color


class RainforestData(BaseChartData):
    """
    an object to contain data for drawing the density diagrams of Rainforest plots
    """
    def __init__(self):
        super().__init__()
        self.lower_cis = None
        self.upper_cis = None
        self.ys = None
        self.means = None
        self.vars = None
        self.weights = None

        # style
        self.zorder = 0
        self.colormap = "Blues"

        self.map_box = None
        self.rev_map_box = None

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        self.map_box, self.rev_map_box, _, _ = MetaWinWidgets.add_chart_colormap_edits(self.colormap, COLORMAPS)
        edit_layout.addWidget(self.rev_map_box, 0, 0)
        edit_layout.addWidget(self.map_box, 1, 0)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.colormap = COLORMAPS[self.map_box.currentText()]
        if self.rev_map_box.isChecked():
            self.colormap += "_r"


class ViolinData(BaseChartData):
    """
    an object to contain data for drawing bootstrap distributions
    """
    def __init__(self):
        super().__init__()
        self.bootstrap_data = None
        self.ys = None

        # style
        self.color = "#FFDF00"
        self.alpha = 1
        self.color_button = None
        self.opacity_box = None

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.color_button, color_label, _, self.opacity_box,
         opacity_label) = MetaWinWidgets.add_chart_color_button(get_text("Color"), self.color, alpha=self.alpha)

        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(opacity_label, 0, 1)
        edit_layout.addWidget(self.opacity_box, 1, 1)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.color = self.color_button.color
        self.alpha = float(self.opacity_box.text())

    def style_text(self) -> str:
        return find_color_name(self.color)


class LineData(BaseChartData):
    """
    an object to contain a line with one or more segments
    """
    def __init__(self):
        super().__init__()
        self.x_values = None
        self.y_values = None
        # style
        self.linestyle = "solid"
        self.color = "silver"
        self.linewidth = 1.5
        self.zorder = 0
        self.color_button = None
        self.linewidth_box = None
        self.linestyle_box = None
        self.linked_style = None
        self.is_linked = False

    def link_style(self, other_line):
        self.linked_style = other_line
        other_line.is_linked = True

    def export_to_list(self) -> list:
        outlist = ["Line Data\n",
                   f"Name\t{self.name}\n",
                   "x\ty\n"]
        for i in range(len(self.x_values)):
            outlist.append(f"{self.x_values[i]}\t{self.y_values[i]}\n")
        return outlist

    def create_edit_panel(self):
        if self.is_linked:
            return self.edit_panel
        else:
            self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
            (self.color_button, color_label, self.linewidth_box, width_label, self.linestyle_box, style_label,
             _, _, _, _) = MetaWinWidgets.add_chart_line_edits(get_text("Color"), self.color,
                                                               get_text("Width"), self.linewidth,
                                                               get_text("Style"), self.linestyle,
                                                               LINE_STYLES)
            edit_layout.addWidget(color_label, 0, 0)
            edit_layout.addWidget(self.color_button, 1, 0)
            edit_layout.addWidget(width_label, 0, 1)
            edit_layout.addWidget(self.linewidth_box, 1, 1)
            edit_layout.addWidget(style_label, 0, 2)
            edit_layout.addWidget(self.linestyle_box, 1, 2)
            for i in range(edit_layout.columnCount()):
                edit_layout.setColumnStretch(i, 1)
            return self.edit_panel

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidth = float(self.linewidth_box.text())
        self.color = self.color_button.color
        if self.linked_style is not None:
            self.linked_style.linestyle = self.linestyle
            self.linked_style.linewidth = self.linewidth
            self.linked_style.color = self.color
            self.linked_style.visible = self.visible

    def style_text(self) -> str:
        return self.linestyle + " " + find_color_name(self.color) + " line"


class ArcData(BaseChartData):
    """
    an object to contain an arc
    """
    def __init__(self):
        super().__init__()
        self.x_center = 0
        self.y_center = 0
        self.height = 0
        self.width = 0
        self.start_angle = 0
        self.end_angle = 0
        # style
        self.color = "silver"
        self.linestyle = "solid"
        self.linewidth = 1.5
        self.zorder = 0
        self.color_button = None
        self.linewidth_box = None
        self.linestyle_box = None

    def export_to_list(self) -> list:
        outlist = ["Arc Data\n",
                   f"Name\t{self.name}\n",
                   "x\ty\twidth\theight\tstart angle\tend angle\n",
                   f"{self.x_center}\t{self.y_center}\t{self.width}\t{self.height}\t{self.start_angle}\t"
                   f"{self.end_angle}\n"]
        return outlist

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        (self.color_button, color_label, self.linewidth_box, width_label,
         self.linestyle_box, style_label,
         _, _, _, _) = MetaWinWidgets.add_chart_line_edits(get_text("Color"), self.color, get_text("Width"),
                                                           self.linewidth, get_text("Style"), self.linestyle,
                                                           LINE_STYLES)
        edit_layout.addWidget(color_label, 0, 0)
        edit_layout.addWidget(self.color_button, 1, 0)
        edit_layout.addWidget(width_label, 0, 1)
        edit_layout.addWidget(self.linewidth_box, 1, 1)
        edit_layout.addWidget(style_label, 0, 2)
        edit_layout.addWidget(self.linestyle_box, 1, 2)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.linestyle = self.linestyle_box.currentText()
        self.linewidth = float(self.linewidth_box.text())
        self.color = self.color_button.color


class AnnotationData(BaseChartData):
    """
    an object to contain figure annotations
    """
    def __init__(self):
        super().__init__()
        self.annotations = []
        self.x = None
        self.y = None
        self.end_x = None
        self.end_y = None
        self.halignment = "left"
        self.valignment = "baseline"
        self.bbox = None
        self.arrowprops = None
        self.size = "medium"

    def export_to_list(self) -> list:
        outlist = ["Annotation Data\n",
                   f"Name\t{self.name}\n"]
        outstr = "x\ty\t"
        if self.end_x is not None:
            outstr += "endx\tendy\t"
        outstr += "Annotation\n"
        outlist.append(outstr)
        for i in range(len(self.annotations)):
            outstr = f"{self.x[i]}\t{self.y[i]}\t"
            if self.end_x is not None:
                outstr += f"{self.end_x[i]}\t{self.end_y[i]}\t"
            outstr += f"{self.annotations[i]}\n"
            outlist.append(outstr)
        return outlist


class RectangleData(BaseChartData):
    """
    an object to draw an arbitrary rectangle on the plot
    """
    def __init__(self):
        super().__init__()
        self.x = None  # lower left corner
        self.y = None  # lower left corner
        self.height = None
        self.width = None
        self.face_color = "white"
        self.edge_color = "black"
        self.zorder = 1
        self.clip = True


class MARCLegendData(BaseChartData):
    """
    an object to contain the legend for MARC plots
    """
    def __init__(self):
        super().__init__()
        self.legend_scale = None
        self.legend_weights = (0.1, 0.01, 0.001)        # fixed values
        self.legend_formats = ("0.1f", "0.2f", "0.3f")  # fixed values
        self.scatter = None


class FillDataX(BaseChartData):
    """
    an object to contain area fills that run between two values on the x-axis
    """
    def __init__(self):
        super().__init__()
        self.x1_values = None
        self.x2_values = None
        self.y_values = None
        # style
        self.color = "silver"
        self.zorder = 0
        self.alpha = 0.5
        self.color_button = None
        self.opacity_box = None
        self.linked_style = None
        self.is_linked = False

    def link_style(self, other_fill):
        self.linked_style = other_fill
        other_fill.is_linked = True

    def create_edit_panel(self):
        if self.is_linked:
            return self.edit_panel
        else:
            self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
            (self.color_button, color_label, _, self.opacity_box,
             opacity_label) = MetaWinWidgets.add_chart_color_button(get_text("Color"), self.color, alpha=self.alpha)

            edit_layout.addWidget(color_label, 0, 0)
            edit_layout.addWidget(self.color_button, 1, 0)
            edit_layout.addWidget(opacity_label, 0, 1)
            edit_layout.addWidget(self.opacity_box, 1, 1)
            for i in range(edit_layout.columnCount()):
                edit_layout.setColumnStretch(i, 1)
            return self.edit_panel

    def update_style(self):
        self.color = self.color_button.color
        self.alpha = float(self.opacity_box.text())
        if self.linked_style is not None:
            self.linked_style.color = self.color
            self.linked_style.visible = self.visible

    def style_text(self) -> str:
        return find_color_name(self.color)


class ColorGrid(BaseChartData):
    """
    an object to contain area fills that run between two values on the x-axis
    """
    def __init__(self):
        super().__init__()
        self.x_values = None
        self.y_values = None
        self.z_values = None
        self.label_name = ""
        # style
        self.colormap = "RdYlGn"
        self.map_box = None
        self.rev_map_box = None
        self.label_box = None

    def create_edit_panel(self):
        self.edit_panel, edit_layout = MetaWinWidgets.add_figure_edit_panel(self)
        self.map_box, self.rev_map_box, label, self.label_box = MetaWinWidgets.add_chart_colormap_edits(self.colormap,
                                                                                                        COLORMAPS,
                                                                                                        self.label_name)
        edit_layout.addWidget(self.rev_map_box, 0, 0)
        edit_layout.addWidget(self.map_box, 1, 0)
        edit_layout.addWidget(label, 0, 1)
        edit_layout.addWidget(self.label_box, 1, 1)
        for i in range(edit_layout.columnCount()):
            edit_layout.setColumnStretch(i, 1)
        return self.edit_panel

    def update_style(self):
        self.colormap = COLORMAPS[self.map_box.currentText()]
        if self.rev_map_box.isChecked():
            self.colormap += "_r"
        self.label_name = self.label_box.text()


# ---------- Chart Caption Classes ---------- #
class NormalQuantileCaption:
    def __init__(self):
        self.prediction_limit = None
        self.means = None
        self.regression = None
        self.regression_scatter = None

    def __str__(self):
        regression_text = self.regression.style_text()
        style_text = get_text("normal_quantile_style").format(regression_text, self.prediction_limit.style_text())
        return get_text("normal_quantile_caption").format(get_citation("Wang_and_Bushman_1998")) + style_text + \
            create_reference_list(["Wang_and_Bushman_1998"], True)


class ScatterCaption:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""

    def __str__(self):
        return get_text("Scatter plot of {} vs. {}.").format(self.y_label, self.x_label)


class HistogramCaption:
    def __init__(self):
        self.e_label = ""
        self.weight_type = WEIGHT_NONE

    def __str__(self):
        caption = get_text("Histogram of {} from individual studies.").format(self.e_label)
        if self.weight_type == WEIGHT_INVVAR:
            caption += get_text(" Counts were weighted by the inverse of the variance of each effect size.")
        elif self.weight_type == WEIGHT_N:
            caption += get_text(" Counts were weighted by a sample size associated with each effect size.")
        return caption


class RadialCaption:
    def __init__(self):
        self.e_label = ""

    def __str__(self):
        return get_text("Radial_chart_caption").format(self.e_label)


class MetaRegressionCaption:
    def __init__(self):
        self.e_label = ""
        self.i_label = ""
        self.model = ""
        self.ref_list = ""
        self.citations = []

    def __str__(self):
        return get_text("metaregression_caption").format(self.e_label, self.i_label, self.model, self.ref_list) + \
                create_reference_list(self.citations, True)


class StndRegressionCaption:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""
        self.model = ""

    def __str__(self):
        return get_text("stndregression_caption").format(self.y_label, self.x_label, self.model)


class TrimAndFillCaption:
    def __init__(self):
        self.e_label = ""
        self.original_scatter = None
        self.inferred_scatter = None
        self.original_mean = None
        self.inferred_mean = None

    def __str__(self):
        original_mean_text = self.original_mean.style_text()
        inferred_mean_text = self.inferred_mean.style_text()
        original_marker_text = self.original_scatter.style_text()
        inferred_marker_text = self.inferred_scatter.style_text()
        new_cites = ["Duval_Tweedie_2000a", "Duval_Tweedie_2000b"]
        return get_text("trim_fill_caption").format(self.e_label, "Duval and Tweedie 2000a, b", original_marker_text,
                                                    inferred_marker_text, original_mean_text,
                                                    inferred_mean_text) + create_reference_list(new_cites, True)


class ForestPlotBaseCaption:
    def __init__(self):
        self.e_label = ""
        self.alpha = 0.05
        self.bootstrap_n = None
        self.normal_ci = True
        self.no_effect = None
        self.means = None
        self.medians = None
        self.boot = None
        self.bias = None
        self.boot_violin = None
        self.style = FP_STYLE_PLAIN

    def base_forest_plot_caption(self) -> str:
        """
        Basic forest plot description
        """
        return get_text("forest_plot_common_caption1").format(self.e_label, self.no_effect.style_text())

    def mid_forest_plot_caption(self) -> str:
        """
        Middle part of forest plot captions, when no study specific intervals are included
        """
        if self.normal_ci:
            dist_text = get_text("normal_ci_dist")
        else:
            dist_text = get_text("t_ci_dist")
        return get_text("mid_forest_plot_caption").format(self.means.style_text(), 1-self.alpha, dist_text)

    def extra_forest_plot_caption(self, inc_median: bool = True) -> str:
        """
        Final part of forest plot captions, to indicate median and bootstrap style markers
        """
        text = ""
        if inc_median:
            text += get_text("forest_plot_median_caption").format(self.medians.style_text())
        if self.bootstrap_n is not None:
            citation = "Adams_et_1997"
            text += (get_text("bootstrap_caption").format(self.bootstrap_n, get_citation(citation),
                                                         self.boot.style_text(), self.bias.style_text(),
                                                         self.boot_violin.style_text()) +
                     create_reference_list([citation], True))
        return text


class ForestPlotCaption(ForestPlotBaseCaption):
    def __str__(self):
        if self.style == FP_STYLE_SCALED:
            scale_text = get_text("forest plot scaled means")
            cite_text = ""
        elif self.style == FP_STYLE_THICK:
            scale_text = get_text("forest plot thick").format(get_citation("Schild_Voracek_2014"))
            cite_text = create_reference_list(["Schild_Voracek_2014"], True)
        elif self.style == FP_STYLE_RAINFOREST:
            scale_text = get_text("rainforest plot").format(get_citation("Schild_Voracek_2014"))
            cite_text = create_reference_list(["Schild_Voracek_2014"], True)
        else:
            scale_text = ""
            cite_text = ""
        return (get_text("Forest plot of individual effect sizes for each study.") +
                self.base_forest_plot_caption() +
                get_text("study_forest_plot_extra").format(self.means.style_text(), 1-self.alpha) + scale_text +
                cite_text)


class BasicAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        if self.normal_ci:
            dist_text = get_text("normal_ci_dist")
        else:
            dist_text = get_text("mixed_ci_dist")

        if self.style == FP_STYLE_SCALED:
            scale_text = get_text("forest plot scaled means")
            cite_text = ""
        elif self.style == FP_STYLE_THICK:
            scale_text = get_text("forest plot thick").format(get_citation("Schild_Voracek_2014"))
            cite_text = create_reference_list(["Schild_Voracek_2014"], True)
        elif self.style == FP_STYLE_RAINFOREST:
            scale_text = get_text("rainforest plot").format(get_citation("Schild_Voracek_2014"))
            cite_text = create_reference_list(["Schild_Voracek_2014"], True)
        else:
            scale_text = ""
            cite_text = ""
        if self.style == FP_STYLE_PLAIN:
            mean_text = ""
        else:
            mean_text = get_text("forest mean scale")
        # return (get_text("Forest plot of individual effect sizes for each study.") +
        #         self.base_forest_plot_caption() +
        #         get_text("study_forest_plot_extra").format(self.means.style_text(), 1-self.alpha) + scale_text +
        #         cite_text)
        return (get_text("Forest plot of individual effect sizes for each study, as well as the overall mean.") +
                self.base_forest_plot_caption() +
                get_text("basic_analysis_forest_plot_extra").format(self.means.style_text(), 1-self.alpha, dist_text) +
                scale_text + mean_text + self.extra_forest_plot_caption() + cite_text)


class GroupedAnalysisCaption(ForestPlotBaseCaption):
    def __init__(self):
        super().__init__()
        self.group_label = ""

    def __str__(self):
        return get_text("group_forest_plot").format(self.group_label) + \
               self.base_forest_plot_caption() + self.mid_forest_plot_caption() + self.extra_forest_plot_caption()


class NestedAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("nest_caption") + self.base_forest_plot_caption() + self.mid_forest_plot_caption() + \
               self.extra_forest_plot_caption()


class CumulativeAnalysisCaption(ForestPlotBaseCaption):
    def __init__(self):
        super().__init__()
        self.order_label = ""

    def __str__(self):
        return get_text("cumulative_forest_plot").format(self.order_label) + \
               self.base_forest_plot_caption() + self.mid_forest_plot_caption() + self.extra_forest_plot_caption()


class JackknifeAnalysisCaption(ForestPlotBaseCaption):
    def __str__(self):
        return get_text("jackknife_forest_plot") + self.base_forest_plot_caption() + self.mid_forest_plot_caption() + \
               self.extra_forest_plot_caption()


class MARCPlotCaption:
    def __init__(self):
        self.e_label = ""
        self.alpha = 0.05
        self.style = MARC_STYLE_0
        self.means = None
        self.no_effect = None

    def __str__(self):
        if self.style == MARC_STYLE_0:
            meanstr = ""
            extrastr = ""
        else:
            meanstr = " and the mean"
            extrastr = get_text("marc_caption2")
        cite_text = create_reference_list(["Fitzgerald_Tipton_2022", "Fitzgerald_et_2025"], True)
        return get_text("marc_caption1").format(meanstr) + extrastr + cite_text


class FunnelPlotCaption:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""
        self.mean_effect = None
        self.pseudo_ci = None
        self.zone99 = None
        self.zone95 = None
        self.zone90 = None
        self.colorgrid = None

    def __str__(self):
        mean_text = self.mean_effect.style_text()
        citations = ["Light_Pillemer_1984"]
        if self.pseudo_ci is None:
            pseudo_text = ""
        else:
            cite_text = get_citation("Sterne_Egger_2001")
            citations.append("Sterne_Egger_2001")
            pseudo_text = get_text("funnel_pseudo_ci_style").format(self.pseudo_ci.style_text(), cite_text)
        if self.zone99 is None:
            contour_text = ""
        else:
            cite_text = get_citation("Peters_et_2008")
            citations.append("Peters_et_2008")
            contour_text = get_text("funnel_contour_style").format(self.zone99.style_text(), self.zone95.style_text(),
                                                                   self.zone90.style_text(), cite_text)
        if self.colorgrid is None:
            sunset_text = ""
        else:
            cite_text = get_citation("Kossmeier_et_2020")
            citations.append("Kossmeier_et_2020")
            sunset_text = get_text("funnel_sunset_style").format(cite_text)

        return get_text("funnel_plot_caption").format(self.x_label, self.y_label, mean_text) + pseudo_text + \
            contour_text + sunset_text + create_reference_list(citations, True)


# ---------- Main Chart Data Class ---------- #
class ChartData:
    """
    an object to contain all data that appears on charts

    this will allow chart data exporting, as well as open up the possibility of figure editing
    """
    def __init__(self, caption_type, multi: Optional[str] = None):
        self.x_label = ""
        self.y_label = ""
        self.multi = multi
        self.data = []
        # special adjustments
        self.suppress_y = False
        self.rescale_x = None
        self.rescale_y = None
        self.invert_y = False
        # caption
        if caption_type == "normal quantile":
            self.caption = NormalQuantileCaption()
        elif caption_type == "scatter plot":
            self.caption = ScatterCaption()
        elif caption_type == "histogram":
            self.caption = HistogramCaption()
        elif caption_type == "radial":
            self.caption = RadialCaption()
        elif caption_type == "regression":
            self.caption = MetaRegressionCaption()
        elif caption_type == "standard regression":
            self.caption = StndRegressionCaption()
        elif caption_type == "trim and fill":
            self.caption = TrimAndFillCaption()
        elif caption_type == "basic analysis":
            self.caption = BasicAnalysisCaption()
        elif caption_type == "grouped analysis":
            self.caption = GroupedAnalysisCaption()
        elif caption_type == "nested analysis":
            self.caption = NestedAnalysisCaption()
        elif caption_type == "cumulative analysis":
            self.caption = CumulativeAnalysisCaption()
        elif caption_type == "jackknife analysis":
            self.caption = JackknifeAnalysisCaption()
        elif caption_type == "forest plot":
            self.caption = ForestPlotCaption()
        elif caption_type == "marc plot":
            self.caption = MARCPlotCaption()
        elif caption_type == "funnel plot":
            self.caption = FunnelPlotCaption()
        else:
            self.caption = ""

    def caption_text(self):
        return str(self.caption)

    def add_scatter(self, name: str, x_data, y_data, marker: Union[str, int] = "o", label="", zorder=0, color="#1f77b4",
                    edgecolors="#1f77b4", size: Union[list, Number] = 36, linewidths=1.5, linestyle="solid",
                    fixed_marker_size: bool = True, min_size=1, max_size=100, weights=None, max_weight: Number = 0,
                    min_weight: Number = 0, alpha: Number = 1, alt_axes: Optional[int] = None):
        new_scatter = ScatterData()
        new_scatter.name = name
        new_scatter.x = x_data
        new_scatter.y = y_data
        new_scatter.marker = marker
        new_scatter.label = label
        new_scatter.zorder = zorder
        new_scatter.color = color
        new_scatter.size = size
        new_scatter.edgecolors = edgecolors
        new_scatter.linewidths = linewidths
        new_scatter.linestyle = linestyle
        new_scatter.single_size = fixed_marker_size
        new_scatter.min_size = min_size
        new_scatter.max_size = max_size
        new_scatter.weights = weights
        new_scatter.max_weight = max_weight
        new_scatter.min_weight = min_weight
        new_scatter.alpha = alpha
        new_scatter.alt_axes = alt_axes
        self.data.append(new_scatter)
        return new_scatter

    def add_line(self, name: str, x_min, y_min, x_max, y_max, linestyle="solid", color="silver", zorder=0,
                 linewidth=1.5):
        new_line = LineData()
        new_line.name = name
        new_line.x_values = [x_min, x_max]
        new_line.y_values = [y_min, y_max]
        new_line.linestyle = linestyle
        new_line.color = color
        new_line.zorder = zorder
        new_line.linewidth = linewidth
        self.data.append(new_line)
        return new_line

    def add_histogram(self, name, cnts, bins, linewidth=1, edgecolor="black", color="#1f77b4", linestyle="solid"):
        new_hist = HistogramData()
        new_hist.name = name
        new_hist.counts = cnts
        new_hist.bins = bins
        new_hist.linewidth = linewidth
        new_hist.linestyle = linestyle
        new_hist.edgecolor = edgecolor
        new_hist.color = color
        self.data.append(new_hist)
        return new_hist

    def add_arc(self, name, xc, yc, height, width, start_angle, end_angle, zorder=0, edgecolor="silver",
                linestyle="solid", linewidth=1.5):
        new_arc = ArcData()
        new_arc.name = name
        new_arc.x_center = xc
        new_arc.y_center = yc
        new_arc.width = width
        new_arc.height = height
        new_arc.start_angle = start_angle
        new_arc.end_angle = end_angle
        new_arc.zorder = zorder
        new_arc.color = edgecolor
        new_arc.linestyle = linestyle
        new_arc.linewidth = linewidth
        self.data.append(new_arc)
        return new_arc

    def add_multi_line(self, name, x_values, y_values, linestyle="solid", color="silver", zorder=0, linewidth=1.5):
        new_ml = LineData()
        new_ml.name = name
        new_ml.x_values = x_values
        new_ml.y_values = y_values
        new_ml.linestyle = linestyle
        new_ml.color = color
        new_ml.zorder = zorder
        new_ml.linewidth = linewidth
        self.data.append(new_ml)
        return new_ml

    def add_ci(self, name, min_x, max_x, y, zorder=0, color="#1f77b4", linestyle="solid", linewidth=1.5,
               fixed_line_width: bool = True, min_width=1, max_width=10, weights=None):
        new_ci = ForestCIData()
        new_ci.name = name
        new_ci.min_x = min_x
        new_ci.max_x = max_x
        new_ci.y = y
        new_ci.zorder = zorder
        new_ci.color = color
        new_ci.linestyle = linestyle
        new_ci.linewidth = linewidth
        new_ci.single_width = fixed_line_width
        new_ci.min_width = min_width
        new_ci.max_width = max_width
        new_ci.weights = weights
        self.data.append(new_ci)
        return new_ci

    def add_labels(self, name, labels, y_data):
        new_labels = LabelData()
        new_labels.name = name
        new_labels.labels = labels
        new_labels.y_pos = y_data
        self.data.append(new_labels)
        return new_labels

    def add_annotations(self, name, annotations, x_data, y_data, end_x_data=None, end_y_data=None,
                        halignment: str = "left",valignment: str = "baseline", bbox=None, arrowprops=None,
                        size="medium", alt_axes: Optional[int] = None):
        new_annotation = AnnotationData()
        new_annotation.name = name
        new_annotation.x = x_data
        new_annotation.y = y_data
        new_annotation.end_x = end_x_data
        new_annotation.end_y = end_y_data
        new_annotation.annotations = annotations
        new_annotation.halignment = halignment
        new_annotation.valignment = valignment
        new_annotation.bbox = bbox
        new_annotation.arrowprops = arrowprops
        new_annotation.size = size
        new_annotation.alt_axes = alt_axes
        self.data.append(new_annotation)
        return new_annotation


    def add_rectangle(self, name, x, y, height, width, facecolor="white", edgecolor="black", zorder=1,
                      clip: bool = True, alt_axes: Optional[int] = None):
        new_rect = RectangleData()
        new_rect.name = name
        new_rect.x = x
        new_rect.y = y
        new_rect.height = height
        new_rect.width = width
        new_rect.face_color = facecolor
        new_rect.edge_color = edgecolor
        new_rect.zorder = zorder
        new_rect.clip = clip
        new_rect.alt_axes = alt_axes
        self.data.append(new_rect)
        return new_rect


    def add_marc_legend(self, name: str, scatter: ScatterData) -> MARCLegendData:
        new_legend = MARCLegendData()
        new_legend.name = name
        new_legend.scatter = scatter
        self.data.append(new_legend)
        return new_legend


    def add_fill_area_x(self, name, x1, x2, y, zorder=0, color="red", alpha=0.5, alt_axes: Optional[int] = None):
        new_fill = FillDataX()
        new_fill.name = name
        new_fill.x1_values = x1
        new_fill.x2_values = x2
        new_fill.y_values = y
        new_fill.color = color
        new_fill.zorder = zorder
        new_fill.alpha = alpha
        new_fill.alt_axes = alt_axes
        self.data.append(new_fill)
        return new_fill

    def add_color_grid(self, name, x, y, z, colormap: str = "inferno", grid_label: str = ""):
        new_grid = ColorGrid()
        new_grid.name = name
        new_grid.x_values = x
        new_grid.y_values = y
        new_grid.z_values = z
        new_grid.colormap = colormap
        new_grid.label_name = grid_label
        self.data.append(new_grid)
        return new_grid

    def add_rainforest(self, name: str, mean_data, var_data, y_data, lower_data, upper_data, weight_data, zorder=0):
        new_rainforest = RainforestData()
        new_rainforest.name = name
        new_rainforest.means = mean_data
        new_rainforest.vars = var_data
        new_rainforest.ys = y_data
        new_rainforest.lower_cis = lower_data
        new_rainforest.upper_cis = upper_data
        new_rainforest.weights = weight_data
        new_rainforest.zorder = zorder
        self.data.append(new_rainforest)
        return new_rainforest

    def add_violin(self, name, bs_data, ys, color: str = "#FFDF00", alpha=1):
        new_violin = ViolinData()
        new_violin.name = name
        new_violin.bootstrap_data = bs_data
        new_violin.ys = ys
        new_violin.color = color
        new_violin.alpha = alpha
        self.data.append(new_violin)
        return new_violin

    def export_to_list(self):
        outlist = [f"X-axis label\t{self.x_label}\n",
                   f"Y-axis label\t{self.y_label}\n\n\n"]
        for dat in self.data:
            outlist.extend(dat.export_to_list())
            outlist.append("\n\n")
        return outlist


def fill_between_cmap(x, y, y0, v, faxes, cmap=None, vmin=None, vmax=None, zorder=0):
    """
    code to fill between two horizontal lines using a color map as one moves horizontally

    this function is heavily modified from code found at
    https://github.com/cristobaltapia/mpl_fill_cmap_between
    """

    # generate coordinates for quadmesh
    """
    duplicate x coordinates so you get x_1 x_1 x_2 x_2 x_3 x_3 etc.
    create new y coordinates alternating between y and y0, y_1 y0_1 y_2 y0_2 etc
    """
    n = x.size
    coords_x = numpy.empty((2 * n), dtype=x.dtype)
    coords_y = numpy.empty((2 * y.size), dtype=y.dtype)
    coords_x[0::2] = x
    coords_x[1::2] = x
    coords_y[0::2] = y0
    coords_y[1::2] = y

    # combine, rearrange, and reshape coordinates
    coords = numpy.vstack((coords_x, coords_y))
    coords = coords.T
    coords = numpy.asarray(coords, numpy.float64).reshape((n, 2, 2))

    # values for the colormap
    """
    duplicate values to match the prior duplication of the coordinates
    """
    vals = numpy.empty((2 * n))
    vals[0::2] = v
    vals[1::2] = v

    collection = QuadMesh(coordinates=coords, shading="gouraud", zorder=zorder)
    collection.set_array(vals)
    collection.set_clim(vmin, vmax)
    collection.set_cmap(cmap)
    collection.autoscale_None()

    faxes.add_collection(collection)


def base_figure(figure_canvas):
    """
    create the baseline figure used for all plots
    """
    figure_canvas.figure.clf()  # clean any existing figures
    figure_canvas.figure.set_layout_engine("none")
    faxes = figure_canvas.figure.subplots()
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    return faxes


def base_figure_multi(figure_canvas, nr: int = 1, nc: int = 1, height_ratios = None, width_ratios = None):
    """
    create the baseline figure used for all plots
    """
    figure_canvas.figure.clf()  # clean any existing figures
    figure_canvas.figure.set_layout_engine("none")
    faxes = figure_canvas.figure.subplots(nr, nc, height_ratios=height_ratios, width_ratios=width_ratios)
    for f in faxes:
        f.spines["right"].set_visible(False)
        f.spines["top"].set_visible(False)
    return faxes


def create_figure(chart_data, figure_canvas):
    """
    create a figure given pre-determined chart data

    this function allows complete separation of the generation of the plot values and the creation of the figure,
    which subsequently can allow user modification of plot styles and redrawing of the figure w/o needing to
    recalculate anything
    """
    if chart_data.multi == MARC_STYLE_2:
        all_axes = base_figure_multi(figure_canvas, nr=2, nc=1, height_ratios=[2, 3])
        faxes = all_axes[1]  # primary plot axis
        faxes2 = all_axes[0]  # area for labeling
        faxes2.spines["left"].set_visible(False)
        faxes2.spines["bottom"].set_visible(False)
        faxes2.set_yticklabels([])
        faxes2.set_xticklabels([])
        faxes2.set_xticks([])
        faxes2.set_yticks([])
    else:
        faxes = base_figure(figure_canvas)
        all_axes = None
        faxes2 = None
    faxes.set_ylabel(chart_data.y_label)
    faxes.set_xlabel(chart_data.x_label)
    for data in chart_data.data:
        if data.visible:
            if isinstance(data, ScatterData):
                if data.single_size:
                    marker_size = data.size
                else:
                    # calculate new marker sizes from weights
                    minw, maxw = data.min_weight, data.max_weight
                    wrange = maxw - minw
                    marker_size = [data.min_size + (data.max_size-data.min_size)*(w-minw)/wrange for w in data.weights]
                if data.alt_axes is None:
                    ax = faxes
                else:
                    ax = all_axes[data.alt_axes]

                ax.scatter(data.x, data.y, marker=data.marker, label=data.label, zorder=data.zorder,
                           color=data.color, edgecolors=data.edgecolors, s=marker_size, linewidths=data.linewidths,
                           linestyle=data.linestyle, alpha=data.alpha)
            elif isinstance(data, LineData):
                faxes.plot(data.x_values, data.y_values, linestyle=data.linestyle, color=data.color, zorder=data.zorder,
                           linewidth=data.linewidth)
            elif isinstance(data, ForestCIData):
                if data.single_width:
                    line_width = data.linewidth
                else:
                    # calculate new line widths from weights
                    minw, maxw = min(data.weights), max(data.weights)
                    wrange = maxw - minw
                    line_width = [data.min_width+(data.max_width-data.min_width)*(w-minw)/wrange for w in data.weights]

                faxes.hlines(data.y, data.min_x, data.max_x, zorder=data.zorder, colors=data.color,
                             linestyles=data.linestyle, linewidth=line_width)
            elif isinstance(data, LabelData):
                faxes.set_yticks([y for y in data.y_pos])
                faxes.set_yticklabels(data.labels)
                faxes.get_yaxis().set_tick_params(length=0)
            elif isinstance(data, ArcData):
                arc = patches.Arc((data.x_center, data.y_center), width=data.width, height=data.height,
                                  theta1=data.start_angle, theta2=data.end_angle, edgecolor=data.color,
                                  linestyle=data.linestyle, zorder=data.zorder, linewidth=data.linewidth)
                faxes.add_patch(arc)
            elif isinstance(data, AnnotationData):
                if data.alt_axes is None:
                    ax = faxes
                else:
                    ax = all_axes[data.alt_axes]
                for i in range(len(data.annotations)):
                    if data.end_x is None:
                        ax.annotate(data.annotations[i], (data.x[i], data.y[i]), ha=data.halignment, va=data.valignment,
                                    bbox=data.bbox, arrowprops=data.arrowprops, wrap=True, size=data.size)
                    else:
                        ax.annotate(data.annotations[i], (data.x[i], data.y[i]), (data.end_x[i], data.end_y[i]),
                                    ha=data.halignment, va=data.valignment, size=data.size, wrap=True,
                                    bbox=data.bbox, arrowprops=data.arrowprops)
            elif isinstance(data, MARCLegendData):
                # calculate new marker sizes
                sc = data.scatter
                minw, maxw = sc.min_weight, sc.max_weight
                wrange = maxw - minw
                legend_size = [math.sqrt(sc.min_size + (sc.max_size - sc.min_size)*(w-minw)/wrange)
                               for w in data.legend_weights]

                legend_elements = []
                for i, s in enumerate(data.legend_weights):
                    legend_elements.append(Line2D([0], [0], marker="o", color="None",
                                                  label=format(s, data.legend_formats[i]),
                                                  markerfacecolor=sc.color, markeredgecolor="None",
                                                  markersize=legend_size[i]))
                # legend_artist = figure_canvas.figure.legend(handles=legend_elements, loc="outside right center", borderpad=1, labelspacing=1,
                #                              title="Relative Weight")
                # figure_canvas.figure.set_layout_engine("constrained")
                legend_artist = faxes.legend(handles=legend_elements, loc="center left", borderpad=1, labelspacing=1,
                                             title="Relative Weight")

                # add arrows around legend
                faxes.annotate("More certain", (0.5, 1), (0.5, 1.5), xycoords=legend_artist,
                               ha="center", va="center", arrowprops=dict(facecolor="black", arrowstyle="<-"))
                faxes.annotate("Less certain", (0.5, 0), (0.5, -0.5), xycoords=legend_artist,
                               ha="center", va="center", arrowprops=dict(facecolor="black", arrowstyle="<-"))


            elif isinstance(data, RectangleData):
                if data.alt_axes is None:
                    ax = faxes
                else:
                    ax = all_axes[data.alt_axes]
                rectangle = matplotlib.patches.Rectangle((data.x, data.y), data.width, data.height,
                                                         facecolor=data.face_color, edgecolor=data.edge_color,
                                                         zorder=data.zorder, clip_on=data.clip)
                ax.add_patch(rectangle)
            elif isinstance(data, HistogramData):
                faxes.hist(data.bins[:-1], data.bins, weights=data.counts, edgecolor=data.edgecolor, color=data.color,
                           linewidth=data.linewidth, linestyle=data.linestyle, alpha=data.alpha)
            elif isinstance(data, FillDataX):
                if data.alt_axes is None:
                    ax = faxes
                else:
                    ax = all_axes[data.alt_axes]
                ax.fill_betweenx(data.y_values, data.x1_values, data.x2_values, color=data.color,
                                 edgecolor="none", zorder=data.zorder, alpha=data.alpha)
            elif isinstance(data, ColorGrid):
                cm = faxes.pcolormesh(data.x_values, data.y_values, data.z_values, shading="gouraud",
                                 cmap=data.colormap, zorder=0, vmin=0, vmax=100)
                figure_canvas.figure.colorbar(cm, ax=faxes, label=data.label_name)
            elif isinstance(data, RainforestData):
                minw, maxw = min(data.weights), max(data.weights)
                wrange = maxw - minw
                nsteps = 500
                sf = 2
                # find max pdf for scaling shading across the rainforest droplets
                maxadj = 0
                for i in range(len(data.means)):
                    wscale = 1+(sf-1)*(data.weights[i] - minw)/wrange  # scale between 1 and scaling factor
                    x = numpy.linspace(data.lower_cis[i], data.upper_cis[i], nsteps)
                    yadj = scipy.stats.norm.pdf(x, loc=data.means[i], scale=math.sqrt(data.vars[i]))
                    maxadj = max(maxadj, max(yadj * wscale))
                # draw rainforest droplets
                for i in range(len(data.means)):
                    wscale = 1+(sf-1)*(data.weights[i] - minw)/wrange  # scale between 1 and scaling factor
                    x = numpy.linspace(data.lower_cis[i], data.upper_cis[i], nsteps)
                    yadj = scipy.stats.norm.pdf(x, loc=data.means[i], scale=math.sqrt(data.vars[i]))
                    fill_between_cmap(x, data.ys[i] + yadj*wscale, data.ys[i] - yadj*wscale, yadj*wscale, faxes,
                                      cmap=data.colormap, vmax=maxadj, zorder=data.zorder)
            elif isinstance(data, ViolinData):
                for i, d in enumerate(data.bootstrap_data):
                    if d is not None:
                        parts = faxes.violinplot(d, [data.ys[i]], points=1000, orientation="horizontal",
                                                 widths=FOREST_STEP-1, showmeans=False, showmedians=False,
                                                 showextrema=False)
                        for pc in parts["bodies"]:
                            pc.set_color(data.color)
                            pc.set_alpha(data.alpha)

    if chart_data.suppress_y:
        faxes.spines["left"].set_visible(False)
    if chart_data.rescale_x is not None:
        faxes.set_xlim(chart_data.rescale_x[0], chart_data.rescale_x[1])
        if chart_data.multi == MARC_STYLE_2:
            faxes2.set_xlim(chart_data.rescale_x[0], chart_data.rescale_x[1])
    if chart_data.rescale_y is not None:
        faxes.set_ylim(chart_data.rescale_y[0], chart_data.rescale_y[1])
    if chart_data.invert_y:
        faxes.invert_yaxis()
    if chart_data.multi == MARC_STYLE_2:
        figure_canvas.figure.subplots_adjust(hspace=0.05)



def chart_forest_plot(analysis_type: str, effect_name, forest_data, alpha: float = 0.05,
                      bootstrap_n: Optional[int] = None, extra_name: Optional[str] = None,
                      normal_ci: bool = True, fp_style: int = FP_STYLE_PLAIN) -> ChartData:
    chart_data = ChartData(analysis_type)
    chart_data.caption.e_label = effect_name
    chart_data.caption.alpha = alpha
    chart_data.caption.bootstrap_n = bootstrap_n
    chart_data.caption.normal_ci = normal_ci
    is_basic = False
    if analysis_type == "grouped analysis":
        chart_data.caption.group_label = extra_name
    elif analysis_type == "cumulative analysis":
        chart_data.caption.order_label = extra_name
    elif analysis_type == "basic analysis":
        is_basic = True

    chart_data.x_label = effect_name
    chart_data.suppress_y = True

    if bootstrap_n is None:
        bootstrap = False
    else:
        bootstrap = True

    n_effects = len(forest_data)

    y_data = [-FOREST_STEP*d.order for d in forest_data]
    ci_y_data = [y for y in y_data for _ in range(2)]
    labels = [d.name for d in forest_data]

    mean_data = [d.mean for d in forest_data]
    var_data = [d.variance for d in forest_data]
    is_data = False
    for d in forest_data:
        if d.median is not None:
            is_data = True
    if is_data:
        median_data = [d.median for d in forest_data]
    else:
        median_data = None

    # used for scaled, thick, and rainforest styles
    if is_basic:
        # for a basic analysis, replace the weight of the first entry (the mean) with the average of the
        # other weights
        tmpweights = [1/d.variance for d in forest_data[1:]]
        # meanw = max(tmpweights)
        meanw = sum(tmpweights)/len(tmpweights)
        weights = [meanw]
        weights.extend(tmpweights)
    else:
        weights = [1/d.variance for d in forest_data]  # get weights

    minw, maxw = min(weights), max(weights)
    wrange = maxw - minw

    min_marker_size = 1
    max_marker_size = 100
    linewidth = 1.5
    min_line_width = 1
    max_line_width = 10
    marker = "o"
    marker_color = "#1f77b4"
    fixed_marker_size = True
    fixed_line_width = True
    ci_color = "#1f77b4"
    no_z = 1
    if fp_style == FP_STYLE_SCALED:
        # scale between min and max marker size
        size = [min_marker_size+(max_marker_size-min_marker_size)*(w - minw)/wrange for w in weights]
        fixed_marker_size = False
    elif fp_style == FP_STYLE_THICK:
        size = 100
        marker = "|"
        marker_color = "red"
        # scale between min and max line widths
        linewidth = [min_line_width+(max_line_width-min_line_width)*(w - minw)/wrange for w in weights]
        fixed_line_width = False
    elif fp_style == FP_STYLE_RAINFOREST:
        size = 200
        marker = "|"
        marker_color = "white"
        linewidth = 1
        ci_color = "white"
        no_z = 10
    else:
        size = 36

    cis = []
    bs_cis = []
    bias_cis = []
    bs_values = []
    for d in forest_data:
        cis.extend([d.lower_ci, d.upper_ci])
    min_cis = [d.lower_ci for d in forest_data]
    max_cis = [d.upper_ci for d in forest_data]
    if bootstrap:
        bs_cis = []
        bias_cis = []
        for i, d in enumerate(forest_data):
            bs_cis.extend([d.lower_bs_ci, d.upper_bs_ci])
            bias_cis.extend([d.lower_bias_ci, d.upper_bias_ci])
            bs_values.append(d.bootstrapped_means)

    chart_data.caption.no_effect = chart_data.add_line(get_text("Line of No Effect"), 0, 0, 0,
                                                       -(FOREST_STEP*(n_effects+1)), color="silver",
                                                       linestyle="dotted", zorder=no_z)
    chart_data.add_ci(get_text("Confidence Intervals"), min_cis, max_cis, y_data, zorder=3, linewidth=linewidth,
                      fixed_line_width=fixed_line_width, min_width=min_line_width, max_width=max_line_width,
                      weights=weights, color=ci_color)
    chart_data.caption.means = chart_data.add_scatter(get_text("Means"), mean_data, y_data, marker=marker, zorder=5,
                                                      label="mean and {:0.0%} CI (t-dist)".format(1-alpha), size=size,
                                                      color=marker_color, fixed_marker_size=fixed_marker_size,
                                                      min_size=min_marker_size, max_size=max_marker_size,
                                                      weights=weights, max_weight=maxw, min_weight=minw)
    if fp_style == FP_STYLE_RAINFOREST:
        chart_data.add_rainforest(get_text("PDF Raindrops"), mean_data, var_data, y_data, min_cis, max_cis, weights)

    chart_data.caption.style = fp_style
    if median_data is not None:
        chart_data.caption.medians = chart_data.add_scatter(get_text("Medians"), median_data, y_data, marker="x",
                                                            label="median", zorder=5, color="#ff7f0e")
    chart_data.add_labels(get_text("Vertical Axis Tick Labels"), labels, y_data)

    if bootstrap:
        chart_data.caption.boot = chart_data.add_scatter(get_text("Bootstrap Confidence Limits"), bs_cis, ci_y_data,
                                                         marker=6, zorder=4, color="#2ca02c",
                                                         label="{:0.0%} CI (bootstrap)".format(1-alpha))

        chart_data.caption.bias = chart_data.add_scatter(get_text("Bias-corrected Bootstrap Confidence Limits"),
                                                         bias_cis, ci_y_data, marker=7, zorder=4, color="#d62728",
                                                         label="{:0.0%} CI (bias-corrected bootstrap)".format(1-alpha))
        chart_data.caption.boot_violin = chart_data.add_violin(get_text("Bootstrap Distribution"), bs_values,
                                                               y_data)

    return chart_data


def chart_marc_plot(analysis_type: str, effect_name, marc_data, alpha: float = 0.05, marc_style: int = 0) -> ChartData:
    if marc_style == MARC_STYLE_2:
        multi = MARC_STYLE_2
    else:
        multi = None
    chart_data = ChartData(analysis_type, multi=multi)
    chart_data.caption.e_label = effect_name
    chart_data.caption.alpha = alpha
    chart_data.caption.style = marc_style

    chart_data.x_label = effect_name
    chart_data.y_label = get_text("Relative Weight")

    if marc_style != MARC_STYLE_0:
        grand_mean = marc_data[0]  # identify the grand mean
    else:
        grand_mean = None

    if marc_style == MARC_STYLE_2:
        # remove the mean from the primary data set for style 2
        marc_data = marc_data[1:]

    mean_data = [d.mean for d in marc_data]
    max_x = max(numpy.abs(mean_data))*1.1  # set x-limits to 10% more than largest value in either direction
    chart_data.rescale_x = [-max_x, max_x]

    raw_weights = [1 / d.variance for d in marc_data]  # get weights
    if marc_style == MARC_STYLE_1:
        total_weights = sum(raw_weights[1:])  # skip first entry (mean) when included
    else:  # used for plot of studies which exclude calculated mean
        total_weights = sum(raw_weights)
    rel_weights = [w/total_weights for w in raw_weights]
    minw, maxw = min(rel_weights), max(rel_weights)

    if marc_style == MARC_STYLE_0:
        if maxw < 0.1:
            maxw = 0.1
        maxwy = maxw
    else:
        if marc_style == MARC_STYLE_2:
            maxwy = maxw
        else:
            maxwy = 1
        maxw = 1
    minw = 0

    wrange = maxwy - minw
    min_marker_size = 1
    if marc_style == MARC_STYLE_0:
        max_marker_size = 400
    else:
        max_marker_size = 1600  # use larger default max when mean is included

    size = [min_marker_size+(max_marker_size-min_marker_size)*(w - minw)/wrange for w in rel_weights]
    max_y = maxwy*1.1
    min_y = -wrange/10
    chart_data.rescale_y = [min_y, max_y]  # set scale for y-axis

    chart_data.caption.no_effect = chart_data.add_line(get_text("Lines of No Effect and Weight"), 0, min_y, 0, max_y,
                                                       color="darkgray", linestyle="solid", zorder=2)
    base_line = chart_data.add_line("", -max_x, 0, max_x, 0, color="darkgray", linestyle="solid", zorder=2)
    chart_data.caption.no_effect.link_style(base_line)

    chart_data.caption.means = chart_data.add_scatter(get_text("Means"), mean_data, rel_weights, marker="o", zorder=5,
                                                      label="mean", size=size, fixed_marker_size=False,
                                                      min_size=min_marker_size, max_size=max_marker_size,
                                                      weights=rel_weights, max_weight=maxw, min_weight=minw)
    if marc_style == MARC_STYLE_2:
        chart_data.add_scatter("", [grand_mean.mean], [1], marker="o", zorder=5, label="mean", size=max_marker_size,
                               weights=[1], max_weight=1, min_weight=minw, alt_axes=0)

    if marc_style != MARC_STYLE_0:
        # simulate point cloud around mean
        nsim = 250  # there is no obvious reason to simulate 10,000 points then subsample from that
        if marc_style == MARC_STYLE_1:
            cloud_scale = 10
        else:
            cloud_scale = 1
        sim_color = "darkblue"
        sim_x = scipy.stats.norm.rvs(loc=grand_mean.mean, scale=math.sqrt(grand_mean.variance), size=nsim)
        # simulate y values for corresponding normal deviates within a raindrop like distribution
        sim_y = scipy.stats.norm.pdf(sim_x, loc=grand_mean.mean, scale=math.sqrt(grand_mean.variance))
        max_sim = max(sim_y)
        sim_y /= max_sim*cloud_scale  # rescale the PDF so values are between 0 and 1/cloud_scale
        sim_y2 = scipy.stats.uniform.rvs(scale=sim_y)  # calculate random uniform deviates based on the rescaled PDF
        sim_y = sim_y2 - sim_y/2 + 1  # shift values so they are centered on a value of 1
        if marc_style == MARC_STYLE_2:
            alt_axes = 0
        else:
            alt_axes = None
        chart_data.add_scatter("", sim_x, sim_y, marker="o", size=9, alpha=0.2, color="white", edgecolors=sim_color,
                               zorder=20, linewidths=0.5, alt_axes=alt_axes)
        min_sim_y = min(sim_y)
        i = numpy.where(sim_y == min_sim_y)[0][0]  # find a point with the lowest y coordinate
        an_x, an_y = sim_x[i], sim_y[i]
        if marc_style == MARC_STYLE_1:
            an_x2, an_y2 = an_x+max_x/10, an_y-0.1
        else:
            an_x2, an_y2 = an_x+max_x/10, 0

        # add annotation to a low point
        tmp_txt = get_text("MARC_point_annotation").format(f"{1-alpha:0.1%}", f"{grand_mean.lower_ci:0.2}",
                                                           f"{grand_mean.upper_ci:0.2}", f"{grand_mean.mean:0.3}")
        chart_data.add_annotations("", [tmp_txt], [an_x], [an_y], end_x_data=[an_x2], end_y_data=[an_y2],
                                   valignment="top", size="small", halignment="center",
                                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkgray", lw=2),
                                   arrowprops=dict(edgecolor=sim_color, arrowstyle="<-",
                                                   connectionstyle="arc3,rad=-0.5"), alt_axes=alt_axes)
        # create background rectangle at top of chart and add text to it
        if marc_style == MARC_STYLE_1:
            chart_data.add_rectangle("", -max_x+max_x/20, 0.91, width=2*max_x-max_x/10, height=0.18, facecolor="white",
                                     zorder=2, edgecolor="black")
        else:
            chart_data.add_rectangle("", -max_x+max_x/20, 0.2, width=2*max_x-max_x/10, height=1.6, facecolor="white",
                                     zorder=2, edgecolor="black", alt_axes=alt_axes)
        chart_data.add_annotations("", [get_text("SUMMARY OF THE EVIDENCE:")], [-max_x+max_x/10], [1],
                                   valignment="center", size="large", halignment="left", alt_axes=alt_axes)
        chart_data.add_annotations("", [get_text("MARC_summary_label").format(f"{grand_mean.mean:0.3}")],
                                   [max_x*0.9], [1], valignment="center", halignment="right", alt_axes=alt_axes)

    # background colors
    chart_data.add_fill_area_x(get_text("Negative Background"), -max_x, 0, [min_y, max_y], color="red", alpha=0.25,
                               zorder=1)
    chart_data.add_fill_area_x(get_text("Positive Background"), 0, max_x, [min_y, max_y], color="blue", alpha=0.25,
                               zorder=1)
    if marc_style == MARC_STYLE_2:
        chart_data.add_fill_area_x(get_text("Negative Background"), -max_x, 0, [-1, 2], color="red", alpha=0.25,
                                   zorder=1, alt_axes=0)
        chart_data.add_fill_area_x(get_text("Positive Background"), 0, max_x, [-1, 2], color="blue", alpha=0.25,
                                   zorder=1, alt_axes=0)

    # bottom annotations
    chart_data.add_annotations("", [get_text("Negative Effect"), get_text("Positive Effect")],
                               [-max_x/2, max_x/2], [min_y/2, min_y/2], halignment="center", valignment="center",
                               bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkgray", lw=2))
    chart_data.add_marc_legend("", chart_data.caption.means)

    return chart_data


def add_regression_to_chart(x_name: str, y_name: str, x_data, y_data, slope: float, intercept: float,
                            x_min: float, x_max: float, chart_data) -> None:
    y_at_min = slope*x_min + intercept
    y_at_max = slope*x_max + intercept

    chart_data.x_label = x_name
    chart_data.y_label = y_name
    chart_data.caption.regression_scatter = chart_data.add_scatter(get_text("Point Data"), x_data, y_data, zorder=10)
    chart_data.caption.regression = chart_data.add_line(get_text("Regression Line"), x_min, y_at_min, x_max, y_at_max,
                                                        zorder=8, color="silver")


def chart_meta_regression(x_name, y_name, x_data, y_data, slope, intercept, model, ref_list,
                          citations) -> ChartData:
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    chart_data = ChartData("regression")
    chart_data.caption.e_label = y_name
    chart_data.caption.i_label = x_name
    chart_data.caption.model = model
    chart_data.caption.ref_list = ref_list
    chart_data.caption.citations = citations

    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    return chart_data


def add_quantile_axes_to_chart(x_data, y_data, slope: float, intercept: float, chart_data, alpha: float = 0.05) -> None:
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    y_min = numpy.min(y_data)
    y_max = numpy.max(y_data)
    n = len(x_data)
    x_mean = numpy.sum(x_data)/n
    y_mean = numpy.sum(y_data)/n

    y_pred = [slope*x + intercept for x in x_data]
    mse = numpy.sum(numpy.square(y_data - y_pred))/(n - 2)  # mean square error
    ss_x = numpy.sum(numpy.square(x_data - x_mean))  # sum of squares of x

    t_score = -scipy.stats.t.ppf(alpha/2, n-2)
    nsteps = 100
    p = [(i + 0.5)/nsteps for i in range(nsteps)]
    x_pos = [scipy.stats.norm.ppf(i) for i in p]
    y_pos = [x*slope + intercept for x in x_pos]
    y_lower = [y_pos[i] - t_score*math.sqrt(mse*(1 + 1/n + ((x_pos[i] - x_mean)**2)/ss_x)) for i in range(nsteps)]
    y_upper = [y_pos[i] + t_score*math.sqrt(mse*(1 + 1/n + ((x_pos[i] - x_mean)**2)/ss_x)) for i in range(nsteps)]

    chart_data.caption.prediction_limit = chart_data.add_multi_line(get_text("Prediction Limits"), x_pos, y_lower,
                                                                    linestyle="dashed", color="silver", zorder=3)
    upper_limit = chart_data.add_multi_line("", x_pos, y_upper, linestyle="dashed", color="silver", zorder=3)
    chart_data.caption.prediction_limit.link_style(upper_limit)

    # draw center lines
    chart_data.caption.means = chart_data.add_line(get_text("Axes Means"), 0, min(y_min, min(y_lower)), 0,
                                                   max(y_max, max(y_upper)), linestyle="dotted", color="silver")
    vertical_mean = chart_data.add_line("", x_min, y_mean, x_max, y_mean, linestyle="dotted", color="silver")
    chart_data.caption.means.link_style(vertical_mean)


def chart_normal_quantile(x_name, y_name, x_data, y_data, slope, intercept,
                          alpha: float = 0.05) -> ChartData:
    chart_data = ChartData("normal quantile")
    add_quantile_axes_to_chart(x_data, y_data, slope, intercept, chart_data, alpha)
    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    return chart_data


def add_radial_curve_to_chart(effect_label: str, r: float, min_e: float, max_e: float, chart_data,
                              is_log: bool = False) -> None:
    start_a = math.atan(min_e)
    end_a = math.atan(max_e)
    chart_data.add_arc(get_text("Radial Arc"), 0, 0, 2*r, 2*r, math.degrees(start_a), math.degrees(end_a), zorder=2,
                       edgecolor="silver", linestyle="dotted")

    if is_log:
        start_label = math.ceil(math.exp(min_e))
        end_label = math.floor(math.exp(max_e))
        curve_label = exponential_label(effect_label)
    else:
        start_label = math.ceil(min_e)
        end_label = math.floor(max_e)
        curve_label = effect_label

    annotation_list = []
    annotation_x = []
    annotation_y = []

    xadj = 0.25
    for s in range(start_label, end_label+1):
        if not is_log:
            slope = s
            label = str(s)
            if s < 0:
                yadj = -0.25
            elif s > 0:
                yadj = 0.25
            else:
                yadj = 0
        else:
            if -1 > s > -10:
                slope = math.log(1/abs(s))
                label = "1/{}".format(abs(s))
                yadj = -0.25
            elif 1 < s < 10:
                slope = math.log(s)
                label = str(s)
                yadj = 0.25
            elif s == 1:
                slope = 0
                label = "1"
                yadj = 0
            else:
                continue
        annotation_list.append(label)
        annotation_x.append(r*math.cos(math.atan(slope)) + xadj)
        annotation_y.append(r*math.sin(math.atan(slope)) + yadj)
    if is_log:
        if min_e < 2/3 < max_e:
            annotation_list.append("2/3")
            annotation_x.append(r*math.cos(math.atan(math.log(2/3))) + xadj)
            annotation_y.append(r*math.sin(math.atan(math.log(2/3))) - 0.25)
        if min_e < 3/2 < max_e:
            annotation_list.append("3/2")
            annotation_x.append(r * math.cos(math.atan(math.log(3/2))) + xadj)
            annotation_y.append(r * math.sin(math.atan(math.log(3/2))) + 0.25)
    else:
        if min_e < 1/2 < max_e:
            annotation_list.append("1/2")
            annotation_x.append(r * math.cos(math.atan(1/2)) + xadj)
            annotation_y.append(r * math.sin(math.atan(1/2)) - 0.25)
        if min_e < -1/2 < max_e:
            annotation_list.append("-1/2")
            annotation_x.append(r * math.cos(math.atan(-1/2)) + xadj)
            annotation_y.append(r * math.sin(math.atan(-1/2)) + 0.25)
    annotation_list.append(curve_label)
    annotation_x.append(r)
    annotation_y.append(2)
    chart_data.add_annotations(get_text("Radial Arc Labels"), annotation_list, annotation_x, annotation_y)

    chart_data.add_line(get_text("Vertical Axis Zero Line"), 0, 0, r+1, 0, color="silver", linestyle="dotted")


def chart_radial(e_name, x_data, y_data, slope, min_e, max_e, is_log: bool = False) -> ChartData:
    chart_data = ChartData("radial")
    chart_data.caption.e_label = e_name
    max_d = numpy.max(numpy.sqrt(numpy.square(x_data) + numpy.square(y_data)))+1
    x_min = 0
    x_max = (max_d + 1)*math.cos(math.atan(slope))
    add_regression_to_chart(get_text("Precision"), get_text("Standardized") + " " + e_name, x_data, y_data,
                            slope, 0, x_min, x_max, chart_data)
    add_radial_curve_to_chart(e_name, max_d, min_e, max_e, chart_data, is_log)
    chart_data.rescale_x = (0, max_d+2)

    return chart_data


def chart_histogram(e_data, w_data, n_bins, e_label, weighted: int = WEIGHT_NONE) -> ChartData:
    if weighted == WEIGHT_NONE:
        cnts, bins = numpy.histogram(e_data, n_bins)
        y_label = get_text("Count")
    else:
        cnts, bins = numpy.histogram(e_data, n_bins, weights=w_data)
        y_label = get_text("Weighted Count")

    chart_data = ChartData("histogram")
    chart_data.caption.e_label = e_label
    chart_data.caption.weight_type = weighted

    chart_data.x_label = e_label
    chart_data.y_label = y_label
    chart_data.add_histogram("Bin Counts", cnts, bins, edgecolor="black", linewidth=1)

    return chart_data


def draw_tree(faxes, tree, minx, maxx, miny, maxy, scale, draw_labels: bool = False, draw_branch_lengths: bool = False):
    """
    minx, maxx, miny, and maxy represent the drawing bounds for the target node, with minx representing the
    horizontal position of the ancestor of the node, maxx representing the right hand edge of the entire tree,
    miny and maxy representing the vertical positioning of the node and all of its descendants.

    scale is a precalculated value that converts branch lengths to the coordinate system
    """

    """
    the following calculates the horizontal area necessary for the horizontal line connecting the node to it's 
    ancestor
    """
    x = tree.branch_length * scale

    """
    if the node has descendants, first draw all of the descendants in the box which goes from the right edge of 
    the horizontal line for this node to the right hand edge of the drawing window, and the vertical box defined 
    for the entire node
    """
    if tree.n_descendants() > 0:  # this is an internal node
        top_vert_line = 0
        bottom_vert_line = 0
        nd = tree.n_tips()
        top_y = miny
        for i, d in enumerate(tree.descendants):
            """
            divide the vertical plotting area for each descendant proportional to the number of tips contained 
            within that descendant
            """
            ndd = d.n_tips()
            bottom_y = top_y + (ndd / nd) * (maxy - miny)
            # draw the descendant in its own smaller bounded box
            y = draw_tree(faxes, d, minx + x, maxx, top_y, bottom_y, scale, draw_labels, draw_branch_lengths)

            """
            the vertical position of the first and last descendants represent the positions to draw the vertical 
            line connecting all of the descendants
            """
            if i == 0:
                bottom_vert_line = y
            elif i == tree.n_descendants() - 1:
                top_vert_line = y
            top_y = bottom_y
        """
        draw the vertical line connecting the descendants at the horizontal position of the node
        """
        faxes.plot([minx+x, minx+x], [bottom_vert_line, top_vert_line], color="black")

        """
        the vertical position of the node should be the midpoint of the
        vertical line connecting the descendants
        """
        y = ((top_vert_line - bottom_vert_line) / 2) + bottom_vert_line
    else:  # this is a tip node
        """
        if the node has no descendants, figure out the vertical position as the
        midpoint of the vertical bounds
        """
        y = (maxy - miny)/2 + miny
        if draw_labels:  # if desired, label the node
            faxes.annotate(tree.name, (minx + x + 5, y - 5))

    # draw the horizontal line connecting the node to its ancestor
    faxes.plot([minx, minx + x], [y, y], color="black")

    # add branch lengths
    if draw_branch_lengths:
        pass
        # not enabled

    return y


def chart_phylogeny(root) -> FigureCanvasQTAgg:
    # set up drawing space
    figure_canvas = FigureCanvasQTAgg(Figure(figsize=(8, 6)))
    faxes = figure_canvas.figure.subplots()
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.spines["bottom"].set_visible(False)
    faxes.spines["left"].set_visible(False)
    faxes.get_xaxis().set_visible(False)
    faxes.get_yaxis().set_visible(False)

    xwidth = 1000
    yheight = 1000
    maxbranch = root.max_node_tip_length()
    scale = (xwidth - 100) / maxbranch
    draw_tree(faxes, root, 0, xwidth, 0, yheight, scale, True, False)
    faxes.set_xlim(0, xwidth+100)
    figure_canvas.figure.tight_layout()

    return figure_canvas


def chart_scatter(x_data, y_data, x_label: str = "x", y_label: str = "y") -> ChartData:
    chart_data = ChartData("scatter plot")
    chart_data.caption.x_label = x_label
    chart_data.caption.y_label = y_label
    chart_data.x_label = x_label
    chart_data.y_label = y_label
    chart_data.add_scatter(get_text("Point Data"), x_data, y_data)

    return chart_data


def chart_trim_fill_plot(effect_label, data, n, original_mean, new_mean) -> ChartData:
    chart_data = ChartData("trim and fill")
    chart_data.caption.e_label = effect_label
    chart_data.x_label = effect_label
    chart_data.y_label = "{} (1/SE)".format(get_text("Precision"))

    # plot original points
    x_data = data[:n, 0]
    y_data = numpy.reciprocal(numpy.sqrt(data[:n, 2]))
    chart_data.caption.original_scatter = chart_data.add_scatter(get_text("Original Data"), x_data, y_data,
                                                                 color="black", edgecolors="black")
    y_min = numpy.min(y_data)
    y_max = numpy.max(y_data)

    # plot inferred points
    x_data = data[n:, 0]
    y_data = numpy.reciprocal(numpy.sqrt(data[n:, 2]))
    chart_data.caption.inferred_scatter = chart_data.add_scatter(get_text("Inferred Data"), x_data, y_data,
                                                                 edgecolors="red", color="none")

    # draw original and new mean
    chart_data.caption.original_mean = chart_data.add_line(get_text("Original Mean"), original_mean, y_min,
                                                           original_mean, y_max, color="silver", linestyle="dashed",
                                                           zorder=1)
    chart_data.caption.inferred_mean = chart_data.add_line(get_text("Inferred Mean"), new_mean, y_min, new_mean, y_max,
                                                           color="red", linestyle="dashed", zorder=1)

    return chart_data


def chart_funnel_plot(x_data, y_data, mean_e, x_label: str = "x", y_label: str = "sample size",
                      do_pseudo: bool = False, do_contour: bool = False, do_power: False = False) -> ChartData:
    chart_data = ChartData("funnel plot")
    chart_data.caption.x_label = x_label
    chart_data.caption.y_label = y_label
    chart_data.x_label = x_label
    chart_data.y_label = y_label
    chart_data.add_scatter(get_text("Point Data"), x_data, y_data, zorder=10)

    y_min = numpy.min(y_data)
    y_max = numpy.max(y_data)

    if y_label in ("standard error", "variance"):
        y_min = min(y_min, 0.001)
    else:
        y_min = y_min*0.85
    y_max = y_max*1.15

    x_min = numpy.min(x_data)
    x_max = numpy.max(x_data)
    chart_data.caption.mean_effect = chart_data.add_line(get_text("Mean Effect Size"), mean_e, y_min, mean_e, y_max,
                                                         color="silver", linestyle="dotted", zorder=5)
    if y_label in ("standard error", "variance"):
        chart_data.invert_y = True

    if (y_label != "sample size") and (do_pseudo or do_contour or do_power):
        curve_y = numpy.linspace(y_min, y_max, 50)  # 50 points for a nice curve
        if y_label == "standard error":
            sey = curve_y
        elif y_label == "precision":
            sey = 1/curve_y
        elif y_label == "variance":
            sey = numpy.sqrt(curve_y)
        else:
            sey = 1/numpy.sqrt(curve_y)

        if do_pseudo:
            curve_x_min, curve_x_max = scipy.stats.norm.interval(confidence=0.95, loc=mean_e, scale=sey)
            chart_data.caption.pseudo_ci = chart_data.add_multi_line(get_text("Pseudo-Confidence Limits"),
                                                                     curve_x_min, curve_y, linestyle="dashed",
                                                                     color="silver", zorder=3)
            pseudo_upper = chart_data.add_multi_line("", curve_x_max, curve_y, linestyle="dashed", color="silver",
                                                     zorder=3)
            chart_data.caption.pseudo_ci.link_style(pseudo_upper)
            x_min = min(numpy.min(curve_x_min), x_min)
            x_max = max(numpy.max(curve_x_max), x_max)

        if do_contour:
            curve_99_min, curve_99_max = scipy.stats.norm.interval(confidence=0.99, loc=0, scale=sey)
            curve_95_min, curve_95_max = scipy.stats.norm.interval(confidence=0.95, loc=0, scale=sey)
            curve_90_min, curve_90_max = scipy.stats.norm.interval(confidence=0.90, loc=0, scale=sey)
            x_min = min(numpy.min(curve_99_min), x_min)
            x_max = max(numpy.max(curve_99_max), x_max)
            chart_data.caption.zone99 = chart_data.add_fill_area_x("P <0.01% zone", x_min, curve_99_min, curve_y,
                                                                   color="#eeeeee", zorder=1)
            up_fill = chart_data.add_fill_area_x("", x_max, curve_99_max, curve_y, color="#eeeeee", zorder=1)
            chart_data.caption.zone99.link_style(up_fill)

            chart_data.caption.zone95 = chart_data.add_fill_area_x("P 0.01-0.05% zone", curve_99_min, curve_95_min,
                                                                   curve_y, color="#cccccc", zorder=1)
            up_fill = chart_data.add_fill_area_x("", curve_99_max, curve_95_max, curve_y, color="#cccccc", zorder=1)
            chart_data.caption.zone95.link_style(up_fill)

            chart_data.caption.zone90 = chart_data.add_fill_area_x("p 0.05-0.1% zone", curve_95_min, curve_90_min,
                                                                   curve_y, color="#a3a3a3", zorder=1)
            up_fill = chart_data.add_fill_area_x("", curve_95_max, curve_90_max, curve_y, color="#a3a3a3", zorder=1)
            chart_data.caption.zone90.link_style(up_fill)

        if do_power:
            z = scipy.stats.norm.ppf(0.975)
            power = 100*(1 - scipy.stats.norm.cdf(z - mean_e/sey) + scipy.stats.norm.cdf(-z - mean_e/sey))
            x = [x_min, x_max]
            xc, yc = numpy.meshgrid(x, curve_y)
            zc = numpy.array([power for _ in x]).transpose()
            chart_data.caption.colorgrid = chart_data.add_color_grid(get_text("Power Color Scheme"), xc, yc, zc,
                                                                     colormap="RdYlGn", grid_label=get_text("Power"))

    return chart_data


def chart_stnd_regression(x_name, y_name, x_data, y_data, slope, intercept, model, y_marker=None) -> ChartData:
    x_min = min(0, numpy.min(x_data))
    x_max = max(0, numpy.max(x_data))
    chart_data = ChartData("standard regression")
    chart_data.caption.y_label = y_name
    chart_data.caption.x_label = x_name
    chart_data.caption.model = model

    add_regression_to_chart(x_name, y_name, x_data, y_data, slope, intercept, x_min, x_max, chart_data)

    if y_marker is not None:
        chart_data.add_line(get_text("Line of No Effect"), x_min, y_marker, x_max, y_marker, color="silver",
                            linestyle="dotted", zorder=1)

    return chart_data


def find_color_name(color: str) -> str:
    """
    Given a color as a hex string, e.g., #0123A5, find the closest named color from a color name space
    and return that name
    """
    if color_name_space == "X11/CSS4":
        color_names = CSS4_COLORS
    else:
        color_names = XKCD_COLORS
    names = list(color_names)
    dist = 10000
    match = "None"
    r, g, b = hex2color(color)
    for n in names:
        rx, gx, bx = hex2color(color_names[n])
        # Squared Euclidean distance in RGB space should be good enough
        #  Squared is more computationally efficient than non-squared, as we skip calculating the square-root
        d = (rx-r)**2 + (gx-g)**2 + (bx-b)**2
        if d < dist:
            match = n
            dist = d
    if color_name_space == "xkcd":
        return match[5:]
    return match
