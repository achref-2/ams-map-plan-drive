import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RVIZ = os.path.join(ROOT, 'rviz', 'exploration.rviz')
EXPLORE = os.path.join(ROOT, 'config', 'explore_params.yaml')

def generate_launch_description():
    world = LaunchConfiguration('world')
    tb3 = get_package_share_directory('turtlebot3_gazebo')
    slam = get_package_share_directory('slam_toolbox')
    nav2 = get_package_share_directory('nav2_bringup')
    nav2_params = os.path.join(ROOT, 'config', 'nav2_params.yaml')
    slam_params = os.path.join(slam, 'config', 'mapper_params_online_async.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='turtlebot3_world'),
        DeclareLaunchArgument('x_pose', default_value='-2.0'),
        DeclareLaunchArgument('y_pose', default_value='-0.5'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('explore', default_value='true'),

        GroupAction([
            IncludeLaunchDescription(PythonLaunchDescriptionSource(
                [os.path.join(tb3, 'launch', ''), world, '.launch.py']),
                launch_arguments={'x_pose': LaunchConfiguration('x_pose'),
                                  'y_pose': LaunchConfiguration('y_pose')}.items()),
        ]),

        GroupAction([
            IncludeLaunchDescription(PythonLaunchDescriptionSource(
                os.path.join(slam, 'launch', 'online_async_launch.py')),
                launch_arguments={'use_sim_time': 'true',
                                  'slam_params_file': slam_params}.items()),
        ]),

        GroupAction([
            IncludeLaunchDescription(PythonLaunchDescriptionSource(
                os.path.join(nav2, 'launch', 'navigation_launch.py')),
                launch_arguments={'use_sim_time': 'true',
                                  'params_file': nav2_params}.items()),
        ]),

        TimerAction(period=20.0, actions=[Node(
            package='explore_lite', executable='explore', name='explore_node',
            output='screen', parameters=[EXPLORE, {'use_sim_time': True}],
            condition=IfCondition(LaunchConfiguration('explore')))]),

        Node(package='rviz2', executable='rviz2', arguments=['-d', RVIZ],
             parameters=[{'use_sim_time': True}], output='screen',
             condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
