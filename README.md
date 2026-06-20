# BB Worlds

Models, worlds and assets used for simulations and live visualizations.

World SDF files live under `worlds/`, launch wrappers live under `launch/`. The package installs environment hooks that add its share directory to `GZ_SIM_RESOURCE_PATH`.

## Usage

Build and source the workspace, then pass a world name to the simulator or use one of the package launch files.

If Gazebo cannot resolve a world or model:

1. Check that the workspace setup file is sourced.
2. Inspect `GZ_SIM_RESOURCE_PATH`.
3. Confirm that referenced model packages, including DAVE assets, are built.
