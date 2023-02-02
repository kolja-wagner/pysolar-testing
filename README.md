# pysolar-testing
an analysis of the [pysolar](https://pysolar.readthedocs.io/en/latest/) package for the calculation of SPA. Source code for example calculations and verification of the algorithm with reference data.

The script for the presentation is available at [missing]()

- scripts: request reference data from the usno data service
- notebooks: example and validation notebooks
- data: storage directory for data files
- results: storage directory for results, in this case the figures from matplotlib.




## Clone the project
_todo_

## Create an enviromnent

A. Create from scratch:

> $ conda create --name pysolar-testing python=3.9
> $ conda activate pysolar-testing
> $ conda install pysolar numpy pandas matplotlib jupyterlab

B. Clone from template:
> $ conda env create --name pysolar-testing --file environment.yml

C. Save for reproducability:
> $ conda env export > environment.yml

 
repository structure inspired by https://goodresearch.dev/index.html