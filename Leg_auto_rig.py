
import maya.cmds as cmds

# cmds.rename("joint1", "jnt_pelvis")
# cmds.rename("joint2", "ikj_hip")
# cmds.rename("joint3", "ikj_knee")
# cmds.rename("joint4", "ikj_ankle")
# cmds.rename("joint5", "ikj_ball")

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