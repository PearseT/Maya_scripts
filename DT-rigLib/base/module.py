"""module for organising rig structure"""

import maya.cmds as cmds
from . import control

scene_object_type = 'rig'


class Base():
    """class for building base rig structures"""

    def __init__(self,
                 character_name='new',
                 scale=1.0,
                 ):

        """
        :param character_name: name of rigged character
        :param scale: base scale of rig
        :return: None
        """

        self.topGrp = cmds.group(name=character_name + '_rig_grp', empty=True)
        self.rigGrp = cmds.group(name='rig_grp', parent=self.topGrp, empty=True)
        self.modelGrp = cmds.group(name='model_grp', parent=self.topGrp, empty=True)

        character_name_attribute = 'character_name'
        scene_object_type_attribute = 'scene_object_type'

        for attr in [character_name_attribute, scene_object_type_attribute]:
            cmds.addAttr(self.topGrp, longName=attr, dataType='string')

        cmds.setAttr(self.topGrp + '.' + character_name_attribute, character_name, type='string', lock=True)
        cmds.setAttr(self.topGrp + '.' + scene_object_type_attribute, scene_object_type, type='string', lock=True)

        # make global controls

        global_1_ctrl = control.Control(
            prefix='global_1',
            parent=self.rigGrp,
            shape='circleY',
            scale=scale * 20,
            lock_channels=['v']
        )

        global_2_ctrl = control.Control(
            prefix='global_2',
            parent=global_1_ctrl.c,
            shape='circleY',
            scale=scale * 18,
            lock_channels=['v', 's']
        )

        # self._flatten_global_ctrl_shape(global_1_ctrl.c)
        # self._flatten_global_ctrl_shape(global_2_ctrl.c)

        # connecting scale attributes
        for axis in ['X', 'Z']:
            cmds.connectAttr(global_1_ctrl.c + '.scaleY', global_1_ctrl.c + '.scale' + axis)
            cmds.setAttr(global_1_ctrl.c + '.scale' + axis, keyable=False)

        # Adding groups for organisation
        self.jointsGrp = cmds.group(name='joints_grp', parent=global_2_ctrl.c, empty=True)
        self.modulesGrp = cmds.group(name='modules_grp', parent=global_2_ctrl.c, empty=True)

        self.partsGrp = cmds.group(name='parts_grp', parent=self.rigGrp, empty=True)
        cmds.setAttr(self.partsGrp + '.inheritsTransform', 0, lock=True)

    # flatten ctrl object shape
    # def _flatten_global_ctrl_shape(
    #                                 self,
    #                                 ctrl_object):
    #     ctrl_shapes = cmds.listRelatives(ctrl_object, shapes=1, type='nurbsCurve')
    #     cls = cmds.cluster(ctrl_shapes)[1]
    #     cmds.setAttr(cls +'.rz', 90)
    #     cmds.delete(ctrl_shapes, constructionHistory=True)


class Module():
    """class for building base module rig structures"""

    def __init__(self,
                 prefix='new',
                 base_object=None,
                 ):
        """
        :param prefix: str, prefix to name all objects (e.g. spine, arm)
        :param base_object: instance of base.module.base class
        :return: None
        """

        self.topGrp = cmds.group(name=prefix + '_module_grp', empty=True)
        self.controlsGrp = cmds.group(name=prefix + '_controles_grp', parent=self.topGrp, empty=True)
        self.jointsGrp = cmds.group(name=prefix + '_joints_grp', parent=self.topGrp, empty=True)
        self.parts = cmds.group(name=prefix + '_parts_grp', parent=self.topGrp, empty=True)
        self.parts_noTrans = cmds.group(name=prefix + '_parts_noTrans_grp', parent=self.topGrp, empty=True)

        cmds.setAttr(self.parts_noTrans + '.inheritsTransform', 0, lock=True)

        # parenting module
        if base_object:
            cmds.parent(self.topGrp, base_object.modulesGrp)
