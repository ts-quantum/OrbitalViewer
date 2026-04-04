import numpy as np

# 1. sp (Linear) [s, pz]
sp = np.array([
    [1/np.sqrt(2),  1/np.sqrt(2)],
    [1/np.sqrt(2), -1/np.sqrt(2)]
])

# 2. sp2 (Trigonal-planar) [s, px, py]
sp2 = np.array([
    [1/np.sqrt(3),  np.sqrt(2)/np.sqrt(3),  0],
    [1/np.sqrt(3), -1/np.sqrt(6),        1/np.sqrt(2)],
    [1/np.sqrt(3), -1/np.sqrt(6),       -1/np.sqrt(2)]
])

# 3. sp3 (Tetraedrisch) [s, px, py, pz]
sp3 = 0.5 * np.array([
    [1,  1,  1,  1],
    [1,  1, -1, -1],
    [1, -1,  1, -1],
    [1, -1, -1,  1]
])

# 4. dsp2 (Quadratic-planar) [s, px, py, dx2y2]
dsp2 = 0.5 * np.array([
    [1,  np.sqrt(2),  0,        1],
    [1, -np.sqrt(2),  0,        1],
    [1,  0,        np.sqrt(2), -1],
    [1,  0,       -np.sqrt(2), -1]
])

# 5. sd3 (Tetrahedral - Metals) [s, dxy, dyz, dxz]
sd3 = 0.5 * np.array([
    [1,  1,  1,  1],
    [1,  1, -1, -1],
    [1, -1, -1,  1],
    [1, -1,  1, -1]
])

# 6. d2sp3 (Octahedral) [s, px, py, pz, dz2, dx2y2]
d2sp3 = np.array([
    [1/np.sqrt(6),  0,        0,        1/np.sqrt(2),  1/np.sqrt(3),  0],        # +z
    [1/np.sqrt(6),  0,        0,       -1/np.sqrt(2),  1/np.sqrt(3),  0],        # -z
    [1/np.sqrt(6),  1/np.sqrt(2),  0,        0,       -1/np.sqrt(12), 0.5],      # +x
    [1/np.sqrt(6), -1/np.sqrt(2),  0,        0,       -1/np.sqrt(12), 0.5],      # -x
    [1/np.sqrt(6),  0,        1/np.sqrt(2),  0,       -1/np.sqrt(12), -0.5],     # +y
    [1/np.sqrt(6),  0,       -1/np.sqrt(2),  0,       -1/np.sqrt(12), -0.5]      # -y
])

# 7. sp3d (Trigonal-bipyramidal) [s, pz, dz2, px, py]
sp3d = np.array([
    [1/np.sqrt(10),  1/np.sqrt(2),  np.sqrt(2/5),  0,           0],          # ax +z
    [1/np.sqrt(10), -1/np.sqrt(2),  np.sqrt(2/5),  0,           0],          # ax -z
    [np.sqrt(4/15),  0,         -np.sqrt(1/15), np.sqrt(2/3),   0],          # eq 1
    [np.sqrt(4/15),  0,         -np.sqrt(1/15), -1/np.sqrt(6),  1/np.sqrt(2)],  # eq 2
    [np.sqrt(4/15),  0,         -np.sqrt(1/15), -1/np.sqrt(6), -1/np.sqrt(2)]   # eq 3
])

# 8. sp3d3 (Pentagonal-bipyramidal) [s, pz, dz2, px, py, dx2y2, dxy]
def get_sp3d3():
    phi = 2 * np.pi / 5
    mat = np.zeros((7, 7))
    # Axial
    mat[0] = [1/np.sqrt(7),  1/np.sqrt(2),  np.sqrt(5/14), 0, 0, 0, 0] # top
    mat[1] = [1/np.sqrt(7), -1/np.sqrt(2),  np.sqrt(5/14), 0, 0, 0, 0] # bottom
    # Equatorial
    for k in range(5):
        angle = k * phi
        mat[k+2] = [
            1/np.sqrt(7),      # s
            0,              # pz
            -np.sqrt(2/35),    # dz2
            np.sqrt(2/5)*np.cos(angle),   # px
            np.sqrt(2/5)*np.sin(angle),   # py
            np.sqrt(2/5)*np.cos(2*angle), # dx2y2
            np.sqrt(2/5)*np.sin(2*angle)  # dxy
        ]
    return mat

sp3d3 = get_sp3d3()

# Dictionary with all matrices
hybrids = {
    "sp": sp, "sp2": sp2, "sp3": sp3, "dsp2": dsp2, 
    "sd3": sd3, "d2sp3": d2sp3, "sp3d": sp3d, "sp3d3": sp3d3
}
