import maya.cmds as cmds

un=''
numberOfBones=3

# will need to add if statment to test for selected and joint
startJoint = cmds.ls(selection=True, )
endJoint = cmds.listRelatives(startJoint)[0]
len = cmds.getAttr(endJoint+'.translateX')

startPoint = cmds.xform(startJoint, query=True, worldSpace=True, translation=True)
endPoint =  cmds.xform(endJoint, query=True, worldSpace=True, translation=True)

#create start + end locators, bones to skin the wire to, and an empty group

startLoc = cmds.spaceLocator(name = 'startLoc')
cmds.delete(cmds.parentConstraint(startJoint, startLoc))
endLoc = cmds.spaceLocator(name = 'endLoc')
cmds.delete(cmds.parentConstraint(endJoint, endLoc))

cmds.select(clear=True)
startWJoint = cmds.joint(name='startWireJoint')
cmds.parent(startWJoint, startLoc, relative=True)
cmds.select(clear=True)
endWJoint = cmds.joint(name='endWireJoint')
cmds.parent(endWJoint, endLoc, relative=True)



sGrp = cmds.group(empty=True, name= un + 'stretchPlaneGrp')
cmds.delete(cmds.parentConstraint(startLoc, endLoc, sGrp))
cmds.delete(cmds.orientConstraint(startLoc, sGrp))

#create NURBS plane and CV curve. Group everything into the new sGrp

sPlane = cmds.nurbsPlane(name= un + 'stretchPlane', width=len, lengthRatio=.2, patchesU=numberOfBones, axis=(0,1,0) )
sPlaneShape = cmds.listRelatives(sPlane, shapes=True)[0]
cmds.delete(cmds.parentConstraint(startLoc, endLoc, sPlane))
cmds.delete(cmds.orientConstraint(startLoc, sPlane))
cmds.delete(sPlane,constructionHistory=True)

sCurve = cmds.curve(degree=1, point=[startPoint, endPoint])
sCurve = cmds.rename(sCurve, un + 'stretchCurve') # if name at the creation time, the shape doesn't get renamed

cmds.parent(startLoc, endLoc, sPlane[0], sCurve, sGrp)

#create wire deformer and dropoffLocator for twisting

sWire = cmds.wire(sPlane[0], wire=sCurve, name=un + 'stretchWire')
cmds.wire(sWire[1], edit=True, dropoffDistance=[(0,20),(1,20)])

cmds.select( sWire[1] + '.u[0]', r=True )
cmds.dropoffLocator( 1.0, 1.0, sWire[0] )
cmds.select( sWire[1] + '.u[1]', r=True )
cmds.dropoffLocator( 1.0, 1.0, sWire[0] )

#skin wire to bone drivesr, connect rotation of locators to drop off locators twist


cmds.connectAttr(startLoc[0]+'.rotateX',sWire[0]+'.wireLocatorTwist[0]')
cmds.connectAttr(endLoc[0]+'.rotateX',sWire[0]+'.wireLocatorTwist[1]')

cmds.skinCluster(startWJoint, endWJoint, sWire[1], maximumInfluences=1, toSelectedBones=True)

#crating follicles on sPlane and joints

sJointsCollection = []
folGrp = cmds.group(empty=True, name= un + 'fillicleGrp')
cmds.parent(folGrp, sGrp)

for x in range (numberOfBones):
    VPosition = (1.0/(numberOfBones+1))*(x+1)
    folShape = cmds.createNode("follicle")
    folTrans = cmds.listRelatives(folShape, parent=True)[0]
    folTrans = cmds.rename(folTrans, un+"follicle_{:02d}".format(x + 1))
    folShape = cmds.listRelatives(folTrans, shapes=True)[0]
    folShape = cmds.rename(folShape, un+"follicleShape_{:02d}".format(x + 1))


    cmds.connectAttr(sPlaneShape+'.worldMatrix[0]', folShape+'.inputWorldMatrix')
    cmds.connectAttr(sPlaneShape+'.local', folShape+'.inputSurface')
    cmds.connectAttr(folShape+'.outTranslate', folTrans+'.translate')
    cmds.connectAttr(folShape + '.outRotate', folTrans + '.rotate')

    cmds.setAttr(folShape+'.parameterU', (VPosition))
    cmds.setAttr(folShape+'.parameterV', .5)

    # here I'm adding a joint, as the follicle is selected the joint is parented under it.
    # im also adding the joint to a list i can use later
    sJointsCollection.append(cmds.joint(name=un+"stretchJoint_{:02d}".format(x + 1)))

    cmds.parent(folTrans,folGrp)

#
# #creating nodes for stretching bones
# sCurveShape = cmds.listRelatives(sCurve, shapes=True)[0]
# sCurveInfo = cmds.createNode('curveInfo', name='SCurveInfo')
# cmds.rename(sCurveInfo, 'SCurveInfo')
# cmds.connectAttr(sCurveShape+'.worldSpace[0]', sCurveInfo+'.inputCurve')
#
# jointScale= cmds.createNode('multiplyDivide', name='sJointScale')
# cmds.setAttr(jointScale+'.operation',2)
# cmds.setAttr(jointScale+'input2X',len)
# cmds.connectAttr(sCurveInfo+'.distance', jointScale+'.input1X')
#
# #connecting up nodes to bones
# for joint in sJointsCollection:
#     cmds.connectAttr(jointScale+'.outputX', joint+'.scaleX')

'''
visability of start wire joint


group all parts except curve and Nhair/bones
-----
make squash adn stretch nodes

connect up squash and stretch nodes

'''