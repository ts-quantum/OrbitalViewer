import numpy as np
import matplotlib.pyplot as plt
from scipy.special import sph_harm_y
from sympy.physics.hydrogen import R_nl
from sympy import symbols, lambdify
from skimage import measure #scikit-image
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
from matplotlib.animation import FuncAnimation
import matplotlib as mpl

from modules.hybrids import *
from modules.basis import *

# Spherical Harmonics:

def plot( widget,ax, el, m, color):
        # Grids of polar and azimuthal angles
        theta = np.linspace(0, np.pi, 100)
        phi = np.linspace(0, 2*np.pi, 100)
        # Create a 2-D meshgrid of (theta, phi) angles.
        theta, phi = np.meshgrid(theta, phi)
        # Calculate the Cartesian coordinates of each point in the mesh.
        xyz = np.array([np.sin(theta) * np.sin(phi),
                np.sin(theta) * np.cos(phi),
                np.cos(theta)])
        # NB In SciPy's sph_harm_y function the azimuthal coordinate, theta,
        # comes before the polar coordinate, phi.
        Y = sph_harm_y(el, abs(m), theta, phi)
        # Linear combination of Y_l,m and Y_l,-m to create the real form.
        if m < 0:
            Y = np.sqrt(2) * (-1)**m * Y.imag
        elif m > 0:
            Y = np.sqrt(2) * (-1)**m * Y.real
        Yx, Yy, Yz = np.abs(Y) * xyz
        # Color the plotted surface according to the sign of Y.  
        # color: 'PRGn', 'coolwarm', 'viridis'
        cmap = plt.cm.ScalarMappable(cmap=plt.get_cmap(color))
        cmap.set_clim(-0.5, 0.5)
        # clear plot window
        ax.clear()
        # 3D-Surface Plot
        surf = ax.plot_surface(Yx, Yy, Yz,
                    facecolors=cmap.to_rgba(Y.real),
                    rstride=2, cstride=2)
        # Draw a set of x, y, z axes for reference.
        ax_lim = 0.5
        ax.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
        # Set the Axes limits and title, turn off the Axes frame.
        ax.set_title(r'$Y_{{{},{}}}$'.format(el, m))
        ax_lim = 0.4
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)
        ax.set_zlim(-ax_lim, ax_lim)
        ax.text(ax_lim,0,0,'x',color='blue', fontsize=10)
        ax.text(0,ax_lim,0,'y',color='blue', fontsize=10)
        ax.text(0,0,ax_lim,'z',color='blue', fontsize=10)
        ax.axis('off')
        # update plot canvas
        widget.canvas.figure.tight_layout()
        widget.canvas.draw()

def plot2(widget,ax, l, m,color):
        #phi = np.linspace(0, np.pi, 100)
        #theta = np.linspace(0, 2 * np.pi, 100)
        theta = np.linspace(0, np.pi, 100)
        phi = np.linspace(0, 2 * np.pi, 100)
        theta, phi = np.meshgrid(theta, phi)
        # The Cartesian coordinates of the unit sphere
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)

        # Calculate the spherical harmonic Y(l,m) and normalize to [0,1]
        #fcolors = sph_harm_y(l, m, theta, phi).real
        Y = sph_harm_y(l, abs(m), theta, phi)
        # Linear combination of Y_l,m and Y_l,-m to create the real form.
        if m > 0:
            Y = np.sqrt(2) * (-1)**m * Y.imag
        elif m < 0:
            Y = np.sqrt(2) * (-1)**m * Y.real
        fcolors=Y.real
        fmax, fmin = fcolors.max(), fcolors.min()
        if (fmax-fmin)!=0:
                fcolors = (fcolors - fmin) / (fmax - fmin)
        else:
              fcolors=fcolors
        # Set the aspect ratio to 1 so our sphere looks spherical
        #fig = plt.figure(figsize=plt.figaspect(1.0))
        #ax = fig.add_subplot(111, projection="3d")
        cmap = plt.get_cmap(color)
        ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=cmap(fcolors))
        # Turn off the axis planes
        #widget.axes.set_axis_off()
        # Draw a set of x, y, z axes for reference.
        ax_lim = 0.5
        ax.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
        # Set the Axes limits and title, turn off the Axes frame.
        ax.set_title(r'$Y_{{{},{}}}$'.format(l, m))
        ax_lim = 0.7
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)
        ax.set_zlim(-ax_lim, ax_lim)
        ax.text(ax_lim,0,0,'x',color='blue', fontsize=10)
        ax.text(0,ax_lim,0,'y',color='blue', fontsize=10)
        ax.text(0,0,ax_lim,'z',color='blue', fontsize=10)
        ax.axis('off')
        # update plot canvas
        widget.canvas.draw()

# Orbital Plot:
def plot_orbital(widget, ax, n:int,l:int,m:int, Points:int, wedge: bool):
        # 1. Create a Cartesian Meshgrid
        limit = n**2 * 3  # Adjust based on orbital size
        n_points = Points
        coords = np.linspace(-limit, limit, n_points)
        X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')

        # 2. Convert Cartesian to Spherical for calculation
        R = np.sqrt(X**2 + Y**2 + Z**2)
        # Handle division by zero at the nucleus
        R_safe = np.where(R == 0, 1e-10, R) 
        THETA = np.arccos(Z / R_safe)     # Polar angle [0, pi]
        PHI = np.arctan2(Y, X)            # Azimuthal angle [0, 2pi]

        # 3. Calculate Radial Part (using your SymPy method)
        r_sym = symbols('r')

        # 4. Calculate Spherical Harmonic (Note: SciPy order is m, l, phi, theta)
        radial_func = lambdify(r_sym, R_nl(n, l, r_sym, Z=1), 'numpy')
        radial_R = radial_func(R)
        if m < 0:
            Y_lm = sph_harm_y(l, m, THETA, PHI).imag #new
        elif m >= 0:
            Y_lm = sph_harm_y(l, m, THETA, PHI).real #new
        psi=radial_R * Y_lm

        if wedge == True:
            #cut 1/4 of the sphere (wedge)
            mask = (X<0) & (Y<0)
            psi[mask]=0

        # 6. Visualization
        # clear plot window
        ax.clear()

        # We use a threshold for the isosurface
        max_val=np.max(np.abs(psi))
        threshold = max_val*0.1
        
        # Positive Part (Red)
        add_iso_surface(ax, psi, threshold, 'red', n_points, limit)
        # Negative Part (Blue)
        add_iso_surface(ax, psi, -threshold, 'blue', n_points, limit)

        ax_lim = limit
        ax.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
        # Set the Axes limits and title, turn off the Axes frame.
        ax.set_title(r'$Psi_{{{},{},{}}}$'.format(n,l, m))
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)
        ax.set_zlim(-ax_lim, ax_lim)
        ax.text(ax_lim,0,0,'x',color='blue', fontsize=10)
        ax.text(0,ax_lim,0,'y',color='blue', fontsize=10)
        ax.text(0,0,ax_lim,'z',color='blue', fontsize=10)
        ax.axis('off')
        widget.canvas.draw()

        return psi, threshold

def plot_2d_grid(widget,n,l,m):
        # --- 1. Set-up Parameters ---
        Z = 1  # Atomic number (Hydrogen = 1)

        # --- 2. Radial part R_nl(r) via SymPy ---
        r_sym = symbols('r')
        # create symbolic formula
        radial_sym_expr = R_nl(n, l, r_sym, Z=Z)
        # convert to NumPy-Function
        radial_func = lambdify(r_sym, radial_sym_expr, 'numpy')

        # --- 3. 2D grid for the cross-section (plane: xz-plane at phi=0) ---
        # Create a grid in the r-theta plane
        r_vals = np.linspace(0, 25, 400)      # adapt size according to n
        theta_vals = np.linspace(0, 2*np.pi, 800)
        R, THETA = np.meshgrid(r_vals, theta_vals)

        # Since a flat cross-section is used, phi remains constant (0 or pi)
        PHI = 0*np.ones_like(R) 

        # --- 4. Calculation of components ---
        # Radial Part (depends on n and l)
        R_part = radial_func(R)

        # IMPORTANT: sph_harm expects THETA [0, pi] and PHI [0, 2pi].
        # Using a projection for a 2D cross-section in the X-Z plane:
        # For THETA > pi (left side), PHI effectively jumps to pi.
        
        PHI_projected = np.where(THETA > np.pi, np.pi, 0)
        THETA_projected = np.where(THETA > np.pi, 2*np.pi - THETA, THETA)

        # Angular component (Spherical harmonic, depends on l and m)
        # Note: scipy.special.sph_harm(m, l, phi, theta)
        if m < 0:
            Y_part = sph_harm_y(m, l, THETA_projected, PHI_projected).imag
        elif m >= 0:
            Y_part = sph_harm_y(m, l, THETA_projected, PHI_projected).real

        # total wavefunction
        psi = R_part * Y_part

        # --- 5. Coordinate transformation for the plot (Polar -> Cartesian) ---
        # Map R and THETA to X and Z coordinates
        X = R * np.sin(THETA)
        Z = R * np.cos(THETA)

        # --- 6. Visualization ---
        # IMPORTANT: Clear entire figure to remove old colorbars
        widget.canvas.figure.clear()
    
        # Create new axis in the cleared figure
        ax = widget.canvas.figure.add_subplot(111)

        # pcolormesh is ideal for displaying the wavefunction
        # RdBu (Red-Blue) represents positive and negative phases perfectly

        norm=np.max(np.abs(psi))
        plot = ax.pcolormesh(X, Z, psi, cmap='RdBu_r', shading='auto', 
                      vmax=norm, vmin=-norm)
        
        # Mirroring (X-axis)
        # ax.pcolormesh(-X, Z, psi, cmap='RdBu_r', shading='auto',
        #          vmax=np.max(np.abs(psi)), vmin=-np.max(np.abs(psi)))

        # Add colorbar to the figure and bind it to axis 'ax'
        cbar = widget.canvas.figure.colorbar(plot, ax=ax)
        cbar.set_label(r'$\psi$')

        try:
            ax.set_title(f'x-z plane of {n}{"spdfg"[l]}-Orbital (m={m})')
        except:
            ax.set_title(f'x-z plane of Orbital (n={n}, l={l}, m={m})')
        ax.set_xlabel('x [Bohr]')
        ax.set_ylabel('z [Bohr]')
        ax.axhline(0, color='black', lw=1, ls='--')
        ax.axvline(0, color='black', lw=1, ls='--')
        widget.canvas.figure.tight_layout()
        widget.canvas.draw()
 
# Hybrid Orbitals
def plot_hyb_orb(widget, ax, hyb, n_points,psi,title):     
        # clear plot window
        ax.clear()
        # threshold for the isosurface
        max_val=np.max(np.abs(psi))
        match hyb:
            case 'sp' | 'sp2' | 'sp3':
                threshold = max_val*0.08
                limit = 2**2 * 3 
            case 'dsp2' | 'd2sp3' | 'sd3' | 'sp3d' | 'sp3d3':
                threshold = max_val*0.04  
                limit = 3**2 * 3   
        # Positive Part (Red)
        add_iso_surface(ax, psi, threshold, 'red', n_points, limit)
        # Negative Part (Blue)
        add_iso_surface(ax, psi, -threshold, 'blue', n_points, limit)

        ax_lim = limit
        ax.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
        # Set the Axes limits and title, turn off the Axes frame.
        ax.set_title(title, fontsize=12)
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)
        ax.set_zlim(-ax_lim, ax_lim)
        ax.text(ax_lim,0,0,'x',color='blue', fontsize=10)
        ax.text(0,ax_lim,0,'y',color='blue', fontsize=10)
        ax.text(0,0,ax_lim,'z',color='blue', fontsize=10)
        ax.axis('off')
        widget.canvas.figure.tight_layout()
        widget.canvas.draw()

# Oscillation
def plot_osc(pbar,widget,color,n,l,m, n_points,N,T):
    #parameters
    E=-1**2/(2*n**2)
    hbar=1
    limit = n**2 * 3  # Adjust based on orbital size
    # 3D Orbital; ax1
    psi_1 = calculate_psi(n=n, l=l, m=m, n_points=n_points) 
    # 2D Projection; ax2
    # 1. Create a Cartesian Meshgrid
    phi = np.linspace(0, np.pi, n_points)
    theta = np.linspace(0, 2*np.pi, n_points)
    PHI, THETA = np.meshgrid(phi, theta)
    # 2. Geometry of the unit sphere
    X = np.sin(PHI) * np.cos(THETA)
    Y = np.sin(PHI) * np.sin(THETA)
    Z = np.cos(PHI)
    # 2. Convert Cartesian to Spherical for calculation
    R = np.sqrt(X**2 + Y**2 + Z**2)
    # Handle division by zero at the nucleus
    R_safe = np.where(R == 0, 1e-10, R) 
    THETA = np.arccos(Z / R_safe)     # Polar angle [0, pi]
    PHI = np.arctan2(Y, X)            # Azimuthal angle [0, 2pi]
    # 3. Calculate Radial Part (using your SymPy method)
    r_sym = symbols('r')
    radial_func = lambdify(r_sym, R_nl(n, l, r_sym, Z=1), 'numpy')
    radial_R = radial_func(R)
    Y_m_l= sph_harm_y(l, m, THETA, PHI).real
    psi_2 = Y_m_l * radial_R

    #calculation prior to plotting
    frames_ax1 = [] # List of Isosurface-Collections
    frames_colors_ax2 = [] # List of Surface Colors
    
    max_psi2 = np.max(np.abs(psi_2))
    norm = plt.Normalize(-max_psi2, max_psi2)
    cmap = plt.colormaps[color]

    for frame in range(N):
        t = frame * T
        cos_term = np.cos(E * t / hbar)
        
        # # Precompute colors for ax2 (store as arrays only)
        colors = cmap(norm(psi_2 * cos_term))
        frames_colors_ax2.append(colors)
        
        # progressBar during (pre)calculation
        pbar.setValue(int(frame / N * 100))
        pbar.repaint()

    # clearing old figure
    widget.figure.clear()
    ax1 = widget.figure.add_subplot(121, projection='3d')
    ax2 = widget.figure.add_subplot(122, projection='3d')

    surf2 = ax2.plot_surface(X, Y, Z, facecolors=frames_colors_ax2[frame], shade=False, antialiased=False)
    # 1. Define normalization and colormap (matching vmin/vmax)
    norm = mpl.colors.Normalize(vmin=-max_psi2, vmax=max_psi2)
    cmap = mpl.colormaps[color]
    # 2. Create ScalarMappable (the "dummy" object for the colorbar)
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([]) # Necessary as no direct data array is linked   
    # 3. Add Colorbar to Widget 
    cbar = widget.canvas.figure.colorbar(sm, ax=ax2)
    cbar.set_label(r'Psi')

    # plot data
    max_val=np.max(np.abs(psi_1))
    threshold = max_val*0.1   
    # Set limits once outside the loop if not using ax.cla()
    ax1.set_xlim(-limit, limit)
    ax1.set_ylim(-limit, limit)
    ax1.set_zlim(-limit, limit)
    ax1.axis('off') # turn off 3D Grid
    ax1.text(limit,0,0,'x',color='blue', fontsize=10)
    ax1.text(0,limit,0,'y',color='blue', fontsize=10)
    ax1.text(0,0,limit,'z',color='blue', fontsize=10)
    ax1.plot([-limit, limit], [0,0], [0,0], c='0.5', lw=1, zorder=10)
    ax1.plot([0,0], [-limit, limit], [0,0], c='0.5', lw=1, zorder=10)
    ax1.plot([0,0], [0,0], [-limit, limit], c='0.5', lw=1, zorder=10)

    ax_lim = 0.5
    ax2.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
    ax2.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
    ax2.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
    # Set the Axes limits and title, turn off the Axes frame.
    ax_lim = 0.7
    ax2.set_xlim(-ax_lim, ax_lim)
    ax2.set_ylim(-ax_lim, ax_lim)
    ax2.set_zlim(-ax_lim, ax_lim)
    ax2.text(ax_lim,0,0,'x',color='blue', fontsize=10)
    ax2.text(0,ax_lim,0,'y',color='blue', fontsize=10)
    ax2.text(0,0,ax_lim,'z',color='blue', fontsize=10)
    ax2.axis('off')

    def update(frame):
        # 1. Clear previous surfaces only, not the whole axes
        # This keeps limits and 3D projection stable
        for artist in ax1.collections:
            artist.remove()
        t = frame * T  # Adjust time scale
        cos_term=np.cos(E * t / hbar)
        # Real part of Psi(t) = psi_spatial * cos(E*t/hbar)
        psi_real_t = psi_1 * cos_term
        #psi_2_real_t = psi_2 * np.cos(E * t / hbar)
        # Draw Positive (Red) and Negative (Blue) Isosurfaces
        add_iso_surface(ax1, psi_real_t, threshold, 'red', n_points, limit)
        add_iso_surface(ax1, psi_real_t, -threshold, 'blue', n_points, limit)

        nonlocal surf2
        surf2.remove()
        surf2 = ax2.plot_surface(X, Y, Z, facecolors=frames_colors_ax2[frame], shade=False, antialiased=False)

        percent=int(frame/N*100)
        pbar.setValue(percent)
        #pbar.repaint() 
            
        #widget.canvas.draw_idle()
        return ax1.collections + [surf2]

    # Store animation as attribute to keep it alive
    ani = FuncAnimation(widget, update, frames=N, interval=25, repeat=True)
    widget.canvas.draw()
    return ani

def plot_osc_offline(export_fig,ax1,ax2,p):
    #parameters
    n = p['n']
    l = p['l']
    m = p['m']
    color = p['color']
    n_points = p['n_points']
    T = p['T']
    N=p['N']
    E=-1**2/(2*n**2)
    hbar=1
    limit = n**2 * 3  # Adjust based on orbital size
    # 3D Orbital; ax1
    psi_1 = calculate_psi(n=n, l=l, m=m, n_points=n_points) 
    # 2D Projection; ax2
    # 1. Create a Cartesian Meshgrid
    phi = np.linspace(0, np.pi, n_points)
    theta = np.linspace(0, 2*np.pi, n_points)
    PHI, THETA = np.meshgrid(phi, theta)
    # 2. Geometry of the unit sphere
    X = np.sin(PHI) * np.cos(THETA)
    Y = np.sin(PHI) * np.sin(THETA)
    Z = np.cos(PHI)
    # 2. Convert Cartesian to Spherical for calculation
    R = np.sqrt(X**2 + Y**2 + Z**2)
    # Handle division by zero at the nucleus
    R_safe = np.where(R == 0, 1e-10, R) 
    THETA = np.arccos(Z / R_safe)     # Polar angle [0, pi]
    PHI = np.arctan2(Y, X)            # Azimuthal angle [0, 2pi]
    # 3. Calculate Radial Part (using your SymPy method)
    r_sym = symbols('r')
    radial_func = lambdify(r_sym, R_nl(n, l, r_sym, Z=1), 'numpy')
    radial_R = radial_func(R)
    Y_m_l= sph_harm_y(l, m, THETA, PHI).real
    psi_2 = Y_m_l * radial_R

    #calculation prior to plotting
    frames_ax1 = [] # List of Isosurface-Collections
    frames_colors_ax2 = [] # List of surface colors
    
    max_psi2 = np.max(np.abs(psi_2))
    norm = plt.Normalize(-max_psi2, max_psi2)
    cmap = plt.colormaps[color]

    for frame in range(N):
        t = frame * T
        cos_term = np.cos(E * t / hbar)
        
        # Precompute colors for ax2 (store arrays only)
        colors = cmap(norm(psi_2 * cos_term))
        frames_colors_ax2.append(colors)

    # clearing old figure
    export_fig.clear()
    ax1 = export_fig.add_subplot(121, projection='3d')
    ax2 = export_fig.add_subplot(122, projection='3d')

    surf2 = ax2.plot_surface(X, Y, Z, facecolors=frames_colors_ax2[frame], shade=False, antialiased=False)
    # 1. Define normalization and Colormap (matching vmin/vmax)
    norm = mpl.colors.Normalize(vmin=-max_psi2, vmax=max_psi2)
    cmap = mpl.colormaps[color]
    # 2. Create ScalarMappable ("Dummy"-Object for the Colorbar)
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([]) # Necessary as no direct data array is linked    
    # 3. Add Colorbar to Widget 
    cbar = export_fig.canvas.figure.colorbar(sm, ax=ax2)
    cbar.set_label(r'Psi')

    # plot data
    max_val=np.max(np.abs(psi_1))
    threshold = max_val*0.1   
    # Set limits once outside the loop if not using ax.cla()
    ax1.set_xlim(-limit, limit)
    ax1.set_ylim(-limit, limit)
    ax1.set_zlim(-limit, limit)
    ax1.axis('off') # turn off 3D Grid
    ax1.text(limit,0,0,'x',color='blue', fontsize=10)
    ax1.text(0,limit,0,'y',color='blue', fontsize=10)
    ax1.text(0,0,limit,'z',color='blue', fontsize=10)
    ax1.plot([-limit, limit], [0,0], [0,0], c='0.5', lw=1, zorder=10)
    ax1.plot([0,0], [-limit, limit], [0,0], c='0.5', lw=1, zorder=10)
    ax1.plot([0,0], [0,0], [-limit, limit], c='0.5', lw=1, zorder=10)

    ax_lim = 0.5
    ax2.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
    ax2.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
    ax2.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
    # Set the Axes limits and title, turn off the Axes frame.
    ax_lim = 0.7
    ax2.set_xlim(-ax_lim, ax_lim)
    ax2.set_ylim(-ax_lim, ax_lim)
    ax2.set_zlim(-ax_lim, ax_lim)
    ax2.text(ax_lim,0,0,'x',color='blue', fontsize=10)
    ax2.text(0,ax_lim,0,'y',color='blue', fontsize=10)
    ax2.text(0,0,ax_lim,'z',color='blue', fontsize=10)
    ax2.axis('off')

    def update(frame):
        # 1. Clear previous surfaces only, not the whole axes
        # This keeps limits and 3D projection stable
        for artist in ax1.collections:
            artist.remove()
        t = frame * T  # Adjust time scale
        cos_term=np.cos(E * t / hbar)
        # Real part of Psi(t) = psi_spatial * cos(E*t/hbar)
        psi_real_t = psi_1 * cos_term
        #psi_2_real_t = psi_2 * np.cos(E * t / hbar)
        # Draw Positive (Red) and Negative (Blue) Isosurfaces
        add_iso_surface(ax1, psi_real_t, threshold, 'red', n_points, limit)
        add_iso_surface(ax1, psi_real_t, -threshold, 'blue', n_points, limit)

        nonlocal surf2
        surf2.remove()
        surf2 = ax2.plot_surface(X, Y, Z, facecolors=frames_colors_ax2[frame], shade=False, antialiased=False)
            
        #widget.canvas.draw_idle()
        return ax1.collections + [surf2]

    # Store animation as attribute to keep it alive
    ani = FuncAnimation(export_fig, update, frames=N, interval=25, repeat=False)
    export_fig.canvas.draw()
    return ani


# Transition
def plot_trans(pbar,widget, ax, n1, l1, m1, n2, l2, m2, n_points, N, T):
     #parameters
    hbar=1
    # 1. State 1: 
    psi1 = calculate_psi(n=n1, l=l1, m=m1, n_points=n_points)
    E1 = -1.0**2 / (2 * 1**2) 
    # 2. State 2: 
    psi2 = calculate_psi(n=n2, l=l2, m=m2, n_points=n_points)
    E2 = -1.0**2 / (2 * 2**2)
    delta_E = E2 - E1
    #in case of external magnetic field:
    #dE=m(l) * µ(B) * B
    n=np.max((n1,n2))
    limit = n**2 * 3  # Adjust based on orbital size
    # clearing old figure
    widget.figure.clear()
    ax = widget.figure.add_subplot(111, projection='3d')

    # Set limits once outside the loop if not using ax.cla()
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.axis('off') # turn off 3D Grid
    ax.text(limit,0,0,'x',color='blue', fontsize=10)
    ax.text(0,limit,0,'y',color='blue', fontsize=10)
    ax.text(0,0,limit,'z',color='blue', fontsize=10)
    ax.plot([-limit, limit], [0,0], [0,0], c='0.5', lw=1, zorder=10)
    ax.plot([0,0], [-limit, limit], [0,0], c='0.5', lw=1, zorder=10)
    ax.plot([0,0], [0,0], [-limit, limit], c='0.5', lw=1, zorder=10)

    def update(frame):
        # 1. Clear previous surfaces only, not the whole axes
        # This keeps limits and 3D projection stable
        for artist in ax.collections:
            artist.remove()
        t = frame * T  # Adjust time scale
            
        # Calculate the oscillating probability density
        # prob = |psi1*exp(-iE1t) + psi2*exp(-iE2t)|^2
        # Which simplifies to:
        density = (psi1**2 + psi2**2 + 2*psi1*psi2*np.cos(delta_E * t / hbar))
        
        # Plot ONE surface representing the moving electron cloud
        # Use a single threshold and color (e.g., green or purple)
        max_dens = np.max(density)
        add_iso_surface(ax, density, max_dens * 0.05, 'green', n_points, limit)

        percent=int(frame/N*100)
        pbar.setValue(percent)
        pbar.repaint() 

        widget.canvas.draw_idle()
        
        return ax.collections # Helpful for some backends

        # Store animation as attribute to keep it alive
    ani = FuncAnimation(widget.figure, update, frames=N, interval=25, repeat=True, blit=False)
    widget.canvas.draw()
    return ani

def plot_trans_offline(export_fig, ax, p):
    #parameters
    n1 = p['n1']
    n2 = p['n2']
    l1 = p['l1']
    l2 = p['l2']
    m1 = p['m1']
    m2 = p['m2']
    n_points = p['n_points']
    T = p['T']
    N=p['N']
    hbar=1
    # 1. State 1: 
    psi1 = calculate_psi(n=n1, l=l1, m=m1, n_points=n_points)
    E1 = -1.0**2 / (2 * 1**2) 
    # 2. State 2: 
    psi2 = calculate_psi(n=n2, l=l2, m=m2, n_points=n_points)
    E2 = -1.0**2 / (2 * 2**2)
    delta_E = E2 - E1
    #in case of external magnetic field:
    #dE=m(l) * µ(B) * B
    n=np.max((n1,n2))
    limit = n**2 * 3  # Adjust based on orbital size
    # clearing old figure
    
    export_fig.clear()
    ax = export_fig.add_subplot(111, projection='3d')
    
    def update(frame):
        # 1. Clear previous surfaces only, not the whole axes
        # This keeps limits and 3D projection stable
        for artist in ax.collections:
            artist.remove()
        t = frame * T  # Adjust time scale
  
        ax.cla()
        # Set limits once outside the loop if not using ax.cla()
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.axis('off') # turn off 3D Grid
        ax.text(limit,0,0,'x',color='blue', fontsize=10)
        ax.text(0,limit,0,'y',color='blue', fontsize=10)
        ax.text(0,0,limit,'z',color='blue', fontsize=10)
        ax.plot([-limit, limit], [0,0], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [-limit, limit], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [0,0], [-limit, limit], c='0.5', lw=1, zorder=10)
        # Calculate the oscillating probability density
        # prob = |psi1*exp(-iE1t) + psi2*exp(-iE2t)|^2
        # Which simplifies to:
        density = (psi1**2 + psi2**2 + 2*psi1*psi2*np.cos(delta_E * t / hbar))
        
        # Plot ONE surface representing the moving electron cloud
        # Use a single threshold and color (e.g., green or purple)
        max_dens = np.max(density)
        add_iso_surface(ax, density, max_dens * 0.05, 'green', n_points, limit)

        export_fig.canvas.draw_idle()
        
        return ax.collections # Helpful for some backends

        # Store animation as attribute to keep it alive
    ani = FuncAnimation(export_fig, update, frames=N, interval=25, repeat=False, blit=False)
    export_fig.canvas.draw()
    return ani
   
# General Procedures

def calculate_psi(n,l,m, n_points):
        limit = n**2 * 3  # Adjust based on orbital size
        # 1. Create a Cartesian Meshgrid
        coords = np.linspace(-limit, limit, n_points)
        X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')
        # 2. Convert Cartesian to Spherical for calculation
        R = np.sqrt(X**2 + Y**2 + Z**2)
        # Handle division by zero at the nucleus
        R_safe = np.where(R == 0, 1e-10, R) 
        THETA = np.arccos(Z / R_safe)     # Polar angle [0, pi]
        PHI = np.arctan2(Y, X)            # Azimuthal angle [0, 2pi]
        # 3. Calculate Radial Part (using your SymPy method)
        r_sym = symbols('r')
        # 4. Calculate Spherical Harmonic (Note: SciPy order is m, l, phi, theta)
        # s
        radial_func = lambdify(r_sym, R_nl(n, l, r_sym, Z=1), 'numpy')
        radial_R = radial_func(R)
        Y_m_l= sph_harm_y(l, m, THETA, PHI).real
        psi=radial_R * Y_m_l
        return psi

def add_iso_surface(ax, data, iso_value, color, n_points, limit):
    try:
        # Create Mesh (Vertices and Surfaces)
        verts, faces, normals, values = measure.marching_cubes(data, level=iso_value)      
        # Scale vertices from index coordinates to real coordinates (-limit to limit)
        # verts is an array of (z, y, x) or (i, j, k) indices
        scale = (2 * limit) / (n_points - 1)
        verts_scaled = verts * scale - limit   

        # define light source
        ls = LightSource(azdeg=315, altdeg=45)
        # Mesh-Objekt erstellen
        mesh = Poly3DCollection(
            verts_scaled[faces], 
            alpha=0.5,
            facecolors=color,
            shade=True,
            lightsource=ls
            )     
        mesh.set_edgecolor('none') # no grid lines (smooth surface)
        ax.add_collection3d(mesh)
    except (ValueError, RuntimeError):
        # If the isovalue is outside the data range (no orbital visible)
        pass

def export_to_pov_mesh2(verts, faces, Object, filename):
    with open(filename, "a") as f:
        f.write(f'#declare {Object} = mesh2 {{\n')
        # 1. (Vertices)
        f.write("  vertex_vectors {\n")
        f.write(f"    {len(verts)},\n")
        for v in verts:
            f.write(f"    <{v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}>,\n")
        f.write("  }\n")
        # 2. (Faces)
        f.write("  face_indices {\n")
        f.write(f"    {len(faces)},\n")
        for face in faces:
            f.write(f"    <{face[0]}, {face[1]}, {face[2]}>,\n")
        f.write("  }\n") 
        f.write("inside_vector <0,0,1> \n")  # important for CSG intersection    
        f.write("}\n")
        f.write(f'/////////END {Object} ////////////////////// \n')

def export_to_pov_mesh2_hyb(path,fname,psi,hyb,n_points):
    with open(path,"w") as f:
        f.write(f'//mesh2 object for Orbital {fname} \n')
        f.write(f'//call as {fname}_pos[i] or {fname}_neg[i], index starting with 0 \n')
        f.write(f'#declare {fname}_pos = array[{len(psi)}] \n')
        f.write(f'#declare {fname}_neg = array[{len(psi)}] \n')
        f.write(f'/////////////////////////////////////////////// \n')

    for j in range(len(psi)):  # for all orbitals in vector psi (initial index 0)
        max_val=np.max(np.abs(psi[j]))
        match hyb:
            case 'sp' | 'sp2' | 'sp3':
                threshold = max_val*0.08
                limit = 2**2 * 3 
            case 'dsp2' | 'd2sp3' | 'sd3' | 'sp3d' | 'sp3d3':
                threshold = max_val*0.04    
                limit = 3**2 * 3 
                
        scale=(2*limit) / (n_points - 1) # important for coordinate shift
        #positive part
        verts_p, faces_p, _,_ =measure.marching_cubes(psi[j], level=threshold) # verts_p index from 0 to n_points-1
        verts_p_scaled = verts_p * scale - limit # shift to center orbitals again!
        export_to_pov_mesh2(verts_p_scaled, faces_p, f'{fname}_pos[{j}]', path)
        #negative part
        verts_n, faces_n, _,_ =measure.marching_cubes(-psi[j], level=threshold)
        verts_n_scaled = verts_n * scale - limit
        export_to_pov_mesh2(verts_n_scaled, faces_n, f'{fname}_neg[{j}]',path)
           
def export_to_pov_mesh2_orb(path, fname, psi, threshold, limit, n_points):
    with open(path,"w") as f:
        f.write(f'//mesh2 object for Orbital {fname} \n')
        f.write(f'//call as {fname}_pos or {fname}_neg \n')
        f.write(f'/////////////////////////////////////////////// \n')
    
    scale=(2*limit) / (n_points - 1) # important for coordinate shift
    #pos part
    verts_p, faces_p, _,_ =measure.marching_cubes(psi, level=threshold) # verts_p index from 0 to n_points-1
    verts_p_scaled = verts_p * scale - limit # shift to center orbitals again!
    export_to_pov_mesh2(verts_p_scaled, faces_p,f'{fname}_pos', path)
    #neg part
    verts_n, faces_n, _,_ =measure.marching_cubes(-psi, level=threshold)
    verts_n_scaled = verts_n * scale - limit
    export_to_pov_mesh2(verts_n_scaled, faces_n, f'{fname}_neg', path)
            