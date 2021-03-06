import os
## check how well pwem and fdfd match
import scipy.io
import numpy as np

import sys
sys.path.append("D:\\RCWA\\")
import matplotlib.patches as mpatches

import matplotlib.pyplot as plt
from convolution_matrices import convmat2D as cm
from PWEM_functions import K_matrix as km
from PWEM_functions import PWEM_eigen_problem as eg
'''
solve PWEM and FDFD band structure for a circle. We know PWEM is basically correct based on a comparison
with Johannopoulos, so we'll need to diagnose the issues with FDFD
'''
### lattice and material parameters
a = 1;
radius = 0.2*a; #matlab file has 0.25
e_r = 8.9;
c0 = 3e8;
#generate irreducible BZ sample
T1 = 2*np.pi/a;
T2 = 2*np.pi/a;

# determine number of orders to use
P = 5;
Q = 5;
PQ = (2*P+1)*(2*Q+1)
# ============== build high resolution circle ==================
Nx = 512; Ny = 512;
A = np.ones((Nx,Ny));
ci = int(Nx/2); cj= int(Ny/2);
cr = (radius/a)*Nx;
I,J=np.meshgrid(np.arange(A.shape[0]),np.arange(A.shape[1]));

dist = np.sqrt((I-ci)**2 + (J-cj)**2);
A[np.where(dist<cr)] = e_r;

#visualize structure
plt.imshow(A);
plt.show()

## =============== Convolution Matrices ==============
E_r = cm.convmat2D(A, P,Q)
print(E_r.shape)
print(type(E_r))
plt.figure();
plt.imshow(abs(E_r), cmap = 'jet');
plt.colorbar()
plt.show()

## =============== K Matrices =========================
beta_x = beta_y = 0;
plt.figure();

## check K-matrices for normal icnidence
Kx, Ky = km.K_matrix_cubic_2D(0,0, a, a, P, Q);
np.set_printoptions(precision = 3)

print(Kx.todense())
print(Ky.todense())

band_cutoff = PQ; #number of bands to plot
## ======================== run band structure calc ==========================##
kx_scan = np.linspace(-np.pi, np.pi, 500)/a;
kx_mat = np.repeat(np.expand_dims(kx_scan, axis = 1), PQ,axis = 1)
eig_store = []
for beta_x in kx_scan:
    beta_y = beta_x;
    beta_y = 0;
    Kx, Ky = km.K_matrix_cubic_2D(beta_x, beta_y, a, a, P, Q);
    eigenvalues, eigenvectors, A_matrix = eg.PWEM2D_TE(Kx, Ky, E_r);
    #eigenvalues...match with the benchmark...but don't match with
    eig_store.append(np.sqrt(np.real(eigenvalues)));
    #plt.plot(beta_x*np.ones((PQ,)), np.sort(np.sqrt(eigenvalues)), '.')
eig_store = np.array(eig_store);

plt.plot(kx_mat[:,0:band_cutoff], eig_store[:,0:band_cutoff]/(2*np.pi),'.g');
plt.title('TE polarization')
plt.ylim([0,1.2])
print('Done procceed to load matlab data')
## =============================non dispersive===================================== ##
matlab_data = os.path.join('non_dispersive_photonic_circle_bandstructure_for_comparison_with_Johannopoulos_book.mat');
mat = scipy.io.loadmat(matlab_data)
print(mat.keys())
L0 = np.squeeze(mat['L0']);
kx_spectra = np.squeeze(mat['kx_spectra'])
k_scan = np.squeeze(mat['k_scan'])
c0_matlab = np.squeeze(mat['c0'])

plt.plot(2*k_scan, kx_spectra*a/(2*np.pi*c0_matlab), '.b')
plt.legend(('pwem','fdfd'));
plt.title('benchmark with non-dispersive FDFD')
plt.xlim([-np.pi, np.pi])

red_patch = mpatches.Patch(color='red', label='fdfd_imag')
blue_patch = mpatches.Patch(color='blue', label='fdfd_real')
green_patch = mpatches.Patch(color='green', label='pwem')

plt.savefig('benchmarking PWEM and FDFD_nondispsersive.png')
plt.show()

## ======================= dispersive benchmark ====================================##

matlab_data = os.path.join('TE_dispersive_photonic_circle_bandstructure_for_comparison_with_Johannopoulos_book.mat');
mat = scipy.io.loadmat(matlab_data)
plt.figure(figsize = (5.5, 5.5));
ax = plt.subplot(111);
handles = [];
a1 = plt.plot(kx_mat[:,0:band_cutoff], eig_store[:,0:band_cutoff]/(2*np.pi),'.g', markersize = 0.8);
plt.title('TE polarization')
plt.ylim([0,1.2])
kx_spectra = np.squeeze(mat['kx_spectra'])
omega_scan = np.squeeze(mat['omega_scan'])
c0_matlab = np.squeeze(mat['c0'])

a2 = plt.plot(kx_spectra, omega_scan, '.b', markersize = 0.8)
a3 = plt.plot(np.imag(kx_spectra), omega_scan, '.r', markersize = 0.8)
print(max(omega_scan))
#plt.legend(handles = [a1, a2, a3])
#plt.legend(('pwem','fdfd_real', 'fdfd_imag'));

red_patch = mpatches.Patch(color='red', label='fdfd_imag')
blue_patch = mpatches.Patch(color='blue', label='fdfd_real')
green_patch = mpatches.Patch(color='green', label='pwem')
plt.xlabel('ka')
plt.ylabel('$\omega a/(2 \pi c_0)$')
plt.legend(handles=[red_patch, blue_patch, green_patch])
plt.title('benchmark with dispersive solution')
plt.xlim([-np.pi, np.pi])
plt.savefig('benchmarking PWEM and FDFD_dispersive.png', dpi = 300)
plt.show()