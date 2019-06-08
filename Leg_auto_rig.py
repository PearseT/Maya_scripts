# taken from https://griffinanimation.blogspot.com/search?updated-max=2016-03-03T22:52:00-05:00

import maya.cmds as cmds

"""
cmds.rename("joint1", "jnt_pelvis")
cmds.rename("joint2", "ikj_hip")
cmds.rename("joint3", "ikj_knee")
cmds.rename("joint4", "ikj_ankle")
cmds.rename("joint5", "ikj_ball")
cmds.rename("joint5", "ikj_toe")
"""
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

cmds.parent('grp_footPivot', 'ctrl_leg')
cmds.makeIdentity('ctrl_leg', a=True, t=True)


