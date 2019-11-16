"""
Module for creating rig control shapes

"""

import maya.cmds as cmds


class Control:
    """class for building rig control shapes"""

    def __init__(
            self,
            prefix='new',
            parent='',
            shape='circle',
            translate_to='',
            rotate_to='',
            scale=1.0,
            lock_channels=['s', 'v']
    ):
        """
        :param prefix: srt, prefix to name new objects
        :param parent: str, object to be parent of new ctrl
        :param shape: str, type of shape adn normal e.g. 'circleX'
        :param translate_to: str, reference object for position
        :param rotate_to: str, reference object for rotation
        :param scale: scale value for size of ctrls
        :param lock_channels: list( str ), list of channels on control to be locked
        :return: None
        """
        # variables
        ctrl_object = None
        circle_normal = [1, 0, 0]

        # make shape for control
        if shape in ['circle', 'circleX']:
            circle_normal = [1, 0, 0]

        elif shape == 'circleY':
            circle_normal = [0, 1, 0]

        elif shape == 'circleZ':
            circle_normal = [0, 0, 1]

        elif shape == 'sphere':

            ctrl_object = cmds.circle(name=prefix + '_ctl', constructionHistory=False, normal=[1, 0, 0], radius=scale)[
                0]
            add_shape = cmds.circle(name=prefix + '_ctl2', constructionHistory=False, normal=[0, 0, 1], radius=scale)[
                0]
            cmds.parent(cmds.listRelatives(add_shape, shapes=1), ctrl_object, relative=1, shape=1)
            cmds.delete(add_shape)

        if not ctrl_object:
            ctrl_object = cmds.circle(name=prefix + '_ctl',
                                      constructionHistory=False,
                                      normal=circle_normal,
                                      radius=scale)[0]

        ctrl_offset = cmds.group(name=prefix + '_offset_grp', empty=1)
        cmds.parent(ctrl_object, ctrl_offset)

        # set control colour
        ctrl_shapes = cmds.listRelatives(ctrl_object, shapes=True)
        for s in ctrl_shapes:
            cmds.setAttr(s + '.overrideEnabled', True)

        if prefix.startswith('L_'):
            for s in ctrl_shapes:
                cmds.setAttr(s + '.overrideColor', 6)

        if prefix.startswith('R_'):
            for s in ctrl_shapes:
                cmds.setAttr(s + '.overrideColor', 13)

        else:
            for s in ctrl_shapes:
                cmds.setAttr(s + '.overrideColor', 22)

        # translate, rotate to parent
        if cmds.objExists(translate_to):
            cmds.delete(cmds.pointConstraint(translate_to, ctrl_object))

        if cmds.objExists(rotate_to):
            cmds.delete(cmds.pointConstraint(rotate_to, ctrl_object))
        # parent control
        if cmds.objExists(parent):
            cmds.parent(ctrl_offset, parent)

        # lock channels

        single_attribute_lock_list = []

        for lockChannel in lock_channels:

            if lockChannel in ['t', 'r', 's']:

                for axis in ['x', 'y', 'z']:
                    at = lockChannel + axis
                    single_attribute_lock_list.append(at)

            else:

                single_attribute_lock_list.append(lockChannel)

        for at in single_attribute_lock_list:
            cmds.setAttr(ctrl_object + '.' + at, l=1, k=0)

        # add public members
        self.c = ctrl_object
        self.off = ctrl_offset
