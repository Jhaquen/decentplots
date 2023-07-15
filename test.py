import matplotlib.pyplot as plt
import sciplots02 as box
import numpy as np

testdata = {
    f"t{n}": np.random.randint(-100,100,size=100) for n in range(20)
}

fig = plt.figure(dpi=150,figsize=(8,5))
ax = fig.add_subplot()
plot = box.Boxplot(
    testdata,ax,
    groups={"test1":["t2","t3","t4"],"test3":["t10","t11","t12"],"test2":["t5","t7","t8"]},
    color=[(.8,.1,.5,.4),(.2,.6,.2,.4),(.1,.5,.5,.4)],
    legend={"bla":(0,0,0)},
    compare=[["t2","t3"],["t10","t12"],["t5","t7"],["t5","t8"],["t3","t7"]]
)
plt.show()