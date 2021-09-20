This is a work directory in which one can run calculations to produce the
data for the notebook in the parent directory.  To run the codes, you need
an appropriate zone XML input file for the NRLEE calculations.  An example
is *input/example_input.xml*.  Edit the input in the *runs.sh* script to
set the overall parameters for the calculations and the
file *input/expl/run.rsp* to set the parameters for the single-zone
calculations.  Once those steps are done, execute the code by typing,
for example:

**./runs.sh --model model1 --input_file input/example_input.xml --rho_low 1.e6--rho_high 1.e10 --n_runs 101 --t9_p 14 --tau 0.1**

The output will be in the user-defined directory and model subdirectory.
The script will also create a gzipped tarball in the output directory.
To get help on running this script, type:

**./runs.sh --help**

The directory also includes a *pbs* script.  If your system supports this,
you can run

**qsub -v model=model1,input_file=input/example_input.xml,rho_low=1.e06,rho_high=1.e10,n_runs=101,t9_p=14,tau=0.1 job.pbs**

Of course you can edit the scripts according to your purposes.
