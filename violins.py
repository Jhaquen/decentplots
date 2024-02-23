import numpy as np
import matplotlib.patches as ptc
from scipy.stats import gaussian_kde
from scipy.signal import savgol_filter

class ViolinHalf:

    def __init__(self,y,x,ax):
        self.ax = ax
        self.x = x; self.y = y

    def drawDensity(self,direction,size,**kwargs):
        kwargs.setdefault("color",None)
        density = gaussian_kde(self.y,bw_method=0.1)
        density_y = np.linspace(np.min(self.y)-15,np.max(self.y)+15,100)
        density_x = density(density_y)
        if direction == "l":
            for i,x_val in enumerate(density_x):
                density_x[i] = self.x - (x_val*size*10)
        else:
            for i,x_val in enumerate(density_x):
                density_x[i] = self.x + (x_val*size*10)
        density_x[0] = self.x; density_x[-1] = self.x
        self.ax.plot(density_x,density_y,c="black",lw=1)
        if kwargs["color"] is not None:
            patch = self.ax.fill_between(density_x,density_y,[1 for _ in range(100)],alpha=1,color=kwargs["color"])
        else:
            patch = self.ax.fill_between(density_x,density_y,[1 for _ in range(100)],alpha=1)
        return patch
    
    def drawIndicators(self,direction,size):
        x = self.x
        quantMarkerSize = -0.03*size if direction == "l" else 0.03*size
        vquantMarkerSize = -0.005*size if direction == "l" else 0.005*size
        mean = np.nanmean(self.y)
        upper = np.nanquantile(self.y,.75)
        lower = np.nanquantile(self.y,.25)
        vupper = np.nanquantile(self.y,.95)
        vlower = np.nanquantile(self.y,.05)
        meanMarker = self.ax.plot([x+quantMarkerSize,x],[mean,mean],lw=1,c="white")
        quantMarker = ptc.Polygon([(x+quantMarkerSize,lower),(x+quantMarkerSize,upper),(x,upper),(x,lower)], closed=True,color="black")
        vquantMarker = ptc.Polygon([(x+vquantMarkerSize,vlower),(x+vquantMarkerSize,vupper),(x,vupper),(x,vlower)], closed=True,color="black")
        self.ax.add_patch(vquantMarker)
        self.ax.add_patch(quantMarker)

class ViolinScatter(ViolinHalf):

    def __init__(self,y,x,ax,**kwargs):
        super().__init__(y,x,ax)
        self.kwargs = kwargs
        self.kwargs.setdefault("ms",1)
        self.x_scatter = self.getXValues(y,x)
        self.drawScatter()
        self.drawDensity("l",5)
        self.drawIndicators("l",1)
        
    def getXValues(self,y,x):
        yDistForMove = (np.max(y) - np.min(y)) / 30
        new_x = []
        y = sorted(y)
        i = 1
        offsetMultiplier = 30 #higher is less
        while i<len(y):
            if y[i] - y[i-1] < yDistForMove:
                n = 1
                new_x.append(x)
                if i+n >= len(y): break
                while y[i+n] - y[i-1] < yDistForMove:
                    new_x.append(x+n/offsetMultiplier)
                    n += 1
                    if i+n >= len(y): break
                i += n
            else:
                new_x.append(x)
                i += 1
        new_x.append(1)
        for i,x in enumerate(new_x):
            new_x[i] += 0.01
        return new_x

    def drawScatter(self):
        artist = self.ax.scatter(x=self.x_scatter, y=self.y,s=self.kwargs["ms"],color="grey",alpha=0.8)

class ViolinFull(ViolinHalf):

    def __init__(self,y,x,ax):
        super().__init__(y,x,ax)
        patch = self.drawDensity("l",5)
        self.drawDensity("r",5,color=patch.get_facecolor())
        self.drawIndicators("l",.7)
        self.drawIndicators("r",.7)