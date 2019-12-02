import sys, os, math
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="arm", positions=None, inheritTemplateRotations=False, radius=1, ikShape="cube"):

	# create template joints if needed
	tmp = None
	if not positions:
		positions = template(name=name)
		tmp = positions[:] # copy

	# positions/orientations from template transforms/joints
	rotations = [None]*4
	for i in range(4):
		if type(positions[i]) == str or type(positions[i]) == unicode:
			if inheritTemplateRotations: rotations[i] = mc.xform(positions[i], q=True, ro=True, ws=True)
			positions[i] = mc.xform(positions[i], q=True, rp=True, ws=True)

	grp = mc.createNode("transform", n=name)

	#
	# ik joints
	#

	ik = [None]*4
	for i in range(1,4):
		ik[i] = mc.createNode("joint", n=name+"_ik"+str(i+1))
		mc.setAttr(ik[i]+".t", positions[i][0], positions[i][1], positions[i][2])
		if inheritTemplateRotations:
			mc.setAttr(ik[i]+".r", rotations[i][0], rotations[i][1], rotations[i][2])

	if not inheritTemplateRotations:
		if positions[1][0] >= -0.001:
			mc.delete(mc.aimConstraint(ik[2], ik[1], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=ik[3]))
			mc.delete(mc.aimConstraint(ik[3], ik[2], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=ik[1]))
			mc.delete(mc.aimConstraint(ik[2], ik[3], aim=(-1,0,0), u=(0,0,-1), wut="object", wuo=ik[1]))
		else:
			mc.delete(mc.aimConstraint(ik[2], ik[1], aim=(-1,0,0), u=(0,0,1), wut="object", wuo=ik[3]))
			mc.delete(mc.aimConstraint(ik[3], ik[2], aim=(-1,0,0), u=(0,0,1), wut="object", wuo=ik[1]))
			mc.delete(mc.aimConstraint(ik[2], ik[3], aim=(1,0,0), u=(0,0,1), wut="object", wuo=ik[1]))

	for i in range(1,4):
		r = mc.getAttr(ik[i]+".r")[0]
		mc.setAttr(ik[i]+".jo", r[0],r[1],r[2])
		mc.setAttr(ik[i]+".r", 0,0,0)
		mc.setAttr(ik[i]+".radius", radius*0.5)

	# first ik joint
	ik[0] = mc.createNode("joint", n=name+"_ik1")
	mc.setAttr(ik[0]+".t", positions[0][0], positions[0][1], positions[0][2])
	if inheritTemplateRotations:
		mc.setAttr(ik[0]+".r", rotations[0][0], rotations[0][1], rotations[0][2])
	else:
		n = mc.createNode("transform")
		mc.delete(mc.pointConstraint(ik[0], n))
		mc.setAttr(n+".tz", mc.getAttr(n+".tz")-1)
		if positions[1][0] >= -0.001:
			mc.delete(mc.aimConstraint(ik[1], ik[0], aim=(1,0,0), u=(0,0,1), wut="object", wuo=n))
		else:
			mc.delete(mc.aimConstraint(ik[1], ik[0], aim=(-1,0,0), u=(0,0,-1), wut="object", wuo=n))
		mc.delete(n)
	r = mc.getAttr(ik[0]+".r")[0]
	mc.setAttr(ik[0]+".jo", r[0],r[1],r[2])
	mc.setAttr(ik[0]+".r", 0,0,0)

	#
	# ik controls
	#

	ik_ctrl_grp = [None]*3
	ik_ctrl = [None]*3
	ik_ctrl_grp[1], ik_ctrl[1] = common.control(name=name+"_ik2", parent=grp, position=ik[3],
								normal=(1,0,0), color=6, radius=radius, shape=ikShape,
								lockAttr=["s","v"], hideAttr=["sx","sy","sz","v"])
	mc.addAttr(ik_ctrl[1], ln="joints", at="bool", dv=True, k=True)
	mc.addAttr(ik_ctrl[1], ln="editJoints", at="bool", k=True)
	mc.addAttr(ik_ctrl[1], ln="fkControls", at="bool", dv=True, k=True)
	mc.addAttr(ik_ctrl[1], ln="ikControls", at="bool", dv=True, k=True)
	mc.addAttr(ik_ctrl[1], ln="stretch", at="bool", k=True)

	ik_ctrl_grp[2], ik_ctrl[2] = common.control(name=name+"_pv", parent=grp,
								position=ik[2], rotation=ik[2], normal=(0,0,1),
								color=6, radius=radius*0.25, shape=ikShape,
								lockAttr=["r","s"], \
								hideAttr=["rx","ry","rz","sx","sy","sz","v"])
	if positions[0][0] <= -0.001:
		mc.move(0,0,-3*radius, ik_ctrl_grp[2], os=True, r=True, wd=True)
	else:
		direction = -1 if inheritTemplateRotations else 1
		mc.move(0,0,direction*3*radius, ik_ctrl_grp[2], os=True, r=True, wd=True)
	mc.connectAttr(ik_ctrl[1]+".ikControls", ik_ctrl[2]+".v")

	#
	# ik stretch joints
	#

	ik2 = [None]*4
	for i in range(4):
		ik2[i] = mc.duplicate(ik[i])[0]
		ik2[i] = mc.rename(ik2[i], name+"_ik"+str(i+1)+"_str")
		if not i: ik2[i] = mc.parent(ik2[i], grp)[0]
		else:
			ik2[i] = mc.parent(ik2[i], ik2[i-1])[0]
			if i < 3:
				c = mc.parentConstraint(ik[i], ik2[i])[0]
				mc.rename(c, name+"_ik"+str(i+1)+"_str_parcon")
			else:
				c = mc.pointConstraint(ik[i], ik2[i])[0]
				mc.rename(c, name+"_ik"+str(i+1)+"_str_pntcon")
			if i == 2: mc.connectAttr(ik[2]+".r", ik2[2]+".r")
		mc.setAttr(ik2[i]+".jo", 0,0,0)

	mc.delete(mc.orientConstraint(ik[3], ik2[3]))
	c = mc.orientConstraint(ik_ctrl[1], ik2[3], mo=True)[0]
	mc.rename(c, ik2[3].split("|")[-1]+"_oricon")

	#
	# fk joints and controls
	#

	fk_ctrl = [None]*4
	jnt = [None]*4
	for i in range(4):
		fk_ctrl[i] = mc.duplicate(ik[i])[0]
		if i:
			fk_ctrl[i] = mc.rename(fk_ctrl[i], name+"_fk"+str(i+1)+"_ctrl")
			mc.connectAttr(ik2[i]+".t", fk_ctrl[i]+".t")
			mc.connectAttr(ik2[i]+".r", fk_ctrl[i]+".jo")
			mc.setAttr(fk_ctrl[i]+".r", 0,0,0)
			if inheritTemplateRotations: common.control(addShapeTo=fk_ctrl[i], normal=(1,0,0), color=13, radius=radius*0.7)
			else: common.control(addShapeTo=fk_ctrl[i], normal=(1,0,0), color=13, radius=radius*0.7)
			mc.connectAttr(ik_ctrl[1]+".fkControls", mc.listRelatives(fk_ctrl[i], pa=True, s=True)[0]+".v")
		else:
			# the first fk control becomes ik one
			fk_ctrl[i] = mc.rename(fk_ctrl[i], name+"_ik1_ctrl")
			common.control(addShapeTo=fk_ctrl[i], normal=(1,0,0), color=6, radius=radius)
			mc.connectAttr(ik_ctrl[1]+".ikControls", mc.listRelatives(fk_ctrl[i], pa=True, s=True)[0]+".v")
		if i == 1: fk_ctrl[i] = mc.parent(fk_ctrl[i], grp)[0]
		elif i > 1: fk_ctrl[i] = mc.parent(fk_ctrl[i], fk_ctrl[i-1])[0]
		mc.setAttr(fk_ctrl[i]+".drawStyle", 2)

		# fk joints
		jnt[i] = mc.duplicate(ik[i])[0]
		if i: jnt[i] = mc.parent(jnt[i], fk_ctrl[i])[0]
		else: jnt[i] = mc.parent(jnt[i], ik[0])[0]
		jnt[i] = mc.rename(jnt[i], name+"_jnt"+str(i+1))
		for a in ["t","r","jo"]: mc.setAttr(jnt[i]+"."+a, 0,0,0)
		mc.connectAttr(ik_ctrl[1]+".joints", jnt[i]+".v")
		if i: mc.setAttr(jnt[i]+".drawStyle", 0)
		mc.setAttr(jnt[i]+".radius", radius*0.5)

	# the first ik joint becomes fk control
	common.control(addShapeTo=ik[0], normal=(1,0,0), color=13, radius=radius*0.7)
	mc.connectAttr(ik_ctrl[1]+".fkControls", mc.listRelatives(ik[0], pa=True, s=True)[0]+".v")
	ik[0] = mc.rename(ik[0], name+"_fk1_ctrl")
	mc.setAttr(ik[0]+".drawStyle", 2)

	fk1_ctrl_grp = mc.createNode("joint", n=name+"_fk1_ctrl_grp", p=grp)
	mc.delete(mc.parentConstraint(ik[0], fk1_ctrl_grp))
	r = mc.getAttr(ik[0]+".jo")[0]
	mc.setAttr(fk1_ctrl_grp+".jo", r[0],r[1],r[2])
	mc.connectAttr(fk_ctrl[0]+".r", fk1_ctrl_grp+".r")
	mc.setAttr(fk1_ctrl_grp+".drawStyle", 2)
	ik[0] = mc.parent(ik[0], fk1_ctrl_grp)[0]
	mc.setAttr(ik[0]+".jo", 0,0,0)

	c = mc.orientConstraint(fk_ctrl[0], ik2[0], mo=True)[0]
	mc.rename(c, name+"_ik"+str(i+1)+"_str_oricon")

	fk2_ctrl_grp = mc.createNode("joint", n=name+"_fk2_ctrl_grp")
	mc.setAttr(fk2_ctrl_grp+".drawStyle", 2)

	#
	# ik handles
	#

	for i in range(2,4): ik[i] = mc.parent(ik[i], ik[i-1])[0]
	mc.select(ik[1:]); mc.SetPreferredAngle()

	ikh = common.ikHandle(name, ik[1], ik[3], parent=ik_ctrl[1])[0]
	pvc = mc.poleVectorConstraint(ik_ctrl[2], ikh)[0]
	mc.rename(pvc, name+"_pvcon")

	#
	# stretch math
	#

	n = mc.createNode("transform", n="str_grp", p=fk_ctrl[0])
	mc.delete(mc.pointConstraint(ik[1], n))
	db1 = mc.createNode("distanceBetween")
	mc.connectAttr(n+".worldMatrix", db1+".inMatrix1")
	mc.connectAttr(ik_ctrl[1]+".worldMatrix", db1+".inMatrix2")
	db2 = mc.createNode("distanceBetween")
	n2 = mc.duplicate(n)[0]
	mc.connectAttr(n2+".worldMatrix", db2+".inMatrix1")
	mc.connectAttr(ik_ctrl_grp[1]+".worldMatrix", db2+".inMatrix2")
	md1 = mc.createNode("multiplyDivide")
	mc.setAttr(md1+".operation", 2)
	mc.connectAttr(db1+".distance", md1+".input1X")
	mc.connectAttr(db2+".distance", md1+".input2X")
	md2 = mc.createNode("multiplyDivide")
	mc.connectAttr(md1+".outputX", md2+".input1X")
	mc.connectAttr(ik_ctrl[1]+".stretch", md2+".input2X")
	c = mc.createNode("condition")
	mc.setAttr(c+".secondTerm", 1)
	mc.setAttr(c+".operation", 3)
	mc.connectAttr(md1+".outputX", c+".colorIfTrueR")
	mc.connectAttr(md2+".outputX", c+".firstTerm")

	mc.connectAttr(c+".outColorR", ik[1]+".sx")
	mc.connectAttr(c+".outColorR", ik[2]+".sx")

	# offset the stretch group to enable full extension
	# of the leg before it starts stretching
	db3 = mc.createNode("distanceBetween")
	mc.connectAttr(fk_ctrl[1]+".worldMatrix", db3+".inMatrix1")
	mc.connectAttr(fk_ctrl[2]+".worldMatrix", db3+".inMatrix2")
	d = mc.getAttr(db3+".distance")
	mc.connectAttr(ik_ctrl[1]+".worldMatrix", db3+".inMatrix1", f=True)
	d += mc.getAttr(db3+".distance") - mc.getAttr(db1+".distance")
	mc.delete(db3)
	p = mc.xform(n2, q=True, rp=True, ws=True)
	p2 = mc.xform(ik_ctrl[1], q=True, rp=True, ws=True)
	p[0] -= p2[0]
	p[1] -= p2[1]
	p[2] -= p2[2]
	m = math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2])
	p[0] /= m
	p[1] /= m
	p[2] /= m
	p2 = mc.getAttr(n2+".t")[0]
	mc.setAttr(n2+".t", p2[0]-p[0]*d, p2[1]-p[1]*d, p2[2]-p[2]*d)
	
	#
	# lock and hide attributes
	#

	for i in range(4):
		for a in ["tx","ty","tz","sx","sy","sz","v","radius"]:
			mc.setAttr(fk_ctrl[i]+"."+a, l=True, k=False, cb=False)
	mc.setAttr(fk_ctrl[2]+".rx", l=True, k=False, cb=False)
	mc.setAttr(fk_ctrl[2]+".rz", l=True, k=False, cb=False)
	for a in ["tx","ty","tz","sx","sy","sz","v","radius"]:
		mc.setAttr(ik[0]+"."+a, l=True, k=False, cb=False)
	
	# selection sets
	ik_ctrl[0] = fk_ctrl.pop(0)
	fk_ctrl.insert(0, ik.pop(0))
	common.sets(name, jnt, fk_ctrl, ik_ctrl)

	# selectable joints
	common.selectable(ik_ctrl[1]+".editJoints", jnt)

	# fk to ik bake ready
	for i in range(4):
		mc.addAttr(ik_ctrl[1], ln="fk"+str(i+1), at="message", h=True)
		mc.addAttr(fk_ctrl[i], ln="fk", at="message", h=True)
		mc.connectAttr(ik_ctrl[1]+".fk"+str(i+1), fk_ctrl[i]+".fk")
	mc.addAttr(ik_ctrl[1], ln="ik1", at="message", h=True)
	mc.addAttr(ik_ctrl[0], ln="ik", at="message", h=True)
	mc.connectAttr(ik_ctrl[1]+".ik1", ik_ctrl[0]+".ik")
	mc.addAttr(ik_ctrl[1], ln="ik2", at="message", h=True)
	mc.addAttr(ik_ctrl[2], ln="ik", at="message", h=True)
	mc.connectAttr(ik_ctrl[1]+".ik2", ik_ctrl[2]+".ik")

	# organize
	if tmp: mc.delete(tmp)
	mc.parent(fk_ctrl[1], fk2_ctrl_grp)[0]
	fk2_ctrl_grp = mc.parent(fk2_ctrl_grp, fk_ctrl[0])[0]
	mc.setAttr(fk2_ctrl_grp+".t", 0,0,0)

	mc.hide(ik[0], ik2[0])
	mc.parent(ik[0], ik_ctrl[0])
	mc.parent(ik_ctrl[0], grp)
	mc.select(grp)
	mc.dgdirty(a=True)

	return grp

def template(name="arm", radius=0.25):

	jnt = [None]*4
	pos = [(0.5,0,0),(2,0,0),(5,0,-0.25),(8,0,0)]
	for i in range(4):
		name2 = name+"_tmp"+str(i+1)
		if mc.objExists(name2):
			jnt[i] = name2
		else:
			jnt[i] = mc.createNode("joint", n=name2)
			mc.setAttr(jnt[i]+".t", pos[i][0], pos[i][1], pos[i][2])
			if i: jnt[i] = mc.parent(jnt[i], jnt[i-1])[0]
		mc.setAttr(jnt[i]+".radius", radius)

	mc.select(jnt[0])

	return jnt
