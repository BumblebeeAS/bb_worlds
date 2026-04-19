# bb_worlds

Gazebo Harmonic (gz-sim) worlds, models, and ROS 2 glue for the BumblebeeAS
multi-vehicle simulator. Home of RobotX / RoboSub / RoboBoat course SDFs plus
the helpers that spawn vehicles and bridge gz ↔ ROS 2.

## Layout

```
bb_worlds/
  bb_worlds/                # Python nodes installed to lib/bb_worlds
    vis_marker_publisher_node.py
  config/                   # YAML spawn configs for vehicles
  hooks/                    # GZ_SIM_RESOURCE_PATH env hooks
  launch/                   # ROS 2 launch files
  media/                    # Textures / imagery used by models
  models/                   # SDF models, grouped by competition year
    robotx24/
    robotx26/               # 2026 assets — see below
    robosub24/ … etc.
  src/
    pose_tf_broadcaster.cc  # gz Pose_V → /tf
    robotx_gz/              # Python helpers (bridges.py, launch.py, model.py)
  worlds/                   # .world / .sdf world files
  CMakeLists.txt, package.xml
```

The ROS nodes that drive the RobotX 2026 beacon and incident system now
live in `bb_robotx_dashboard` (see its README), which also owns the launch
file that wires them up. `bb_worlds` keeps the world-file and SDF model
assets only.

## Build

```bash
colcon build --symlink-install --packages-select bb_worlds
source install/setup.bash
```

## RobotX 2026 assets

`bb_worlds` ships the SDF geometry for the 2026 autonomy challenge.
Runtime behaviour (LED state machine, incident spawn/clear/zone check)
and the launch wiring live in `bb_robotx_dashboard` — see that package's
README for states, params, services, and the ROS contract.

### Floating dock — `models/robotx26/floating_dock_simple`

Simplified Task 3 (Coordinated Logistics) platform: static 2m × 2m deck
with three colored disks (~65cm diameter) on top. The red/green/blue
tins are **baked into the dock model as child visuals** (they reference
`model://robotx24/tins/<color>/<color>_tin.glb` with a π/2 X-rotation to
bring the Y-up mesh into the world's Z-up frame). Embedding them in the
dock model — rather than spawning each tin as an independent include —
keeps them locked to the deck and the poses/yaws varied so they don't
sit dead-centre on the color circles.

### Safe Passage beacon — four SDF models

| Model | Role |
|---|---|
| `models/robotx26/led_beacon` | Buoy base + dark "off" LED (always visible) |
| `models/robotx26/led_beacon_red` | Red emissive cylinder, parked at z=-1000 |
| `models/robotx26/led_beacon_green` | Green cylinder, parked at z=-1000 |
| `models/robotx26/led_beacon_blue` | Blue cylinder, parked at z=-1000 |

The driver that teleports the correct color into view is
`bb_robotx_dashboard.nodes.led_beacon_driver`; see the dashboard README
for the state table, SEQUENCE timeline, and params.

### Incident cube template — `models/robotx26/incident_cube/model.sdf`

Magenta cube + translucent inflation ring, used by RoboCommand's
Disruptive Tier. Static — it sits wherever `incident_manager` spawned
it. If you want it somewhere else, despawn and respawn. The SDF is a
**template** with two placeholders that
`bb_robotx_dashboard.nodes.incident_manager` substitutes at spawn time:

- `{radius}` — inflation ring radius (m)
- `{model_name}` — gz model name (e.g. `incident_obstacle_0`)

Spawned model names match the `.*obstacle.*` regex in
`filters/scripts/robotx/robotx_sim_obstacles_converter.py`, so the cube
lands on `/robotx/detections` with no extra glue.

## Launch

The RobotX 2026 driver nodes are started via
`bb_robotx_dashboard`'s `launch/robotx_2026_sim.launch.py` (see that
package's README). `bb_worlds` only ships the world file + SDF assets
that the driver operates on.

## `robotx_gz` helpers (`src/robotx_gz/`)

Python helpers used by the launch system. Most relevant for extending the
sim:

- `bridges.py` — factory functions returning `Bridge` records (one per ros_gz
  topic). Reuse `set_pose(name)` and `robotx_obstacle_pose(name)` when adding
  more dynamic models.
- `launch.py` — `simulation(world_name, ...)` launches gz-sim;
  `spawn(sim_mode, world_name, models, robot)` inserts a `Model` at runtime
  via `ros_gz_sim create`; `competition_bridges(world_name, ...)` wires up
  task-specific topic bridges.
- `model.py` — `Model` class + YAML loader used by the vehicle configs under
  `config/`.

## Adding a new model

1. Drop the files under `models/<category>/<name>/` (at minimum `model.sdf`
   and `model.config`). Static visual-only models can follow the pattern of
   `models/robotx24/helipad`.
2. `colcon build --packages-select bb_worlds` — the existing
   `install(DIRECTORY models ...)` rule installs anything under `models/`.
3. Either add an `<include>` to a world SDF, or spawn at runtime via
   `robotx_gz.launch.spawn(...)` or `ros_gz_sim create`.

## Known quirks

- **`incident_cube/model.sdf` contains `{radius}` / `{model_name}`
  placeholders** and will not load in Gazebo's GUI model preview directly.
  It is only valid after `incident_manager.py` (in `bb_robotx_dashboard`)
  substitutes the tokens at spawn time.
- **Tins are child visuals inside `floating_dock_simple/model.sdf`, not
  separate models.** If you edit the dock geometry, also adjust the tin
  visual poses so they stay resting on the deck top.
