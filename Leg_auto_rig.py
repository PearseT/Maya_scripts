
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

pelvisPos = cmds.xform('COG', query=True, worldSpace=True, translation=True)
hipPos = cmds.xform('hip', query=True, worldSpace=True, translation=True)
kneePos = cmds.xform('knee', query=True, worldSpace=True, translation=True)
anklePos = cmds.xform('ankle', query=True, worldSpace=True, translation=True)
ballPos = cmds.xform('ball', query=True, worldSpace=True, translation=True)
toePos = cmds.xform('toe', query=True, worldSpace=True, translation=True)

# creating
si = 'L_'
un = ''


pelvisJnt = cmds.joint(name='pelvis', absolute=True, radius=2, position=pelvisPos)

hipJnt = cmds.joint(name= si + un + 'hip', absolute=True, radius=2, position=hipPos)
kneeJnt = cmds.joint(name= si + un + 'knee', absolute=True, radius=2, position=kneePos)
ankleJnt = cmds.joint(name= si + un + 'ankle', absolute=True, radius=2, position=anklePos)
ballJnt = cmds.joint(name= si + un + 'ball', absolute=True, radius=2, position=ballPos)
toeJnt = cmds.joint(name= si + un + 'toe', absolute=True, radius=2, position=toePos)

cmds.select(pelvisJnt, hipJnt, kneeJnt, ankleJnt, ballJnt, toeJnt)
cmds.joint(edit=True, orientJoint='xyz', secondaryAxisOrient='yup' )

cmds.select(clear=True)
pvHipJnt = cmds.joint(name= si + un + 'pvHip', absolute=True, radius=2, position=hipPos)
pvKneeJnt = cmds.joint(name= si + un + 'pvKnee', absolute=True, radius=2, position=kneePos)
pvAnkleJnt = cmds.joint(name= si + un + 'pvAnkle', absolute=True, radius=2, position=anklePos)
pvBallJnt = cmds.joint(name= si + un + 'pvBall', absolute=True, radius=2, position=ballPos)
pvToeJnt = cmds.joint(name= si + un + 'pvToe', absolute=True, radius=2, position=toePos)

cmds.select(pvHipJnt, pvKneeJnt, pvAnkleJnt, pvBallJnt, pvToeJnt)
cmds.joint(edit=True, orientJoint='xyz', secondaryAxisOrient='yup' )

kneeLocTemp = cmds.spaceLocator(n='KneeLoc_TEMP')
cmds.delete(cmds.pointConstraint(hipJnt, ankleJnt, kneeLocTemp))
cmds.delete(cmds.aimConstraint(kneeJnt, kneeLocTemp, aimVector=(0,0,1)))

# when createing the knee aim ctrl , constrain between hip and ankle , del, then aim constraint to the knee bone so i can be suer there won't be any popping
# i can use this to set the offset on the polevectro leg as well
# just need to figure out how to code up the connections for a stretch leg


cmds.select(kneeJnt, kneeLoc)
cmds.align(x='mid' ,alignToLead=True)
'''
cmds.ikHandle(n="ikh_leg", sj="ikj_hip", ee="ikj_ankle", sol="ikRPsolver")
cmds.ikHandle(n="ikh_ball", sj="ikj_ankle", ee="ikj_ball", sol="ikSCsolver")
cmds.ikHandle(n="ikh_toe", sj="ikj_ball", ee="ikj_toe", sol="ikSCsolver")

footGroups = ("grp_footPivot", "grp_heel", "grp_toe", "grp_ball", "grp_flap")

for item in footGroups:
    cmds.group(n=item, empty=1, world=1)

hipPos = cmds.xform("ikj_hip", q=True, ws=True, t=True)
anklePos = cmds.xform("ikj_ankle", q=True, ws=True, t=True)
ballPos = cmds.xform("ikj_ball", q=True, ws=True, t=True)
toePos = cmds.xform("ikj_toe", q=True, ws=True, t=True)

cmds.xform("grp_toe", ws=True, t=toePos)
cmds.xform("grp_ball", ws=True, t=ballPos)
cmds.xform("grp_flap", ws=True, t=ballPos)

cmds.parent('grp_heel', 'grp_footPivot')
cmds.parent('grp_toe', 'grp_heel')
cmds.parent('grp_ball', 'grp_toe')
cmds.parent('grp_flap', 'grp_toe')
cmds.parent('ikh_leg', 'grp_ball')
cmds.parent('ikh_ball', 'grp_ball')
cmds.parent('ikh_toe', 'grp_flap')

# create control for the foot
cmds.circle(nr=(0, 1, 0), r=3, n="ctrl_leg")
cmds.xform("ctrl_leg", t=ballPos)
cmds.parent('grp_footPivot', 'ctrl_leg')
cmds.makeIdentity('ctrl_leg', a=True, t=True)

# creating no flip knee
# create locator
cmds.spaceLocator(n='lctrPv_leg')
pelvisPos = cmds.xform('jnt_pelvis', q=True, ws=True, t=True)
cmds.xform('lctrPv_leg', ws=True, t=pelvisPos)

# set up polvector with new locator
cmds.poleVectorConstraint ('lctrPv_leg', 'ikh_leg', weight=1)
cmds.select("ctrl_leg")
cmds.addAttr( shortName='Twist', longName='Twist', defaultValue=0, k=True)

# Creating and connecting Nodes

cmds.shadingNode("plusMinusAverage", asUtility=True, n='pmaNode_LegTwist')
cmds.shadingNode("multiplyDivide", asUtility=True, n='mdNode_LegTwist')

cmds.connectAttr('ctrl_leg.Twist', 'mdNode_LegTwist.input1X')
cmds.connectAttr('ctrl_leg.ry', 'mdNode_LegTwist.input1Y')
cmds.connectAttr('jnt_pelvis.ry', 'mdNode_LegTwist.input1Z')
cmds.setAttr('mdNode_LegTwist.input2X', -1)
cmds.setAttr('mdNode_LegTwist.input2Y', -1)
cmds.setAttr('mdNode_LegTwist.input2Z', -1)
cmds.connectAttr('mdNode_LegTwist.input1X', 'pmaNode_LegTwist.input1D[0]')
cmds.connectAttr('mdNode_LegTwist.input1Y', 'pmaNode_LegTwist.input1D[1]')
cmds.connectAttr('pmaNode_LegTwist.output1D', 'ikh_leg.twist')



# Creating the stretchy IK, start with creating the nodes, add attributes mesure distance and connect nodes

cmds.shadingNode("addDoubleLinear", asUtility=True, n='adlNode_LegStretch')
cmds.shadingNode("clamp", asUtility=True, n='clampNode_LegStretch')
cmds.shadingNode("multiplyDivide", asUtility=True, n='mdNode_LegStretch')
cmds.shadingNode("multiplyDivide", asUtility=True, n='mdNode_KneeStretch')
cmds.shadingNode("multiplyDivide", asUtility=True, n='mdNode_AnkleStretch')

# add stretch attribute to ctrl_leg

cmds.select('ctrl_leg')
cmds.addAttr( shortName='Stretch', longName='Stretch', defaultValue=0, k=True)

# creating distance tool

hipPos = cmds.xform('ikj_hip', q=True, ws=True, t=True)
anklePos = cmds.xform('ikj_ankle', q=True, ws=True, t=True)
disDim = cmds.distanceDimension(sp=(hipPos), ep=(anklePos))

cmds.rename('distanceDimension1', 'disDimNode_legStretch')
cmds.rename('locator1', 'lctrDis_hip')
cmds.rename('locator2', 'lctrDis_ankle')
cmds.parent('lctrDis_hip', 'jnt_pelvis')
cmds.parent('lctrDis_ankle', 'grp_ball')

kneeLen = cmds.getAttr('ikj_knee.tx')
print kneeLen

ankleLen = cmds.getAttr('ikj_ankle.tx')
print ankleLen

legLen = (kneeLen + ankleLen)
print legLen

cmds.setAttr('adlNode_LegStretch.input2', legLen)
cmds.setAttr('mdNode_LegStretch.input2X', legLen)
cmds.setAttr('mdNode_KneeStretch.input2X', kneeLen)
cmds.setAttr('mdNode_AnkleStretch.input2X', ankleLen)

# Connect the nodes to get the final stretch value that will be applied to our joints.
# The clamp node lets us control the amount of stretch.

cmds.connectAttr('ctrl_leg.Stretch', 'adlNode_LegStretch.input1')
cmds.setAttr ("clampNode_LegStretch.minR", 12.800084)
cmds.setAttr ("mdNode_LegStretch.operation",  2)

cmds.connectAttr('disDimNode_legStretch.distance', 'clampNode_LegStretch.inputR')
cmds.connectAttr( 'adlNode_LegStretch.output', 'clampNode_LegStretch.maxR')

cmds.connectAttr('clampNode_LegStretch.outputR', 'mdNode_LegStretch.input1X')
cmds.connectAttr('mdNode_LegStretch.outputX', 'mdNode_KneeStretch.input1X')
cmds.connectAttr('mdNode_LegStretch.outputX', 'mdNode_AnkleStretch.input1X')

cmds.connectAttr('mdNode_KneeStretch.outputX', 'ikj_knee.tx')
cmds.connectAttr('mdNode_AnkleStretch.outputX', 'ikj_ankle.tx')

# setting up foot, creating utility nodes and adding attributes

cmds.select('ctrl_leg')
cmds.addAttr( shortName='Roll_Break', longName='Roll_Break', defaultValue=0, k=True)
cmds.addAttr( shortName='Foot_Roll', longName='Foot_Roll', defaultValue=0, k=True)

cmds.shadingNode("condition", asUtility=True, n='conNode_ballRoll')
cmds.shadingNode("condition", asUtility=True, n='conNode_negBallRoll')
cmds.shadingNode("condition", asUtility=True, n='conNode_toeRoll')
cmds.shadingNode("plusMinusAverage", asUtility=True, n='pmaNode_ballRoll')
cmds.shadingNode("plusMinusAverage", asUtility=True, n='pmaNode_toeRoll')
cmds.shadingNode("condition", asUtility=True, n='conNode_heelRoll')
cmds.setAttr('pmaNode_toeRoll.operation', 2)
cmds.setAttr ("conNode_toeRoll.operation", 2)
cmds.setAttr ("conNode_toeRoll.colorIfFalseR", 0)
cmds.setAttr ("conNode_toeRoll.colorIfFalseG", 0)
cmds.setAttr ("conNode_toeRoll.colorIfFalseB", 0)
cmds.setAttr ('conNode_heelRoll.operation', 4)
cmds.setAttr('conNode_heelRoll.colorIfFalseB', 0)
cmds.setAttr('conNode_heelRoll.colorIfFalseR', 0)
cmds.setAttr('conNode_heelRoll.colorIfFalseG', 0)
cmds.setAttr("pmaNode_ballRoll.operation", 2)
cmds.setAttr ("conNode_negBallRoll.operation", 3)
cmds.setAttr ("conNode_ballRoll.operation", 3)

#setting up toe

cmds.connectAttr('ctrl_leg.Foot_Roll', 'conNode_toeRoll.firstTerm')
cmds.connectAttr('ctrl_leg.Foot_Roll', 'conNode_toeRoll.colorIfTrueR')
cmds.connectAttr('ctrl_leg.Roll_Break', 'conNode_toeRoll.secondTerm')
cmds.connectAttr('ctrl_leg.Roll_Break', 'conNode_toeRoll.colorIfFalseR')
cmds.connectAttr('ctrl_leg.Roll_Break', 'pmaNode_toeRoll.input1D[1]')
cmds.connectAttr('conNode_toeRoll.outColorR', 'pmaNode_toeRoll.input1D[0]')
cmds.connectAttr('pmaNode_toeRoll.output1D', 'grp_toe.rx')

# setting up heel

cmds.connectAttr('ctrl_leg.Foot_Roll', 'conNode_heelRoll.firstTerm')
cmds.connectAttr('ctrl_leg.Foot_Roll', 'conNode_heelRoll.colorIfTrueR')
cmds.connectAttr('conNode_heelRoll.outColorR', 'grp_heel.rotateX')

# setting up ball, and toe flap

cmds.connectAttr('ctrl_leg.Foot_Roll', 'conNode_ballRoll.firstTerm')
cmds.connectAttr('ctrl_leg.Foot_Roll', 'conNode_ballRoll.colorIfTrueR')
cmds.connectAttr('ctrl_leg.Roll_Break', 'conNode_negBallRoll.secondTerm')
cmds.connectAttr('ctrl_leg.Roll_Break', 'conNode_negBallRoll.colorIfTrueR')
cmds.connectAttr('conNode_negBallRoll.outColorR', 'pmaNode_ballRoll.input1D[0]')
cmds.connectAttr('grp_toe.rx', 'pmaNode_ballRoll.input1D[1]')
cmds.connectAttr('pmaNode_ballRoll.output1D', 'grp_ball.rx')
cmds.connectAttr('conNode_ballRoll.outColorR', 'conNode_negBallRoll.firstTerm')
cmds.connectAttr('conNode_ballRoll.outColorR', 'conNode_negBallRoll.colorIfFalseR')

cmds.select('ctrl_leg')
cmds.addAttr( shortName='Toe_Flap', longName='Toe_Flap', defaultValue=0, k=True)
cmds.connectAttr('ctrl_leg.Toe_Flap', 'grp_flap.rx')

# set up Piviot for banck and twist

cmds.circle(name='ctrl_footPivot', normal=(0,0,1), radius=(1))

ballPos = cmds.xform('grp_ball', q=True, t=True, ws=True)
cmds.xform('ctrl_footPivot', t=ballPos)

cmds.group(n='grp_ctrl_footPivot', empty=True)

cmds.parent('grp_ctrl_footPivot', 'ctrl_footPivot')

cmds.parent('ctrl_footPivot', 'ctrl_leg')
cmds.makeIdentity( apply=True )

cmds.connectAttr('grp_ctrl_footPivot.translate', 'grp_footPivot.rotatePivot')

cmds.xform('grp_ctrl_footPivot', t=ballPos)


cmds.select('ctrl_leg')
cmds.addAttr( shortName='Foot_Pivot', longName='Foot_Pivot', defaultValue=0, k=True)
cmds.addAttr( shortName='Foot_Bank', longName='Foot_Bank', defaultValue=0, k=True)
cmds.connectAttr('ctrl_leg.Foot_Pivot', 'grp_footPivot.ry')
cmds.connectAttr('ctrl_leg.Foot_Bank', 'grp_footPivot.rz')

'''