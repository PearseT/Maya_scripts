
import maya.cmds as cmds

cmds.polySphere(name='Mr_sphear')
cmds.move(0,10,0)

cmds.polyCube()

cmds.move(0,-5,0, 'Mr_sphear', r=True)