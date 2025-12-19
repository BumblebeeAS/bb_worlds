cmake_minimum_required(VERSION 3.10.2 FATAL_ERROR)
project(bb_worlds)

find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()
#============================================================================
# Hooks
ament_environment_hooks(
  "${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")
ament_environment_hooks("hooks/resource_paths.dsv.in")
ament_environment_hooks("hooks/resource_paths.sh")

ament_python_install_package(
  robotx_gz
  PACKAGE_DIR src/robotx_gz
)

# Install bb_worlds Python package
ament_python_install_package(${PROJECT_NAME})

add_executable(pose_tf_broadcaster src/pose_tf_broadcaster.cc)
ament_target_dependencies(pose_tf_broadcaster
  geometry_msgs
  rclcpp
  tf2
  tf2_ros
  tf2_msgs
)

# Resources
install(TARGETS
  pose_tf_broadcaster
  DESTINATION lib/${PROJECT_NAME})

#============================================================================
# Resources
install(DIRECTORY
  config
  launch
  media
  models
  worlds
  DESTINATION share/${PROJECT_NAME})

install(PROGRAMS
  ${PROJECT_NAME}/vis_marker_publisher_node.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
