from violins import *
from distPlot import *
from artistMock import *
import numpy as np

class Violinplot(DistributionPlot):

    #ingroupdistance values above 0.8 dont work, why???
    vioplotKwargDefaults = {
        "ingroupDistance": 0.8,
        "groupDistance": 4,
        "kind": "full"
    }

    def __init__(self,data,ax,**kwargs):
        super().kwargDefaults.update(self.vioplotKwargDefaults)
        super().__init__(data,ax,**kwargs)
        self.vioFunc = ViolinFull if self.kwargs["kind"] != "scatter" else ViolinScatter
        self.artist = self.drawViolins(self.data,self.artistXPos,ax)
        super().compare()
        super().stylePlot()
    
    def drawViolins(self,data,xpos,ax):
        artists = {"violins":[],"whiskers":[],"fliers":[]}
        for (_,d),x in zip(data.items(),xpos):
            vio = self.vioFunc(d,x,ax)
            # this is neccecary for statsIndicatorConnection.py to work properly
            artists["violins"].append(vio)
            artists["fliers"].append(artistMock(-np.inf,x))
            artists["whiskers"].append(artistMock(np.nanmax(d)+((np.nanmax(d)-np.nanmin(d))/10),x))
            artists["whiskers"].append(artistMock(np.nanmax(d)+((np.nanmax(d)-np.nanmin(d))/10),x))
        return artists