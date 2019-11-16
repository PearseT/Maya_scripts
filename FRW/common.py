import os
import maya.cmds as mc
import tools; reload(tools)

def sets(name, jnt, fk, ik):

	if not mc.objExists("joints_set") and not mc.objExists(name+"_set"):
		mc.sets(n=name+"_set", em=True)

	if type(jnt) == str or type(jnt) == unicode: jnt = [jnt]
	if jnt:
		if mc.objExists(name+"_joints_set"): ss = name+"_joints_set"
		else: ss = mc.sets(n=name+"_joints_set", em=True)
		for n in jnt: mc.connectAttr(n+".message", ss+".dnSetMembers", na=True)
		if mc.objExists("joints_set"): mc.sets(ss, fe="joints_set")
		else: mc.sets(ss, fe=name+"_set")

	if type(fk) == str or type(fk) == unicode: fk = [fk]
	if fk:
		if mc.objExists(name+"_fk_controls_set"): ss = name+"_fk_controls_set"
		else: ss = mc.sets(n=name+"_fk_controls_set", em=True)
		for n in fk: mc.connectAttr(n+".message", ss+".dnSetMembers", na=True)
		if mc.objExists("fk_controls_set"): mc.sets(ss, fe="fk_controls_set")
		else: mc.sets(ss, fe=name+"_set")

	if type(ik) == str or type(ik) == unicode: ik = [ik]
	if ik:
		if mc.objExists(name+"_ik_controls_set"): ss = name+"_ik_controls_set"
		else: ss = mc.sets(n=name+"_ik_controls_set", em=True)
		for n in ik: mc.connectAttr(n+".message", ss+".dnSetMembers", na=True)
		if mc.objExists("ik_controls_set"): mc.sets(ss, fe="ik_controls_set")
		else: mc.sets(ss, fe=name+"_set")

def ikHandle(name, jnt1, jnt2, parent=None):

	mc.select(jnt1, jnt2)
	ikh, eff = mc.ikHandle()
	mc.hide(ikh)
	if parent: ikh = mc.parent(ikh, parent)[0]
	ikh = mc.rename(ikh, name+"_ikh")
	eff = mc.rename(eff, name+"_eff")

	return ikh, eff

def control(name="default", parent=None, position=None, rotation=None,
	numOffsetGroups=0, color=17, radius=1, normal=(0,1,0), addShapeTo=None,
	shape="circle", lockAttr=[], hideAttr=[]):

	# don't create new control, but add shape to existing node and return it
	if addShapeTo:
		if shape == "circle": ctrl = mc.circle(ch=False, nr=normal, r=radius)[0]
		elif shape == "square":
			if type(radius) == int or type(radius) == float:
				f = 0.5 * radius
				plane = mc.polyPlane(w=f, h=f, sx=1, sy=1, ax=normal)[0]
			elif type(radius) == tuple or type(radius) == list:
				w = 0.5 * radius[0]
				h = 0.5 * radius[1]
				plane = mc.polyPlane(w=w, h=h, sx=1, sy=1, ax=normal)[0]
			p1 = mc.pointPosition(plane+".vtx[0]")
			p2 = mc.pointPosition(plane+".vtx[1]")
			p3 = mc.pointPosition(plane+".vtx[2]")
			p4 = mc.pointPosition(plane+".vtx[3]")
			ctrl = mc.curve(d=1, p=[p1,p2,p4,p3,p1], k=(0,1,2,3,4))
			mc.delete(plane)
		else:
			f = 0.5 * radius
			ctrl = mc.curve(d=1, p=[(-f,-f,f),(f,-f,f),(f,-f,-f),
					(-f,-f,-f),(-f,-f,f),(-f,f,f),(f,f,f),
					(f,-f,f),(f,f,f),(f,f,-f),(f,-f,-f),
					(f,f,-f),(-f,f,-f),(-f,-f,-f),(-f,f,-f),
					(-f,f,f)], k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15))
		shape = mc.listRelatives(ctrl, pa=True, s=True)[0]
		mc.setAttr(shape+".overrideEnabled", True)
		mc.setAttr(shape+".overrideColor", color)
		shape = mc.parent(shape, addShapeTo, add=True, s=True)[0]
		mc.delete(ctrl)

		return mc.rename(shape, addShapeTo.split("|")[-1]+"Shape")

	# zero group
	grp = mc.createNode("transform", n=name+"_ctrl_grp")
	if type(position) == str or type(position) == unicode:
		mc.delete(mc.pointConstraint(position, grp))
	if type(rotation) == str or type(rotation) == unicode:
		mc.delete(mc.orientConstraint(rotation, grp))
	if type(position) == list or type(position) == tuple:
		mc.setAttr(grp+".t", position[0], position[1], position[2])
	if type(rotation) == list or type(rotation) == tuple:
		mc.setAttr(grp+".r", rotation[0], rotation[1], rotation[2])
	if parent: grp = mc.parent(grp, parent)[0]

	# offset group(s)
	if numOffsetGroups:
		off = grp
		for i in range(numOffsetGroups):
			off = mc.createNode("transform", n=name+"_off#", p=off)
			mc.setAttr(off+".t", 0,0,0)
			mc.setAttr(off+".r", 0,0,0)
			mc.setAttr(off+".s", 1,1,1)
	else:
		off = grp

	# the control
	if shape == "circle": ctrl = mc.circle(ch=False, nr=normal, r=radius, n=name+"_ctrl")[0]
	elif shape == "square":
		if type(radius) == int or type(radius) == float:
			plane = mc.polyPlane(w=0.5*radius, h=0.5*radius, sx=1, sy=1, ax=normal)[0]
		elif type(radius) == tuple or type(radius) == list:
			plane = mc.polyPlane(w=0.5*radius[0], h=0.5*radius[1], sx=1, sy=1, ax=normal)[0]
		p1 = mc.pointPosition(plane+".vtx[0]")
		p2 = mc.pointPosition(plane+".vtx[1]")
		p3 = mc.pointPosition(plane+".vtx[2]")
		p4 = mc.pointPosition(plane+".vtx[3]")
		ctrl = mc.curve(d=1, p=[p1,p2,p4,p3,p1], k=(0,1,2,3,4), n=name+"_ctrl")
		mc.delete(plane)
	else:
		f = 0.5 * radius
		ctrl = mc.curve(d=1, p=[(-f,-f,f),(f,-f,f),(f,-f,-f),
				(-f,-f,-f),(-f,-f,f),(-f,f,f),(f,f,f),
				(f,-f,f),(f,f,f),(f,f,-f),(f,-f,-f),
				(f,f,-f),(-f,f,-f),(-f,-f,-f),(-f,f,-f),
				(-f,f,f)], k=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15),
				n=name+"_ctrl")
	shape = mc.listRelatives(ctrl, pa=True, s=True)[0]
	shape = mc.rename(shape, name+"_ctrlShape")
	mc.setAttr(shape+".overrideEnabled", True)
	mc.setAttr(shape+".overrideColor", color)
	ctrl = mc.parent(ctrl, off)[0]
	mc.setAttr(ctrl+".t", 0,0,0)
	mc.setAttr(ctrl+".r", 0,0,0)
	mc.setAttr(ctrl+".s", 1,1,1)

	# lock and hide attributes
	for a in hideAttr: mc.setAttr(ctrl+"."+a, k=False, cb=False)
	for a in lockAttr: mc.setAttr(ctrl+"."+a, l=True)

	mc.select(ctrl)

	return grp, ctrl

def space(base, target, control=None, constraint="parent", name=None):

	if not control: control = base
	if not name: name = target

	if not mc.objExists(base+"."+constraint+"_constraint_space"):
		mc.addAttr(base, ln=""+constraint+"_constraint_space", at="message")
	try: grp = mc.listConnections(base+"."+constraint+"_constraint_space", s=True, d=False)[0]
	except:
		grp = None
		if mc.objExists(base+"_spc"): grp_name = base+"_spc#"
		else: grp_name = base+"_spc"
		try: grp = mc.createNode("transform", n=grp_name, p=mc.listRelatives(base, pa=True, p=True)[0])
		except: grp = mc.createNode("transform", n=grp_name)
		mc.setAttr(grp+".t", 0,0,0)
		mc.setAttr(grp+".r", 0,0,0)
		mc.setAttr(grp+".s", 1,1,1)
		mc.connectAttr(grp+".message", base+"."+constraint+"_constraint_space")
		base = mc.parent(base, grp)[0]

	if constraint == "parent":
		c = mc.parentConstraint(target, grp, mo=True)[0]
		c = mc.rename(c, grp+"_parcon")
	elif constraint == "point":
		c = mc.pointConstraint(target, grp, mo=True)[0]
		c = mc.rename(c, grp+"_pntcon")
	elif constraint == "orient":
		n = mc.createNode("transform", n=base+"___space#")
		mc.delete(mc.orientConstraint(target, n))
		r = mc.getAttr(n+".r")[0]
		if abs(r[0]) > 0.001 or abs(r[1]) > 0.001 or abs(r[2]) > 0.001:
			n = mc.parent(n, target)
			mc.delete(mc.orientConstraint(grp, n))
			c = mc.orientConstraint(n, grp)[0]
		else:
			mc.delete(n)
			c = mc.orientConstraint(target, grp)[0]
		c = mc.rename(c, grp+"_oricon")

	tgt_idx = int(mc.listAttr(c+".target", m=True)[-1].split("[")[-1].split("]")[0])

	if not mc.objExists(control+".space"):
		mc.addAttr(control, ln="space", at="enum", en=name+":", k=True)
		enm_idx = 0
	else:
		l = mc.attributeQuery("space", node=control, le=True)[0].split(":")
		s = ":".join(str(s) for s in l)
		mc.addAttr(control+".space", e=True, en=s+":"+name+":")
		enm_idx = len(l)

	con = mc.createNode("condition")
	mc.setAttr(con+".firstTerm", enm_idx)
	mc.setAttr(con+".colorIfTrueR", 1)
	mc.setAttr(con+".colorIfFalseR", 0)
	mc.connectAttr(control+".space", con+".secondTerm")
	mc.connectAttr(con+".outColorR", c+".target["+str(tgt_idx)+"].targetWeight", f=True)

def selectable(controlNodeAttr, nodes):

	rev = mc.createNode("reverse")
	mc.connectAttr(controlNodeAttr, rev+".inputX")
	if type(nodes) == str or type(nodes) == unicode: nodes = [nodes]
	for n in nodes:
		mc.setAttr(n+".overrideDisplayType", 2)
		mc.connectAttr(rev+".outputX", n+".overrideEnabled")

def saveControlShapes(filepath, controls=None):

	if not controls: controls = mc.ls(sl=True, o=True) or []
	c = len(controls)
	if c == 0: return

	l = [None]*c
	for i in range(c):
		if not mc.objExists(controls[i]+".worldSpace"): continue
		l[i] = mc.curve(d=1, p=(0,0,0), k=(0))
		mc.connectAttr(controls[i]+".worldSpace", l[i]+".create")
		shape = mc.listRelatives(controls[i], pa=True, s=True)[0]
		mc.setAttr(l[i]+".overrideEnabled", True)
		mc.setAttr(l[i]+".overrideColor", mc.getAttr(shape+".overrideColor"))
		l[i] = mc.rename(l[i], controls[i])

	mc.dgdirty(a=True)

	for i in range(len(l)):
		na = mc.listConnections(l[i]+".create", s=True, d=False, p=True)[0]
		mc.disconnectAttr(na, l[i]+".create")

	mc.select(l)
	mc.file(filepath, f=True, op="v=0;", typ="mayaAscii", es=True)
	mc.delete(l)
	print("Result: "+filepath)

def loadControlShapes(filepath):

	ns = os.path.splitext(os.path.split(filepath)[1])[0]
	f = mc.file(filepath, r=True, mnc=False, ns=ns, op="v=0;")
	nodes = mc.referenceQuery(f, n=True) or []
	if len(nodes) == 0: return

	for n in nodes:
		control = n.split(":")[1]
		if mc.nodeType(n) != "transform" or not mc.objExists(control+".create"): continue
		mc.connectAttr(n+".local", control+".create")
		shape = mc.listRelatives(control, pa=True, s=True)[0]
		mc.setAttr(shape+".overrideColor", mc.getAttr(n+".overrideColor"))

	mc.dgdirty(a=True)
	mc.file(filepath, rr=True, f=True)
	print("Result: "+filepath)

def loadTemplate(filepath, scale=1):

	if not os.path.isfile(filepath): return
	if not mc.objExists("template"):
		mc.file(filepath, i=True, f=True, mnc=True)
		mc.setAttr("template.s", scale, scale, scale)
		mc.select("template")

def loadModel(filepath):

	if type(filepath) == str or type(filepath) == unicode: filepath = [filepath]
	if type(filepath) != list: return

	l = mc.ls(assemblies=True) or []
	for f in filepath:
		if os.path.isfile(f):
			mc.file(filepath, i=True, f=True, mnc=True)
	if mc.objExists("geometry"):
		l = list(set(mc.ls(assemblies=True)) - set(l))
		if len(l) > 0: mc.parent(l, "geometry")

def bind(directory, method="index"):

	if not mc.objExists("geometry"): return

	nodes = []
	l = mc.listRelatives("geometry", ad=True) or []
	for n in l:
		t = mc.nodeType(n)
		if t == "mesh" or t == "nurbsCurve" or t == "nurbsSurface":
			if not mc.getAttr(n+".io"):
				nodes.append(mc.listRelatives(n, pa=True, p=True)[0])
	if len(nodes) > 0:
		tools.importDeformerWeights(nodes=nodes, directory=directory, method=method)
