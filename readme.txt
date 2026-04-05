# Quantum Orbitals Visualizer

An advanced interactive Python application for visualizing atomic orbitals, spherical harmonics, and wave function dynamics. This tool provides 2D/3D visualizations, animation of quantum transitions, and high-quality exports.

## Features

The application is organized into five specialized modules:

- **Spherical Harmonics**: 
  - Visualize $Y_{lm}$ functions based on $l$ and $m$ quantum numbers.
  - Spatial 3D representation and 2D projection on the sphere.
  - Interactive selection: Click on subplots to enlarge specific $m$-states for a given $l$.
- **Atomic Orbitals**: 
  - Render hydrogenic wave functions by defining $n, l, m$.
  - Features a 3D volumetric view and 2D cross-sections.
  - "Corner Cut" mode to inspect internal radial structures.
  - **POV-Ray Export**: Generates `.inc` files for high-end raytraced rendering.
- **Hybridization**: 
  - Explore orbital hybridization ($sp, sp^2, sp^3, dsp^2, sd^3, d^2sp^3, sp^3d, sp^3d^3$).
  - Browse all individual hybrids within a set (e.g., select specific axial/radial hybrids in $d^2sp^3$).
- **Oscillation**: 
  - Dynamic animation of orbitals as standing waves.
  - Customizable grid points, time steps, and frame counts.
  - Video export functionality.
- **Transition**: 
  - Visualize the quantum leap between two states ($n_1, l_1, m_1 \to n_2, l_2, m_2$).
  - Observe time-dependent dipole moments (e.g., $2s \to 2p$ vs. $2s \to 3s$).
  - Export animations as video files.

## Project Structure

```text
.
├── orbitals2.py          # Main application entry point
├── requirements.txt      # Project dependencies
├── README.md             # Documentation
├── /modules              # Core logic and UI components
│   ├── Basis.py          # basis functions for Hybridization
│   ├── Custom.py         # Specialized plotting routines
│   ├── hybrids.py        # Hybridization matrices and logic
│   ├── window.ui         # Qt Designer UI file
│   └── [Header files]    # Matplotlib widget configurations
│   └── [icon files]      # icons for pushButtons
├── /screenshots          # 
    ├── ...               # examples

## Installation

1. Clone the repository
    git clone https://github.com
    cd OrbitalViewer

2. Install dependencies
    pip install -r requirements.txt

    Requirements
        Python 3.x
        PyQt5
        Matplotlib
        NumPy, SciPy, SymPy
        Scikit-Image (for Marching Cubes)

## Usage

    python3 orbitals2.py

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.