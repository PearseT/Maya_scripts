
import maya.cmds as cmds

cmds.select(all=True)
cmds.delete()

# Create locators for leg and foot positions
cmds.spaceLocator(name='COG')
cmds.move(0,56.647,2.321)
cmds.spaceLocator(name='hip')
cmds.move(5.334,52.917,2.396)
cmds.spaceLocator(name='knee')
cmds.move(6.351,32.140,1.757)
cmds.spaceLocator(name='ankle')
cmds.move(6.351,4.747,-2.785)
cmds.spaceLocator(name='ball')
cmds.move(6.351,0.018,6.030)
cmds.spaceLocator(name='toe')
cmds.move(6.351,0.067,10.598)

cmds.select(clear=True)

# set side and unique name
si = 'L_'
un = ''


''' building joints for leg '''

# get position from locators
pelvisPos = cmds.xform('COG', query=True, worldSpace=True, translation=True)
hipPos = cmds.xform('hip', query=True, worldSpace=True, translation=True)
kneePos = cmds.xform('knee', query=True, worldSpace=True, translation=True)
anklePos = cmds.xform('ankle', query=True, worldSpace=True, translation=True)
ballPos = cmds.xform('ball', query=True, worldSpace=True, translation=True)
toePos = cmds.xform('toe', query=True, worldSpace=True, translation=True)

pvKneeLoc = cmds.spaceLocator(n='KneeLocTemp')
pvCtrlLoc = cmds.spaceLocator(n='pvKneeCtrlLoc')
cmds.parent(pvCtrlLoc,pvKneeLoc)

cmds.delete(cmds.pointConstraint('hip', 'ankle', pvKneeLoc))
cmds.select(pvKneeLoc, 'knee')
cmds.align(x='mid' ,alignToLead=True)
cmds.align(y='mid' ,alignToLead=True)
cmds.move(0,0,20, pvCtrlLoc, localSpace=True)
cmds.select(clear=True)

# make bind joints
pelvisJnt = cmds.joint(name='pelvis', absolute=True, radius=2, position=pelvisPos)

hipJnt = cmds.joint(name= si + un + 'hip', absolute=True, radius=2, position=hipPos)
kneeJnt = cmds.joint(name= si + un + 'knee', absolute=True, radius=2, position=kneePos)
ankleJnt = cmds.joint(name= si + un + 'ankle', absolute=True, radius=2, position=anklePos)
ballJnt = cmds.joint(name= si + un + 'ball', absolute=True, radius=2, position=ballPos)
toeJnt = cmds.joint(name= si + un + 'toe', absolute=True, radius=2, position=toePos)

cmds.select(hipJnt, kneeJnt, ankleJnt, ballJnt, toeJnt)
cmds.joint(edit=True, orientJoint='xyz', secondaryAxisOrient='yup' )

cmds.select(clear=True)

#make IK joints
pvHipJnt = cmds.joint(name= si + un + 'pvHip', absolute=True, radius=2, position=hipPos)
pvKneeJnt = cmds.joint(name= si + un + 'pvKnee', absolute=True, radius=2, position=kneePos)
pvAnkleJnt = cmds.joint(name= si + un + 'pvAnkle', absolute=True, radius=2, position=anklePos)
pvBallJnt = cmds.joint(name= si + un + 'pvBall', absolute=True, radius=2, position=ballPos)
pvToeJnt = cmds.joint(name= si + un + 'pvToe', absolute=True, radius=2, position=toePos)

cmds.select(pvHipJnt, pvKneeJnt, pvAnkleJnt, pvBallJnt, pvToeJnt)
cmds.joint(edit=True, orientJoint='xyz', secondaryAxisOrient='yup' )

ik_handle = cmds.ikHandle(startJoint=pvHipJnt, endEffector=pvAnkleJnt, name='LegIkRPsolver_ikh', sol = 'ikRPsolver')

# cmds.delete(cmds.aimConstraint(kneeJnt, kneeLocTemp, aimVector=(0,0,1)))

# when createing the knee aim ctrl , constrain between hip and ankle , del, then aim constraint to the knee bone so i can be suer there won't be any popping
# i can use this to set the offset on the polevectro leg as well
# just need to figure out how to code up the connections for a stretch leg


# cmds.select(kneeJnt, kneeLocTemp)
# cmds.align(x='mid' ,alignToLead=True)


