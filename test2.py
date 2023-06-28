import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

testdata = pd.DataFrame.from_dict({
    f"t{n}": np.random.randint(-100,100,size=100) for n in range(6)
})

fig = plt.figure()
ax = fig.add_subplot(111)
box = ax.boxplot(testdata)

ax.set_ylabel("test")

plt.show()