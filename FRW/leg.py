import sys, os, math
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="leg", positions=None, inheritTemplateRotations=False,
		footWidth=1, radius=1, ikShape="cube"):

	# create template joints if needed
	tmp = None
	if not positions:
		positions = template(name=name)
		tmp = positions[:] # copy

	# positions/orientations from template transforms/joints
	rotations = [None]*6
	for i in range(6):
		if type(positions[i]) == str or type(positions[i]) == unicode:
			if inheritTemplateRotations: rotations[i] = mc.xform(positions[i], q=True, ro=True, ws=True)
			positions[i] = mc.xform(positions[i], q=True, rp=True, ws=True)

	grp = mc.createNode("transform", n=name)

	#
	# ik joints
	#

	ik = [None]*5
	for i in range(5):
		ik[i] = mc.createNode("joint", n=name+"_ik"+str(i+1))
		mc.setAttr(ik[i]+".t", positions[i][0], positions[i][1], positions[i][2])
		if inheritTemplateRotations:
			mc.setAttr(ik[i]+".r", rotations[i][0], rotations[i][1], rotations[i][2])

	if not inheritTemplateRotations:
		if positions[0][0] >= -0.001:
			mc.delete(mc.aimConstraint(ik[1], ik[0], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=ik[2]))
			mc.delete(mc.aimConstraint(ik[2], ik[1], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=ik[0]))
			mc.delete(mc.aimConstraint(ik[1], ik[2], aim=(-1,0,0), u=(0,0,-1), wut="object", wuo=ik[0]))
			mc.delete(mc.aimConstraint(ik[4], ik[3], aim=(1,0,0), u=(0,0,1), wut="object", wuo=ik[1]))
			mc.delete(mc.aimConstraint(ik[3], ik[4], aim=(-1,0,0), u=(0,0,1), wut="object", wuo=ik[1]))
		else:
			mc.delete(mc.aimConstraint(ik[1], ik[0], aim=(-1,0,0), u=(0,0,1), wut="object", wuo=ik[2]))
			mc.delete(mc.aimConstraint(ik[2], ik[1], aim=(-1,0,0), u=(0,0,1), wut="object", wuo=ik[0]))
			mc.delete(mc.aimConstraint(ik[1], ik[2], aim=(1,0,0), u=(0,0,1), wut="object", wuo=ik[0]))
			mc.delete(mc.aimConstraint(ik[4], ik[3], aim=(-1,0,0), u=(0,0,-1), wut="object", wuo=ik[1]))
			mc.delete(mc.aimConstraint(ik[3], ik[4], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=ik[1]))

	for i in range(5):
		r = mc.getAttr(ik[i]+".r")[0]
		mc.setAttr(ik[i]+".jo", r[0],r[1],r[2])
		mc.setAttr(ik[i]+".r", 0,0,0)
		mc.setAttr(ik[i]+".radius", radius*0.5)

	#
	# ik controls
	#

	ik_ctrl_grp = [None]*2
	ik_ctrl = [None]*2
	ik_ctrl_grp[0], ik_ctrl[0] = common.control(name=name+"_ik1", parent=grp,
								position=ik[2], color=6, radius=radius, shape=ikShape,
								lockAttr=["s","v"], hideAttr=["sx","sy","sz","v"])
	mc.addAttr(ik_ctrl[0], ln="joints", at="bool", dv=True, k=True)
	mc.addAttr(ik_ctrl[0], ln="editJoints", at="bool", k=True)
	mc.addAttr(ik_ctrl[0], ln="fkControls", at="bool", dv=True, k=True)
	mc.addAttr(ik_ctrl[0], ln="ikControls", at="bool", dv=True, k=True)
	mc.addAttr(ik_ctrl[0], ln="stretch", at="bool", k=True)
	mc.addAttr(ik_ctrl[0], ln="footRoll", at="double", k=True)
	mc.addAttr(ik_ctrl[0], ln="footSide", at="double", k=True)
	mc.addAttr(ik_ctrl[0], ln="heelTwist", at="double", k=True)
	mc.addAttr(ik_ctrl[0], ln="ballLift", at="double", k=True)
	mc.addAttr(ik_ctrl[0], ln="toeLift", at="double", k=True)
	mc.addAttr(ik_ctrl[0], ln="toeTwist", at="double", k=True)

	heel = mc.createNode("transform", n=name+"_heel_grp")
	mc.setAttr(heel+".t", positions[5][0],positions[5][1],positions[5][2])
	heel = mc.parent(heel, ik_ctrl[0])[0]
	mc.setAttr(heel+".r", 0,0,0)
	mc.connectAttr(ik_ctrl[0]+".footRoll", heel+".rx")
	mc.connectAttr(ik_ctrl[0]+".heelTwist", heel+".ry")
	mc.transformLimits(heel, rx=(0,0), erx=(False,True))
	mc.hide(heel)

	side_rt = mc.createNode("transform", n=name+"_side_rt_grp", p=heel)
	mc.setAttr(side_rt+".r", 0,0,0)
	mc.delete(mc.pointConstraint(ik[3], side_rt))
	mc.setAttr(side_rt+".tx", -footWidth)
	mc.connectAttr(ik_ctrl[0]+".footSide", side_rt+".rz")
	mc.transformLimits(side_rt, rz=(0,0), erz=(True,False))

	side_lf = mc.createNode("transform", n=name+"_side_lf_grp", p=side_rt)
	mc.delete(mc.pointConstraint(ik[3], side_lf))
	mc.setAttr(side_lf+".r", 0,0,0)
	mc.setAttr(side_lf+".tx", footWidth*2)
	mc.connectAttr(ik_ctrl[0]+".footSide", side_lf+".rz")
	mc.transformLimits(side_lf, rz=(0,0), erz=(False,True))

	toe = mc.createNode("transform", n=name+"_toe_grp", p=side_lf)
	mc.delete(mc.pointConstraint(ik[4], toe))
	mc.setAttr(toe+".r", 0,0,0)
	mc.connectAttr(ik_ctrl[0]+".toeTwist", toe+".ry")
	mc.setDrivenKeyframe(toe+".rx", v=0, dv=45, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")
	mc.setDrivenKeyframe(toe+".rx", v=45, dv=90, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")

	ball = mc.createNode("transform", n=name+"_ball_grp", p=toe)
	mc.delete(mc.pointConstraint(ik[3], ball))
	mc.setAttr(ball+".r", 0,0,0)
#	mc.connectAttr(ik_ctrl[0]+".ballLift", ball+".rax")
	mc.setDrivenKeyframe(ball+".rx", v=0, dv=0, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")
	mc.setDrivenKeyframe(ball+".rx", v=45, dv=45, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")

	ik_ctrl_grp[1], ik_ctrl[1] = common.control(name=name+"_pv", parent=grp,
							position=ik[1], rotation=ik[1], normal=(0,0,1),
							color=6, radius=radius*0.25, shape=ikShape,
							lockAttr=["r","s"],
							hideAttr=["rx","ry","rz","sx","sy","sz","v"])
	if positions[0][0] <= -0.001:
		direction = 1 if inheritTemplateRotations else -1
		mc.move(0,0,direction*3*radius, ik_ctrl_grp[1], os=True, r=True, wd=True)
	else:
		mc.move(0,0,3*radius, ik_ctrl_grp[1], os=True, r=True, wd=True)
	mc.setAttr(ik_ctrl_grp[1]+".r", 0,0,0)
	mc.connectAttr(ik_ctrl[0]+".ikControls", ik_ctrl_grp[1]+".v")

	#
	# ik stretch joints
	#

	ik2 = [None]*3
	for i in range(3):
		ik2[i] = mc.duplicate(ik[i])[0]
		ik2[i] = mc.rename(ik2[i], name+"_ik"+str(i+1)+"_str")
		if i == 0: ik2[i] = mc.parent(ik2[i], grp)[0]
		else: ik2[i] = mc.parent(ik2[i], ik2[i-1])[0]
		c = mc.parentConstraint(ik[i], ik2[i])[0]
		mc.rename(c, name+"_ik"+str(i+1)+"_parcon")
		mc.setAttr(ik2[i]+".jo", 0,0,0)

	#
	# fk joints and controls
	#

	fk_ctrl = [None]*4
	jnt = [None]*4
	for i in range(4):
		# fk controls
		fk_ctrl[i] = mc.duplicate(ik[i])[0]
		fk_ctrl[i] = mc.rename(fk_ctrl[i], name+"_fk"+str(i+1)+"_ctrl")
		if i != 3:
			mc.connectAttr(ik2[i]+".t", fk_ctrl[i]+".t")
			mc.connectAttr(ik2[i]+".r", fk_ctrl[i]+".jo")
		else:
			mc.connectAttr(ik[i]+".t", fk_ctrl[i]+".t")
			mc.connectAttr(ik[i]+".jo", fk_ctrl[i]+".jo")
		mc.setAttr(fk_ctrl[i]+".r", 0,0,0)

		common.control(addShapeTo=fk_ctrl[i], normal=(1,0,0), color=13, radius=radius*0.7)
		mc.connectAttr(ik_ctrl[0]+".fkControls", mc.listRelatives(fk_ctrl[i], pa=True, s=True)[0]+".v")
		if i: fk_ctrl[i] = mc.parent(fk_ctrl[i], fk_ctrl[i-1])[0]
		else: fk_ctrl[i] = mc.parent(fk_ctrl[i], grp)[0]
		mc.setAttr(fk_ctrl[i]+".drawStyle", 2)

		# fk joints
		jnt[i] = mc.duplicate(ik[i])[0]
		jnt[i] = mc.parent(jnt[i], fk_ctrl[i])[0]
		jnt[i] = mc.rename(jnt[i], name+"_jnt"+str(i+1))
		for a in ["t","r","jo"]: mc.setAttr(jnt[i]+"."+a, 0,0,0)
		mc.connectAttr(ik_ctrl[0]+".joints", jnt[i]+".v")
		mc.setAttr(fk_ctrl[i]+".drawStyle", 2)

	rev = mc.createNode("reverse")
	mc.connectAttr(ik_ctrl[0]+".toeLift", rev+".inputX")
	mc.connectAttr(rev+".outputX", jnt[3]+".ry")

	mc.setDrivenKeyframe(fk_ctrl[3]+".ray", v=30, dv=-30, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")
	mc.setDrivenKeyframe(fk_ctrl[3]+".ray", v=0, dv=0, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")
	mc.setDrivenKeyframe(fk_ctrl[3]+".ray", v=-45, dv=45, cd=ik_ctrl[0]+".footRoll", itt="linear", ott="linear")

	#
	# ik handles
	#

	for i in range(1,5): ik[i] = mc.parent(ik[i], ik[i-1])[0]
	mc.select(ik); mc.SetPreferredAngle()

	common.ikHandle(name+"_ball", ik[2], ik[3], parent=ball)
	common.ikHandle(name+"_toe", ik[3], ik[4], parent=toe)
	ikh = common.ikHandle(name, ik[0], ik[2], parent=ball)[0]
	pvc = mc.poleVectorConstraint(ik_ctrl[1], ikh)[0]
	mc.rename(pvc, name+"_pvcon")

	#
	# stretch math
	#

	ik1_jnt_grp = mc.createNode("transform", n=ik[0]+"_grp", p=grp)
	mc.delete(mc.pointConstraint(ik[0], ik1_jnt_grp))
	n = mc.duplicate(ik1_jnt_grp)[0]
	n = mc.rename(n, "str_grp")
	db1 = mc.createNode("distanceBetween")
	mc.connectAttr(ik1_jnt_grp+".worldMatrix", db1+".inMatrix1")
	mc.connectAttr(ik_ctrl[0]+".worldMatrix", db1+".inMatrix2")
	db2 = mc.createNode("distanceBetween")
	mc.connectAttr(n+".worldMatrix", db2+".inMatrix1")
	mc.connectAttr(ik_ctrl_grp[0]+".worldMatrix", db2+".inMatrix2")
	md1 = mc.createNode("multiplyDivide")
	mc.setAttr(md1+".operation", 2)
	mc.connectAttr(db1+".distance", md1+".input1X")
	mc.connectAttr(db2+".distance", md1+".input2X")
	md2 = mc.createNode("multiplyDivide")
	mc.connectAttr(md1+".outputX", md2+".input1X")
	mc.connectAttr(ik_ctrl[0]+".stretch", md2+".input2X")
	c = mc.createNode("condition")
	mc.setAttr(c+".secondTerm", 1)
	mc.setAttr(c+".operation", 3)
	mc.connectAttr(md1+".outputX", c+".colorIfTrueR")
	mc.connectAttr(md2+".outputX", c+".firstTerm")

	mc.connectAttr(c+".outColorR", ik[0]+".sx")
	mc.connectAttr(c+".outColorR", ik[1]+".sx")

	# offset the stretch group to enable full extension
	# of the leg before it starts stretching
	db3 = mc.createNode("distanceBetween")
	mc.connectAttr(ik[0]+".worldMatrix", db3+".inMatrix1")
	mc.connectAttr(ik[1]+".worldMatrix", db3+".inMatrix2")
	d = mc.getAttr(db3+".distance")
	mc.connectAttr(ik[2]+".worldMatrix", db3+".inMatrix1", f=True)
	d += mc.getAttr(db3+".distance") - mc.getAttr(db1+".distance")
	mc.delete(db3)
	p = mc.xform(ik[0], q=True, rp=True, ws=True)
	p2 = mc.xform(ik[2], q=True, rp=True, ws=True)
	p[0] -= p2[0]
	p[1] -= p2[1]
	p[2] -= p2[2]
	m = math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2])
	p[0] /= m
	p[1] /= m
	p[2] /= m
	p2 = mc.getAttr(n+".t")[0]
	mc.setAttr(n+".t", p2[0]+p[0]*d, p2[1]+p[1]*d, p2[2]+p[2]*d)
	
	#
	# lock and hide attributes
	#

	for i in range(4):
		if i == 0 or i == 2:
			for a in ["tx","ty","tz","sx","sy","sz","v","radius"]:
				mc.setAttr(fk_ctrl[i]+"."+a, l=True, k=False, cb=False)
		else:
			for a in ["tx","ty","tz","rx","rz","sx","sy","sz","v","radius"]:
				mc.setAttr(fk_ctrl[i]+"."+a, l=True, k=False, cb=False)

	# selection sets
	common.sets(name, jnt, fk_ctrl, ik_ctrl)

	# selectable joints
	common.selectable(ik_ctrl[0]+".editJoints", jnt)

	# fk to ik bake ready
	for i in range(3):
		mc.addAttr(ik_ctrl[0], ln="fk"+str(i+1), at="message", h=True)
		mc.addAttr(fk_ctrl[i], ln="fk", at="message", h=True)
		mc.connectAttr(ik_ctrl[0]+".fk"+str(i+1), fk_ctrl[i]+".fk")
	mc.addAttr(ik_ctrl[0], ln="ik1", at="message", h=True)
	mc.addAttr(ik_ctrl[1], ln="ik", at="message", h=True)
	mc.connectAttr(ik_ctrl[0]+".ik1", ik_ctrl[1]+".ik")

	# organize
	if tmp: mc.delete(tmp)
	mc.hide(ik[0], ik2[0])
	mc.parent(ik[0], ik1_jnt_grp)
	mc.select(grp)
	mc.dgdirty(a=True)

	return grp

def template(name="leg", radius=0.25):

	jnt = [None]*6
	pos = [(0,9,0),(0,5,0.25),(0,0.5,0),(0,0,1.5),(0,0,2.5),(0,0,-0.5)]
	for i in range(6):
		name2 = name+"_tmp"+str(i+1)
		if mc.objExists(name2): jnt[i] = name2
		else:
			jnt[i] = mc.createNode("joint", n=name2)
			mc.setAttr(jnt[i]+".t", pos[i][0], pos[i][1], pos[i][2])
			if i == 5: jnt[i] = mc.parent(jnt[i], jnt[2])[0]
			elif i: jnt[i] = mc.parent(jnt[i], jnt[i-1])[0]
		mc.setAttr(jnt[i]+".radius", radius)

	mc.select(jnt[0])

	return jnt
