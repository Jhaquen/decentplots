   
from setuptools import setup, find_packages
from setuptools import find_packages, setup

VERSION = '0.0.01'
DESCRIPTION = 'Some decent plots'
LONG_DESCRIPTION = 'Some decent plots build on matplotlib'

# Setting up
setup(
    name="decentplots",
    version=VERSION,
    author="NeuralNine (Florian Dedov)",
    author_email="<mail@neuralnine.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["matplotlib","numpy","pandas","scipy"],
    keywords=['python', "plots"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)