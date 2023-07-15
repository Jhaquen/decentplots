import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MultipleLocator
import matplotlib.lines as mlines

class Boxplot:

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

    def __init__(self,data,ax,**kwargs):
        self.kwargs = kwargs
        self.ax = ax
        self.setKwargDefaults()
        self.data = self.setDataColumns(data)
        self.calcStats()
        self.boxXPosDict,self.boxXPos = self.calcBoxXPos()
        self.artist = ax.boxplot(
            [vals.dropna() for _, vals in self.data.items()],
            patch_artist=True,widths=[self.kwargs["boxSize"] for _ in self.data.columns],positions=self.boxXPos
        )
        self.boxMap = self.mapBoxesToData()
        if "compare" in self.kwargs:
            self.drawComparisonIndicators()
        self.stylePlot()
    
    def setKwargDefaults(self):
        self.kwargs.setdefault("medianColor","black")
        self.kwargs.setdefault("whiskerSize",0.7)
        self.kwargs.setdefault("flierSize",2)
        self.kwargs.setdefault("flierColor","black")
        self.kwargs.setdefault("boxLineWidth",0.7)
        self.kwargs.setdefault("boxSize",0.2)
        self.kwargs.setdefault("title","default")
        self.kwargs.setdefault("titleY",1)
        self.kwargs.setdefault("titleFontsize",10)
        self.kwargs.setdefault("yLabel","default")
        self.kwargs.setdefault("xLabel","default")
        self.kwargs.setdefault("axesFontsize",8)
        self.kwargs.setdefault("grid",True)
        self.kwargs.setdefault("legendMarkersize",5)
        self.kwargs.setdefault("legendFontsize",10)
        self.kwargs.setdefault("tickFontsize",6)
    
    ##
    # Set displayed data and calculate box positions
    ######
    
    def setDataColumns(self,data):
        if type(data) == dict: data = pd.DataFrame.from_dict(data)
        if "columns" in self.kwargs and "groups" in self.kwargs:
            print("Warning: Using groups and columns is redundat")
            return data[[j for i in self.kwargs["groups"].values() for j in i]]
        elif "groups" in self.kwargs:
            return data[[j for i in self.kwargs["groups"].values() for j in i]]
        elif "columns" in self.kwargs: 
            return data[self.kwargs["columns"]]
        else: 
            return data
        

    def calcBoxXPos(self):
        if "groups" not in self.kwargs:
            return  None,[i for i in range(self.data.shape[1])]
        else:
            # distance between groups should always be the same!
            # here it gets larger when groups get larger
            # also should be settable by kwargs?
            # Maybe thats not the case but now the ticks are at the wrong pos
            posdict = {}
            ingroupdistance = 0.3; groupDistance = 1
            for groupnumber,(group,col) in enumerate(self.kwargs["groups"].items()):
                groupCenterX = (groupnumber + ((len(col)-1)*groupnumber) + ((len(col)-1) / 2))*groupDistance
                posdict[groupCenterX] = [
                    groupCenterX + ((itemnumber+groupnumber - groupCenterX)*ingroupdistance)
                    for itemnumber,_ in enumerate(col)
                ]
            return posdict,[v for key,val in posdict.items() for v in val]
    
    def mapBoxesToData(self):
        return { item:box for box,item in zip(self.artist["boxes"],self.data) } 

    ##
    # Statistics
    #####

    def calcStats(self):
        self.simpleStats = self.calcSimpleStats()
        self.dataRange, self.dataMin, self.dataMax = self.calcDataRange()

    def calcDataRange(self):
        min = np.min(list(self.data.min()))
        max = np.max(list(self.data.max()))
        return max-min, min, max

    def calcSimpleStats(self):
        stats = pd.DataFrame({
            col:[
                np.nanmean(self.data[col]),
                np.nanmedian(self.data[col]),
                np.nanquantile(self.data[col],0.75),
                np.nanquantile(self.data[col],0.25)
            ] for col in self.data.columns
        },index=["mean","median","75quant","25quant"])
        return stats
    
    ##
    # Drawing Statistics
    #####

    def drawComparisonIndicators(self):
        vLinePos = self.calcVLinePos()
        heightMaps,heightMapSingle, vLinePos = self.calcConnectionHeight(vLinePos)
        for dataset,vline in vLinePos.items():
                # would be better to not do this with ax.plot()
                if dataset in list(heightMapSingle.keys()):
                    self.ax.plot(
                        [vline["x"],vline["x"]],
                        [vline["y"],heightMapSingle[dataset]],
                        c="black",lw=1
                    )
        for comparison,heightMap in zip(self.kwargs["compare"], heightMaps):
            self.ax.plot(
                [vLinePos[heightMap["start"]]["x"],vLinePos[heightMap["end"]]["x"]],
                [heightMap["height"],heightMap["height"]],
                c="black",lw=1
            )

    def calcVLinePos(self):
        # if there are fliers this should contain flier hights not whisker heights
        whiskerPos = [whisker.get_path().get_extents() for i,whisker in enumerate(self.artist["whiskers"]) if i%2]
        heightOffset = self.dataRange / 10
        verticalLinePosAll = {label:[pos.x1,pos.y1 + heightOffset] for pos,label in zip(whiskerPos,self.data.columns)}
        vLinePos = {}
        for dataset, pos in verticalLinePosAll.items():
            if dataset in [item for groups in self.kwargs["compare"] for item in groups]:
                vLinePos[dataset]  = {"x":pos[0],"y":pos[1]}
        return vLinePos

    def calcConnectionHeight(self, verticalLines):
        heightsComp = []
        heightsSingle = {}
        order = list(self.data.columns)
        compared = []
        heightOffset = self.dataRange / 10
        baseheight = self.dataMax + self.dataRange / 7
        for comparison in self.kwargs["compare"]:
            if comparison[0] not in compared and comparison[1] not in compared:
                heightsComp.append({"start":comparison[0],"end":comparison[1],"height":baseheight})
                heightsSingle[comparison[0]] = baseheight
                heightsSingle[comparison[1]] = baseheight
            else:
                nOccurences = compared.count(comparison[0]) if compared.count(comparison[0]) > compared.count(comparison[1]) else compared.count(comparison[1]) 
                heightsComp.append({"start":comparison[0],"end":comparison[1],"height":baseheight + heightOffset*nOccurences})
                if comparison[0] in compared and comparison[1] in compared:
                    verticalLines[comparison[0]+f"__{nOccurences}"] = {"y":baseheight - heightOffset/2 + heightOffset*nOccurences, "x":verticalLines[comparison[0]]["x"]}
                    verticalLines[comparison[1]+f"__{nOccurences}"] = {"y":baseheight - heightOffset/2 + heightOffset*nOccurences, "x":verticalLines[comparison[1]]["x"]}
                    heightsSingle[comparison[0]+f"__{nOccurences}"] = baseheight + heightOffset*nOccurences
                    heightsSingle[comparison[1]+f"__{nOccurences}"] = baseheight + heightOffset*nOccurences
                elif comparison[0] in compared:
                    verticalLines[comparison[0]+f"__{nOccurences}"] = {"y":baseheight - heightOffset/2 + heightOffset*nOccurences, "x":verticalLines[comparison[0]]["x"]}
                    heightsSingle[comparison[0]+f"__{nOccurences}"] = baseheight + heightOffset*nOccurences
                    heightsSingle[comparison[1]] = baseheight + heightOffset*nOccurences
                elif comparison[0] in compared:
                    verticalLines[comparison[1]+f"__{nOccurences}"] = {"y":baseheight - heightOffset/2 + heightOffset*nOccurences, "x":verticalLines[comparison[1]]["x"]}
                    heightsSingle[comparison[1]+f"__{nOccurences}"] = baseheight +  heightOffset*nOccurences
                    heightsSingle[comparison[0]] = baseheight + heightOffset*nOccurences
            start = False; first = True
            for item in order:
                if item == comparison[0] or item == comparison[1] and first==True: start = True
                if start == True and (item == comparison[0] or item == comparison[1]) and first == False: break
                if start == True: compared.append(item); first = False
        return heightsComp, heightsSingle, verticalLines

    def drawStars(self):
        pass

    ##
    # Styling
    #####

    def stylePlot(self):
        self.drawXTickLabels()
        self.styleTickLabels()
        self.styleIndicators()
        self.styleBoxes()
        self.styleSpines()
        self.drawGrid()
        self.drawLegend()
        self.drawLabels()

    def drawXTickLabels(self):
        if "groups" not in self.kwargs:
            self.ax.set_xticklabels(self.data.columns)
        else:
            # for some reason this does not match the center. Center propably not where it should be
            self.ax.set_xticks([xpos for xpos in self.boxXPosDict])
            self.ax.set_xticklabels([grouplabel for grouplabel in self.kwargs["groups"]])
    
    def styleTickLabels(self):
        self.ax.set_xticklabels(self.ax.get_xticklabels(), fontsize=self.kwargs["tickFontsize"])
        self.ax.set_yticklabels(self.ax.get_yticklabels(), fontsize=self.kwargs["tickFontsize"])

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
    
    def styleSpines(self):
        self.ax.spines["right"].set_color("none"); 
        self.ax.spines["top"].set_color("none")
        self.ax.spines["left"].set_position(("outward",15))
        self.ax.spines["bottom"].set_position(("outward",15))
        if "ylim" in self.kwargs: self.ax.set_ylim(*self.kwargs["ylim"])
        if "xlim" in self.kwargs: self.ax.set_ylim(*self.kwargs["xlim"])
        self.ax.spines["left"].set_bounds(self.ax.get_yticks()[0],self.ax.get_yticks()[-1])
        self.ax.set_yticks(self.ax.get_yticks())
        self.ax.spines["bottom"].set_bounds(self.ax.get_xticks()[0],self.ax.get_xticks()[-1])
    
    def drawLabels(self):
        self.ax.set_title(self.kwargs["title"],fontsize=self.kwargs["titleFontsize"],y=self.kwargs["titleY"])
        self.ax.set_ylabel(self.kwargs["yLabel"],fontsize=self.kwargs["axesFontsize"])
        self.ax.set_xlabel(self.kwargs["xLabel"],fontsize=self.kwargs["axesFontsize"])
    
    def drawGrid(self):
        # Draw minor ticks always at a position that makes sense (like in steps of 5 or smth)
        self.ax.yaxis.set_minor_locator(MultipleLocator(abs(self.ax.get_yticks()[1]-self.ax.get_yticks()[0])/4))
        self.ax.grid(self.kwargs["grid"],alpha=0.5,ls=":",which="both",axis="y")
    
    def drawLegend(self):
        if type(self.kwargs["legend"]) == dict:
            self.ax.legend(
                handles=[
                    mlines.Line2D([],[],color=color,label=label,marker="o",lw=0,markersize=self.kwargs["legendMarkersize"])
                    for label,color in self.kwargs["legend"].items()
                ],
                loc="lower right",frameon=False, fontsize=self.kwargs["legendFontsize"]
            )
