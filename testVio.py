import matplotlib.pyplot as plt
import violinPlot as vio
import numpy as np

testdata = {
    f"t{n}": np.random.randint(-100,100,size=100) for n in range(10)
}

testdata.update({
    f"t{n}": np.random.randint(-24,210,size=100) for n in range(10,20)
})

fig = plt.figure(dpi=150,figsize=(8,5))
ax = fig.add_subplot()

plot = vio.Violinplot(
    testdata,ax,
    groups={"test1":["t2","t3","t4"],"test3":["t16","t17","t18"],"test2":["t5","t7","t8"]},
    color=[(.8,.1,.5,.4),(.2,.6,.2,.4),(.1,.5,.5,.4)],
    legend={"bla":(0,0,0)},
    compare=[["t2","t3"],["t16","t18"],["t16","t17"],["t17","t18"],["t5","t7"],["t5","t8"],["t3","t7"],["t3","t17"]],
    kind="full"
)
"""
plot = vio.Violinplot(
    testdata,ax,
    columns = ["t2","t18"]
)
"""
print(plot.simpleStats)
print(plot.boxMap)
plt.show()