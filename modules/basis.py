from sympy.physics.hydrogen import R_nl
from sympy import symbols, lambdify, Matrix, Znm
import numpy as np
from hybrids import *


r_sym, theta_sym, phi_sym = symbols('r theta phi')
# 4. Define Orbitals (Note: SciPy order is m, l, phi, theta)
def get_psi_sym(n, l, m):
    radial = R_nl(n, l, r_sym, Z=1)
    angular = Znm(l, m, theta_sym, phi_sym) 
    return (radial * angular).expand(func=True)

# Basis Functions
psi_2s=get_psi_sym(2,0,0) #2s
psi_2px=get_psi_sym(2,1,1)  # 2px m=1
psi_2py=get_psi_sym(2,1,-1)  # 2py m=-1
psi_2pz=get_psi_sym(2,1,0)  # 2pz m=0
psi_3dxy=get_psi_sym(3,2,-2) # 3dxy m=-2
psi_3dyz=get_psi_sym(3,2,-1) # 3dyz m=-1
psi_3dxz=get_psi_sym(3,2,1) # 3dxz m=1
psi_3dx2y2=get_psi_sym(3,2,2) # 3dx2y2 m=2
psi_3dz2=get_psi_sym(3,2,0) # 3dx2y2 m=0
# Basis Vectors for each Hybridization
b_sp=( Matrix( [psi_2s, psi_2pz ]) ) # sp: [s,pz]
b_sp2=( Matrix( [psi_2s, psi_2px, psi_2py ]) ) # sp2: [s,px,py]
b_sp3=( Matrix([psi_2s, psi_2px, psi_2py, psi_2pz]) ) # sp3: [s,px,py,pz]
b_dsp2=( Matrix( [psi_2s,psi_2px, psi_2py, psi_3dx2y2] ) ) # dsp2: [s, px, py, dx2y2]
b_sd3=( Matrix( [psi_2s, psi_3dxy, psi_3dyz, psi_3dxz] ) ) # sd3: [s, dxy, dyz, dxz]
b_d2sp3=( Matrix( [psi_2s, psi_2px, psi_2py, psi_2pz, psi_3dz2, psi_3dx2y2 ] ) ) # d2sp3: [s, px, py, pz, dz2, dx2y2]
b_sp3d=( Matrix( [psi_2s,psi_2pz, psi_3dz2, psi_2px, psi_2py ] ) ) # sp3d: [s, pz, dz2, px, py]
b_sp3d3=( Matrix( [psi_2s,psi_2pz,psi_3dz2, psi_2px, psi_2py, psi_3dx2y2, psi_3dxy ] ) ) # sp3d3: [s, pz, dz2, px, py, dx2y2, dxy]
#create dictionary of basis vectors
basis_sym = {
        "sp": b_sp, "sp2": b_sp2, "sp3": b_sp3, "dsp2": b_dsp2,
        "sd3": b_sd3, "d2sp3": b_d2sp3, "sp3d": b_sp3d, "sp3d3": b_sp3d3
            }

def get_psi_num(hyb,n_points):
    match hyb:
            case 'sp' | 'sp2' | 'sp3':
                limit = 2**2 * 3 
            case 'dsp2' | 'd2sp3' | 'sd3' | 'sp3d' | 'sp3d3':
                limit = 3**2 * 3 
     # 6. Visualization
    coords = np.linspace(-limit, limit, n_points)
    X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')
    # 2. Convert Cartesian to Spherical for calculation
    R = np.sqrt(X**2 + Y**2 + Z**2)
    # Handle division by zero at the nucleus
    R_safe = np.where(R == 0, 1e-10, R) 
    THETA = np.arccos(Z / R_safe)     # Polar angle [0, pi]
    PHI = np.arctan2(Y, X)            # Azimuthal angle [0, 2pi]
    # Hybrid, symbolic calculations
    psi_v_sym = Matrix(hybrids[hyb]) * basis_sym[hyb]
    # conversion into numerical function
    psi_v_func = lambdify((r_sym, theta_sym, phi_sym), psi_v_sym, 'numpy')
    psi_v_num = psi_v_func(R, THETA, PHI)
    psi_v_num = np.array(psi_v_num)
    psi_v_num = np.squeeze(psi_v_num)   
    return psi_v_num

