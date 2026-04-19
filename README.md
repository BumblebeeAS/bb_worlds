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

The ROS nodes that drive the RobotX 2026 beacon and dynamic incidents now
live in `bb_robotx_dashboard` (see its README), which also owns the launch
file that wires them up. `bb_worlds` keeps the world-file and SDF model
assets only.

## Build

```bash
colcon build --symlink-install --packages-select bb_worlds
source install/setup.bash
```

## RobotX 2026 features

Three new simulation features for the 2026 autonomy challenge. They layer onto
`worlds/robotx_2026_sg_river.world` and are controlled via ROS 2 topics/services
(driven by `bb_robotx_dashboard` or by hand with `ros2 topic pub` /
`ros2 service call`).

### 1. Floating dock — `models/robotx26/floating_dock_simple`

Simplified Task 3 (Coordinated Logistics) platform: static 2m × 2m deck with
three colored disks (~65cm diameter) on top. The red/green/blue tins are
**baked into the dock model as child visuals** (they reference
`model://robotx24/tins/<color>/<color>_tin.glb` with a π/2 X-rotation to
bring the Y-up mesh into the world's Z-up frame). Embedding them in the dock
model — rather than spawning each tin as an independent include — keeps
them locked to the deck and the poses/yaws varied so they don't sit dead-
centre on the color circles.

No runtime control surface — purely geometric.

### 2. Safe Passage beacon — 5 controllable LED states

Four SDF models make up the beacon:

| Model | Purpose |
|---|---|
| `models/robotx26/led_beacon` | Buoy base + dark "off" LED (always present) |
| `models/robotx26/led_beacon_red` | Red emissive cylinder, parked at z=-1000 |
| `models/robotx26/led_beacon_green` | Green cylinder, parked at z=-1000 |
| `models/robotx26/led_beacon_blue` | Blue cylinder, parked at z=-1000 |

The driver that teleports the correct color into view on each state change
lives in **`bb_robotx_dashboard.nodes.led_beacon_driver`**.

| `state` constant | Effect |
|---|---|
| `OFF` (0) | All colored LEDs hidden; base's dark LED visible |
| `FLASH_RED` (1) | Red toggles in/out every 1 s (per handbook) |
| `FLASH_GREEN` (2) | Green toggles in/out every 1 s |
| `FLASH_BLUE` (3) | Blue toggles in/out every 1 s |
| `STEADY_BLUE` (4) | Blue stays visible |
| `SEQUENCE` (5) | 5 s GREEN intro, then repeats `1 s first_color, 1 s off, 1 s second_color, 2 s off`. `first_color` / `second_color` are carried on the same message. |

For `SEQUENCE`, the same message also carries `first_color` and
`second_color` (each one of `COLOR_OFF / COLOR_RED / COLOR_GREEN /
COLOR_BLUE`). The cadence is fixed at 1 s on / 1 s off / 1 s on / 2 s off
after a 5 s green intro — tuned in the driver, not on the message.

QoS on the subscriber is reliable + transient-local, so a late-joining
publisher's last state is picked up.

**Driver params** (`ros2 param` on `/led_beacon_driver`):
- `world_name` — world hosting the `UserCommands` service (default `robotx_2026_sg_river`)
- `beacon_x`, `beacon_y` (m) — world-frame position of the beacon
- `beacon_z` (m) — top-of-buoy height where the active LED sits (default 0.365)
- `tick_period_s` — how often the driver re-evaluates visibility (default 0.1)
- `red_model`, `green_model`, `blue_model` — model names (default `led_beacon_<color>`)
- `set_pose_timeout_ms` — per-call timeout on the `gz service` subprocess (default 500)

The full flashing-mechanism writeup (why it's teleport-to-hide, the elapsed-
time state machine, the SEQUENCE timeline diagram) lives in
`bb_robotx_dashboard/README.md` under *How the LED beacon flashing works*.

### 3. Dynamic incident response

For RoboCommand's Disruptive Tier: spawn a magenta cube surrounded by a
translucent inflation ring (10 m radius by default — the handbook standoff
distance). The cube drifts at a constant heading and speed.

**Template model:** `models/robotx26/incident_cube/model.sdf` uses two
placeholders that `incident_manager.py` substitutes before spawning:

- `{radius}` — inflation ring radius (m)
- `{model_name}` — gz model name (e.g. `incident_obstacle_0`)

Model names match the `.*obstacle.*` regex in
`filters/scripts/robotx/robotx_sim_obstacles_converter.py`, so the cube lands
on `/robotx/detections` with no extra glue.

The manager node lives in **`bb_robotx_dashboard.nodes.incident_manager`**.
It exposes:

| Interface | Name | Type |
|---|---|---|
| Spawn | `/robotx/incident/spawn` | `bb_robotx_msgs/srv/SpawnIncident` |
| Clear | `/robotx/incident/clear` | `bb_robotx_msgs/srv/ClearIncident` |

`SpawnIncident.Request` fields: `incident_id` (opaque handle),
`pose` (initial world pose), `heading_deg`, `speed_mps`, `inflation_radius_m`.
A bounded slot pool (default 4) maps each `incident_id` to a pre-bridged
`incident_obstacle_<slot>` model name. Motion is a 20 Hz linear advance
published on `/incident_obstacle_<slot>/set_pose`.

`SpawnIncident.Response` also returns `affected_vehicles` (string list) and
`affected_distances_m` (float list) — vehicles configured in `vehicle_names`
/ `vehicle_frames` whose TF pose is within `inflation_radius_m` of the
spawn point at the moment of the call.

Spawn shells out to `ros2 run ros_gz_sim create`; clear uses
`gz service /world/<w>/remove` — those factory services aren't bridged by
`ros_gz_bridge`.

**Manager params** (`ros2 param` on `/incident_manager`):
- `world_name` (default `robotx_2026_sg_river`)
- `tick_hz` (default 20) — rate at which moving cubes have their pose pushed
- `num_slots` (default 4 — must match the bridge pool size in
  `bb_robotx_dashboard/launch/robotx_2026_sim.launch.py`)
- `parent_frame` (default `world`) — fixed frame for the TF lookup
- `vehicle_names` (default `["asv5", "auv4"]`) — labels returned in the response
- `vehicle_frames` (default `["asv5", "auv4"]`) — TF child frames to look up
- `tf_lookup_timeout_s` (default 0.5)

## Launch

The RobotX 2026 driver nodes are started via
`bb_robotx_dashboard`'s `launch/robotx_2026_sim.launch.py` (see that
package's README). `bb_worlds` only ships the world file + SDF assets that
the driver operates on.

## Verification

With the `robotx_2026_sg_river` world running and the sim-side driver launch
up, verify each feature with plain ROS 2 CLI calls (no dashboard needed):

```bash
# Beacon — flashing and steady
ros2 topic pub --once /robotx/beacon/state bb_robotx_msgs/msg/BeaconState "{state: 1}"  # flash red
ros2 topic pub --once /robotx/beacon/state bb_robotx_msgs/msg/BeaconState "{state: 4}"  # steady blue

# Beacon — SEQUENCE (5 s green intro, then 1 s RED / 1 s off / 1 s BLUE / 2 s off, repeat)
ros2 topic pub --once /robotx/beacon/state bb_robotx_msgs/msg/BeaconState \
  "{state: 5, first_color: 1, second_color: 3}"

# Incident — spawn near the ASV/AUV midpoint (135,-127 / 130,-135 in the world)
ros2 service call /robotx/incident/spawn bb_robotx_msgs/srv/SpawnIncident \
  "{incident_id: 'a', pose: {position: {x: 133.0, y: -131.0, z: 0.0}}, heading_deg: 45.0, speed_mps: 0.5, inflation_radius_m: 10.0}"

ros2 topic echo /robotx/detections    # cube appears in the detection stream

ros2 service call /robotx/incident/clear bb_robotx_msgs/srv/ClearIncident "{incident_id: 'a'}"
```

## ROS contract (summary)

| Surface | Name | Type | Direction |
|---|---|---|---|
| LED command | `/robotx/beacon/state` | `bb_robotx_msgs/msg/BeaconState` | → sim |
| Incident spawn | `/robotx/incident/spawn` | `bb_robotx_msgs/srv/SpawnIncident` | → sim |
| Incident clear | `/robotx/incident/clear` | `bb_robotx_msgs/srv/ClearIncident` | → sim |
| Obstacle detections (existing pipeline) | `/robotx/detections` | `bb_perception_msgs/msg/DetectedObject3DArray` | sim → stack |

## How the RobotX 2026 pieces fit together

```
       bb_robotx_dashboard                                         bb_worlds
       ───────────────────                                         ──────────
                                                                  world file
   FastAPI backend                                                 robotx_2026_sg_river.world
   (laptop)
        │                                                          SDF models
        ▼                                                          models/robotx26/
   /robotx/beacon/state  ──▶  led_beacon_driver      ──gz service──▶ floating_dock_simple/
   /robotx/incident/*    ──▶  incident_manager       ──gz service──▶ led_beacon / _red / _green / _blue
                                                                     incident_cube/    (template)
```

`bb_robotx_dashboard` owns all behaviour (subscribers, services, state
machines, subprocess calls). `bb_worlds` owns only the static geometry and
the worlds that reference it.

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

- **`rosidl_generate_interfaces` lives inside `if(BUILD_TESTING)`** in the
  `bb_robotx_msgs` CMakeLists — this is a pre-existing quirk. If the new
  `BeaconState` / `SpawnIncident` / `ClearIncident` interfaces stop
  generating, check that gate first.
- **`incident_cube/model.sdf` contains `{radius}` / `{model_name}`
  placeholders** and will not load in Gazebo's GUI model preview directly. It
  is only valid after `incident_manager.py` substitutes the tokens at spawn
  time.
- **Tins are child visuals inside `floating_dock_simple/model.sdf`, not
  separate models.** If you edit the dock geometry, remember to also adjust
  the tin visual poses so they stay resting on the deck top.
