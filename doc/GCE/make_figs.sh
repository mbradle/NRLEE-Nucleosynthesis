rm -fr python
rm -fr python.tar.gz
rm -fr data
rm -fr figures

mkdir figures
mkdir data

curl -J -L -o data/gce.h5.gz https://osf.io/me9cr/download
curl -J -L -o data/gce_no_nrlee.h5.gz https://osf.io/e6mqk/download
curl -J -L -o data/gce_ti46.h5.gz https://osf.io/ack5d/download
curl -J -L -o data/data.xml https://osf.io/wj5rd/download
curl -J -L -o data/Anders.xml https://osf.io/w8ktc/download

curl -J -L -o python.tar.gz https://osf.io/78w6k/download

tar zxvf python.tar.gz
rm -fr python.tar.gz
gunzip data/gce.h5.gz
gunzip data/gce_no_nrlee.h5.gz
gunzip data/gce_ti46.h5.gz

python python/plot_gas_frac.py figures/gas_frac.pdf
python python/plot_sol_comp.py figures/sol_comp.pdf
python python/plot_dust.py figures/dust_mass.pdf
python python/plot_x.py figures/x.pdf
python python/plot_x_comp.py figures/x_comp.pdf

python python/plot_ca.py figures/ca.pdf
python python/plot_ti.py figures/ti.pdf
python python/plot_cr.py figures/cr.pdf
python python/plot_fe.py figures/fe.pdf
python python/plot_ni.py figures/ni.pdf

python python/plot_two_species_data_only.py ca figures/ca48_ti50_data_only.pdf
python python/plot_two_species_data_only.py ca_ti figures/ti46_ca48_data_only.pdf
python python/plot_two_species_data_only.py ti figures/ti46_ti50_data_only.pdf
python python/plot_two_species_data_only.py cr figures/cr54_ti50_data_only.pdf nc_ci

python python/plot_two_species.py ca figures/ca48_ti50.pdf
python python/plot_two_species.py ca_ti figures/ti46_ca48.pdf
python python/plot_two_species_ti46.py ca_ti figures/ti46_ca48_mod.pdf
python python/plot_two_species.py ti figures/ti46_ti50.pdf
python python/plot_two_species.py cr figures/cr54_ti50.pdf ci_nc

