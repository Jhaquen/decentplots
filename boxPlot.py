from statsIndicatorConnection import Indicator
from distPlot import *

class Boxplot(DistributionPlot):

    # Kwargs ######################
    # columns -> list: list of columns of dataframe or keys of dict to include
    # groups -> dict {grouplabel:[columns]}: groups data visually 
    # color-> list / dict {grouplabel:color} / {grouplabel:[color1, color2, ..]}
    # ylim / xlim -> [lower, upper]
    # legend -> bool / dict {label:color}
    # etc:
    # medianColor -> str
    # whiskerSize -> int
    # flierSize -> int 
    # flierColor -> black

    # ToDo: 
    # Finish styling -> colors and etc styling
    # Statistics
    # Statistics styling

    boxplotKwargDefaults = {
        "medianColor":"black",
        "whiskerSize":0.7,
        "flierSize":2,
        "flierColor":"black",
        "boxLineWidth":0.7,
        "boxSize":0.2,
        "ingroupDistance": 0.3,
        "groupDistance": 0.7
    }

    def __init__(self,data,ax,**kwargs):
        super().kwargDefaults.update(self.boxplotKwargDefaults)
        super().__init__(data,ax,**kwargs)
        self.artist = ax.boxplot(
            [vals.dropna() for _, vals in self.data.items()],
            patch_artist=True,widths=[self.kwargs["boxSize"] for _ in self.data.columns],positions=self.artistXPos
        )
        super().compare()
        super().stylePlot()
        self.styleBoxPlot()

    ##
    # Styling
    #####

    def styleBoxPlot(self):
        self.styleIndicators()
        self.styleBoxes()

    def styleIndicators(self):
        for median in self.artist["medians"]:
            median.set_color(self.kwargs["medianColor"])
        for flier in self.artist["fliers"]:
            flier.set_markersize(self.kwargs["flierSize"])
            flier.set_color(self.kwargs["flierColor"])
        for whisker in self.artist["whiskers"]:
            whisker.set_linewidth(self.kwargs["whiskerSize"])
    
    def styleBoxes(self):
        for box in self.artist["boxes"]:
            box.set_linewidth(self.kwargs["boxLineWidth"])
        if "color" in self.kwargs: self.colorBoxes()
    
    def colorBoxes(self):
        if "groups" not in self.kwargs: self.colorBoxes_NoGroups()
        else:
            if type(self.kwargs["color"]) == list: self.colorBoxes_DiffColorInGroup_List()
            elif type(list(self.kwargs["color"].values())[0]) == tuple: self.colorBoxes_OneColorPerGroup_Dict()
            elif type(list(self.kwargs["color"])) == dict: self.colorBoxes_DiffColorInGroup_Dict()
            else: raise Exception
            
    def colorBoxes_NoGroups(self):
        i = 0
        while len(self.artist["boxes"]) > len(self.kwargs["color"]):
            self.kwargs["color"].append(self.kwargs["color"][i])
            i += 1
        for col,box in zip(self.kwargs["color"],self.artist["boxes"]):
            box.set_facecolor(col)

    def colorBoxes_DiffColorInGroup_List(self):
        if len(list(self.kwargs["groups"].values())[0]) != len(list(self.kwargs["color"])): 
            raise Exception("Length of list must be the same length as items per group")
        else:
            colors = [col for _ in self.kwargs["groups"] for col in self.kwargs["color"]]
            for box,color in zip(self.artist["boxes"],colors):
                box.set_facecolor(color)
    
    def colorBoxes_OneColorPerGroup_Dict(self):
        colors = []
        for group in self.kwargs["groups"]:
            if group not in self.kwargs["color"]:
                colors += [(.6,.6,.6) for _ in self.kwargs["groups"][group]]
            else:
                colors += [self.kwargs["color"][group] for _ in self.kwargs["groups"][group]]
        for box,color in zip(self.artist["boxes"],colors):
            box.set_facecolor(color)

    def colorBoxes_DiffColorInGroup_Dict(self):
        # This should color groups based on label with a list as value of dict, diffrent color in group
        raise Exception
    