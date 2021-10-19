"""Functionality for working with the JHTDB."""

from numbers import Number

import matplotlib

matplotlib.use("nbAgg")

import pyJHTDB
import numpy as np
from tqdm.auto import tqdm
from sqlitedict import SqliteDict

# Get velocity and pressure gradients and Hessians for all points and time average

# Adapted from example notebook

# Note my token is in my home directory at ~/.config/JHTDB/auth_token.txt

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

all_points = np.meshgrid(all_x, all_y, all_z)


def get_data_at_points(
    t, points, quantity="VelocityGradient", verbose=False, cache=True
):
    # Convert points to 2-D array with single precision values
    points = np.array(points, dtype="float32")
    if isinstance(t, Number):
        t = np.array([t])
    t = np.array(t, dtype="float32")
    res = []
    _cache = SqliteDict("data/jhtdb-transitional-bl/cache.db", autocommit=True)
    all_params = []
    # TODO: Refactor to query batches of points at a time for efficiency
    non_cached_points = {}
    cached = {}
    for ti in t:
        if ti not in all_times:
            raise ValueError(
                f"Time {ti} not in array and interpolation not enabled"
            )
        for pi in points:
            all_params.append([ti, pi])
    for ti, pi in tqdm(all_params):
        if verbose:
            print(f"Getting {quantity} at {pi} for t={ti}")
        key = f"{quantity}-{ti}-{pi}"
        if key in _cache:
            res.append(_cache[key])
        else:
            resi = lTDB.getData(
                ti,
                np.array([pi], dtype="float32"),
                data_set="transition_bl",
                sinterp=FD4NoInt,
                tinterp=temporalInterp,
                getFunction=f"get{quantity}",
            )
            if cache:
                _cache[key] = resi
            res.append(resi)
    return np.asarray(res)


def get_data_at_points_for_all_time(
    points, quantity="VelocityGradient", verbose=False, cache=True
):
    return get_data_at_points(
        all_times, points, quantity=quantity, verbose=verbose, cache=cache
    )


def get_mean_data_at_points(
    points,
    quantity="VelocityGradient",
    verbose=False,
    cache=True,
    cache_all_times=False,
):
    _cache = SqliteDict(
        "data/jhtdb-transitional-bl/cache-mean.db", autocommit=True
    )
    res = []
    for pi in tqdm(points):
        key = f"{quantity}-{pi}"
        if key in _cache:
            res.append(_cache[key])
        else:
            vals = get_data_at_points_for_all_time(
                [pi], quantity=quantity, cache=cache_all_times, verbose=verbose
            )
            ri = vals.mean(axis=0)
            res.append(ri)
            if cache:
                _cache[key] = ri
    return np.asarray(res)
