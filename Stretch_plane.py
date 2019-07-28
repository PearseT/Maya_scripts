import maya.cmds as cmds

un=''
numberOfBones=3

#will need to add if statment to test for selected and joint
startJoint = cmds.ls(selection=True, )
endJoint = cmds.listRelatives(startJoint)[0]
len = cmds.getAttr(endJoint+'.translateX')

startPoint = cmds.xform(startJoint, query=True, worldSpace=True, translation=True)
endPoint =  cmds.xform(endJoint, query=True, worldSpace=True, translation=True)

#create start and end locators and an empty group

startLoc = cmds.spaceLocator(name = 'startLoc')
cmds.delete(cmds.parentConstraint(startJoint, startLoc))

endLoc = cmds.spaceLocator(name = 'endLoc')
cmds.delete(cmds.parentConstraint(endJoint, endLoc))

sGrp = cmds.group(empty=True, name= un + 'stretchPlaneGrp')
cmds.delete(cmds.parentConstraint(startLoc, endLoc, sGrp))
cmds.delete(cmds.orientConstraint(startLoc, sGrp))

#create NURBS plane and CV curve

sPlane = cmds.nurbsPlane(name= un + 'stretchPlane', width= len ,lengthRatio=.2, patchesU=numberOfBones, axis=(0,1,0) )
cmds.delete(cmds.parentConstraint(startLoc, endLoc, sPlane))
cmds.delete(cmds.orientConstraint(startLoc, sPlane))
sCurve = cmds.curve(name= un + 'stretchCurve', p=[startPoint,endPoint])

cmds.parent()
'''


create NURBS plane with length from second bone

create cv curve

create twist modifier 
Make N hair
deleat extra parts 
parent bones to Nhair groups 

group all parts except curve and Nhair/bones
-----
make squash adn stretch nodes

connect up squash and stretch nodes

'''