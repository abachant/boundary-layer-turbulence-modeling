"""Functionality for working with the JHTDB."""

import pyJHTDB
import numpy as np

# Get velocity and pressure gradients and Hessians for all points and time average

# Adapted from example notebook

# Note my token is in my home directory at ~/.config/JHTDB/auth_token.txt

# load shared library
lTDB = pyJHTDB.libJHTDB()
# initialize webservices
lTDB.initialize()

dataset = "transition_bl"

spatialInterp = 0  # no spatial interpolation
temporalInterp = 0  # no time interpolation
FD4NoInt = 40  # 4th-order FD, no spatial interpolation

# Database domain size and number of grid points
x_min = 30.2185
x_max = 1000.0650
y_min = 0.0036
y_max = 26.4880
z_min = 0.0000
z_max = 240.0000
d99i = 0.9648
d99f = 15.0433

nx = 3320
ny = 224
nz = 2048

# Database time duration
Ti = 0
Tf = Ti + 1175
dt = 0.25
all_times = np.arange(Ti, Tf + dt, dt)

# Create surface
# nix = round(nx / 4)
# niz = round(nz / 4)
nix = 10
niy = 10
niz = 1
x = np.linspace(x_min, x_max, nix)
all_x = np.linspace(x_min, x_max, nx)
all_y = np.linspace(y_min, y_max, ny)
all_z = np.linspace(z_min, z_max, nz)
mid_z = 120.0
mid_x = (x_max - x_min) / 2 + x_min
mid_y = (y_max - y_min) / 2 + y_min
# z = np.linspace(z_min, z_max, niz)
z = np.array([120.0])
# y = d99i
y = np.linspace(y_min, y_max, niy)

[X, Y] = np.meshgrid(x, y)
points = np.zeros((nix, niy, 3))
points[:, :, 0] = X.transpose()
points[:, :, 1] = Y.transpose()
points[:, :, 2] = 120.0
# points[:, :, 2] = 120.0

all_points = np.meshgrid(all_x, all_y, all_z)


def get_data_at_points(t, points, quantity="VelocityGradient"):
    # Convert points to 2-D array with single precision values
    points = np.array(points, dtype="float32")
    print(f"Requesting {quantity} at {len(points)} points")
    if t not in all_times:
        raise ValueError("Time not in array and interpolation not enabled")
    res = lTDB.getData(
        t,
        points,
        data_set="transition_bl",
        sinterp=FD4NoInt,
        tinterp=temporalInterp,
        getFunction=f"get{quantity}",
    )
    return res
