import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as stats
from matplotlib.ticker import MultipleLocator
import matplotlib.lines as mlines
from statsIndicatorConnection import Indicator
import warnings
warnings.filterwarnings("ignore", message="FixedFormatter should only be used together with FixedLocator")

class DistributionPlot:
    # This class contains basic functions for Boxplot and Violinplot
    kwargDefaults = {
        "title":"default",
        "titleY":1,
        "titleFontsize":10,
        "yLabel":"default",
        "xLabel":"default",
        "axesFontsize":8,
        "grid":True,
        "legendMarkersize":5,
        "legendFontsize":10,
        "tickFontsize":6,
        "legend": None,
        "related": False
    }

    def __init__(self,data,ax,**kwargs):
        self.kwargs = kwargs
        self.ax = ax
        self.setKwargDefaults()
        self.data = self.setDataColumns(data)
        self.calcStats()
        self.GroupXPosMap,self.artistXPos = self.calcBoxXPos()
        self.boxMap = self.mapBoxesXToData()
        # compare() is called in child class

    def setKwargDefaults(self):
        for default in self.kwargDefaults.items():
            self.kwargs.setdefault(*default)

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
            # I belive everything is fixed but i cant remember doing it
            posdict = {}
            ingroupdistance = self.kwargs["ingroupDistance"]; groupDistance = self.kwargs["groupDistance"]
            for groupnumber,(group,col) in enumerate(self.kwargs["groups"].items()):
                groupCenterX = (groupnumber + ((len(col)-1)*groupnumber) + ((len(col)-1) / 2))*groupDistance
                posdict[groupCenterX] = [
                    groupCenterX + ((itemnumber+groupnumber - groupCenterX)*ingroupdistance)
                    for itemnumber,_ in enumerate(col)
                ]
            return {np.mean(val):val for _,val in posdict.items()},[v for _,val in posdict.items() for v in val]
    
    def mapBoxesXToData(self):
        return { item:{"index":index, "x":xpos} for (index,xpos),item in zip(enumerate(self.artistXPos),self.data)}
        
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
    
    def compare(self):
        if "compare" not in self.kwargs: return
        self.comparisons = self.kwargs["compare"]
        self.normality = self.checkNormality()
        self.varianceHomogenity = self.checkVarianceHomogenity()
        self.comparisonResults = self.compareDistributions()
        self.drawComparisonIndicators()
            
    def checkNormality(self):
        # rewrite this for performance improvements
        normality = pd.DataFrame({ col:[stats.shapiro(self.data[col]).pvalue,stats.shapiro(self.data[col]).statistic] for col in self.data.columns },index=["p-value","statistic"])
        normality = pd.concat([ normality,normality.loc[["p-value"]].applymap(lambda x: True if x>0.05 else False).set_axis(["normal(boolean)"]) ])
        return normality

    def checkVarianceHomogenity(self):
        #this could use bartlett as well. appartently levene is more rubust for non-normal distributions
        results = pd.DataFrame([],index=["p-value","statistic"])
        for comp in self.comparisons:
            levene = stats.levene(*[self.data[comp][col] for col in comp])
            results = pd.concat([ results, pd.DataFrame([levene.pvalue, levene.statistic], index=["p-value","statistic"], columns=[f"{comp[0]}-{comp[1]}"])],axis=1)
        results = pd.concat([ results, results.loc[["p-value"]].applymap(lambda x: True if x>0.05 else False).set_axis(["levene(boolean)"])])
        return results

    def compareDistributions(self):
        # this could be done more elegantly, but i dont want to. maybe some settings are nececcary down the line
        results = pd.DataFrame([],index=["p-value","statistic","significance","function"])
        for index,comp in enumerate(self.comparisons):
            if not all([norm for norm in self.normality[comp].loc["normal(boolean)"]]):
                if not self.varianceHomogenity.iloc[2,index]:
                    result, test = self.parametricTests(self.data[comp[0]], self.data[comp[1]])
                else:
                    result, test = self.nonparametricTests(self.data[comp[0]], self.data[comp[1]])
            else:
                result, test = self.nonparametricTests(self.data[comp[0]], self.data[comp[1]])
            results = pd.concat( [results, pd.DataFrame([result.pvalue, result.statistic, self.pvalueToSigStr(result.pvalue), test], index=["p-value","statistic", "significance", "function"], columns=[f"{comp[0]}-{comp[1]}"])] ,axis=1 )
        return results

    def parametricTests(self, samp1, samp2):
        if self.kwargs["related"]: return self.ttest_rel(samp1, samp2)
        else: return self.ttest_ind(samp1, samp2)

    def ttest_ind(self, samp1, samp2):
        return [stats.ttest_ind(samp1, samp2), "ttest_ind"]

    def ttest_rel(self, samp1, samp2):
        return [stats.ttest_rel(samp1,samp2), "ttest_rel"]
    
    def nonparametricTests(self, samp1, samp2):
        if self.kwargs["related"]: return self.wilcoxon_SignedRang(samp1, samp2)
        else: return self.wilcoxon_MWU(samp1, samp2)

    def wilcoxon_MWU(self, samp1, samp2):
        return [stats.mannwhitneyu(samp1, samp2), "MWU"]

    def wilcoxon_SignedRang(self, samp1, samp2):
        return [stats.wilcoxon(samp1, samp2), "wilcoxonSingedRang"]
    
    def pvalueToSigStr(self, pvalue):
        if pvalue > 0.05: return "n.s."
        elif pvalue > 0.01: return "*"
        elif pvalue > 0.001: return "**"
        else: return "***" 

    ##
    # Drawing Statistics
    #####

    def drawComparisonIndicators(self):
        statsIndicators = Indicator(self.data.shape[1],self.artist,self.dataRange)
        statsIndicators.newConnections([(self.boxMap[comparison[0]]["index"],self.boxMap[comparison[1]]["index"]) for comparison in self.kwargs["compare"]])
        statsIndicators.drawConnections(self.ax,self.artist,"black",1)
        statsIndicators.drawStars(self.comparisonResults,self.ax,self.artist,"black",7)

    ##
    # Styling
    #####

    def stylePlot(self):
        self.drawXTickLabels()
        self.styleTickLabels()
        self.styleSpines()
        self.drawGrid()
        self.drawLegend()
        self.drawLabels()
    
    def drawXTickLabels(self):
        if "groups" not in self.kwargs:
            self.ax.set_xticklabels(self.data.columns)
        else:
            # for some reason this does not match the center. Center propably not where it should be
            self.ax.set_xticks([xpos for xpos in self.GroupXPosMap])
            self.ax.set_xticklabels([grouplabel for grouplabel in self.kwargs["groups"]])
    
    def styleTickLabels(self):
        self.ax.set_xticklabels(self.ax.get_xticklabels(), fontsize=self.kwargs["tickFontsize"])
        self.ax.set_yticklabels(self.ax.get_yticklabels(), fontsize=self.kwargs["tickFontsize"])
    
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