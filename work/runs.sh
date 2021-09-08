# Clone the necessary codes.

if [[ ! -d wn_user ]]
then
   git clone https://bitbucket.org/mbradle/wn_user
else
   git -C wn_user pull
fi

if [[ ! -d single_zone ]]
then
   git clone https://bitbucket.org/mbradle/single_zone
else
   git -C single_zone pull
fi

# Set the includes and make the code.

cd wn_user
git checkout develop
cd ..
export WN_USER=1
cp input/master.h single_zone
cd single_zone
git checkout develop
./project_make

make data

# Return to main directory.

cd ..

# Set key data

out_dir=output
model=$1

# Create output and store input.

output=${out_dir}/${model}

mkdir -p ${output}
cp $2 ${output}/input.xml

rho_low=$3
rho_high=$4
n_runs=$5
t9_p=$6
tau=$7

# Record the execution command and data

echo ./run.sh ${output} ${rho_low} ${rho_high} ${n_runs} ${t9_p} ${tau} > ${output}/execute.txt

cp input/expl/run.rsp ${output}

# Run the explosion

cd input/expl

mkdir -p txt

./run.sh ${output} ${rho_low} ${rho_high} ${n_runs} ${t9_p} ${tau}

# Tar and zip model

cd ../..
cd ${out_dir}
tar cvf ${model}.tar ${model}/full.xml ${model}/runs ${model}/zones ${model}/input.xml ${model}/run.rsp ${model}/exec.txt
gzip ${model}.tar
