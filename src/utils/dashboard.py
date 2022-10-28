import collections
import uuid

class plot:

    """Class to store a plot object"""

    def __init__(self, title = str(uuid.uuid1())):

        self.title = title
        self.labels = []
        self.xvals = []
        self.yvals = []
        self.colors = []
        self.drawstyle = []
        self.linewidth = []
        self.logx = False
        self.logy = False
        self.xaxis_title = ""
        self.yaxis_title = ""
        self.doubleyaxis = False
        self.doubleyaxis_title = None
        self.doubleyaxis_graphs = []
        self.showlegend = True
        self.cleaning = False

    def __str__(self):
        return "plot: " + str(vars(self))

    def __add__(self, other):
        self.labels += other.labels
        self.xvals += other.xvals
        self.yvals += other.yvals
        self.colors += other.colors
        self.drawstyle += other.drawstyle
        self.linewidth += other.linewidth
        self.doubleyaxis_graphs += other.doubleyaxis_graphs
        self.xaxis_title = other.xaxis_title
        self.yaxis_title = other.yaxis_title
        self.doubleyaxis_title = other.doubleyaxis_title
        self.cleaning = other.cleaning
        self.title = other.title
        self.logy = other.logy
        return self

    def add_graph(self, label, xvals, yvals, color="black", drawstyle=1, linewidth=1):
        self.labels.append(label)
        self.xvals.append(xvals)
        self.yvals.append(yvals)
        self.colors.append(color)
        self.drawstyle.append(drawstyle)
        self.linewidth.append(linewidth)

    def get_graph(self, label):
        if label in self.labels:
            try:
                num = self.labels.index(label)
                output = {"xvals": self.xvals[num], "yvals": self.yvals[num], "colors": self.colors[num], "drawstyle": self.drawstyle[num], "xaxis_title": self.xaxis_title, "yaxis_title": self.yaxis_title}
                if not self.doubleyaxis:
                    return output
                else:
                    output["doubleyaxis_graphs"] = self.doubleyaxis_graphs[num]
                    return output
            except:
                return {"xvals": [], "yvals": [], "colors": "", "drawstyle": "", "xaxis_title": "", "yaxis_title": ""}

    def del_graph(self, label):
        if label in self.labels:
            num = self.labels.index(label)
            del(self.labels[num])
            del(self.xvals[num])
            del(self.yvals[num])
            del(self.colors[num])
            del(self.drawstyle[num])
            del(self.linewidth[num])


class dashboard:

    """Class to store a collection of plots"""

    def __init__(self):

        self.title = ""
        self.plots = collections.OrderedDict()
        self.layout = []
        self.row_height = 400
        self.max_plots_per_row = 3
        self.use_full_width = True
        self.global_range = False

    def __str__(self):
        return "dashboard: " + str(vars(self))

    def __add__(self, other):
        for label in other.plots:
            self.add_plot(label, other.plots[label])
        return self

    def add_plot(self, label, plot):
        self.plots[label] = plot

        # add to layout:
        if len(self.layout) == 0:
            # add first plot in first row
            self.layout.append([label])
            return

        if len(self.layout[-1]) < self.max_plots_per_row:
            # add plot to current row:
            self.layout[-1].append(label)
        else:
            # begin new row:
            self.layout.append([label])

    def get_plot(self, label):
        return self.plots[label]
