"""
transform @ utils
Functions to manipulate and create transforms
"""

import maya.cmds as cmds
from . import name

def make_offset_grp(object, prefix=''):
    """
    make offset group for  given object
    :param object: transform object to be offset
    :param prefix: srt, prefix to name new objects
    :return: str, name of new offset group
    """

    if not prefix:
        prefix = name.remove_suffix(object)

    offset_grp = cmds.group(name=prefix+'_offset_grp', empty=True)

    # if there is a parent we need to parent the offset group to that
    object_parent = cmds.listRelatives(object, parent=True)
    if object_parent:
        cmds.parent(offset_grp, object_parent[0])

    # match transform and scale
    cmds.delete(cmds.parentConstraint(object, offset_grp))
    cmds.delete(cmds.scaleConstraint(object, offset_grp))

    # parent object under offset
    cmds.parent(object, offset_grp)

    return offset_grp