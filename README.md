## SquiggleFilter: An Accelerator for Portable Virus Detection
[![DOI](https://zenodo.org/badge/308382397.svg)](https://zenodo.org/badge/latestdoi/308382397)

Please cite SquiggleFilter if you compare to/use it in your work:

>Dunn, Tim, Harisankar Sadasivan, Jack Wadden, Kush Goliya, Kuan-Yu Chen, David Blaauw, Reetuparna Das, and Satish Narayanasamy. "SquiggleFilter: An Accelerator for Portable Virus Detection." In MICRO-54: 54th Annual IEEE/ACM International Symposium on Microarchitecture, pp. 535-549. 2021.

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

This pipeline will run our custom software sDTW implementation (`sdtw()`, in cell 13 (cells are numbered after being run)) on 1000 random human and viral reads from the selected datasets. Figures 11 and 17a from our paper are regenerated, showing the human and virus alignment cost distributions and classification accuracies, respectively.

Next, our Read Until runtime model is provided (`Reads()`, `Flowcell()`, `Classifier()`, and `Run()`, in cell 23). This estimates and plots expected Read Until runtime (Figures 17b/c) based on statistics measured after running our sDTW algorithm on the random subsample of reads.

Lastly, we provide the scripts used for generating multiple figures from our paper (Figures 2, 5, 10, 16a, 16b, 18, 19, and 21).

### Hardware Evaluation

Please note that the hardware artifact submission is intended only for functional verification and not for ASIC synthesis. 
Please install Vivado 2019.1 from [this link](https://www.xilinx.com/support/documentation-navigation/design-hubs/2019-1/dh0013-vivado-installation-and-licensing-hub.html).
If Vivado does not open or crashes, please check the [Xilinx SDK requirements](https://www.xilinx.com/html_docs/xilinx2019_1/SDK_Doc/xsct/intro/xsct_system_requirements.html). We succesfully ran it on a Quadcore i-5 8th gen with 8G memory. The intention of this setup is only for functionally verifying the design and not for ASIC synthesis.


#### Loading the environment
1. Uncompress `design/verilog_v2.rar`. The project folder is compressed to avoid GitHub size limits. You can simply uncompress this, install Vivado, and run the project.

2. Open a project on Vivado under the `File` tab and load `design/verilog_v2/verilog_v2.xpr from the uncompressed folder`. This sets up the functional verification environment with the testbench as the top file.

#### Settings

1. Set the reference filename on the `reference_filename` and local query filepath on the `query_filename` in `testbench_top.sv`. Make sure to do this in all three places it appears in the file.
2. Set simulation runtime under `Tools->Settings` to 18ms.

#### Defaults & description
- `testbench_top.sv` is the top file of the testbench simulation environment.
- `warper_top.sv` is the top file of the systolic array.
- `normalizer_top.sv` is the top file of the normalizer.
- `constants.h`: the reference length can be controlled with `REF_MAX_LEN` and `QUERY_LEN` can be controlled with `QUERY_LEN`.
- This project does use integer adder, subtractor, divider and accumulator IPs from Xilinx. They are linked to the project environment.
- A smaller `QUERY` size of 100 instead of the original SARS-CoV-2 reference is used for this artifact to achieve simulation times and resource usage. However, if you wish to reconfigure, you can vary `QUERY_LEN` under `constants.vh` from 1-500 on the datasets in `design/sv_sim_datasets`.
- The BRAM and DRAM are not connected and query and reference sequences are loaded from text file.

#### Testbench

The testbench loads test vectors from a subset of our public datasets in `design/sv_sim_datasets`. Make sure to update your local path in testbench before starting simulation. It compares the output of the design in `result` to our expectation when `done` is set high : 1 for virus and 0 for human.

#### Behavioral simulation using the testbench

Go to the flow navigator on the left hand side tab and press `Run Simulation` to start the simulation. Watch the test case number and `PASSED/FAILED` displays on the tcl console for functionally verifying the design. We observe and expect all 18 testcases to pass. Additionally, the behavioral simulation may also be closely inspected by looking at the waveform. waveform.wcfg in the working directory should be automatically loaded into the waveform viewer and following signals maybe observed to further verify the functionality.

Signals in waveform.wcfg to help guide waveform inspection:

-`testcase_no`: 0-17 (0-7:virus reads, 8-17: human reads)<br />
-`clk`: clock for SquiggleFilter<br />
-`rst4`: resets the systolic array processors<br />
-`start1`: signals start of systolic array processing<br />
-`reference`:reference current samples for SARS-Cov-2 genome<br />
-`scaled_op`: normalized query from normalizer (input to systolic array)<br />
-`done`: signals completion of SquiggleFilter processing for a read<br />
-`result`: SquiggleFilter output, 1 for virus detection, 0 for human<br />
-`expected_result`: Testbench provided expected result value, 1 for virus detection, 0 for human<br />
