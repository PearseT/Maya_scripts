import maya.cmds as cmds

def align(source, target):
    # type: (str, str) -> list[float]
    matrix = cmds.xform(target, query=True, worldSpace=True, matrix=True)
    cmds.xform(source, worldSpace=True, matrix=matrix)
    return matrix


def make_stretch_plane(**kwargs)
    # still need to make my doc string

    start_joint = kwargs.setdefault('start_joint', cmds.ls(selection=True))
    end_joint = kwargs.setdefault('end_joint', cmds.listRelatives(start_joint)[0])
    number_of_bones = kwargs.setdefault('number_of_bones', 3 )
    prefix = kwargs.setdefault('name', start_joint+ '.name')
    stretch_len = cmds.getAttr(end_joint + '.translateX') #TODO need to get actual distance between points for spine

    if start_joint = None:
        print "no joint selected"

    start_point = cmds.xform(start_joint, query=True, worldSpace=True, translation=True)
    end_point = cmds.xform(end_joint, query=True, worldSpace=True, translation=True)

    # create start + end locators, bones to skin the wire to, and an empty group
    start_loc = cmds.spaceLocator(name='startloc')
    align(start_joint, start_loc))
    end_loc = cmds.spaceLocator(name='endLoc')
    align(end_joint, end_loc))

    cmds.select(clear=True)
    start_w_joint = cmds.joint(name='startWireJoint')
    align(start_w_joint, start_loc)
    cmds.select(clear=True)
    end_w_joint = cmds.joint(name='endWireJoint')
    align(end_w_joint, end_loc)

    s_grp = cmds.group(empty=True, name=prefix + 'stretchPlaneGrp')
    cmds.delete(cmds.parentConstraint(start_loc, s_grp))

    # create NURBS plane and CV curve. Group everything into the new sGrp
    s_plane = cmds.nurbsPlane(name=prefix + 'stretchPlane', width=stretch_len, lengthRatio=.2, patchesU=number_of_bones, axis=(0, 1, 0))
    s_plane_shape = cmds.listRelatives(s_plane, shapes=True)[0]
    cmds.delete(cmds.parentConstraint(start_loc, end_loc, s_plane))
    cmds.delete(cmds.orientConstraint(start_loc, s_plane))
    cmds.delete(s_plane, constructionHistory=True)

    s_curve = cmds.curve(degree=1, point=[start_point, end_point])
    s_curve = cmds.rename(s_curve, prefix + 'stretchCurve')  # If named at the creation time, the shape node doesn't get renamed

    cmds.parent(start_loc, end_loc, s_plane[0], s_curve, s_grp)

    # create wire deformer and dropoffLocator for twisting
    s_wire_transform, s_wire = cmds.wire(s_plane[0], wire=s_curve, name=prefix + 'stretchWire')
    cmds.wire(s_wire, edit=True, dropoffDistance=[(0, 20), (1, 20)])

    cmds.select(s_wire + '.u[0]', r=True)
    cmds.dropoffLocator(1.0, 1.0, s_wire_transform)
    cmds.select(s_wire + '.u[1]', r=True)
    cmds.dropoffLocator(1.0, 1.0, s_wire_transform)

    # skin wire to bone driver, connect rotation of locators to drop off locators twist


    cmds.connectAttr(start_loc[0] + '.rotateX', s_wire_transform + '.wireLocatorTwist[0]')
    cmds.connectAttr(end_loc[0] + '.rotateX', s_wire_transform + '.wireLocatorTwist[1]')

    cmds.skinCluster(start_w_joint, end_w_joint, s_wire_transform, maximumInfluences=1, toSelectedBones=True)

    # crating follicles on sPlane and joints

    s_joints_collection = []
    fol_grp = cmds.group(empty=True, name=prefix + 'follicleGrp')
    cmds.parent(fol_grp, s_grp)

    for x in range(number_of_bones):
        v_position = (1.0 / (number_of_bones + 1)) * (x + 1)
        fol_shape = cmds.createNode("follicle")
        fol_trans = cmds.listRelatives(fol_shape, parent=True)[0]
        fol_trans = cmds.rename(fol_trans, prefix + "follicle_{:02d}".format(x + 1))
        fol_shape = cmds.listRelatives(fol_trans, shapes=True)[0]
        fol_shape = cmds.rename(fol_shape, prefix + "follicleShape_{:02d}".format(x + 1))

        cmds.connectAttr(s_plane_shape + '.worldMatrix[0]', fol_shape + '.inputWorldMatrix')
        cmds.connectAttr(s_plane_shape + '.local', fol_shape + '.inputSurface')
        cmds.connectAttr(fol_shape + '.outTranslate', fol_trans + '.translate')
        cmds.connectAttr(fol_shape + '.outRotate', fol_trans + '.rotate')

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
    s_base_wire = cmds.listConnections(s_wire[0] + '.baseWire', destination=False, source=True)[0]

    # creating group inorder to help organisation and prevent double transforms
    s_rig_grp = cmds.group(empty=True, name=prefix + 'stretchPlaneRigGrp')
    cmds.delete(cmds.parentConstraint(start_loc, s_rig_grp))

    cmds.parent(s_rig_grp, s_grp)
    cmds.parent(s_plane[0], s_base_wire, start_loc, end_loc, s_rig_grp)
    cmds.setAttr(start_w_joint + ".visibility", False)
    cmds.setAttr(end_w_joint + ".visibility", False)

    # Connecting end locators to driving joints -will have to do this properly in the main script
    cmds.pointConstraint(end_joint, end_loc)
    cmds.connectAttr(end_joint + '.rotateZ', end_loc[0] + '.rotateX') # TODO: add if statment for elbow/wrist rotations
    cmds.parent(s_rig_grp, start_joint)

if __name__ == '__main__':
    make_stretch_plane()


'''
for V0.2
make squash nodes
connect to global scale
'''