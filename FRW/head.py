import sys, os
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="head", control=None, parent=None, positions=None,
		radius=1, ikControlOffset=5, ikShape="cube"):

	# create template joints if needed
	tmp = None
	if not positions:
		positions = template(name=name)
		tmp = positions[:] # copy

	# positions from template transforms/joints
	for i in range(3):
		if type(positions[i]) == str or type(positions[i]) == unicode:
			positions[i] = mc.xform(positions[i], q=True, rp=True, ws=True)

	if not control:
		center = [0,0,0]
		c = len(positions)
		for i in range(3):
			center[0] += positions[i][0]
			center[1] += positions[i][1]
			center[2] += positions[i][2]
		center[0] /= c
		center[1] /= c
		center[2] /= c

		control = common.control(name=name, position=center, normal=(0,1,0),
					color=17, radius=radius*2, lockAttr=("v"), hideAttr=("v"))[1]

	if not parent: parent = control

	if not mc.objExists(control+".joints"):
		mc.addAttr(control, ln="joints", at="bool", dv=True, k=True)
	if not mc.objExists(control+".editJoints"):
		mc.addAttr(control, ln="editJoints", at="bool", k=True)
	if not mc.objExists(control+".fkControls"):
		mc.addAttr(control, ln="fkControls", at="bool", dv=True, k=True)
	if not mc.objExists(control+".ikControls"):
		mc.addAttr(control, ln="ikControls", at="bool", dv=True, k=True)

	#
	# fk controls
	#

	fk_ctrl_grp = [None]*3
	fk_ctrl = [None]*3
	fk_ctrl_grp[0], fk_ctrl[0] = common.control(name=name+"_jaw_fk", parent=control, position=positions[0],
					normal=(1,0,0), color=13, radius=radius*0.75, lockAttr=["t","s","v"],
					hideAttr=["tx","ty","tz","sx","sy","sz","v"])
	c = mc.parentConstraint(parent, fk_ctrl_grp[0], mo=True)[0]
	mc.rename(c, fk_ctrl_grp[0]+"_parcon")
	fk_ctrl_grp[1], fk_ctrl[1] = common.control(name=name+"_eye_lf_fk", parent=control, position=positions[1],
					numOffsetGroups=1, normal=(0,0,1), color=13, radius=radius*0.5, lockAttr=["t","rz","s","v"],
					hideAttr=["tx","ty","tz","rz","sx","sy","sz","v"])
	mc.addAttr(fk_ctrl[1], ln="lookAt", at="float", min=0, max=10, dv=10, k=True)
	c = mc.parentConstraint(parent, fk_ctrl_grp[1], mo=True)[0]
	mc.rename(c, fk_ctrl_grp[1]+"_parcon")
	fk_ctrl_grp[2], fk_ctrl[2] = common.control(name=name+"_eye_rt_fk", parent=control, position=positions[2],
					numOffsetGroups=1, normal=(0,0,1), color=13, radius=radius*0.5, lockAttr=["t","rz","s","v"],
					hideAttr=["tx","ty","tz","rz","sx","sy","sz","v"])
	mc.addAttr(fk_ctrl[2], ln="lookAt", at="float", min=0, max=10, dv=10, k=True)
	c = mc.parentConstraint(parent, fk_ctrl_grp[2], mo=True)[0]
	mc.rename(c, fk_ctrl_grp[2]+"_parcon")

	for n in fk_ctrl: mc.connectAttr(control+".fkControls", mc.listRelatives(n, pa=True, s=True)[0]+".v")

	#
	# fk joints
	#

	jnt = [None]*3
	jnt[0] = mc.createNode("joint", n="jaw_jnt", p=fk_ctrl[0])
	jnt[1] = mc.createNode("joint", n="eye_lf_jnt", p=fk_ctrl[1])
	jnt[2] = mc.createNode("joint", n="eye_rt_jnt", p=fk_ctrl[2])

	for n in jnt:
		mc.setAttr(n+".radius", radius*0.5)
		mc.connectAttr(control+".joints", n+".v")

	#
	# ik controls
	#

	positions[0] = [0,0,0]
	positions[0][0] = (positions[1][0]+positions[2][0]) * 0.5
	positions[0][1] = (positions[1][1]+positions[2][1]) * 0.5
	positions[0][2] = (positions[1][2]+positions[2][2]) * 0.5 + ikControlOffset*radius
	ik_ctrl_grp, ik_ctrl = common.control(name=name+"_eyes_ik", parent=control,
							position=positions[0], normal=(0,0,1), color=6,
							radius=radius*0.5, shape=ikShape, lockAttr=["sy","sz","v"],
							hideAttr=["sy","sz","v"])
	mc.connectAttr(control+".ikControls", mc.listRelatives(ik_ctrl, pa=True, s=True)[0]+".v")
	eye_lf_aim = mc.createNode("transform", n="eye_lf_aim", p=ik_ctrl)
	mc.delete(mc.pointConstraint(jnt[1], eye_lf_aim))
	mc.setAttr(eye_lf_aim+".tz", 0)
	eye_rt_aim = mc.createNode("transform", n="eye_rt_aim", p=ik_ctrl)
	mc.delete(mc.pointConstraint(jnt[2], eye_rt_aim))
	mc.setAttr(eye_rt_aim+".tz", 0)

	n = mc.listRelatives(fk_ctrl[1], pa=True, p=True)[0]
	n2 = mc.listRelatives(mc.listRelatives(fk_ctrl[1], pa=True, p=True)[0], pa=True, p=True)[0]
	n2 = mc.createNode("transform", n=name+"_lf_eye_base_dir", p=n2)
	mc.delete(mc.parentConstraint(fk_ctrl[1], n2))
	mc.setAttr(n2+".tz", 1)
	c = mc.aimConstraint(n2, n, aim=(0,0,1), u=(0,1,0), wut="objectrotation", wu=(0,1,0), wuo=ik_ctrl, mo=True)[0]
	mc.aimConstraint(eye_lf_aim, n, aim=(0,0,1), u=(0,1,0), wut="objectrotation", wu=(0,1,0), wuo=ik_ctrl, mo=True)
	mc.setDrivenKeyframe(c+"."+n2+"W0", v=1, dv=0, cd=fk_ctrl[1]+".lookAt", itt="linear", ott="linear")
	mc.setDrivenKeyframe(c+"."+n2+"W0", v=0, dv=10, cd=fk_ctrl[1]+".lookAt", itt="linear", ott="linear")
	mc.setDrivenKeyframe(c+"."+eye_lf_aim+"W1", v=0, dv=0, cd=fk_ctrl[1]+".lookAt", itt="linear", ott="linear")
	mc.setDrivenKeyframe(c+"."+eye_lf_aim+"W1", v=1, dv=10, cd=fk_ctrl[1]+".lookAt", itt="linear", ott="linear")
	mc.rename(c, n+"_aimcon")
	n = mc.listRelatives(fk_ctrl[2], pa=True, p=True)[0]
	n2 = mc.listRelatives(mc.listRelatives(fk_ctrl[2], pa=True, p=True)[0], pa=True, p=True)[0]
	n2 = mc.createNode("transform", n=name+"_rt_eye_base_dir", p=n2)
	mc.delete(mc.parentConstraint(fk_ctrl[2], n2))
	mc.setAttr(n2+".tz", 1)
	c = mc.aimConstraint(n2, n, aim=(0,0,1), u=(0,1,0), wut="objectrotation", wu=(0,1,0), wuo=ik_ctrl, mo=True)[0]
	mc.aimConstraint(eye_rt_aim, n, aim=(0,0,1), u=(0,1,0), wut="objectrotation", wu=(0,1,0), wuo=ik_ctrl, mo=True)
	mc.setDrivenKeyframe(c+"."+n2+"W0", v=1, dv=0, cd=fk_ctrl[2]+".lookAt", itt="linear", ott="linear")
	mc.setDrivenKeyframe(c+"."+n2+"W0", v=0, dv=10, cd=fk_ctrl[2]+".lookAt", itt="linear", ott="linear")
	mc.setDrivenKeyframe(c+"."+eye_rt_aim+"W1", v=0, dv=0, cd=fk_ctrl[2]+".lookAt", itt="linear", ott="linear")
	mc.setDrivenKeyframe(c+"."+eye_rt_aim+"W1", v=1, dv=10, cd=fk_ctrl[2]+".lookAt", itt="linear", ott="linear")
	mc.rename(c, n+"_aimcon")

	# selection sets
	common.sets(name, jnt, fk_ctrl, [ik_ctrl])

	# selectable joints
	common.selectable(control+".editJoints", jnt)

	if tmp: mc.delete(tmp)
	mc.select(control)
	mc.dgdirty(a=True)

	return control

def template(name="head", radius=0.25):

	jnt = [None]*3
	pos = [(0,-0.5,0.25),(0.5,0.5,1),(-0.5,0.5,1)]
	names = [name+"_jaw_tmp", name+"_eye_lf_tmp", name+"_eye_rt_tmp"]
	for i in range(3):
		if mc.objExists(names[i]): jnt[i] = names[i]
		else:
			jnt[i] = mc.createNode("joint", n=names[i])
			mc.setAttr(jnt[i]+".t", pos[i][0], pos[i][1], pos[i][2])
		mc.setAttr(jnt[i]+".radius", radius)

	mc.select(jnt)

	return jnt
