import sys, os, copy
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="hand", side="", control=None, parent=None, positions=None,
		inheritTemplateRotations=False, radius=1):

	# create template joints if needed
	tmp = None
	if not positions:
		positions = template(name=name)
		tmp = copy.deepcopy(positions)
	cnt = len(positions)
	if cnt == 0: return

	# positions from template transforms/joints
	rotations = {}
	for i in range(cnt):
		cnt2 = len(positions[i])
		if cnt2 < 3: raise Exception("At least 3 joints are needed to form a finger.")
		for j in range(cnt2):
			if type(positions[i][j]) == str or type(positions[i][j]) == unicode:
				if inheritTemplateRotations:
					if i not in rotations.viewkeys(): rotations[i] = [None]*cnt2
					rotations[i][j] = mc.xform(positions[i][j], q=True, ro=True, ws=True)
				positions[i][j] = mc.xform(positions[i][j], q=True, rp=True, ws=True)

	if not control:
		center = [0,0,0]
		for i in range(cnt):
			center[0] += positions[i][0][0]
			center[1] += positions[i][0][1]
			center[2] += positions[i][0][2]
		center[0] /= cnt
		center[1] /= cnt
		center[2] /= cnt

		control = common.control(name=name, position=center, normal=(1,0,0),
					color=17, radius=radius*2, lockAttr=("v"), hideAttr=("v"))[1]
		parent = control

	if not mc.objExists(control+".joints"):
		mc.addAttr(control, ln="joints", at="bool", dv=True, k=True)
	if not mc.objExists(control+".editJoints"):
		mc.addAttr(control, ln="editJoints", at="bool", dv=True, k=True)
	if not mc.objExists(control+".fingerControls"):
		mc.addAttr(control, ln="fingerControls", at="bool", dv=True, k=True)
	if not mc.objExists(control+".bend"):
		mc.addAttr(control, ln="bend", at="double", min=-10, max=10, k=True)
	if not mc.objExists(control+".splay"):
		mc.addAttr(control, ln="splay", at="double", min=-10, max=10, k=True)

	md1 = mc.createNode("multiplyDivide")
	mc.connectAttr(control+".bend", md1+".input1.input1X")
	mc.connectAttr(control+".bend", md1+".input1.input1Y")
	mc.connectAttr(control+".bend", md1+".input1.input1Z")
	mc.setAttr(md1+".input2X", 6)
	mc.setAttr(md1+".input2Y", 9)
	mc.setAttr(md1+".input2Z", 9)
	md2 = mc.createNode("multiplyDivide")
	mc.connectAttr(control+".bend", md2+".input1.input1X")
	mc.connectAttr(control+".bend", md2+".input1.input1Y")
	mc.connectAttr(control+".bend", md2+".input1.input1Z")
	mc.setAttr(md2+".input2X", 8)
	mc.setAttr(md2+".input2Y", 11)
	mc.setAttr(md2+".input2Z", 7.5)

	jnt = [None]*cnt
	ctrl_grp = [None]*cnt
	ctrl = [None]*cnt
	for i in range(cnt):
		mc.select(cl=True)
		cnt2 = len(positions[i])
		jnt[i] = [None]*cnt2
		if cnt2 == 3: j = 0
		else: j = 1
		jnt[i][0] = mc.createNode("joint", n="finger_"+side+str(i+1)+"_jnt"+str(j+1))
		mc.setAttr(jnt[i][0]+".t", positions[i][j][0], positions[i][j][1], positions[i][j][2])
		jnt[i][1] = mc.createNode("joint", n="finger_"+side+str(i+1)+"_jnt"+str(j+2))
		mc.setAttr(jnt[i][1]+".t", positions[i][j+1][0], positions[i][j+1][1], positions[i][j+1][2])
		jnt[i][2] = mc.createNode("joint", n="finger_"+side+str(i+1)+"_jnt"+str(j+3))
		mc.setAttr(jnt[i][2]+".t", positions[i][j+2][0], positions[i][j+2][1], positions[i][j+2][2])

		if j:
			jnt[i][3] = mc.createNode("joint", n="finger_"+side+str(i+1)+"_jnt1")
			mc.setAttr(jnt[i][3]+".t", positions[i][0][0], positions[i][0][1], positions[i][0][2])
			c = mc.aimConstraint(jnt[i][0], jnt[i][3], aim=(1,0,0), u=(0,0,1), wut="objectrotation", wuo=parent)[0]
			mc.rename(c, jnt[i][3]+"_aimcon")
			jnt[i][3] = mc.parent(jnt[i][3], parent)[0]
			mc.setAttr(jnt[i][3]+".radius", radius*0.3)
			mc.connectAttr(control+".joints", jnt[i][3]+".v")

		if not inheritTemplateRotations:
			n = mc.createNode("transform")
			mc.delete(mc.pointConstraint(jnt[i][0], jnt[i][2], n))
			mc.delete(mc.aimConstraint(jnt[i][2], n, aim=(1,0,0), u=(0,0,1), wut="object", wuo=jnt[i][1]))
			mc.delete(mc.aimConstraint(jnt[i][1], jnt[i][0], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=n))
			mc.delete(mc.aimConstraint(jnt[i][2], jnt[i][1], aim=(1,0,0), u=(0,0,-1), wut="object", wuo=n))
			mc.delete(mc.orientConstraint(jnt[i][1], jnt[i][2]))
			mc.delete(n)
		else:
			for j in range(cnt2):
				mc.setAttr(jnt[i][j]+".r", rotations[i][j][0], rotations[i][j][1], rotations[i][j][2])

		r = mc.getAttr(jnt[i][0]+".r")[0]
		mc.setAttr(jnt[i][0]+".jo", r[0],r[1],r[2])
		mc.setAttr(jnt[i][0]+".r", 0,0,0)
		r = mc.getAttr(jnt[i][1]+".r")[0]
		mc.setAttr(jnt[i][1]+".jo", r[0],r[1],r[2])
		mc.setAttr(jnt[i][1]+".r", 0,0,0)
		mc.parent(jnt[i][1], jnt[i][0])
		r = mc.getAttr(jnt[i][2]+".r")[0]
		mc.setAttr(jnt[i][2]+".jo", r[0],r[1],r[2])
		mc.setAttr(jnt[i][2]+".r", 0,0,0)
		mc.parent(jnt[i][2], jnt[i][1])

		ctrl_grp[i] = [None,None,None]
		ctrl[i] = [None,None,None]
		for j in range(3):
			if j:
				_parent = ctrl[i][j-1]
				lockAttr = ("t","rx","rz","s","v")
				hideAttr = ("tx","ty","tz","rx","rz","sx","sy","sz","v")
			else:
				_parent = parent
				lockAttr = ("s","v")
				hideAttr = ("sx","sy","sz","v")
			ctrl_grp[i][j], ctrl[i][j] = common.control(name="finger_"+side+str(i+1)+"_fk"+str(j+1),
				parent=_parent, position=jnt[i][j], rotation=jnt[i][j], normal=(1,0,0), color=13,
				radius=radius*0.3, lockAttr=lockAttr, hideAttr=hideAttr, numOffsetGroups=True)
			mc.connectAttr(control+".fingerControls", mc.listRelatives(ctrl[i][j], pa=True, s=True)[0]+".v")
			jnt[i][j] = mc.parent(jnt[i][j], ctrl[i][j])[0]
			mc.setAttr(jnt[i][j]+".radius", radius*0.3)
			mc.connectAttr(control+".joints", jnt[i][j]+".v")

		# bend
		mc.connectAttr(md2+".outputX", ctrl_grp[i][0]+".ray")
		mc.connectAttr(md2+".outputY", ctrl_grp[i][1]+".ray")
		mc.connectAttr(md2+".outputZ", ctrl_grp[i][2]+".ray")

	# splay
	delta = 3.0 / (cnt*0.5)
	for i in range(cnt):
		md = mc.createNode("multiplyDivide")
		mc.connectAttr(control+".splay", md+".input1.input1X")
		if mc.xform(ctrl_grp[i][0], q=True, rp=True, ws=True)[0] >= -0.001: mc.setAttr(md+".input2X", -3 + delta*i)
		else: mc.setAttr(md+".input2X", 3 - delta*i)
		if len(jnt[i]) == 4: mc.connectAttr(md+".outputX", ctrl_grp[i][0]+".raz")
		else: mc.connectAttr(md+".outputX", mc.listRelatives(ctrl[i][0], pa=True, p=True)[0]+".raz")

	# selection sets
	if side: name += "_"+side
	common.sets(name, sum(jnt,[]), sum(ctrl,[]), None)

	# selectable joints
	common.selectable(control+".editJoints", sum(jnt,[]))

	if tmp: mc.delete(sum(tmp,[]))
	mc.select(control)
	mc.dgdirty(a=True)

	return control

def template(name="hand", radius=0.25,
			positions = [[(0.35,-0.45,0.65),(0.8,-0.764,1.161),(1.158,-1.016,1.57)],
			[(0.25,0,0.35),(1,0,0.35),(1.75,0,0.35),(2.35,0,0.35)],
			[(0.25,0,0),(1,0,0),(1.75,0,0),(2.35,0,0)],
			[(0.25,0,-0.35),(1,0,-0.35),(1.75,0,-0.35),(2.35,0,-0.35)],
			[(0.25,0,-0.7),(1,0,-0.7),(1.75,0,-0.7),(2.35,0,-0.7)]]):

	l = mc.ls(name+"_finger_tmp*_1", typ="joint") or []
	if len(l):
		jnt = []
		l = mc.ls(name+"_finger_tmp*_1", typ="joint") or []
		for n in l:
			l2 = mc.listRelatives(n, pa=True, ad=True) or []
			jnt.append(sorted([n]+l2))
	else:
		# create new or reuse existing template joints
		cnt = len(positions)
		jnt = [None]*cnt
		for i in range(cnt):
			cnt2 = len(positions[i])
			if cnt2 < 3: raise Exception("At least 3 joints are needed to form a finger.")
			jnt[i] = [None]*cnt2
			for j in range(cnt2):
				name2 = name+"_finger_tmp"+str(i+1)+"_"+str(j+1)
				if mc.objExists(name2): jnt[i][j] = name2
				else:
					jnt[i][j] = mc.createNode("joint", n=name2)
					mc.setAttr(jnt[i][j]+".t", positions[i][j][0], positions[i][j][1], positions[i][j][2])
					if j: jnt[i][j] = mc.parent(jnt[i][j], jnt[i][j-1])[0]
				mc.setAttr(jnt[i][j]+".radius", radius)

	mc.select([n[0] for n in jnt])

	return jnt
