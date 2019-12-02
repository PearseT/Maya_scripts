import sys, os
import maya.cmds as mc
import maya.mel as mm
THIS_DIR, THIS_FILE = os.path.split(__file__); sys.path.append(THIS_DIR)
import root; reload(root)
import common; reload(common)

def main(templateFile=None, inheritTemplateRotations=False,
		controlShapes=None, fbx=False, scale=1, radius=1):

	template(filepath=templateFile, scale=scale)

	root.main(name="assembly", fbx=fbx, radius=radius, body=False, pelvis=False)
	mc.parent("cog_jnt", "cog_ctrl")
	mc.connectAttr("assembly.joints", "cog_jnt.v")
	common.selectable("assembly.editJoints", "cog_jnt")
	common.sets("root", "cog_jnt", None, None)
	mc.delete("template")

	if fbx:
		mc.createNode("joint", n="root_fbx", p="skeleton_fbx")
		mc.setAttr("root_fbx.radius", radius*0.25)
		c = mc.pointConstraint("cog_ctrl", "root_fbx", sk=["y"])[0]
		mc.parent(c, "constraints_fbx")
		c = mc.orientConstraint("cog_ctrl", "root_fbx", sk=["x","z"])[0]
		mc.parent(c, "constraints_fbx")
		c = mc.scaleConstraint("cog_ctrl", "root_fbx")[0]
		mc.parent(c, "constraints_fbx")
		mc.createNode("joint", n="cog_fbx", p="root_fbx")
		mc.setAttr("cog_fbx.radius", radius*0.25)
		c = mc.parentConstraint("cog_jnt", "cog_fbx")[0]
		mc.parent(c, "constraints_fbx")
		c = mc.scaleConstraint("cog_jnt", "cog_fbx")[0]
		mc.parent(c, "constraints_fbx")

	if controlShapes:
		if os.path.isfile(THIS_DIR+"/"+controlShapes):
			common.loadControlShapes(THIS_DIR+"/"+controlShapes)
		elif os.path.isfile(controlShapes):
			common.loadControlShapes(controlShapes)

	mc.select(cl=True)
	mc.dgdirty(a=True)

def template(filepath=None, scale=1):

	if not filepath: filepath = THIS_DIR+"/"+THIS_FILE.split(".")[0]+".ma"
	if not os.path.isfile(filepath): filepath = THIS_DIR+"/"+filepath
	common.loadTemplate(filepath=filepath, scale=scale)
