import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress

class decentplot:

    def __init__(self,ax,data,kwargs):

        self.datatype = self.getDataType(data)
        if self.datatype == "dict": labels = [label for x,y,label in self.get2Ddata(data,self.datatype)]

        # kwarg handeling
        # defaults:
        # c: black
        # lw: 0.8
        # ls: "-"
        # ms: 3
        kwargs_keys = list(kwargs.keys())
        # c / color
        if "c" in kwargs_keys: self.color = kwargs["c"] if self.datatype == "2D" else {label:kwargs["c"][i] for i,label in enumerate(labels)}
        elif "color" in kwargs_keys: self.color = kwargs["color"] if self.datatype == "2D" else {label:kwargs["color"][i] for i,label in enumerate(labels)}
        else: self.color = "black" if self.datatype == "2D" else ["black" for _ in range(1000)]
        # etc
        self.legend = None if "legend" not in kwargs_keys else kwargs["legend"]
        self.lw = 0.8 if "lw" not in kwargs_keys else kwargs["lw"]
        self.ls = "-" if "ls" not in kwargs_keys else kwargs["ls"]
        self.ms = 1 if "ms" not in kwargs_keys else kwargs["ms"]
 
    @classmethod
    def getKwargs(self, typ, **kwargs):
        # Passing base values for kwargs
        if typ=="plot":
            if kwargs["label"]:
                return {
                "c":self.color[kwargs["label"]],
                "lw":self.lw,
                "ls":self.ls
            }
            else:
                return {
                    "c":self.color,
                    "lw":self.lw,
                    "ls":self.ls
                }
        elif typ=="scatter":
            return {
                "ms":self.ms,
                "ls":"",
                "marker":"o"
            }

    @classmethod
    def TwoDPlot(self, data, func, typ):
        if self.datatype == "2D": 
            x_data, y_data = self.get2Ddata(data,self.datatype)
            actor = func(x_data, y_data, **self.getKwargs(typ))
        elif self.datatype == "dict":
            for x_data, y_data, label in self.get2Ddata(data,self.datatype):
                actor = func(x_data, y_data, **self.getKwargs(typ,label=label))
                actor.set_label(label)
        return actor

    @classmethod
    def scatter(self, ax, data, **kwargs):
        #########################################
        #   data: {"x":[],"y":[]} or {"y":[],data1/"data1":[],..}   
        #
        #   kwargs
        #
        #   color: 
        #   ms: float
        self.__init__(self, ax, data, kwargs)
        self.TwoDPlot(data, ax.errorbar, "scatter")

    @classmethod
    def line(self, ax, data, **kwargs):
        #########################################
        #   data: {"x":[],"y":[]} or {"y":[],data1/"data1":[],..}   
        #   
        #   kwargs      
        # 
        #   color: str or [str,..] or {dataset:str,..}
        #   legend: str
        self.__init__(self, ax, data, kwargs)
        line = self.TwoDPlot(data, ax.errorbar, "plot")

        ####################
        #     Styling      #
        ####################

        # Lines
        #if datatype == "2Ddata": c = self.color

        # Axes
        ax.spines.top.set_visible(False); ax.spines.right.set_visible(False)
        ax.minorticks_on()
        ax.grid(True, "both", lw=0.7, ls="--", alpha=0.7)
        ax.set_xlim(*self.getDataBoundaries(data,self.datatype))

        # etc
        if type(self.legend)==str and len(self.legend)>0: ax.legend(self.legend)
        elif self.legend: ax.legend()
        
        return line
    
    @classmethod
    def fit(self, ax, data, fit_func, **kwargs):
        #########################################
        #   data: {"x":[],"y":[]} or {"y":[],data1/"data1":[],..}   
        #   
        #   kwargs      
        # 
        #   color: str or [str,..] or {dataset:str,..}
        self.__init__(self, ax, data, kwargs)
        scatter = self.TwoDPlot(data, ax.errorbar, "scatter")
        fit_res = [
            {
                l:res for res,l in zip(curve_fit(fit_func, x_data, y_data),["popt","pcov"])
            } for x_data, y_data, label in self.get2Ddata(data, self.datatype)
        ]
        for res in fit_res:
            ax.plot(
                np.linspace(*self.getDataBoundaries(data,self.datatype),1000),
                fit_func(np.linspace(*self.getDataBoundaries(data,self.datatype),1000),*res["popt"])
            )
    
    @staticmethod
    def getDataType(data):
        # define how to treat data
        # either dict or df, or dict with {x:[], y:[]}
        if type(data) == dict:
            keys = list(data.keys())
            if "x" in keys and "y" in keys:
                if type(data[keys[0]] == list):
                    return "2D"
            else:
                if type(data[keys[0]] == list):
                    return "dict"
                else:
                    raise Exception
    
    @staticmethod
    def get2Ddata(data,datatype):
        if datatype == "2D":
            x_data = data["x"]; y_data = data["y"]
            return x_data, y_data, "y"
        elif datatype == "dict":
            x_data = data["x"]
            data_keys = list(data.keys())
            data_keys.remove("x")
            data_len = len(data_keys)
            i = 0
            while i<data_len:
                y_data = data[data_keys[i]]
                label = data_keys[i]
                yield x_data, y_data, label
                i += 1
    
    @staticmethod
    def getDataBoundaries(data,datatype):
        if datatype == "2D":
            return np.min(data["x"]), np.max(data["y"])
        elif datatype == "dict":
            maxima = [np.max(xdata) for xdata,_,_ in decentplot.get2Ddata(data,datatype)]
            minima = [np.min(xdata) for xdata,_,_ in decentplot.get2Ddata(data,datatype)]
            return np.min(minima),np.max(maxima)

if __name__ == "__main__":

    test_dict = {
        "x":np.linspace(200,600,999),
        1:[np.random.randint(0,1000*i) for i in range(1,1000)]
    }

    fig = plt.figure(figsize=(7,5))
    ax = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)

    decentplot.line(
        ax,
        test_dict,
        legend=True
    )

    decentplot.scatter(
        ax2,
        test_dict,
        ms=1
    )

    decentplot.fit(
        ax3,
        test_dict,
        lambda x, m, b: b + m*x
    )
    plt.tight_layout()
    plt.show()
