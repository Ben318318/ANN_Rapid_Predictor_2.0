import os
import sys
import json
import math
import argparse
import numpy as np

# ---- Configure Mayavi/Qt BEFORE importing mlab ----
import os

# Configure Qt backend
os.environ['ETS_TOOLKIT'] = 'qt'
os.environ['QT_API'] = 'pyqt5'
os.environ['QT_QPA_PLATFORM'] = 'windows'  # Force Windows backend
os.environ['MAYAVI_BACKEND'] = 'auto'

# Initialize Qt
from PyQt5.QtWidgets import QApplication

# Create Qt application
app = QApplication.instance()
if app is None:
    app = QApplication([''])

# Now configure and import mayavi
from tvtk.api import tvtk
from mayavi import mlab

# Configure rendering
mlab.options.offscreen = False  # Use interactive mode
mlab.options.backend = 'auto'

# Create a figure with a white background
engine = mlab.get_engine()
if engine.current_scene is None:
    fig = mlab.figure(size=(1024, 768), bgcolor=(1, 1, 1))


pulse_widths = [60, 75, 90, 105, 120, 135, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500]

def mkdirp(dir):
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)

def read_tract_file(path):
    fibers = []
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            nums = [float(x) for x in parts]
            if len(nums) % 3 != 0:
                raise ValueError(f"Line {i+1} in tract file does not have a 3N number of floats")
            pts = [(nums[j], nums[j+1], nums[j+2]) for j in range(0, len(nums), 3)]
            fibers.append(pts)
    return fibers

def load_thresholds(path):
    with open(path) as f:
        data = json.load(f)

    thresholds = []
    for pw in pulse_widths:
        key = str(pw/1000)  # e.g., "0.06"
        row = []
        # data[key] is a dict: { "0": thr0, "1": thr1, ... }
        for fib_ind in range(len(data[key])):
            row.append(data[key][str(fib_ind)])
        thresholds.append(row)
    return thresholds

def _bounds_from_fibers(fibers):
    if not fibers:
        return (0, 1), (0, 1), (0, 1)
    xs = [p[0] for fib in fibers for p in fib]
    ys = [p[1] for fib in fibers for p in fib]
    zs = [p[2] for fib in fibers for p in fib]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

def plot_electrode_cube(bounds, color=(0, 0, 1), opacity=0.35):
    """Draw a translucent cuboid via a triangular mesh in Mayavi.

    bounds: [[xmin, xmax], [ymin, ymax], [zmin, zmax]]
    """
    (xmin, xmax), (ymin, ymax), (zmin, zmax) = bounds
    vx = np.array([xmin, xmax, xmax, xmin, xmin, xmax, xmax, xmin], dtype=float)
    vy = np.array([ymin, ymin, ymax, ymax, ymin, ymin, ymax, ymax], dtype=float)
    vz = np.array([zmin, zmin, zmin, zmin, zmax, zmax, zmax, zmax], dtype=float)

    # 12 triangles (two per face) with vertices indexed 0..7
    tris = np.array([
        [0,1,2], [0,2,3],   # bottom z=zmin
        [4,5,6], [4,6,7],   # top    z=zmax
        [0,1,5], [0,5,4],   # front  y=ymin
        [2,3,7], [2,7,6],   # back   y=ymax
        [1,2,6], [1,6,5],   # right  x=xmax
        [0,3,7], [0,7,4],   # left   x=xmin
    ], dtype=int)

    # Create points and triangles
    points = tvtk.Points()
    points.from_array(np.column_stack([vx, vy, vz]))
    
    triangles = tvtk.CellArray()
    triangles.from_array(tris)
    
    # Create mesh data
    mesh = tvtk.PolyData()
    mesh.points = points
    mesh.polys = triangles
    
    # Add scalars
    scalars = np.ones(len(vx), dtype=np.float32)  # Explicitly use float32
    s = tvtk.FloatArray()
    s.from_array(scalars)
    s.name = 'scalars'
    mesh.point_data.scalars = s
    
    # Create the visualization
    src = mlab.pipeline.add_dataset(mesh)
    surf = mlab.pipeline.surface(src, color=color, opacity=opacity)

def color_tuple(name):
    if isinstance(name, tuple):
        return name
    # simple map for 'r','k','blue' compatibility
    m = {
        'r': (1, 0, 0),
        'k': (0, 0, 0),
        'blue': (0, 0, 1),
        'red': (1, 0, 0),
        'black': (0, 0, 0),
    }
    return m.get(name, (0.2, 0.2, 0.2))

def render_scene_mayavi(fibers, thresholds_row, voltage_limit, leftLeadPos,
                        title='', save_png=None, interactive=False):
    """
    thresholds_row: list of thresholds for a SINGLE pulse width (len == n_fibers)
    If interactive=True, show rotatable window; else just save PNG if path given.
    """
    # Batch rendering can be offscreen; interactive must be onscreen
    mlab.options.offscreen = not interactive

    fig = mlab.figure(bgcolor=(1, 1, 1), size=(900, 900))

    # Plot fibers
    activated = []
    for i, fib in enumerate(fibers):
        thr = math.inf
        if i < len(thresholds_row) and thresholds_row[i] is not None:
            try:
                thr = float(thresholds_row[i])
            except Exception:
                thr = math.inf
        col = color_tuple('r' if thr < voltage_limit else 'k')
        if thr < voltage_limit:
            activated.append(i)

        xs = [p[0] for p in fib]
        ys = [p[1] for p in fib]
        zs = [p[2] for p in fib]
        # tube_radius gives nicer 3D lines; keep small for performance
        # Use simpler tube filter and lower quality settings to reduce texture/memory usage
        tube = mlab.plot3d(xs, ys, zs, color=col, tube_radius=0.08, line_width=1.0, figure=fig,
                          tube_sides=6, opacity=0.99)  # Slightly transparent to reduce texture load
        tube.module_manager.scalar_lut_manager.show_scalar_bar = False

    # Electrode cuboid (your leftLeadPos uses bounds [[x0,x1],[y0,y1],[z0,z1]])
    plot_electrode_cube(leftLeadPos, color=color_tuple('blue'), opacity=0.40)

    # Scene helpers: outline of global bounds + axes gizmo
    bx, by, bz = _bounds_from_fibers(fibers)
    # Outline box around data bounds
    mlab.outline(extent=(bx[0], bx[1], by[0], by[1], bz[0], bz[1]), color=(0, 0, 0), figure=fig)
    mlab.orientation_axes(figure=fig)

    # Camera: look at center of data
    cx = 0.5 * (bx[0] + bx[1])
    cy = 0.5 * (by[0] + by[1])
    cz = 0.5 * (bz[0] + bz[1])
    mlab.view(azimuth=45, elevation=65, distance='auto', focalpoint=(cx, cy, cz), figure=fig)
    mlab.title(title, size=0.35, height=0.96, color=(0, 0, 0), figure=fig)

    if save_png:
        mlab.savefig(save_png, figure=fig, magnification=2)  # ~1800x1800
    if interactive:
        mlab.show()   # rotatable window

    mlab.close(fig)   # close regardless to match your per-PW lifecycle
    return activated

def plot_activation_mayavi(fibers, pulse_widths, thresholds, voltage_limit, out_folder, leftLeadPos, interactive_pw=None):
    os.makedirs(out_folder, exist_ok=True)
    n_fibers = len(fibers)
    n_thr_rows = len(thresholds[0]) if thresholds else 0
    if n_thr_rows < n_fibers:
        print(f"Warning: thresholds provided for {n_thr_rows} fibers but tract has {n_fibers}. Missing => non-activated.")

    activation_summary = {}

    if interactive_pw is not None:
        # Render a single PW interactively
        pw_idx = int(interactive_pw)
        if pw_idx < 0 or pw_idx >= len(pulse_widths):
            raise ValueError(f"--interactive_pw {pw_idx} out of range [0, {len(pulse_widths)-1}]")
        pw = pulse_widths[pw_idx]
        row = thresholds[pw_idx] if pw_idx < len(thresholds) else []
        title = f"Pulse width: {pw} μs (index {pw_idx}) — interactive"
        print(f"Rendering interactive view for PW index {pw_idx} (PW={pw})...")
        activated = render_scene_mayavi(
            fibers, row, voltage_limit, leftLeadPos,
            title=title, save_png=None, interactive=True
        )
        activation_summary[str(pw)] = activated
    else:
        # Batch over all PWs (no GUI), save PNGs
        for pw_idx, pw in enumerate(pulse_widths):
            row = thresholds[pw_idx] if pw_idx < len(thresholds) else []
            title = f"Pulse width: {pw} μs (index {pw_idx})"
            out_png = os.path.join(out_folder, f"activation_pw_{pw_idx}.png")
            print(f"Rendering {out_png} ...")
            activated = render_scene_mayavi(
                fibers, row, voltage_limit, leftLeadPos,
                title=title, save_png=out_png, interactive=False
            )
            print(f"Saved {out_png} (activated: {len(activated)})")
            activation_summary[str(pw)] = activated

    # write activation summary
    with open(os.path.join(out_folder, 'activation_summary.json'), 'w') as f:
        json.dump({'pulse_widths': pulse_widths, 'voltage_limit': voltage_limit, 'activated': activation_summary}, f, indent=2)
    print(f"Wrote activation summary to {os.path.join(out_folder, 'activation_summary.json')}")

def main():
    parser = argparse.ArgumentParser(description="Plot activation by pulse width using Mayavi (rotatable interactive or batch).")
    parser.add_argument("tract_file")
    parser.add_argument("thresholds_json")
    parser.add_argument("voltage_limit", type=float)
    parser.add_argument("conductivity", choices=["anisotropic", "isotropic"])
    parser.add_argument("out_folder")
    parser.add_argument("--interactive_pw", type=int, default=None,
                        help="Render a single pulse width (index) in a rotatable window")
    args = parser.parse_args()

    mkdirp(args.out_folder)

    if args.conductivity == "anisotropic":
        leftLeadPos = [[167,161],[223,222],[143,159]]
    else:  # isotropic
        leftLeadPos = [[0,0],[0,0],[0,10]]

    fibers = read_tract_file(args.tract_file)
    thresholds = load_thresholds(args.thresholds_json)

    print(f"Read {len(fibers)} fibers, {len(pulse_widths)} pulse widths. Voltage limit={args.voltage_limit}")
    plot_activation_mayavi(
        fibers, pulse_widths, thresholds, args.voltage_limit, args.out_folder,
        leftLeadPos, interactive_pw=args.interactive_pw
    )

if __name__ == '__main__':
    main()
