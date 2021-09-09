margs=7

function example {
    echo -e "example: $0 --model model1 --input_file input/example_input.xml --rho_low 1.e6 --rho_high 1.e10 --n_runs 201 --t9_p 14 --tau 0.1\n"
}

function usage {
    echo -e "usage: $0 MANDATORY [OPTION]\n"
}

function help {
  usage
    echo -e "MANDATORY:"
    echo -e "  --model  VAL  The output subdirectory"
    echo -e "  --input_file  VAL  The input XML file"
    echo -e "  --rho_low  VAL  The lower limit on the density"
    echo -e "  --rho_high VAL  The upper limit on the density"
    echo -e "  --n_runs VAL  The number of logarithmically spaced runs in density"
    echo -e "  --t9_p VAL  The peak t9 at the maximum density"
    echo -e "  --tau VAL  The density expansion e-folding timescale"
    echo -e "OPTION:"
    echo -e "  -h, --help  Prints this help\n"
  example
}

function margs_precheck {
	if [ $2 ] && [ $1 -lt $margs ]; then
		if [ $2 == "--help" ] || [ $2 == "-h" ]; then
			help
			exit
		else
	    	usage
			example
	    	exit 1 # error
		fi
	fi
}

function margs_check {
	if [ $# -lt $margs ]; then
	    usage
	  	example
	    exit 1 # error
	fi
}

margs_precheck $# $1

# Args while-loop

while [ "$1" != "" ];
do
   case $1 in
   --model )  shift
              model=$1
              ;;
   --input_file )  shift
              input_file=$1
              ;;
   --rho_low )  shift
              rho_low=$1
              ;;
   --rho_high )  shift
              rho_high=$1
              ;;
   --n_runs )  shift
              n_runs=$1
              ;;
   --t9_p  )  shift
              t9_p=$1
              ;;
   --tau  )  shift
              tau=$1
              ;;
   -h   | --help )        help
                          exit
                          ;;
   *)                     
                          echo "$script: illegal option $1"
                          usage
						  example
						  exit 1 # error
                          ;;
    esac
    shift
done

# Mandatory paramter check

margs_check ${model} ${input_file} ${rho_low} ${rho_high} ${n_runs} ${t9_p} ${tau}

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

# Create output and store input.

output=${out_dir}/${model}

mkdir -p ${output}
cp ${input_file} ${output}/input.xml

# Record the execution command and data

echo ./runs.sh --model ${model1} --input_file ${input_file} --rho_low ${rho_low} --rho_high ${rho_high} --n_runs ${n_runs}  --t9_p ${t9_p} --tau ${tau} > ${output}/execute.txt

cp input/expl/run.rsp ${output}

# Run the explosion

cd input/expl

mkdir -p txt

./run.sh ${output} ${rho_low} ${rho_high} ${n_runs} ${t9_p} ${tau}

# Tar and zip model

cd ../..
cd ${out_dir}
tar cvf ${model}.tar ${model}/full.xml ${model}/runs ${model}/zones ${model}/input.xml ${model}/run.rsp ${model}/execute.txt
gzip ${model}.tar
