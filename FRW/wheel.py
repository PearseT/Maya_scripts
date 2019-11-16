import sys, os
import maya.cmds as mc
import maya.mel as mm
THIS_DIR, THIS_FILE = os.path.split(__file__); sys.path.append(THIS_DIR)
import root; reload(root)
import common; reload(common)
import terrain as _terrain; reload(_terrain)

def main(name="wheel", terrain=None, radius=1, scale=1):

	if terrain == None:
		l = mc.ls(sl=True, o=True) or []
		for n in l:
			if mc.nodeType(n) == "mesh":
				terrain = n
				break
			else:
				l2 = mc.listRelatives(n, pa=True, s=True, ni=True) or []
				for n2 in l2:
					if mc.nodeType(n2) == "mesh":
						terrain = n
						break
			if terrain: break

	grp, ctrl = common.control(name=name+"_placer", color=6, radius=radius*3, shape="square",
								hideAttr=["tx","tz","rx","ry","rz","sx","sy","sz","v"],
								lockAttr=["tx","tz","rx","ry","rz","sx","sy","sz"])
	grp = mc.rename(grp, name+"_grp")

	susp = mc.curve(d=1, p=[(0,-0.5,0),(0,0.5,0)], k=(0,1), n=name+"_susp")
	mc.setAttr(susp+".template", True)
	susp = mc.parent(susp, ctrl)[0]

	grp2, ctrl2 = common.control(name=name, numOffsetGroups=1, color=13, radius=radius*1.25,
					normal=(1,0,0), parent=grp, lockAttr=["tx","tz","rx"],
					hideAttr=["tx","tz","rx","sx","sy","sz"])
	tilt = mc.listRelatives(ctrl2, pa=True, p=True)[0]
	tilt = mc.rename(tilt, name+"_tilt_grp")
	mc.addAttr(ctrl2, ln="joints", at="bool", dv=True, k=True)
	mc.addAttr(ctrl2, ln="editJoints", at="bool", k=True)
	mc.addAttr(ctrl2, ln="placer", at="bool", dv=True, k=True)
	mc.addAttr(ctrl2, ln="wheel", at="bool", dv=True, k=True)
	mc.addAttr(ctrl2, ln="terrain", at="bool", dv=True, k=True)
	mc.addAttr(ctrl2, ln="editTerrain", at="bool", dv=False, k=True)
	mc.addAttr(ctrl2, ln="spin", at="double", k=True)
	mc.addAttr(ctrl2, ln="tilt", at="double", dv=1, k=True)
	mc.addAttr(ctrl2, ln="size", at="double", dv=1, min=0, k=True)
	mc.addAttr(ctrl2, ln="terrainDetection", at="bool", dv=True, k=True)
	mc.addAttr(ctrl2, ln="suspensionOffset", at="double", min=0, k=True)
	mc.addAttr(ctrl2, ln="suspensionLength", at="double", dv=1, min=0, k=True)

	mc.connectAttr(ctrl2+".placer", ctrl+"Shape.v")

	wheel = mc.polyCylinder(h=0.5, ax=(1,0,0), sc=1, ch=False, n=name+"_pxy")[0]
	mc.select(wheel+".e[0:19]", wheel+".e[20:39]")
	mc.polyBevel(wheel+".e[0:39]", o=0.1, ch=False)
	mc.setAttr(wheel+"Shape.overrideEnabled", True)
	mc.setAttr(wheel+"Shape.overrideDisplayType", 2)
	mc.setAttr(wheel+"Shape.overrideShading", 0)
	mc.setAttr(wheel+"Shape.overrideColor", 1)
	mc.setAttr(wheel+".castsShadows", 0)
	mc.setAttr(wheel+".receiveShadows", 0)
	mc.setAttr(wheel+".primaryVisibility", 0)
	mc.setAttr(wheel+".visibleInReflections", 0)
	mc.setAttr(wheel+".visibleInRefractions", 0)
	mc.setAttr(wheel+".doubleSided", 0)
	mc.connectAttr(ctrl2+".wheel", wheel+"Shape.v")
	mc.parent(wheel, ctrl)

	jnt = mc.createNode("joint", n=name+"_jnt", p=ctrl, ss=True)
	mc.connectAttr(wheel+".t", jnt+".t")
	mc.connectAttr(wheel+".r", jnt+".r")
	mc.connectAttr(ctrl2+".joints", jnt+".v")
	mc.setAttr(jnt+".radius", radius*0.5)
	common.selectable(ctrl2+".editJoints", jnt)
	common.sets("wheel", jnt, None, None)

	if terrain == None:
		terrain = _terrain.main(name=name, parent=grp)
		mc.connectAttr(ctrl2+".terrain", terrain+".v")
		r = mc.createNode("reverse", ss=True)
		mc.connectAttr(ctrl2+".editTerrain", r+".inputX")
		mc.connectAttr(r+".outputX", terrain+".template")

	ter_ted = mc.createNode("transform", p=ctrl, n=name+"_terrain_detection", ss=True)
	pc = mc.parentConstraint(ctrl2, wheel)[0]
	mc.pointConstraint(susp, ter_ted)
	gc = mc.geometryConstraint(terrain, ter_ted)[0]
	mc.connectAttr(ctrl2+".terrainDetection", gc+"."+terrain+"W0")
	susp_orig = mc.createNode("transform", p=ctrl, n=name+"_suspension_origin", ss=True)
	mc.pointConstraint(ter_ted, susp_orig)
	mc.geometryConstraint(susp, susp_orig)
	sPntConst = mc.pointConstraint(susp_orig, grp2)[0]

	mc.connectAttr(ctrl2+".suspensionOffset", susp+".ty")
	mc.connectAttr(ctrl2+".suspensionLength", susp+".sy")
	mc.connectAttr(ctrl2+".placer", susp+".v")
	adl = mc.createNode("addDoubleLinear", ss=True)
	mc.connectAttr(ctrl2+".spin", adl+".input1")
	mc.connectAttr(adl+".output", pc+".target[0].targetOffsetRotateX")
	adl = mc.createNode("addDoubleLinear", ss=True)
	mc.connectAttr(ctrl2+".tilt", adl+".input1")
	md = mc.createNode("multiplyDivide", ss=True)
	mc.setAttr(md+".input2Y", -1)
	mc.connectAttr(ctrl2+".size", md+".input1Y")
	mc.connectAttr(md+".outputY", tilt+".rotatePivotY")
	mc.connectAttr(md+".outputY", tilt+".scalePivotY")
	mc.connectAttr(ctrl2+".s", wheel+".s")
	mc.connectAttr(ctrl2+".size", sPntConst+".oy")
	mc.connectAttr(ctrl2+".size", ctrl2+".sx")
	mc.connectAttr(ctrl2+".size", ctrl2+".sy")
	mc.connectAttr(ctrl2+".size", ctrl2+".sz")
	mc.setAttr(ctrl2+".s", l=True)
	mc.move(0, -1, 0, tilt+".scalePivot", tilt+".rotatePivot", r=True)

	mc.expression(s=tilt+".rz = "+ctrl2+".ry * -"+adl+".output * 0.25", o="", ae=True, uc="all", n=name+"_wheel_exp")

	common.sets("wheel", None, [ctrl, ctrl2], None)

	mc.select(grp)
	mc.dgdirty(a=True)

	return grp, ctrl, ctrl2, wheel