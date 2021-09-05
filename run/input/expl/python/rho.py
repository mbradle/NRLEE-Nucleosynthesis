import sys
import numpy as np

rho_1 = float(sys.argv[1])
rho_2 = float(sys.argv[2])
n = int(sys.argv[3])

rho = np.logspace(np.log10(rho_1), np.log10(rho_2), n)

for r in rho:
     print('{:.2e}'.format(r))
