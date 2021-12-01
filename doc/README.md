# nrlee-nucleosynthesis
To build the paper, first create the figures.  The scripts require [python](https://www.python.org) and the [wnutils](https://wnutils.readthedocs.io) package.  Type

**./create_figures.sh**

This will take a while to download the data and make all the figures.  Then make the paper with [pdflatex](https://www.tug.org/applications/pdftex/).  Type

**./make_paper.sh**

The output will be the file *nrlee-nucleosynthesis.pdf*.

To clean up the directory, type

**./clean_paper.sh**
