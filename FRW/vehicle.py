import sys, os
import maya.cmds as mc
import maya.mel as mm
THIS_DIR, THIS_FILE = os.path.split(__file__); sys.path.append(THIS_DIR)
import common; reload(common)
import root; reload(root)
import wheel; reload(wheel)
import chassis; reload(chassis)
import terrain; reload(terrain)

def main(templateFile=None, controlShapes=None, fbx=False, scale=1, radius=1):

	template(filepath=templateFile, scale=scale)

	root.main(name="assembly", fbx=fbx, radius=radius, body=False, pelvis=False)
	mc.addAttr("assembly", ln="placers", at="bool", k=True)
	mc.addAttr("assembly", ln="wheels", at="bool", dv=True, k=True)
	mc.addAttr("assembly", ln="terrain", at="bool", dv=True, k=True)
	mc.addAttr("assembly", ln="editTerrain", at="bool", k=True)
	mc.addAttr("assembly", ln="terrainDetection", at="bool", dv=True, k=True)

	t = terrain.main(parent="world_ctrl", scale=scale*10)

	wheels = []
	jnts = mc.ls(typ="joint") or []
	for jnt in jnts:
		if jnt.startswith("wheel"):
			grp, ctrl, ctrl2, _wheel = wheel.main(name=jnt.replace("_tmp",""),
												terrain=t, radius=radius)
			mc.delete(mc.parentConstraint(jnt, grp, st="y"))
			ty = mc.xform(jnt, q=True, ws=True, rp=True)[1]
			mc.setAttr(ctrl2+".size", ty)
			wheels.append(grp)

	grp, ctrl = chassis.main(wheels=wheels, parent="world_ctrl", radius=radius)
	mc.parent(wheels, grp)
	mc.parent(grp, "cog_ctrl")

	mc.connectAttr("assembly.joints", ctrl+".joints")
	mc.setAttr(ctrl+".joints", k=False)
	mc.connectAttr("assembly.editJoints", ctrl+".editJoints")
	mc.setAttr(ctrl+".editJoints", k=False)
	mc.connectAttr("assembly.controls", ctrl+".controls")
	mc.connectAttr("assembly.controls", "chassis_ctrlShape.v")
	mc.setAttr(ctrl+".controls", k=False)
	mc.connectAttr("assembly.placers", ctrl+".placers")
	mc.setAttr(ctrl+".placers", k=False)
	mc.connectAttr("assembly.wheels", ctrl+".wheels")
	mc.setAttr(ctrl+".wheels", k=False)
	mc.connectAttr("assembly.terrain", t+".v")
	mc.setAttr(ctrl+".terrain", k=False)
	r = mc.createNode("reverse", ss=True)
	mc.connectAttr("assembly.editTerrain", r+".inputX")
	mc.connectAttr(r+".outputX", t+".template")
	mc.setAttr(ctrl+".editTerrain", k=False)
	mc.connectAttr("assembly.terrainDetection", ctrl+".terrainDetection")
	mc.setAttr(ctrl+".terrainDetection", k=False)

	if fbx:
		mc.createNode("joint", n="root_fbx", p="skeleton_fbx")
		mc.setAttr("root_fbx.radius", radius*0.25)
		c = mc.pointConstraint("cog_ctrl", "root_fbx", sk=["y"])[0]
		mc.parent(c, "constraints_fbx")
		c = mc.orientConstraint("cog_ctrl", "root_fbx", sk=["x","z"])[0]
		mc.parent(c, "constraints_fbx")
		c = mc.scaleConstraint("cog_ctrl", "root_fbx")[0]
		mc.parent(c, "constraints_fbx")
		mc.createNode("joint", n="chassis_fbx", p="root_fbx")
		mc.setAttr("chassis_fbx.radius", radius*0.25)
		c = mc.parentConstraint("chassis_jnt", "chassis_fbx")[0]
		mc.parent(c, "constraints_fbx")
		c = mc.scaleConstraint("chassis_jnt", "chassis_fbx")[0]
		mc.parent(c, "constraints_fbx")
		for n in wheels:
			n = n.replace("_grp","")
			mc.createNode("joint", n=n+"_fbx", p="chassis_fbx")
			mc.setAttr(n+"_fbx.radius", radius*0.25)
			c = mc.parentConstraint(n+"_jnt", n+"_fbx")[0]
			mc.parent(c, "constraints_fbx")
			c = mc.scaleConstraint(n+"_jnt", n+"_fbx")[0]
			mc.parent(c, "constraints_fbx")

	if controlShapes:
		if os.path.isfile(THIS_DIR+"/"+controlShapes):
			common.loadControlShapes(THIS_DIR+"/"+controlShapes)
		elif os.path.isfile(controlShapes):
			common.loadControlShapes(controlShapes)

	mc.delete("template")
	mc.select(cl=True)
	mc.dgdirty(a=True)

def template(filepath=None, scale=1):

	if not filepath: filepath = THIS_DIR+"/"+THIS_FILE.split(".")[0]+".ma"
	if not os.path.isfile(filepath): filepath = THIS_DIR+"/"+filepath
	common.loadTemplate(filepath=filepath, scale=scale)
