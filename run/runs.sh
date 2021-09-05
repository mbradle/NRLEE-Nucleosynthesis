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
model=model1

rho_low=1.e6
rho_high=1.e10
n_runs=201
t9_p=14

# Create output and store input.

output=${out_dir}/${model}

mkdir -p ${output}
cp $1 ${output}/input.xml

# Run the explosion

cd input/expl

mkdir -p txt

echo ${rho_low} > txt/rho_1.txt
echo ${rho_high} > txt/rho_2.txt
echo ${n_runs} > txt/n.txt
echo ${t9_p}  > txt/t9_p.txt

./run.sh ${output}

# Tar and zip model

cd ../..
cd ${out_dir}
tar cvf ${model}.tar ${model}/full.xml ${model}/runs ${model}/zones ${model}/input.xml
gzip ${model}.tar
