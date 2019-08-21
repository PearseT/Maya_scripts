import maya.cmds as cmds




def make_stretch_plane(**kwargs)
    # still need to make my doc string

    start_joint = kwargs.setdefault('start_joint', cmds.ls(selection=True))
    end_joint = kwargs.setdefault('end_joint', cmds.listRelatives(start_joint)[0])
    number_of_bones = kwargs.setdefault('number_of_bones', 3 )
    prefix = kwargs.setdefault('name', start_joint+ '.name')
    stretch_len = cmds.getAttr(end_joint + '.translateX')

    if start_joint = None
        print "no joint selected"

    start_point = cmds.xform(start_joint, query=True, worldSpace=True, translation=True)
    end_point = cmds.xform(end_joint, query=True, worldSpace=True, translation=True)

    # create start + end locators, bones to skin the wire to, and an empty group
    startLoc = cmds.spaceLocator(name='startLoc')
    cmds.delete(cmds.parentConstraint(start_joint, startLoc))
    endLoc = cmds.spaceLocator(name='endLoc')
    cmds.delete(cmds.parentConstraint(end_joint, endLoc))

    cmds.select(clear=True)
    startWJoint = cmds.joint(name='startWireJoint')
    cmds.parent(startWJoint, startLoc, relative=True)
    cmds.select(clear=True)
    endWJoint = cmds.joint(name='endWireJoint')
    cmds.parent(endWJoint, endLoc, relative=True)

    sGrp = cmds.group(empty=True, name=prefix + 'stretchPlaneGrp')
    cmds.delete(cmds.parentConstraint(startLoc, sGrp))

    # create NURBS plane and CV curve. Group everything into the new sGrp
    sPlane = cmds.nurbsPlane(name=prefix + 'stretchPlane', width=stretch_len, lengthRatio=.2, patchesU=number_of_bones, axis=(0, 1, 0))
    sPlaneShape = cmds.listRelatives(sPlane, shapes=True)[0]
    cmds.delete(cmds.parentConstraint(startLoc, endLoc, sPlane))
    cmds.delete(cmds.orientConstraint(startLoc, sPlane))
    cmds.delete(sPlane, constructionHistory=True)

    sCurve = cmds.curve(degree=1, point=[start_point, end_point])
    sCurve = cmds.rename(sCurve, prefix + 'stretchCurve')  # If named at the creation time, the shape node doesn't get renamed

    cmds.parent(startLoc, endLoc, sPlane[0], sCurve, sGrp)

    # create wire deformer and dropoffLocator for twisting
    sWire = cmds.wire(sPlane[0], wire=sCurve, name=prefix + 'stretchWire')
    cmds.wire(sWire[1], edit=True, dropoffDistance=[(0, 20), (1, 20)])

    cmds.select(sWire[1] + '.u[0]', r=True)
    cmds.dropoffLocator(1.0, 1.0, sWire[0])
    cmds.select(sWire[1] + '.u[1]', r=True)
    cmds.dropoffLocator(1.0, 1.0, sWire[0])

    # skin wire to bone driver, connect rotation of locators to drop off locators twist


    cmds.connectAttr(startLoc[0] + '.rotateX', sWire[0] + '.wireLocatorTwist[0]')
    cmds.connectAttr(endLoc[0] + '.rotateX', sWire[0] + '.wireLocatorTwist[1]')

    cmds.skinCluster(startWJoint, endWJoint, sWire[1], maximumInfluences=1, toSelectedBones=True)

    # crating follicles on sPlane and joints

    sJointsCollection = []
    folGrp = cmds.group(empty=True, name=prefix + 'follicleGrp')
    cmds.parent(folGrp, sGrp)

    for x in range(number_of_bones):
        VPosition = (1.0 / (number_of_bones + 1)) * (x + 1)
        folShape = cmds.createNode("follicle")
        folTrans = cmds.listRelatives(folShape, parent=True)[0]
        folTrans = cmds.rename(folTrans, prefix + "follicle_{:02d}".format(x + 1))
        folShape = cmds.listRelatives(folTrans, shapes=True)[0]
        folShape = cmds.rename(folShape, prefix + "follicleShape_{:02d}".format(x + 1))

        cmds.connectAttr(sPlaneShape + '.worldMatrix[0]', folShape + '.inputWorldMatrix')
        cmds.connectAttr(sPlaneShape + '.local', folShape + '.inputSurface')
        cmds.connectAttr(folShape + '.outTranslate', folTrans + '.translate')
        cmds.connectAttr(folShape + '.outRotate', folTrans + '.rotate')

        cmds.setAttr(folShape + '.parameterU', VPosition)
        cmds.setAttr(folShape + '.parameterV', .5)

        # here I'm adding a joint, as the follicle is selected the joint is parented under it.
        # im also adding the joint to a list i can use later
        sJointsCollection.append(cmds.joint(name=prefix + "stretchJoint_{:02d}".format(x + 1)))

        cmds.parent(folTrans, folGrp)

    # creating nodes for stretching bones
    sCurveShape = cmds.listRelatives(sCurve, shapes=True)[0]
    sCurveInfo = cmds.createNode('curveInfo', name='SCurveInfo')
    cmds.rename(sCurveInfo, 'SCurveInfo')
    cmds.connectAttr(sCurveShape + '.worldSpace[0]', sCurveInfo + '.inputCurve')

    jointScale = cmds.createNode('multiplyDivide', name='sJointScale')
    cmds.setAttr(jointScale + '.operation', 2)
    cmds.setAttr(jointScale + '.input2X', stretch_len)
    cmds.connectAttr(sCurveInfo + '.arcLength', jointScale + '.input1X')

    # connecting up nodes to bones
    for joint in sJointsCollection:
        cmds.connectAttr(jointScale + '.outputX', joint + '.scaleX')

    # creating a variable for the base wire of the wire deformer
    sBaseWire = cmds.listConnections(sWire[0] + '.baseWire', destination=False, source=True)[0]

    # creating group inorder to help organisation and prevent double transforms
    sRigGrp = cmds.group(empty=True, name=prefix + 'stretchPlaneRigGrp')
    cmds.delete(cmds.parentConstraint(startLoc, sRigGrp))

    cmds.parent(sRigGrp, sGrp)
    cmds.parent(sPlane[0], sBaseWire, startLoc, endLoc, sRigGrp)
    cmds.setAttr(startWJoint + ".visibility", False)
    cmds.setAttr(endWJoint + ".visibility", False)

    # Connecting end locators to driving joints -will have to do this properly in the main script
    cmds.pointConstraint(end_joint, endLoc)
    cmds.connectAttr(end_joint + '.rotateZ', endLoc[0] + '.rotateX') # TODO: add if statment for elbow/wrist rotations
    cmds.parent(sRigGrp, startJointe)

if __name__ == '__main__':
    make_stretch_plane()


'''
for V0.2
make squash nodes
connect to global scale
'''