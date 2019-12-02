"""
joint utils @ utils
utilities for working with joints
"""
import maya.cmds as cmds


def list_hierarchy(
        top_joint,
        with_end_joints=True,
                    ):
    """
    list joint hierarchy starting with top joint
    :param top_joint: str, root joint of listed hierarchy
    :param with_end_joints: bool, true - include end joints
    :return: list [str ], list of joints in hierarchy
    """
    listed_joints = cmds.listRelatives(top_joint, type='joint', ad=True)
    listed_joints.append(top_joint)
    listed_joints.reverse()

    complete_joints = listed_joints[:]
    # without the [:] we would just be creating an instance of listed_joints. all changes to one would happen to both

    if not with_end_joints:
        complete_joints = [j for j in listed_joints if cmds.listRelatives(j, type='joint', children=True)]

    return complete_joints
