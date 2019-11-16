import os
from operator import add
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om

def switchSpace(space=None, startFrame=None, endFrame=None, replace=False):

	if not space: raise Exception("Specify transformation space.")

	controls = mc.ls(sl=True, o=True) or []
	if not len(controls): raise Exception("Nothing is selected. Select one or more controls.")
	controls = list(set(controls))

	mc.dgdirty(a=True)

	try:
		if startFrame == None:
			if mm.eval("timeControl -q -rv $gPlayBackSlider"):
				startFrame = mm.eval("timeControl -q -ra $gPlayBackSlider")[0]
			else: startFrame = mc.playbackOptions(q=True, min=True)
		if endFrame == None:
			if mm.eval("timeControl -q -rv $gPlayBackSlider"):
				endFrame = mm.eval("timeControl -q -ra $gPlayBackSlider")[1]
			else: endFrame = mc.playbackOptions(q=True, max=True)

		if not replace:
			mc.selectKey(controls, k=True, t=(-999999999, startFrame-1))
			mc.selectKey(controls, k=True, t=(endFrame+1, 999999999), add=True)
			mc.copyKey(an="keys")

		baked = {}
		for control in controls:
			if not mc.objExists(control+".space"): continue
			spaces = mc.attributeQuery("space", node=control, le=True)[0].split(":")
			if space not in spaces: continue
			currentSpaceId = mc.getAttr(control+".space")
			if spaces[currentSpaceId] == space: continue
			baked[control] = mc.createNode("transform", ss=True)
			mc.parentConstraint(control, baked[control])

		mc.bakeResults(baked.values(), t=(startFrame, endFrame), sm=True, at=["t","tx","ty","tz","r","rx","ry","rz"])

		for control in baked.viewkeys():
			spaces = mc.attributeQuery("space", node=control, le=True)[0].split(":")
			currentSpaceId = mc.getAttr(control+".space")
			for i in range(len(spaces)):
				if spaces[i] == space:
					newSpaceId = i
					break
			mc.setKeyframe(control+".space", v=currentSpaceId, t=startFrame-1)
			mc.setKeyframe(control+".space", v=newSpaceId, t=startFrame)
			for a in ["t","tx","ty","tz","r","rx","ry","rz"]:
				mm.eval("CBdeleteConnection "+control+"."+a)
				try: mc.setAttr(control+"."+a, 0)
				except: pass

		constraints = []
		for control in controls:
			for i in range(len(spaces)):
				if space == spaces[i]:
					mc.setAttr(control+".space", i)
					break
			try: constraints.append(mc.parentConstraint(baked[control], control)[0])
			except:
				try: constraints.append(mc.pointConstraint(baked[control], control)[0])
				except:
					try: constraints.append(mc.orientConstraint(baked[control], control)[0])
					except: pass

		mc.bakeResults(controls, t=(startFrame, endFrame), sm=True, at=["t","tx","ty","tz","r","rx","ry","rz"])
		mc.delete(constraints, baked.values())

		if not replace: mc.pasteKey(controls, o="merge", cp=1, c=False, to=0, fo=0, vo=0)
	except:
		pass

	mc.dgdirty(a=True)

	mc.select(controls)

def bakeFkToIk(startFrame=None, endFrame=None, replace=False):

	controls = mc.ls(sl=True, o=True) or []
	if not len(controls): raise Exception("Nothing is selected. Select arm/leg ik control(s).")
	controls = list(set(controls))

	fk = {}
	ik = {}
	baked = {}
	for control in controls:
		fk[control] = []
		ik[control] = []
		for i in range(1,5):
			na = control+".fk"+str(i)
			if mc.objExists(na):
				fk[control].insert(0, mc.listConnections(na, s=False, d=True)[0])
			na = control+".ik"+str(i)
			if mc.objExists(na):
				ik[control].insert(0, mc.listConnections(na, s=False, d=True)[0])
		if not len(fk[control]) or not len(ik[control]):
			try: del(fk[control])
			except: pass
			try: del(ik[control])
			except: pass
			continue
		ik[control].insert(0, control)
		baked[control] = []

	# consider pole-vector controls
	for control in controls:
		try: controls.append(ik[control][1])
		except: pass

	if not len(fk): raise Exception("At least one arm/leg ik control should be selected.")

	mc.dgdirty(a=True)

	try:
		for control in fk.viewkeys():
			for i in range(len(fk[control])):
				n = mc.createNode("transform")
				mc.parentConstraint(fk[control][i], n)
				baked[control].append(n)

		if startFrame == None:
			if mm.eval("timeControl -q -rv $gPlayBackSlider"):
				startFrame = mm.eval("timeControl -q -ra $gPlayBackSlider")[0]
			else: startFrame = mc.playbackOptions(q=True, min=True)
		if endFrame == None:
			if mm.eval("timeControl -q -rv $gPlayBackSlider"):
				endFrame = mm.eval("timeControl -q -ra $gPlayBackSlider")[1]
			else: endFrame = mc.playbackOptions(q=True, max=True)
		mc.bakeResults(sum(baked.values(),[]), t=(startFrame, endFrame), sm=True, at=["t","tx","ty","tz","r","rx","ry","rz"])

		mc.select(controls)
		for control in controls:
			for a in ["t","tx","ty","tz","r","rx","ry","rz"]:
				l = mc.listConnections(control+"."+a, s=True, d=False) or []
				if len(l) == 0: continue
				try:
					mc.setKeyframe(control+"."+a, v=mc.getAttr(control+"."+a, t=startFrame-1), t=startFrame-1)
					mc.setKeyframe(control+"."+a, v=mc.getAttr(control+"."+a, t=endFrame+1), t=endFrame+1)
				except:
					pass

		if not replace:
			mc.selectKey(controls, k=True, t=(-999999999, startFrame-1))
			mc.selectKey(controls, k=True, t=(endFrame+1, 999999999), add=True)
			mc.copyKey(an="keys")

		for n in sum(fk.values(),[]):
			for a in ["r","rx","ry","rz"]:
				mm.eval("CBdeleteConnection "+n+"."+a)
				try: mc.setAttr(n+"."+a, 0)
				except: pass
		for l in ik.viewvalues():
			for i in range(len(l)):
				for a in ["t","tx","ty","tz","r","rx","ry","rz"]:
					mm.eval("CBdeleteConnection "+l[i]+"."+a)
					try: mc.setAttr(l[i]+"."+a, 0)
					except: pass

		for control in fk.viewkeys():
			n = mc.createNode("transform")
			mc.delete(mc.parentConstraint(fk[control][0], n))
			mc.parentConstraint(n, control, mo=True)
			n = mc.parent(n, baked[control][0])[0]
			mc.setAttr(n+".t", 0,0,0)
			mc.setAttr(n+".r", 0,0,0)
			if len(ik[control]) > 2:
				n = mc.createNode("transform")
				mc.delete(mc.orientConstraint(fk[control][3], n))
				mc.orientConstraint(n, ik[control][2], mo=True)
				n = mc.parent(n, baked[control][3])[0]
				mc.setAttr(n+".t", 0,0,0)
				mc.setAttr(n+".r", 0,0,0)

		for control in fk.viewkeys():
			try: mc.pointConstraint(baked[control][1], ik[control][1])
			except: pass

		mc.bakeResults(sum(ik.values(),[]), t=(startFrame, endFrame), sm=True, at=["t","tx","ty","tz","r","rx","ry","rz"])
		mc.delete(sum(baked.values(),[]))

		if not replace: mc.pasteKey(controls, o="merge", cp=1, c=False, to=0, fo=0, vo=0)
	except:
		pass

	mc.dgdirty(a=True)

	mc.select(controls)

def centroid():

	l = mc.ls(sl=True, fl=True) or []
	if not len(l): return

	c = 0
	p = [0,0,0]
	for o in l:
		try: p = map(add, mc.pointPosition(o, w=True), p)
		except:
			try: p = map(add, mc.xform(o, q=True, ws=True, rp=True), p)
			except: continue
		c += 1

	if c:
		n = mc.createNode("transform", n="centroid#")
		mc.setAttr(n+".t", p[0]/c,p[1]/c,p[2]/c)
		mc.setAttr(n+".displayHandle", True)

		return n

# Unsupported example only !
# Mocap skeleton should follow HumanIK's naming convention.
# Select the mocap skeleton's top node and SHIFT-select any
# control from the rig before calling the function.
def transferMocap(scale=1):

	src, tgt = mc.ls(sl=True)[:2]
	if ":" in src: ns_src = src.split(":")[0]+":"
	else: ns_src = ""
	if ":" in tgt: ns_tgt = tgt.split(":")[0]+":"
	else: ns_tgt = ""

	grp = mc.createNode("transform")
	src = mc.parent(src, grp)[0]
	mc.setAttr(grp+".s", scale,scale,scale)

	for n in mc.listRelatives(ns_src+"Reference", pa=True, ad=True): mc.setAttr(n+".r", 0,0,0)
	mc.setAttr(ns_src+"Reference.tx", 0)
	mc.setAttr(ns_src+"Reference.tz", 0)

	grp2 = mc.createNode("transform")
	mc.delete(mc.pointConstraint(ns_src+"LeftFoot", grp2))
	mc.parent(grp, grp2)
	mc.setAttr(grp2+".ty", mc.xform(ns_tgt+"ankle_lf_ik_control", q=True, ws=True, rp=True)[1])

	l = []
	l.append(mc.parentConstraint(ns_src+"Hips", ns_tgt+"cog_control", mo=True)[0])
	l.append(mc.orientConstraint(ns_src+"Spine", ns_tgt+"waist_control", mo=False)[0])
	l.append(mc.orientConstraint(ns_src+"Spine1", ns_tgt+"chest_control", mo=False)[0])
	l.append(mc.orientConstraint(ns_src+"Neck", ns_tgt+"neck_control", mo=False)[0])
	l.append(mc.orientConstraint(ns_src+"Head", ns_tgt+"head_control", mo=False)[0])

	mc.setAttr(ns_tgt+"arm_rt_pv_control.space", 0)
	mc.setAttr(ns_tgt+"arm_lf_pv_control.space", 0)
	l.append(mc.parentConstraint(ns_src+"RightLeg", ns_tgt+"leg_rt_pv_control_grp", mo=True)[0])
	l.append(mc.pointConstraint(ns_src+"RightFoot", ns_tgt+"ankle_rt_ik_control")[0])
	l.append(mc.orientConstraint(ns_src+"RightFoot", ns_tgt+"ankle_rt_ik_control", mo=True)[0])

	l.append(mc.orientConstraint(ns_src+"RightShoulder", ns_tgt+"shoulder_rt_ik_control", mo=True)[0])
	l.append(mc.pointConstraint(ns_src+"RightForeArm", ns_tgt+"arm_rt_pv_control")[0])
	mc.delete(mc.pointConstraint(ns_src+"RightHand", ns_tgt+"wrist_rt_ik_control"))
	mc.setAttr(ns_tgt+"wrist_rt_ik_control.ty", 0)
	mc.setAttr(ns_tgt+"wrist_rt_ik_control.tz", 0)
	l.append(mc.parentConstraint(ns_src+"RightHand", ns_tgt+"wrist_rt_ik_control", mo=True)[0])

	l.append(mc.parentConstraint(ns_src+"LeftLeg", ns_tgt+"leg_lf_pv_control_grp", mo=True)[0])
	l.append(mc.pointConstraint(ns_src+"LeftFoot", ns_tgt+"ankle_lf_ik_control")[0])
	l.append(mc.orientConstraint(ns_src+"LeftFoot", ns_tgt+"ankle_lf_ik_control", mo=True)[0])

	l.append(mc.orientConstraint(ns_src+"LeftShoulder", ns_tgt+"shoulder_lf_ik_control", mo=True)[0])
	l.append(mc.pointConstraint(ns_src+"LeftForeArm", ns_tgt+"arm_lf_pv_control")[0])
	mc.delete(mc.pointConstraint(ns_src+"LeftHand", ns_tgt+"wrist_lf_ik_control"))
	mc.setAttr(ns_tgt+"wrist_lf_ik_control.ty", 0)
	mc.setAttr(ns_tgt+"wrist_lf_ik_control.tz", 0)
	l.append(mc.parentConstraint(ns_src+"LeftHand", ns_tgt+"wrist_lf_ik_control", mo=True)[0])

	sf = mc.playbackOptions(q=True, min=True)
	ef = mc.playbackOptions(q=True, max=True)
	mc.bakeResults(mc.sets(ns_tgt+"ik_controls_set", q=True), t=(sf,ef), sm=True)
	mc.delete(grp2)

def exportDeformerWeights(nodes=None, directory="/tmp/"):

	if type(nodes) == str or type(nodes) == unicode: l = [nodes]
	elif type(nodes) == list: l = nodes
	elif nodes == None:
		l = mc.ls(sl=True, o=True) or []
		if len(l) == 0: raise Exception("Nothing is selected. Select objects with applied deformers.")

	nodes = []
	for n in l:
		t = mc.nodeType(n)
		if t == "mesh" or t == "nurbsCurve" or t == "nurbsSurface":
			nodes.append(mc.listRelatives(n, pa=True, p=True)[0])
		else:
			for t in ["mesh", "nurbsCurve", "nurbsSurface"]:
				l2 = mc.listRelatives(n, pa=True, s=True, ni=True, typ=t) or []
				if len(l2) > 0:
					nodes.append(n)
					break

	if not os.path.isdir(directory):
		try: os.makedirs(directory)
		except: raise Exception("Cannot create directory: "+directory)

	for n in nodes:
		deformers = []
		for n2 in mc.listHistory(n):
			l2 = mc.nodeType(n2, i=True)
			if "geometryFilter" in l2 and "tweak" not in l2: deformers.append(n2)
		if len(deformers) == 0: continue
		try: mc.deformerWeights(n+".xml", p=directory, df=deformers, ex=True, vc=True, ws=True, at="*")
		except: pass

def importDeformerWeights(nodes=None, directory="/tmp/", method="index"):

	if not os.path.isdir(directory): raise Exception("Directory not found: "+directory)

	if method not in ["index", "nearest", "barycentric", "bilinear", "over"]:
		raise Exception('Keyword argument "method" can be "index", "nearest", "barycentric", "bilinear", or "over".')

	if type(nodes) == str or type(nodes) == unicode: l = [nodes]
	elif type(nodes) == list: l = nodes
	elif nodes == None:
		l = mc.ls(sl=True, o=True) or []
		if len(l) == 0: raise Exception("Nothing is selected. Select objects with applied deformers.")
	nodes = []
	
	for f in os.listdir(directory):
		if not f.endswith(".xml"): continue
		n = f.split(".")[0]
		if n not in l: continue
		mc.deformerWeights(f, p=directory, im=True, deformer="*", sh=n, m=method)

def mirrorPose():

	l = mc.ls(sl=True, o=True) or []
	for n in l:
		if not n.endswith("_ctrl"): continue
		side = "_lf"
		side2 = "_rt"
		if "_rt" in n:
			side = "_rt"
			side2 = "_lf"
		n2 = n.replace(side, side2)
		if not mc.objExists(n2): continue
		if "_ik_" in n:
			for a in ["tx","ry","rz"]:
				invert = 1 if "shoulder_" in n and a in ["ry","rz"] else -1
				try: mc.setAttr(n2+"."+a, mc.getAttr(n+"."+a) * invert)
				except: pass
			for a in ["ty","tz","rx","sx","sy","sz"]:
				try: mc.setAttr(n2+"."+a, mc.getAttr(n+"."+a))
				except: pass
		elif "_fk" in n:
			for a in ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
				if n.split(":")[-1].startswith("finger_"):
					invert = -1 if a in ["ty","rx","rz"] else 1
				else:
					invert = -1 if "head_eye_" in n and a == "ry" else 1
				try: mc.setAttr(n2+"."+a, mc.getAttr(n+"."+a) * invert)
				except: pass
		elif "_pv_" in n:
			for a in ["tx","ty","tz"]:
				try: mc.setAttr(n2+"."+a, -mc.getAttr(n+"."+a))
				except: pass

def mirrorAnimation():

	mirrorPose()

	l = mc.ls(sl=True, o=True) or []
	for n in l:
		if not n.endswith("_ctrl"): continue
		side = "_lf"
		side2 = "_rt"
		if "_rt" in n:
			side = "_rt"
			side2 = "_lf"
		n2 = n.replace(side, side2)
		if not mc.objExists(n2): continue
		# delete existing anim curves attached to the node on the "other" side
		l2 = mc.listAttr(n2, k=True) or []
		for a in l2:
			l3 = mc.listConnections(n2+"."+a, s=True, d=False, scn=True, t="animCurve") or []
			for n3 in l3:
				try: mc.delete(n3)
				except: pass
		# copy existing anim curves from the node on "this" onto the node on the "other" side
		l2 = mc.listAttr(n, k=True, sn=True) or []
		for a in l2:
			try: n3 = mc.listConnections(n+"."+a, s=True, d=False, scn=True, t="animCurve")[0]
			except: continue
			n3 = mc.duplicate(n3)[0]
			try: mc.connectAttr(n3+".output", n2+"."+a)
			except:
				mc.delete(n3)
				continue
			# mirror keyframes if needed
			if "_ik_" in n and a in ["tx","ry","rz"]:
				if "shoulder_" in n and a in ["ry","rz"]: continue
				mc.select(n3)
				mc.selectKey(n3, k=True, t=(-999999999,999999999))
				mc.scaleKey(iub=False, ts=1, tp=0, fs=1, fp=0, vs=-1, vp=0, an="keys")
			elif "_fk" in n and "head_eye_" in n and a == "ry":
				mc.select(n3)
				mc.selectKey(n3, k=True, t=(-999999999,999999999))
				mc.scaleKey(iub=False, ts=1, tp=0, fs=1, fp=0, vs=-1, vp=0, an="keys")
			elif n.plit(":")[-1].startswith("finger_") and a in ["ty","rx","rz"]:
				mc.select(n3)
				mc.selectKey(n3, k=True, t=(-999999999,999999999))
				mc.scaleKey(iub=False, ts=1, tp=0, fs=1, fp=0, vs=-1, vp=0, an="keys")
			elif "_pv_" in n and a in ["tx","ty","tz"]:
				mc.select(n3)
				mc.selectKey(n3, k=True, t=(-999999999,999999999))
				mc.scaleKey(iub=False, ts=1, tp=0, fs=1, fp=0, vs=-1, vp=0, an="keys")
	if len(l) > 0: mc.select(l)

def spinWheels():

	wheels = []
	namespaces = []
	l = mc.ls(sl=True, o=True) or []
	for n in l: namespaces.append(":".join(s for s in n.split(":")[:-1]))
	for ns in set(namespaces):
		if ns == "": wheels += mc.ls("wheel*_ctrl.spin", o=True, typ="transform") or []
		else: wheels += mc.ls(ns+":wheel*_ctrl.spin", o=True, typ="transform") or []
	if len(wheels) == 0: return

	mm.eval("source channelBoxCommand")

	d = {}
	for wheel in wheels:
		try: mc.setAttr(wheel+".spin", l=False)
		except: continue
		mm.eval("CBdeleteConnection "+wheel+".spin")
		if not ":" in wheel: cog = "cog_ctrl"
		else: cog = ":".join(s for s in wheel.split(":")[:-1])+":cog_ctrl"
		n = mc.createNode("transform", p=cog)
		mc.pointConstraint(wheel, n)
		mc.orientConstraint(cog, n)
		d[n] = [wheel, mc.getAttr(wheel+".size")]
	if len(d) == 0: return

	sf = int(mc.playbackOptions(q=True, min=True))
	ef = int(mc.playbackOptions(q=True, max=True))+1

	mm.eval("paneLayout -e -vis 0 $gMainPane")

	mc.bakeResults(d.keys(), sm=True, t=(sf-1, ef),
					sb=1, dic=False, pok=False,
					sac=False, cp=False, s=False)

	d2 = {}
	t = om.MTime()
	p = om.MPlug()
	for n in d.viewkeys():
		sl = om.MSelectionList()
		sl.add(n+".worldMatrix")
		sl.getPlug(0, p)

		spin = 0.0
		for i in range(sf, ef):
			t.setValue(i)
			dgc = om.MDGContext(t)
			o = p.asMObject(dgc)
			m = om.MFnMatrixData(o).matrix()
			tm = om.MTransformationMatrix(m)
			cp = tm.getTranslation(om.MSpace.kObject)

			t.setValue(float(i-1))
			dgc = om.MDGContext(t)
			o = p.asMObject(dgc)
			m = om.MFnMatrixData(o).matrix()
			tm = om.MTransformationMatrix(m)
			pp = tm.getTranslation(om.MSpace.kObject)

			spin += ((cp.z-pp.z) / d[n][1]) * 57.2957795
			try: mc.setKeyframe(d[n][0]+".spin", t=float(i), v=spin)
			except: pass

	mc.delete(d.keys())

	mm.eval("paneLayout -e -vis 1 $gMainPane")
