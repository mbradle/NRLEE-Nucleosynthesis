import numpy as np
import matplotlib.pyplot as plt
import wnutils.xml as wx
import os, io, requests

from scipy.integrate import odeint
from scipy.optimize import root_scalar

#----------------------------------------------------------------------------
# Define overabundance routine.
#----------------------------------------------------------------------------

def calc_overabundances(xml, species, rp=None):
    ov = {}
    x = xml.get_mass_fractions(species)

    for sp in species:
        if sp in rp:
            rsp = rp[sp]
        else:
            rsp = sp
        tup = xml.get_z_a_state_from_nuclide_name(rsp)
        ov[sp] = x[sp] / solar_zone['0']['mass fractions'][(rsp, tup[0], tup[1])]
        
    return ov

#----------------------------------------------------------------------------
# Define polytrope routines.
#----------------------------------------------------------------------------

def lane_emden(y, x, n):
    theta, dtheta = y
    dydx = [dtheta, -2. * dtheta / (x + 1.e-300) - np.power(np.abs(theta), n)]
    return dydx

def f(x, phi_0, n):
    assert(n > 0 and n < 5)
    y0 = [1., 0.]
    xsol = np.linspace(0, x, 2)
    sol = odeint(lane_emden, y0, xsol, args=(n,))
    result = sol[sol.shape[0]-1, 0] - phi_0
    if abs(result) < 1.e-6:
        result = 0
    return result

def get_masses(n, rhos, M):
    Ms = []
    dM = []

    r_sol = root_scalar(f, args=(0, n), x0 = 0, x1 = 1)
    xsi_1 = r_sol.root
    x = np.linspace(0, xsi_1, 101)
    msol = odeint(lane_emden, [1., 0.], x, args=(n,))
    dphi_1 = msol[msol.shape[0]-1, 1]
    rho_c = rhos[len(rhos)-1]

    for r in rhos:
         phi_0 = (r / rho_c)**(1./n)
         r_sol = root_scalar(f, args=(phi_0, n), x0 = 0, x1 = 1)
         xsi = r_sol.root
         x = np.linspace(0, xsi, 101)
         msol = odeint(lane_emden, [1., 0.], x, args=(n,))
         dphi = msol[msol.shape[0]-1, 1]
         Ms.append(M * xsi**2 * dphi / (xsi_1**2 * dphi_1))
    
    for i in range(len(Ms)-1):
        dM.append(Ms[i+1] - Ms[i])
    
    dM.append(M - Ms[len(Ms)-1])

    return (Ms, dM)

#----------------------------------------------------------------------------
# Define plotting routines vs. Mr
#----------------------------------------------------------------------------

def plot_prop_vs_mr(Mr, prop, fig_name,
                    xscale = 'linear', yscale = 'log',
                    xlabel = '$M_r\ (M_\\odot)$', ylabel = '$\\rho_0\ (g/cc)$',
                    xlim = [0,1.4], ylim = [1.e6, 1.e10]):

    plt.plot(Mr, prop)
    plt.yscale(yscale)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close()

def plot_x_vs_mr(xml, Mr, species, fig_name,
                 xscale = 'linear', yscale = 'log',
                 xlabel = '$M_r\ (M_\\odot)$', ylabel = 'Mass Fraction',
                 xlim = [0,1.4], ylim = [1.e-4,1]):

    x = xml.get_mass_fractions(species)
    lnames = xml.get_latex_names(species)
    for sp in species:
        plt.plot(Mr, x[sp], label = lnames[sp] )

    plt.yscale(yscale)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close()

def plot_over_vs_mr(model, Mr, species, daughters, fig_name,
                    xscale = 'linear', yscale = 'log',
                    xlabel = '$M_r\ (M_\\odot)$', ylabel = '$X / X_\\odot$',
                    xlim = [0,1.4], ylim = [100,1.e7]):

    lnames = model7.get_latex_names(species)

    ov = calc_overabundances(model7, species, rp = daughters)
    for sp in ov:
        plt.plot(Mr, ov[sp], label=lnames[sp])
    
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close()

#----------------------------------------------------------------------------
# Define routine to compute exponential average of exposures.
#----------------------------------------------------------------------------

def compute_s_proc_average(my_xml, tau_0):
    props = my_xml.get_properties_as_floats([('exposure', 'n')])
    y = my_xml.get_all_abundances_in_zones()
    
    dtau = []
    tau_old = 0

    for tau in props[('exposure','n')]:
        dtau.append(tau - tau_old)
        tau_old = tau

    if tau_0 < 0:
        raise Exception("tau_0 must be >= 0")
    w = 0
    y_sum = np.zeros((y.shape[1], y.shape[1] + y.shape[2]))
        
    if tau_0 > 0:
        for i in range(y.shape[0]):
            factor = dtau[i] * np.exp(-props[('exposure','n')][i] / tau_0) / tau_0
            w += factor
            for z in range(y.shape[1]):
                for n in range(y.shape[2]):
                    y_sum[z,z+n] += y[i,z,n] * factor
                
        y_sum /= w
    else:
        for z in range(y.shape[1]):
               for n in range(y.shape[2]):
                    y_sum[z,z+n] += y[0,z,n]
    return y_sum

#----------------------------------------------------------------------------
# Read solar abundances.
#----------------------------------------------------------------------------

solar = wx.Xml(io.BytesIO(requests.get('https://osf.io/j67qa/download').content))
solar_zone = solar.get_zone_data()

#----------------------------------------------------------------------------
# Read models and retrieve properties.
#----------------------------------------------------------------------------

sproc = wx.Xml(io.BytesIO(requests.get('https://osf.io/mg76w/download').content))

model7 = wx.Xml('../models/NRLEE/model7/full.xml')
model8 = wx.Xml('../models/NRLEE/model8/full.xml')
model9 = wx.Xml('../models/NRLEE/model9/full.xml')

mprops1 = model7.get_properties_as_floats(['t9_0', 'rho_0'])
mprops2 = model8.get_properties_as_floats(['t9_0', 'rho_0'])
mprops3 = model9.get_properties_as_floats(['t9_0', 'rho_0'])

#===========================================================================
# Full plots
#===========================================================================

#----------------------------------------------------------------------------
# Plot abundance vs. A 
#----------------------------------------------------------------------------

tau_0 = 0.3
ys = compute_s_proc_average(sproc, tau_0)
yas =  np.sum(ys, axis=0)
yis = sproc.get_abundances_vs_nucleon_number(zone_xpath = "[position() = 1]")

plt.plot(yis[0,:], label = 'He burning')
plt.plot(yas, label = '$\\tau_0 = $' + str(tau_0) + ' $mb^{-1}$')

plt.xlim([0,250])
plt.yscale('log')
plt.ylim([1.e-12,1])
plt.xlabel('Mass Number, A')
plt.ylabel('Abundance per nucleon')
plt.legend()
plt.tight_layout()
plt.savefig('../figures/ys_fig.pdf')
plt.close()

#----------------------------------------------------------------------------
# T9 vs. rho
#----------------------------------------------------------------------------

plt.plot(mprops1['rho_0'], mprops1['t9_0'])
plt.xlim([1.e6, 1.e10])
plt.xscale('log')
plt.xlabel('$\\rho_0$ (g/cc)')
plt.ylabel('$T_9$')
plt.tight_layout()
plt.savefig('../figures/t9_vs_rho.pdf')
plt.close()

#----------------------------------------------------------------------------
# Ye vs. rho
#----------------------------------------------------------------------------

y = model7.get_all_abundances_in_zones()
ye1 = np.sum(np.dot(np.swapaxes(y, 1, 2), np.arange(y.shape[1])), axis=1)
y = model8.get_all_abundances_in_zones()
ye2 = np.sum(np.dot(np.swapaxes(y, 1, 2), np.arange(y.shape[1])), axis=1)
y = model9.get_all_abundances_in_zones()
ye3 = np.sum(np.dot(np.swapaxes(y, 1, 2), np.arange(y.shape[1])), axis=1)

plt.plot(mprops1['rho_0'], ye1, label = '0.1')
plt.plot(mprops2['rho_0'], ye2, label = '0.2')
plt.plot(mprops3['rho_0'], ye3, label = '0.5')

plt.xscale('log')
plt.xlim([1.e6, 1.e10])
plt.ylim([0.42,0.5])
plt.xlabel('$\\rho_0$ (g/cc)')
plt.ylabel('$Y_e$')
plt.legend(title = '$\\tau$ (s)')
plt.tight_layout()
plt.savefig('../figures/ye_vs_rho.pdf')
plt.close()

#----------------------------------------------------------------------------
# Mass fractions
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# Carbon and Oxygen
#----------------------------------------------------------------------------

species = ['c12', 'o16', 'ne20', 'mg24', 'si28']
model7.plot_mass_fractions_vs_property('rho_0', species, xscale = 'log', ylim = [0, 1.], savefig = '../figures/c_o_ne_mg_si_vs_rho.pdf', xlabel = '$\\rho_0\ (g/cc)$', use_latex_names=True, xlim = [1.e6, 1.e10])

#----------------------------------------------------------------------------
# Calcium
#----------------------------------------------------------------------------

species = ['ca40', 'ca41', 'ca42', 'ca43', 'ca44', 'ca45', 'ca46', 'ca47', 'ca48']
model7.plot_mass_fractions_vs_property('rho_0', species, xscale = 'log', yscale = 'log', ylim = [1.e-8, 1.], savefig = '../figures/ca_vs_rho.pdf', xlabel = '$\\rho_0\ (g/cc)$', use_latex_names=True, xlim = [1.e6, 1.e10])

#----------------------------------------------------------------------------
# Titanium
#----------------------------------------------------------------------------

species = ['ti44', 'ti46', 'ti47', 'ti48', 'ti49', 'ti50', 'cr48']
model7.plot_mass_fractions_vs_property('rho_0', species, xscale = 'log', yscale = 'log', ylim = [1.e-8, 1.], savefig = '../figures/ti_vs_rho.pdf', xlabel = '$\\rho_0\ (g/cc)$', use_latex_names=True, xlim = [1.e6, 1.e10])

#----------------------------------------------------------------------------
# Strontium
#----------------------------------------------------------------------------

species = ['sr84', 'sr85', 'sr86', 'sr87', 'sr88']
model7.plot_mass_fractions_vs_property('rho_0', species, xscale = 'log', yscale = 'log', ylim = [1.e-8, 1.], savefig = '../figures/sr_vs_rho.pdf', xlabel = '$\\rho_0\ (g/cc)$', use_latex_names=True, xlim = [1.e6, 1.e10])

#----------------------------------------------------------------------------
# Zirconium
#----------------------------------------------------------------------------

species = ['zr90', 'zr91', 'zr92', 'zr93', 'zr94', 'zr95', 'zr96']
model7.plot_mass_fractions_vs_property('rho_0', species, xscale = 'log', yscale = 'log', ylim = [1.e-8, 1.], savefig = '../figures/zr_vs_rho.pdf', xlabel = '$\\rho_0\ (g/cc)$', use_latex_names=True, xlim = [1.e6, 1.e10])

#----------------------------------------------------------------------------
# Overabundances
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# Titanium overabundances
#----------------------------------------------------------------------------

species = ['ti44', 'ti46', 'ti47', 'ti48', 'ti49', 'ti50', 'cr48']
daughters = {'ti44': 'ca44', 'cr48': 'ti48'}
lnames = model7.get_latex_names(species)

ov = calc_overabundances(model7, species, rp = daughters)
for sp in ov:
    plt.plot(mprops1['rho_0'], ov[sp], label=lnames[sp])
    
plt.xscale('log')    
plt.yscale('log')
plt.xlim([1.e6, 1.e10])
plt.ylim([100,1.e7])
plt.xlabel('$\\rho_{0}$ (g/cc)')
plt.ylabel('$X / X_\\odot$')
plt.legend()
plt.tight_layout()
plt.savefig('../figures/ti_over_vs_rho.pdf')
plt.close()

#----------------------------------------------------------------------------
# Calcium overabundances
#----------------------------------------------------------------------------

species = ['ca40', 'ca41', 'ca42', 'ca43', 'ca44', 'ca45', 'ca46', 'ca47', 'ca48']
daughters = {'ca41': 'k41', 'ca45': 'sc45', 'ca47': 'ti47'}
lnames = model7.get_latex_names(species)

ov = calc_overabundances(model7, species, rp = daughters)
for sp in ov:
    plt.plot(mprops1['rho_0'], ov[sp], label=lnames[sp])
    
plt.xscale('log')    
plt.yscale('log')
plt.xlim([1.e6, 1.e10])
plt.ylim([100,1.e7])
plt.xlabel('$\\rho_{0}$ (g/cc)')
plt.ylabel('$X / X_\\odot$')
plt.legend()
plt.tight_layout()
plt.savefig('../figures/ca_over_vs_rho.pdf')
plt.close()

#----------------------------------------------------------------------------
# Compute Mr.
#----------------------------------------------------------------------------

n = 3
M = 1.4

Mr, dM = get_masses(n, mprops1['rho_0'], M)

#----------------------------------------------------------------------------
# Plot rho vs. Mr
#----------------------------------------------------------------------------

plot_prop_vs_mr(Mr, mprops1['rho_0'], '../figures/rho_vs_mr.pdf')

#----------------------------------------------------------------------------
# Plot t9 vs. Mr
#----------------------------------------------------------------------------

plot_prop_vs_mr(Mr, mprops1['t9_0'], '../figures/t9_vs_mr.pdf',
                yscale = 'linear', ylim = [0, 15],
                ylabel = '$T_9$')

#----------------------------------------------------------------------------
# Ye vs. Mr
#----------------------------------------------------------------------------

plt.plot(Mr, ye1, label = '0.1')
plt.plot(Mr, ye2, label = '0.2')
plt.plot(Mr, ye3, label = '0.5')

plt.xlim([0, 1.4])
plt.ylim([0.42,0.5])
plt.xlabel('$M_r\ (M_\\odot)$')
plt.ylabel('$Y_e$')
plt.legend(title = '$\\tau$ (s)')
plt.tight_layout()
plt.savefig('../figures/ye_vs_mr.pdf')
plt.close()

#----------------------------------------------------------------------------
# Ti, Carbon, and oxygen vs. Mr
#----------------------------------------------------------------------------

species = ['c12', 'o16', 'ti44', 'ti46', 'ti47', 'ti48', 'ti49', 'ti50']

x = model7.get_mass_fractions(species)
plot_x_vs_mr(model7, Mr, species, '../figures/ti_c_o_vs_mr.pdf', ylim = [1.e-6,1])

#----------------------------------------------------------------------------
# Nickel and iron vs. Mr
#----------------------------------------------------------------------------

#species = ['fe54', 'fe56', 'fe57', 'fe58', 'fe60', 'ni56', 'ni57', 'ni58',
#           'ni60', 'ni61', 'ni62', 'ni64', 'ni66']
species = ['fe54', 'fe56', 'fe57', 'fe58', 'fe60', 'ni56', 'ni58',
           'ni60', 'ni62', 'ni64', 'ni66']

x = model7.get_mass_fractions(species)
plot_x_vs_mr(model7, Mr, species, '../figures/fe_ni_vs_mr.pdf', ylim = [0,1], yscale = 'linear')

#----------------------------------------------------------------------------
# Calcium overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['ca40', 'ca41', 'ca42', 'ca43', 'ca44', 'ca45', 'ca46', 'ca47', 'ca48']
daughters = {'ca41': 'k41', 'ca45': 'sc45', 'ca47': 'ti47'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/ca_over_vs_mr.pdf')

#----------------------------------------------------------------------------
# Titanium overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['ti44', 'ti46', 'ti47', 'ti48', 'ti49', 'ti50', 'cr48']
daughters = {'ti44': 'ca44', 'cr48': 'ti48'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/ti_over_vs_mr.pdf')

#----------------------------------------------------------------------------
# Chromium overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['cr50', 'cr52', 'cr53', 'cr54', 'mn54']
daughters = {'mn52': 'cr52', 'mn54': 'cr54'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/cr_over_vs_mr.pdf')

#----------------------------------------------------------------------------
# Fe overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['fe54', 'fe56', 'fe57', 'fe58', 'ni56']
daughters = {'ti44': 'ca44', 'ni56': 'fe56'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/fe_over_vs_mr.pdf',
                ylim = [100, 1.e6])

#----------------------------------------------------------------------------
# Ni overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['ni58', 'ni60', 'ni61', 'ni62', 'ni64', 'fe60']
daughters = {'ni56': 'fe56', 'ni57': 'fe57', 'ni59': 'co59', 'fe60': 'ni60'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/ni_over_vs_mr.pdf',
                ylim = [100, 1.e6])

#----------------------------------------------------------------------------
# Strontium overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['sr84', 'sr85', 'sr86', 'sr87', 'sr88']
daughters = {'sr85': 'rb85'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/sr_over_vs_mr.pdf',
                xlim = [1.275,1.4], ylim = [100, 1.e6])

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/sr_over_vs_mr_linear.pdf',
                xlim = [1.275,1.4], yscale = 'linear', ylim = [0, 5.e5])

#----------------------------------------------------------------------------
# Zirconium overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['zr90', 'zr91', 'zr92', 'zr94', 'zr96']
daughters = {'zr93': 'nb93', 'zr95': 'mo95'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/zr_over_vs_mr.pdf',
                xlim = [1.275,1.4], ylim = [100, 1.e6])

plot_over_vs_mr(model7, Mr, species, daughters,
                '../figures/zr_over_vs_mr_linear.pdf',
                xlim = [1.275,1.4], yscale = 'linear', ylim = [0, 1.4e5])

#----------------------------------------------------------------------------
# Molybdenum overabundances vs. Mr
#----------------------------------------------------------------------------

species = ['mo92', 'mo94', 'mo95', 'mo96', 'mo97', 'mo98', 'mo100', 'zr95', 'nb95']
daughters = {'zr95': 'mo95', 'nb95': 'mo95', 'zr97': 'mo97', 'nb96': 'mo96'}

plot_over_vs_mr(model7, Mr, species, daughters, '../figures/mo_over_vs_mr.pdf',
                xlim = [1.275,1.4], ylim = [100, 1.e6])

plot_over_vs_mr(model7, Mr, species, daughters,
                '../figures/mo_over_vs_mr_linear.pdf',
                xlim = [1.275,1.4], yscale = 'linear', ylim = [0, 60000])

#===========================================================================
# Single-zone plots
#===========================================================================

#----------------------------------------------------------------------------
# Ye vs. time
#----------------------------------------------------------------------------

rho_0='7.59e+09.xml'

inner1 = wx.Xml('../models/NRLEE/model7/zones/' + rho_0)
inner2 = wx.Xml('../models/NRLEE/model8/zones/' + rho_0)
inner3 = wx.Xml('../models/NRLEE/model9/zones/' + rho_0)

y1 = inner1.get_all_abundances_in_zones()
y2 = inner2.get_all_abundances_in_zones()
y3 = inner3.get_all_abundances_in_zones()

ye1 = np.sum(np.dot(np.swapaxes(y1, 1, 2), np.arange(y1.shape[1])), axis=1)
ye2 = np.sum(np.dot(np.swapaxes(y2, 1, 2), np.arange(y2.shape[1])), axis=1)
ye3 = np.sum(np.dot(np.swapaxes(y3, 1, 2), np.arange(y3.shape[1])), axis=1)

props1 = inner1.get_properties_as_floats(['time', 't9', 'rho', 'rho_0'])
props2 = inner2.get_properties_as_floats(['time', 't9', 'rho', 'rho_0'])
props3 = inner3.get_properties_as_floats(['time', 't9', 'rho', 'rho_0'])

plt.plot(props1['time'], ye1, label = '0.1')
plt.plot(props2['time'], ye2, label = '0.2')
plt.plot(props3['time'], ye3, label = '0.5')

plt.xscale('log')
plt.xlim([1.e-6,100])
plt.ylim([0.38,0.5])
plt.xlabel('time (s)')
plt.ylabel('$Y_e$')
plt.legend(title = '$\\tau$ (s)')
plt.tight_layout()

plt.savefig('../figures/ye_vs_time.pdf')
plt.close()

#----------------------------------------------------------------------------
# Inner X vs. time
#----------------------------------------------------------------------------

species = ['n', 'h1', 'he4', 'c12', 'o16', 'si28', 'ca48', 'ti50']
inner1.plot_mass_fractions_vs_property('time', species, xlim = [1.e-15, 100],
    xscale = 'log', yscale = 'log', ylim = [1.e-8, 1], xlabel = 'time (s)',
    use_latex_names = True,
    savefig = '../figures/inner_x_vs_time.pdf')

#----------------------------------------------------------------------------
# Zr vs. time
#----------------------------------------------------------------------------

rho_0='7.59e+06.xml'

outer1 = wx.Xml('../models/NRLEE/model7/zones/' + rho_0)

species = ['zr90', 'zr91', 'zr92', 'zr93', 'zr94', 'zr95', 'zr96']
outer1.plot_mass_fractions_vs_property('time', species, yscale = 'log',
                                       ylim = [1.e-8, 1.e-4],
                                       use_latex_names=True,
                                       xlabel = 'time (s)',
                                       xscale = 'log',
                                       xlim = [1.e-12, 100],
                                       savefig = '../figures/zr_vs_time.pdf')

#----------------------------------------------------------------------------
# n_n vs. time
#----------------------------------------------------------------------------

props = outer1.get_properties_as_floats(['time', 'rho'])
x = outer1.get_mass_fractions(['n'])

n_n = props['rho'] * x['n'] * 6.02e23
plt.plot(props['time'], n_n)

plt.xscale('log')
plt.xlim([1.e-12,100])
plt.yscale('log')
plt.ylim([1.e10, 1.e24])
plt.xlabel('time (s)')
plt.ylabel('Neutron-Number Density (per cc)')
plt.tight_layout()
plt.savefig('../figures/n_n_vs_time.pdf')
