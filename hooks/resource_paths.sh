ament_prepend_unique_value GZ_SIM_RESOURCE_PATH "$AMENT_CURRENT_PREFIX/share/"
ament_prepend_unique_value GZ_SIM_RESOURCE_PATH "$AMENT_CURRENT_PREFIX/share/robotx_gazebo_worlds/worlds"
ament_prepend_unique_value GZ_SIM_RESOURCE_PATH "$AMENT_CURRENT_PREFIX/share/robotx_gazebo_worlds/models"
ament_prepend_unique_value GZ_SIM_RESOURCE_PATH "~/.simulation-gazebo/models"
ament_prepend_unique_value GZ_SIM_RESOURCE_PATH "~/.simulation-gazebo/worlds"
ament_prepend_unique_value GZ_SIM_SYSTEM_PLUGIN_PATH "$AMENT_CURRENT_PREFIX/lib"

ament_prepend_unique_value LD_LIBRARY_PATH "$AMENT_CURRENT_PREFIX/lib"
