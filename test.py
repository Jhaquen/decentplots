import matplotlib.pyplot as plt
import boxplot as box
import numpy as np

testdata = {
    f"t{n}": np.random.randint(-100,100,size=100) for n in range(20)
}

fig = plt.figure(dpi=150,figsize=(8,5))
ax = fig.add_subplot()
plot = box.Boxplot(
    testdata,ax,
    columns=[f"t{n}" for n in range(20)],
    groups={"test1":["t2","t3","t4"],"test3":["t10","t11","t12"],"test2":["t5","t7","t8"]},
    color=[(0,0,0),(.2,.2,.2),(.5,.5,.5)],
    legend={"bla":(0,0,0)}
)
print(plot.simpleStats)
plt.show()