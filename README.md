## SquiggleFilter: An Accelerator for Portable Virus Detection

### Software Evaluation

#### System Requirements

Ubuntu 18 is recommended for ease of installation, and at least 10GB RAM.

#### Instructions

First, install the required packages and clone the repository:
```bash                                                                         
# install basic required packages
sudo apt update && sudo apt install git curl python3.6 python3-pip python3-dev jupyter

# clone SquiggleFilter repository
git clone https://github.com/TimD1/SquiggleFilter && cd SquiggleFilter
``` 

All remaining setup is handled by the `setup.sh` script, which will install the command-line AWS S3 tool, download the SARS-CoV-2 and human datasets, and create a Jupyter Notebook environment with all required dependencies:
```bash                                                                         
chmod +x setup.sh && ./setup.sh
``` 

Once the dataset downloads complete, run the main Jupyter Notebook `sdtw_analysis.ipynb`:
```bash                                                                         
jupyter notebook sdtw_analysis.ipynb
``` 

If the notebook does not automatically open in a browser, navigate in any browser to `http://localhost:8888/notebooks/sdtw_analysis.ipynb`. From there, ensure that the `sf-venv3` kernel is selected, and choose `Kernel -> Restart and Run All` from the Jupyter Notebook menu.

This pipeline will run our custom software sDTW implementation (`sdtw()`, in cell 13 (i cell numberings labeled after being run)) on 1000 random human and viral reads from the selected datasets. Figures 11 and 17a from our paper are regenerated, showing the human and virus alignment cost distributions and classification accuracies, respectively.

Next, our Read Until runtime model is provided (`Reads()`, `Flowcell()`, `Classifier()`, and `Run()`, in cell 23). This estimates and plots expected Read Until runtime (Figures 17b/c) based on statistics measured after running our sDTW algorithm on the random subsample of reads.

Lastly, we provide the scripts used for generating multiple figures from our paper (Figures 2, 5, 10, 16a, 16b, 18, 19, and 21).

### Hardware Evaluation

