import sys, os
from operator import add
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="spine", positions=None, radius=1):

	# create template joints if needed
	tmp = None
	if not positions:
		positions = template()
		tmp = positions[:] # copy

	# positions from template transforms/joints
	for i in range(6):
		if type(positions[i]) == str or type(positions[i]) == unicode:
			positions[i] = mc.xform(positions[i], q=True, rp=True, ws=True)

	grp = mc.createNode("transform", n=name)
	
	#
	# joints, part 1
	#

	ik = [None]*9
	mc.select(cl=True)
	ik[0] = mc.joint(p=positions[0], n=name+"_ik1_off")
	ik[2] = mc.joint(p=positions[1], n=name+"_ik2")
	mc.joint(ik[0], e=True, oj="xyz", sao="xup", ch=False, zso=True)
	# insert an "offset" joint for proper ik spline twist
	ik[3] = mc.joint(p=[i*0.5 for i in map(add, positions[1], positions[2])], n=name+"_ik3_off")
	mc.joint(ik[2], e=True, oj="xyz", sao="xup", ch=False, zso=True)
	ik[4] = mc.joint(p=positions[2], n=name+"_ik3")
	mc.joint(ik[3], e=True, oj="xyz", sao="xup", ch=False, zso=True)
	ik[5] = mc.joint(p=positions[3], n=name+"_ik4")
	mc.joint(ik[4], e=True, oj="xyz", sao="xup", ch=False, zso=True)
	ik[6] = mc.joint(p=positions[4], n=name+"_ik5")
	mc.joint(ik[5], e=True, oj="xyz", sao="xup", ch=False, zso=True)
	mc.setAttr(ik[6]+".jo", 0,0,0)
	# insert an "offset" joint for proper ik spline twist
	ik[7] = mc.joint(p=[i*0.5 for i in map(add, positions[4], positions[5])], n=name+"_ik6_off")
	mc.joint(ik[6], e=True, oj="xyz", sao="xup", ch=False, zso=True)
	ik[8] = mc.joint(p=positions[5], n=name+"_ik6")
	mc.joint(ik[7], e=True, oj="xyz", sao="xup", ch=False, zso=True)

	ik[1] = mc.duplicate(ik[0])[0]
	ik[1] = mc.rename(ik[1], name+"_ik1")
	mc.delete(mc.listRelatives(ik[1], pa=True, ad=True))
	ik[1] = mc.parent(ik[1], ik[0])[0]

	for n in ik: mc.setAttr(n+".radius", radius*0.5)
	for n in [ik[0], ik[3],ik[7]]: mc.setAttr(n+".drawStyle", 2)

	#
	# controls
	#

	ctrl_grp = [None]*5
	ctrl = [None]*5
	ctrl_grp[0], ctrl[0] = common.control(name=name+"_ik1", parent=grp,
					position=ik[0], radius=radius*2, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])
	mc.addAttr(ctrl[0], ln="joints", at="bool", dv=True, k=True)
	mc.addAttr(ctrl[0], ln="editJoints", at="bool", k=True)

	ctrl_grp[1], ctrl[1] = common.control(name=name+"_ik2", parent=ctrl[0],
					position=ik[2], radius=radius*2, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])

	ctrl_grp[2], ctrl[2] = common.control(name=name+"_ik3", parent=ctrl[1],
					position=ik[4], radius=radius*2, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])
	mc.addAttr(ctrl[2], ln="stretchAbove", at="bool", k=True)
	mc.addAttr(ctrl[2], ln="stretchBelow", at="bool", k=True)

	ctrl_grp[3], ctrl[3] = common.control(name=name+"_ik5", parent=ctrl[2],
					position=ik[6], radius=radius, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])
	anchor = mc.createNode("transform", n="spine_ik4_anchor", p=ik[4])
	mc.delete(mc.parentConstraint(ik[5], anchor))
	c = mc.parentConstraint(anchor, ctrl_grp[3], mo=True)[0]
	mc.rename(c, ctrl_grp[3]+"_parcon")

	ctrl_grp[4], ctrl[4] = common.control(name=name+"_ik6", parent=ctrl[3],
					position=ik[8], radius=radius, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])
	mc.addAttr(ctrl[4], ln="stretch", at="bool", k=True)

	md = mc.createNode("multiplyDivide")
	mc.setAttr(md+".operation", 2)
	mc.setAttr(md+".input1X", 1)
	mc.connectAttr(ik[4]+".sx", md+".input2X")
	mc.connectAttr(md+".outputX", anchor+".sx")
	

	#
	# joints, part 2
	#

	c = mc.orientConstraint(ctrl[2], ik[4], mo=True)[0]
	mc.rename(c, ik[4]+"_oricon")

	#
	# ik handles
	#

	mc.select(ik[0], ik[4])
	ikh, eff, crv = mc.ikHandle(sol="ikSplineSolver")
	crv = mc.parent(crv, grp)[0]
	mc.setAttr(crv+".it", False)
	mc.setAttr(ikh+".dTwistControlEnable", True)
	mc.setAttr(ikh+".dWorldUpType", 4)
	mc.setAttr(ikh+".dWorldUpAxis", 3)
	mc.setAttr(ikh+".dWorldUpVector", 0,0,-1)
	mc.setAttr(ikh+".dWorldUpVectorEnd", 0,0,-1)
	ikh = mc.parent(ikh, grp)[0]
	mc.hide(ikh, crv)
	ikh = mc.rename(ikh, name+"_ikh#")
	mc.rename(eff, name+"_eff#")

	# adjust "offset" joint position for proper ik spline twist
	mc.move(positions[2][0],positions[2][1],positions[2][2], ik[3]+".scalePivot", ik[3]+".rotatePivot")
	mc.move(0,-0.001,0, ik[3]+".scalePivot", ik[3]+".rotatePivot", r=True)

	c1 = mc.cluster(crv+".cv[0]")[1]
	c2 = mc.cluster(crv+".cv[1]", crv+".cv[2]")[1]
	c3 = mc.cluster(crv+".cv[3]")[1]
	mc.hide(c1, c2, c3)
	mc.parent(c1, ctrl[0])
	mc.parent(c2, ctrl[1])
	mc.parent(c3, ctrl[2])

	mc.connectAttr(ctrl[0]+".worldMatrix", ikh+".dWorldUpMatrix")
	mc.connectAttr(ctrl[2]+".worldMatrix", ikh+".dWorldUpMatrixEnd")



	mc.select(ik[5], ik[8])
	ikh, eff, crv2 = mc.ikHandle(sol="ikSplineSolver")
	crv2 = mc.parent(crv2, grp)[0]
	mc.setAttr(crv2+".t", 0,0,0)
	mc.setAttr(crv2+".r", 0,0,0)
	mc.setAttr(crv2+".s", 1,1,1)
	mc.setAttr(crv2+".it", False)
	mc.setAttr(ikh+".dTwistControlEnable", True)
	mc.setAttr(ikh+".dWorldUpType", 4)
	mc.setAttr(ikh+".dWorldUpAxis", 3)
	mc.setAttr(ikh+".dWorldUpVector", 0,0,-1)
	mc.setAttr(ikh+".dWorldUpVectorEnd", 0,0,-1)
	ikh = mc.parent(ikh, grp)[0]
	mc.hide(ikh, crv2)
	ikh = mc.rename(ikh, name+"_ikh#")
	mc.rename(eff, name+"_eff#")

	# adjust "offset" joint position for proper ik spline twist
	mc.move(positions[5][0],positions[5][1],positions[5][2], ik[7]+".scalePivot", ik[7]+".rotatePivot")
	mc.move(0,-0.001,0, ik[7]+".scalePivot", ik[7]+".rotatePivot", r=True)

	c1 = mc.cluster(crv2+".cv[0]")[1]
	c2 = mc.cluster(crv2+".cv[1]", crv2+".cv[2]")[1]
	c3 = mc.cluster(crv2+".cv[3]")[1]
	mc.hide(c1, c2, c3)
	mc.parent(c1, ik[4])
	mc.parent(c2, ctrl[3])
	mc.parent(c3, ctrl[4])

	mc.connectAttr(ctrl[2]+".worldMatrix", ikh+".dWorldUpMatrix")
	mc.connectAttr(ctrl[4]+".worldMatrix", ikh+".dWorldUpMatrixEnd")

	mc.delete(mc.ls(typ="tweak"))

	c = mc.orientConstraint(ctrl[0], ik[1], mo=True)[0]
	mc.rename(c, ik[1]+"_oricon")
	c = mc.orientConstraint(ctrl[4], ik[8], mo=True)[0]
	mc.rename(c, ik[8]+"_oricon")

	#
	# stretch math
	#

	ci = mc.createNode("curveInfo")
	mc.connectAttr(crv+".worldSpace", ci+".inputCurve")

	ci2 = mc.createNode("curveInfo")
	mc.connectAttr(crv2+".worldSpace", ci2+".inputCurve")

	n = mc.listRelatives(crv, pa=True, s=True)[1]
	tg = mc.createNode("transformGeometry")
	mc.connectAttr(n+".worldSpace", tg+".inputGeometry")
	mc.connectAttr(grp+".worldMatrix", tg+".transform")
	ci3 = mc.createNode("curveInfo")
	mc.connectAttr(tg+".outputGeometry", ci3+".inputCurve")

	n = mc.listRelatives(crv2, pa=True, s=True)[1]
	tg = mc.createNode("transformGeometry")
	mc.connectAttr(n+".worldSpace", tg+".inputGeometry")
	mc.connectAttr(grp+".worldMatrix", tg+".transform")
	ci4 = mc.createNode("curveInfo")
	mc.connectAttr(tg+".outputGeometry", ci4+".inputCurve")

	md1 = mc.createNode("multiplyDivide")
	mc.setAttr(md1+".operation", 2)
	mc.connectAttr(ci+".arcLength", md1+".input1X")
	mc.connectAttr(ci3+".arcLength", md1+".input2X")
	md2 = mc.createNode("multiplyDivide")
	mc.connectAttr(md1+".outputX", md2+".input1X")
	mc.connectAttr(ctrl[2]+".stretchBelow", md2+".input2X")
	c = mc.createNode("condition")
	mc.setAttr(c+".secondTerm", 1)
	mc.setAttr(c+".operation", 3)
	mc.connectAttr(md1+".outputX", c+".colorIfTrueR")
	mc.connectAttr(md2+".outputX", c+".firstTerm")
	mc.connectAttr(c+".outColorR", ik[0]+".sx")
	mc.connectAttr(c+".outColorR", ik[2]+".sx")

	md2 = mc.createNode("multiplyDivide")
	mc.connectAttr(md1+".outputX", md2+".input1X")
	mc.connectAttr(ctrl[2]+".stretchAbove", md2+".input2X")
	c = mc.createNode("condition")
	mc.setAttr(c+".secondTerm", 1)
	mc.setAttr(c+".operation", 3)
	mc.connectAttr(md1+".outputX", c+".colorIfTrueR")
	mc.connectAttr(md2+".outputX", c+".firstTerm")
	mc.connectAttr(c+".outColorR", ik[4]+".sx")

	md1 = mc.createNode("multiplyDivide")
	mc.setAttr(md1+".operation", 2)
	mc.connectAttr(ci2+".arcLength", md1+".input1X")
	mc.connectAttr(ci4+".arcLength", md1+".input2X")
	md2 = mc.createNode("multiplyDivide")
	mc.connectAttr(md1+".outputX", md2+".input1X")
	mc.connectAttr(ctrl[4]+".stretch", md2+".input2X")
	c = mc.createNode("condition")
	mc.setAttr(c+".secondTerm", 1)
	mc.setAttr(c+".operation", 3)
	mc.connectAttr(md1+".outputX", c+".colorIfTrueR")
	mc.connectAttr(md2+".outputX", c+".firstTerm")
	mc.connectAttr(c+".outColorR", ik[5]+".sx")
	mc.connectAttr(c+".outColorR", ik[6]+".sx")

	j = 0
	jnt = [None]*6
	for i in range(1,9):
		if i == 3 or i == 7: continue
		jnt[j] = mc.createNode("joint", n=name+"_jnt"+str(j+1), p=grp)
		mc.setAttr(jnt[j]+".radius", radius*0.5)
		mc.connectAttr(ctrl[0]+".joints", jnt[j]+".v")
		c = mc.parentConstraint(ik[i], jnt[j])[0]
		mc.rename(c, name+"_jnt"+str(j)+"_parcon")
		j += 1

	# selection sets
	common.sets(name, jnt, None, ctrl)

	# selectable joints
	common.selectable(ctrl[0]+".editJoints", jnt)

	if tmp: mc.delete(tmp)
	ik[0] = mc.parent(ik[0], grp)[0]
	mc.hide(ik[0])
	mc.select(grp)
	mc.dgdirty(a=True)

	return grp

def template(name="spine", radius=0.25):

	ik = [None]*6
	pos = [(0,1,0),(0,3,0),(0,5,0),(0,9,0),(0,10,0),(0,11,0)]
	for i in range(6):
		name2 = name+"_tmp"+str(i+1)
		if mc.objExists(name2): ik[i] = name2
		else:
			ik[i] = mc.createNode("joint", n=name2)
			mc.setAttr(ik[i]+".t", pos[i][0], pos[i][1], pos[i][2])
			if i: ik[i] = mc.parent(ik[i], ik[i-1])[0]
		mc.setAttr(ik[i]+".radius", radius)

	mc.select(ik[0])

	return ik
