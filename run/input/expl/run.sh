bin_dir=../../single_zone
out_dir=../../$1/

mkdir -p ${out_dir}/runs
mkdir -p ${out_dir}/zones

# Run calculations for inner zones (include electron capture, etc.)

rho_1=`cat txt/rho_1.txt`
rho_2=`cat txt/rho_2.txt`
t9_p=`cat txt/t9_p.txt`
n=`cat txt/n.txt`

python3 python/rho.py ${rho_1} ${rho_2} $n > txt/rho.txt

for rho_0 in `cat txt/rho.txt`
do
    t9_0=`python3 python/power_rho.py $rho_2 ${t9_p} ${rho_0}`
    echo "${bin_dir}/single_zone_network @run.rsp --rho_0 $rho_0 --t9_0 $t9_0 --aa522a25_update_net true --output_xml ${out_dir}/${rho_0}.xml --zone_xml ${out_dir}/input.xml > ${out_dir}/log_${rho_0}.txt" >> ${out_dir}/command_file
done

parallel -j ${OMP_NUM_THREADS} < ${out_dir}/command_file

# Create summary xml files.

python3 python/create_xmls.py txt/rho.txt ${out_dir} runs zones full.xml
