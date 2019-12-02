"""create stretch plain from 2 bones"""

import maya.cmds as cmds


def align(target, source):
    # type: (str, str) -> list[float]
    matrix = cmds.xform(target, query=True, worldSpace=True, matrix=True)
    cmds.xform(source, worldSpace=True, matrix=matrix)
    return matrix


def make_stretch_plane(
        prefix='',
        start_joint =cmds.ls(selection=True)[0],
        end_joint =cmds.listRelatives(start_joint)[0],
        number_of_bones=3,
        stretch_len=cmds.getAttr(end_joint + '.translateX')
         ):
    """
    :param prefix: str, name of objects
    :param start_joint: str, start point of stretch plane and parent bone
    :param end_joint: str, end point of stretch plane (right now its just the child of the start joint)
    :param number_of_bones: float, how many bones will be placed along the length of the plane
    :param stretch_len: float, the length of the plane, from start joint to end joint
    :return: list[], containing all stretch joints for skinning
    """

    # TODO need to get actual distance between points for spine

    start_point = cmds.xform(start_joint, query=True, worldSpace=True, translation=True)
    end_point = cmds.xform(end_joint, query=True, worldSpace=True, translation=True)

    # create start + end locators, bones to skin the wire to, and an empty group
    start_loc = cmds.spaceLocator(name='start_loc')
    cmds.parent(start_loc, start_joint, relative=True)
    end_loc = cmds.spaceLocator(name='end_loc')
    cmds.parent(end_loc, end_joint, relative=True)

    start_w_joint = cmds.joint(name='startWireJoint')
    cmds.parent(start_w_joint, start_loc)
    end_w_joint = cmds.joint(name='endWireJoint')
    cmds.parent(end_w_joint, end_loc)

    s_grp = cmds.group(empty=True, name=prefix + 'stretchPlaneGrp')
    cmds.delete(cmds.parentConstraint(start_loc, s_grp))

    # create NURBS plane and CV curve. Group everything into the new sGrp
    s_plane = cmds.nurbsPlane(name=prefix + 'stretchPlane',
                              width=stretch_len,
                              lengthRatio=.2,
                              patchesU=number_of_bones,
                              axis=(0, 1, 0))
    s_plane_shape = cmds.listRelatives(s_plane, shapes=True)[0]
    cmds.delete(cmds.parentConstraint(start_loc, end_loc, s_plane))
    cmds.delete(cmds.orientConstraint(start_loc, s_plane))
    cmds.delete(s_plane, constructionHistory=True)

    s_curve = cmds.curve(degree=1, point=[start_point, end_point])
    s_curve = cmds.rename(s_curve,
                          prefix + 'stretchCurve')  # If named at the creation time, the shape node doesn't get renamed

    cmds.parent(start_loc, end_loc, s_plane[0], s_curve, s_grp)

    # create wire deformer and dropoffLocator for twisting
    s_wire_deform = cmds.wire(s_plane[0], wire=s_curve, name=prefix + 'stretchWire')[0]
    cmds.wire(s_curve, edit=True, dropoffDistance=[(0, 20), (1, 20)])

    cmds.select(s_curve + '.u[0]', r=True)
    cmds.dropoffLocator(1.0, 1.0, s_wire_deform)
    cmds.select(s_curve + '.u[1]', r=True)
    cmds.dropoffLocator(1.0, 1.0, s_wire_deform)

    # connect rotation of locators to drop off locators twist, skin wire to bone driver

    cmds.connectAttr(start_loc[0] + '.rotateX', s_wire_deform + '.wireLocatorTwist[0]')
    cmds.connectAttr(end_loc[0] + '.rotateZ', s_wire_deform + '.wireLocatorTwist[1]')

    cmds.skinCluster(start_w_joint, end_w_joint, s_curve, maximumInfluences=1, toSelectedBones=True)

    # crating follicles on sPlane and joints

    s_joints_collection = []
    fol_grp = cmds.group(empty=True, name=prefix + 'follicleGrp')
    cmds.parent(fol_grp, s_grp)

    for x in range(number_of_bones):
        fol_shape = cmds.createNode("follicle")
        fol_trans = cmds.listRelatives(fol_shape, parent=True)[0]
        fol_trans = cmds.rename(fol_trans, prefix + "follicle_{:02d}".format(x + 1))
        fol_shape = cmds.listRelatives(fol_trans, shapes=True)[0]
        fol_shape = cmds.rename(fol_shape, prefix + "follicleShape_{:02d}".format(x + 1))

        cmds.connectAttr(s_plane_shape + '.worldMatrix[0]', fol_shape + '.inputWorldMatrix')
        cmds.connectAttr(s_plane_shape + '.local', fol_shape + '.inputSurface')
        cmds.connectAttr(fol_shape + '.outTranslate', fol_trans + '.translate')
        cmds.connectAttr(fol_shape + '.outRotate', fol_trans + '.rotate')

        v_position = (1.0 / (number_of_bones + 1)) * (x + 1)
        cmds.setAttr(fol_shape + '.parameterU', v_position)
        cmds.setAttr(fol_shape + '.parameterV', .5)

        # here I'm adding a joint, as the follicle is selected the joint is parented under it.
        # im also adding the joint to a list i can use later
        s_joints_collection.append(cmds.joint(name=prefix + "stretchJoint_{:02d}".format(x + 1)))

        cmds.parent(fol_trans, fol_grp)

    # creating nodes for stretching bones
    s_curve_shape = cmds.listRelatives(s_curve, shapes=True)[0]
    s_curve_info = cmds.createNode('curveInfo', name='SCurveInfo')
    cmds.rename(s_curve_info, 'SCurveInfo')
    cmds.connectAttr(s_curve_shape + '.worldSpace[0]', s_curve_info + '.inputCurve')

    joint_scale = cmds.createNode('multiplyDivide', name='sJointScale')
    cmds.setAttr(joint_scale + '.operation', 2)
    cmds.setAttr(joint_scale + '.input2X', stretch_len)
    cmds.connectAttr(s_curve_info + '.arcLength', joint_scale + '.input1X')

    # connecting up nodes to bones
    for joint in s_joints_collection:
        cmds.connectAttr(joint_scale + '.outputX', joint + '.scaleX')

    # creating a variable for the base wire of the wire deformer
    s_base_wire = cmds.listConnections(
        s_wire_deform + ".baseWire", destination=False, source=True
    )[0]

    # creating group inorder to help organisation and prevent double transforms
    s_rig_grp = cmds.group(empty=True, name=prefix + 'stretchPlaneRigGrp')
    align(start_joint, s_rig_grp)

    cmds.parent(s_rig_grp, s_grp)
    cmds.parent(s_plane[0], s_base_wire, start_loc, end_loc, s_rig_grp)
    cmds.setAttr(start_w_joint + ".visibility", False)
    cmds.setAttr(end_w_joint + ".visibility", False)

    # Connecting end locators to driving joints -will have to do this properly in the main script
    cmds.pointConstraint(end_joint, end_loc)
    cmds.connectAttr(end_joint + '.rotateZ', end_loc[0] + '.rotateZ')  # TODO: add if statment for elbow/wrist rotations
    cmds.parent(s_rig_grp, start_joint)

    return s_joints_collection
if __name__ == '__main__':
    make_stretch_plane()
    '''
    for V0.2
    make squash nodes
    connect to global scale
    '''
