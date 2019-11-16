import sys, os
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="assembly", position=(0,0,0), radius=1, fbx=False,
		cog=True, body=True, pelvis=True):

	if type(position) == str or type(position) == unicode:
		position = mc.xform(position, q=True, rp=True, ws=True)

	grp = mc.createNode("transform", n=name)
	mc.addAttr(grp, ln="joints", at="bool", dv=True, k=True)
	mc.addAttr(grp, ln="editJoints", at="bool", k=True)
	if fbx:
		mc.setAttr(grp+".joints", False)
		mc.addAttr(grp, ln="fbxJoints", at="bool", dv=True, k=True)
		mc.addAttr(grp, ln="editFbxJoints", at="bool", k=True)
	mc.addAttr(grp, ln="controls", at="bool", dv=True, k=True)
	mc.addAttr(grp, ln="_geometry", at="bool", dv=True, k=True)
	mc.addAttr(grp, ln="editGeometry", at="bool", k=True)

	#
	# controls
	#

	ctrl = []
	ctrl.append(common.control(name="world", parent=grp, radius=radius*5, color=13,
					lockAttr=["v"], hideAttr=["v"])[1])

	if cog:
		ctrl.append(common.control(name="cog", parent=ctrl[0], position=position,
					color=13, radius=radius*4, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])[1])

	if body:
		ctrl.append(common.control(name="body", parent=ctrl[1], position=ctrl[1],
					color=13, radius=radius*3, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])[1])

	if pelvis:
		ctrl.append(common.control(name="pelvis", parent=ctrl[2], position=ctrl[2],
					radius=radius*2, lockAttr=["s","v"],
					hideAttr=["sx","sy","sz","v"])[1])

	grps = [None]*2
	rev = mc.createNode("reverse")
	if fbx:
		grps[0] = mc.createNode("transform", n="skeleton_fbx")
		grps[1] = mc.createNode("transform", n="geometry_fbx")
		mc.connectAttr(grp+".fbxJoints", grps[0]+".v")
		mc.setAttr(grps[0]+".overrideDisplayType", 2)
		mc.connectAttr(grp+".editFbxJoints", rev+".inputX")
		mc.connectAttr(rev+".outputX", grps[0]+".overrideEnabled")
		mc.createNode("transform", n="constraints_fbx", p=grp)
	else:
		grps[1] = mc.createNode("transform", n="geometry", p=grp)
	mc.connectAttr(grp+"._geometry", grps[1]+".v")
	mc.connectAttr(grp+".editGeometry", rev+".inputY")
	mc.connectAttr(rev+".outputY", grps[1]+".overrideEnabled")
	mc.setAttr(grps[1]+".overrideDisplayType", 2)

	for n in grps:
		for a in ["tx","ty","tz","rx","ry","rz","sx","sy","sz","v"]:
			try: mc.setAttr(n+"."+a, l=True, k=False, cb=False)
			except: pass

	#
	# selection sets
	#

	n1 = mc.sets(n="ik_controls_set", em=True)
	n2 = mc.sets(n="fk_controls_set", em=True)
	for n in ctrl: mc.connectAttr(n+".message", n2+".dnSetMembers", na=True)
	n3 = mc.sets(n="joints_set", em=True)
	n4 = mc.sets(n=name+"_set", em=True)
	mc.sets(n1, n2, n3, add=n4)

	mc.select(grp)
	mc.dgdirty(a=True)

	return grp
