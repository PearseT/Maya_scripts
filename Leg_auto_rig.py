
import maya.cmds as cmds

cmds.select(clear=True)
# global variables
side = 'L_'
prefix = 'name'

# Initial positions

COG = (0,9,0)
hipPos = (0,5,0.25)
kneePos = (0,0.5,0)
anklePos = (0,0,1.5)
ballPos = (0,0,2.5)
toePos = (0,0,-0.5)
# heelPos =()
# footInnerPos =()
# footOuterPos =()



#make template joints
hipJntTemp = cmds.joint(name= side + prefix + 'hip', absolute=True, radius=2, position=hipPos)
kneeJntTemp = cmds.joint(name= side + prefix + 'knee', absolute=True, radius=2, position=kneePos)
ankleJntTemp = cmds.joint(name= side + prefix + 'ankle', absolute=True, radius=2, position=anklePos)
ballJntTemp = cmds.joint(name= side + prefix + 'ball', absolute=True, radius=2, position=ballPos)
toeJntTemp = cmds.joint(name= side + prefix + 'toe', absolute=True, radius=2, position=toePos)



# ---------old code, remove when finalising
#
#
# cmds.select(clear=True)
#
# # set side and unique name
# si = 'L_'
# un = ''
#
#
# ''' building joints for leg '''
#
# # get position from locators
# pelvisPos = cmds.xform('COG', query=True, worldSpace=True, translation=True)
# hipPos = cmds.xform('hip', query=True, worldSpace=True, translation=True)
# kneePos = cmds.xform('knee', query=True, worldSpace=True, translation=True)
# anklePos = cmds.xform('ankle', query=True, worldSpace=True, translation=True)
# ballPos = cmds.xform('ball', query=True, worldSpace=True, translation=True)
# toePos = cmds.xform('toe', query=True, worldSpace=True, translation=True)
#
# # pvKneeLoc = cmds.spaceLocator(n='KneeLocTemp')
# # pvCtrlLoc = cmds.spaceLocator(n='pvKneeCtrlLoc')
# # cmds.parent(pvCtrlLoc,pvKneeLoc)
# #
# # cmds.delete(cmds.pointConstraint('hip', 'ankle', pvKneeLoc))
# # cmds.select(pvKneeLoc, 'knee')
# # cmds.align(x='mid' ,alignToLead=True)
# # cmds.align(y='mid' ,alignToLead=True)
# # cmds.move(0,0,20, pvCtrlLoc, localSpace=True)
# # cmds.select(clear=True)
#
# # --make bind joints
# pelvisJnt = cmds.joint(name='pelvis', absolute=True, radius=2, position=pelvisPos)
#
# hipJnt = cmds.joint(name= si + un + 'hip', absolute=True, radius=2, position=hipPos)
# kneeJnt = cmds.joint(name= si + un + 'knee', absolute=True, radius=2, position=kneePos)
# ankleJnt = cmds.joint(name= si + un + 'ankle', absolute=True, radius=2, position=anklePos)
# ballJnt = cmds.joint(name= si + un + 'ball', absolute=True, radius=2, position=ballPos)
# toeJnt = cmds.joint(name= si + un + 'toe', absolute=True, radius=2, position=toePos)
#
# cmds.select(hipJnt)
# cmds.joint(edit=True, children=True, orientJoint='xzy', secondaryAxisOrient='xdown' )
# cmds.select(clear=True)
#
# # --make IK joints
# # pvHipJnt = cmds.joint(name= si + un + 'pvHip', absolute=True, radius=2, position=hipPos)
# # pvKneeJnt = cmds.joint(name= si + un + 'pvKnee', absolute=True, radius=2, position=kneePos)
# # pvAnkleJnt = cmds.joint(name= si + un + 'pvAnkle', absolute=True, radius=2, position=anklePos)
# # pvBallJnt = cmds.joint(name= si + un + 'pvBall', absolute=True, radius=2, position=ballPos)
# # pvToeJnt = cmds.joint(name= si + un + 'pvToe', absolute=True, radius=2, position=toePos)
# #
# # cmds.select(pvHipJnt, pvKneeJnt, pvAnkleJnt, pvBallJnt, pvToeJnt)
# # cmds.joint(edit=True, orientJoint='xyz', secondaryAxisOrient='yup' )
# #
# # ik_handle = cmds.ikHandle(startJoint=pvHipJnt, endEffector=pvAnkleJnt, name='LegIkRPsolver_ikh', sol = 'ikRPsolver')
# #
# # cmds.delete(cmds.aimConstraint(kneeJnt, kneeLocTemp, aimVector=(0,0,1), worldUpVector=hipJnt))
#
# # when createing the knee aim ctrl , constrain between hip and ankle , del, then aim constraint to the knee bone so i can be suer there won't be any popping
# # i can use this to set the offset on the polevectro leg as well
# # just need to figure out how to code up the connections for a stretch leg
#
#
# # cmds.select(kneeJnt, kneeLocTemp)
# # cmds.align(x='mid' ,alignToLead=True)
#
#
