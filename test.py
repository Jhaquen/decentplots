from decentplots import *

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