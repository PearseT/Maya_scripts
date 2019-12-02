import sys, os
import maya.cmds as mc
import maya.mel as mm
THIS_DIR, THIS_FILE = os.path.split(__file__); sys.path.append(THIS_DIR)
import root; reload(root)
import common; reload(common)

def main(wheels=None, parent=None, radius=1):

	if wheels == None: wheels = mc.ls(sl=True, o=True) or []
	if len(wheels) < 2: return

	grp = mc.createNode("transform", n="chassis", ss=True)

	bb = mc.exactWorldBoundingBox(wheels)
	tx = (bb[3]+bb[0])*0.5
	ty = (bb[4]+bb[1])*0.5
	tz = (bb[5]+bb[2])*0.5
	sx = (bb[3]-bb[0])*2*radius
	sz = (bb[5]-bb[2])*2*radius
	grp2, ctrl = common.control(name="chassis", position=[tx,ty,tz],
								radius=[sx,sz], shape="square",
								parent=grp, lockAttr="v", hideAttr="v")
	mc.addAttr(ctrl, ln="joints", at="bool", dv=True, k=True)
	mc.addAttr(ctrl, ln="editJoints", at="bool", k=True)
	mc.addAttr(ctrl, ln="controls", at="bool", dv=True, k=True)
	mc.addAttr(ctrl, ln="placers", at="bool", k=True)
	mc.addAttr(ctrl, ln="wheels", at="bool", dv=True, k=True)
	mc.addAttr(ctrl, ln="terrain", at="bool", dv=True, k=True)
	mc.addAttr(ctrl, ln="editTerrain", at="bool", k=True)
	mc.addAttr(ctrl, ln="terrainDetection", at="bool", dv=True, k=True)

	jnt = mc.createNode("joint", n="chassis_jnt", p=ctrl, ss=True)
	mc.setAttr(jnt+".radius", radius*0.5)
	mc.connectAttr(ctrl+".joints", jnt+".v")
	common.selectable(ctrl+".editJoints", jnt)
	common.sets("chassis", jnt, None, None)

	fr_wheels = []
	bk_wheels = []
	lf_wheels = []
	rt_wheels = []
	for n in wheels:
		name = n.replace("_grp", "")
		mc.connectAttr(ctrl+".joints", name+"_ctrl.joints")
		mc.setAttr(name+"_ctrl.joints", k=False)
		mc.connectAttr(ctrl+".editJoints", name+"_ctrl.editJoints")
		mc.setAttr(name+"_ctrl.editJoints", k=False)
		mc.connectAttr(ctrl+".controls", name+"_ctrl.v")
		mc.setAttr(name+"_ctrl.v", k=False)
		mc.connectAttr(ctrl+".controls", name+"_placer_ctrlShape.overrideVisibility")
		mc.connectAttr(ctrl+".placers", name+"_ctrl.placer")
		mc.setAttr(name+"_ctrl.placer", k=False)
		mc.connectAttr(ctrl+".wheels", name+"_ctrl.wheel")
		mc.setAttr(name+"_ctrl.wheel", k=False)
		mc.connectAttr(ctrl+".terrain", name+"_ctrl.terrain")
		mc.setAttr(name+"_ctrl.terrain", k=False)
		mc.connectAttr(ctrl+".editTerrain", name+"_ctrl.editTerrain")
		mc.setAttr(name+"_ctrl.editTerrain", k=False)
		mc.connectAttr(ctrl+".terrainDetection", name+"_ctrl.terrainDetection")
		mc.setAttr(name+"_ctrl.terrainDetection", k=False)
		p = mc.xform(n, q=True, ws=True, rp=True)
		if p[0] >= 0: lf_wheels.append(n)
		else: rt_wheels.append(n)
		if p[2] >= 0: fr_wheels.append(n)
		else: bk_wheels.append(n)

	bb = mc.exactWorldBoundingBox(fr_wheels)
	tx = (bb[3]+bb[0])*0.5
	ty = bb[4]*1.25
	tz = (bb[5]+bb[2])*0.5
	r = (bb[3]+bb[0])*0.25
	if r < (bb[4]+bb[1])*0.25: r = (bb[4]+bb[1])*0.25
	if r < (bb[5]+bb[2])*0.25: r = (bb[5]+bb[2])*0.25
	grp3, ctrl2 = common.control(name="steering", position=[tx,ty,tz], radius=radius*r,
								parent=grp, lockAttr=["tx","ty","tz","rx","rz","sx","sy","sz"],
								hideAttr=["tx","ty","tz","rx","rz","sx","sy","sz","v"])
	mc.connectAttr(ctrl+".controls", ctrl2+".v")
	mc.transformLimits(ctrl2, ry=(-55,55), ery=(1,1))

	fr_pos_grp = mc.createNode("transform", p=grp, n=name+"_fr_pos_grp", ss=True)
	bk_pos_grp = mc.createNode("transform", p=grp, n=name+"_bk_pos_grp", ss=True)
	lf_pos_grp = mc.createNode("transform", p=grp, n=name+"_lf_pos_grp", ss=True)
	rt_pos_grp = mc.createNode("transform", p=grp, n=name+"_rt_pos_grp", ss=True)
	fr_lf_pos_grp = mc.createNode("transform", p=grp, n=name+"_fr_lf_aim_grp", ss=True)
	bk_lf_pos_grp = mc.createNode("transform", p=grp, n=name+"_bk_lf_aim_grp", ss=True)
	bk_rt_pos_grp = mc.createNode("transform", p=grp, n=name+"_bk_rt_aim_grp", ss=True)
	fr_rt_pos_grp = mc.createNode("transform", p=grp, n=name+"_fr_rt_aim_grp", ss=True)

	for n in wheels:
		wheel_ctrl = n.replace("_grp", "_ctrl")
		if n in fr_wheels:
			mc.connectAttr(ctrl2+".ry", wheel_ctrl+".ry")
			mc.setAttr(wheel_ctrl+".ry", k=False, l=True)
		else:
			mc.setAttr(wheel_ctrl+".tilt", 0)
		mc.pointConstraint(wheel_ctrl, grp2, skip=("x"))
		if n in lf_wheels: mc.pointConstraint(wheel_ctrl, lf_pos_grp)
		elif n in rt_wheels: mc.pointConstraint(wheel_ctrl, rt_pos_grp)
		if n in fr_wheels:
			mc.pointConstraint(wheel_ctrl, fr_pos_grp, skip=("x"))
		elif n in bk_wheels:
			mc.pointConstraint(wheel_ctrl, bk_pos_grp)
			mc.setAttr(wheel_ctrl+".ry", k=False, l=True)
		mc.connectAttr(grp2+".rz", wheel_ctrl+".rz")
		mc.setAttr(wheel_ctrl+".rz", k=False, l=True)

	mc.pointConstraint(fr_pos_grp, bk_pos_grp, lf_pos_grp, rt_pos_grp, fr_lf_pos_grp)
	mc.pointConstraint(fr_pos_grp, bk_pos_grp, lf_pos_grp, rt_pos_grp, bk_lf_pos_grp)
	mc.pointConstraint(fr_pos_grp, bk_pos_grp, lf_pos_grp, rt_pos_grp, bk_rt_pos_grp)
	mc.pointConstraint(fr_pos_grp, bk_pos_grp, lf_pos_grp, rt_pos_grp, fr_rt_pos_grp)
	mc.aimConstraint(fr_pos_grp, fr_lf_pos_grp, aim=[0,0,1], u=[1,0,0], wut="object", wuo=lf_pos_grp)
	mc.aimConstraint(lf_pos_grp, bk_lf_pos_grp, aim=[1,0,0], u=[0,0,-1], wut="object", wuo=bk_pos_grp)
	mc.aimConstraint(bk_pos_grp, bk_rt_pos_grp, aim=[0,0,-1], u=[-1,0,0], wut="object", wuo=rt_pos_grp)
	mc.aimConstraint(rt_pos_grp, fr_rt_pos_grp, aim=[-1,0,0], u=[1,0,0], wut="object", wuo=fr_pos_grp)
	mc.orientConstraint(fr_lf_pos_grp, bk_lf_pos_grp, bk_rt_pos_grp, fr_rt_pos_grp, grp2, mo=True)

	common.sets("chassis", None, [ctrl, ctrl2], None)

	mc.select(grp)
	mc.dgdirty(a=True)

	return grp, ctrl
