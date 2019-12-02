import sys, os
import maya.cmds as mc
import maya.mel as mm
THIS_DIR, THIS_FILE = os.path.split(__file__); sys.path.append(THIS_DIR)
import root, spine, head, leg, arm, hand, twist, common
reload(root); reload(spine); reload(head); reload(leg);
reload(arm); reload(hand); reload(twist); reload(common)

def main(templateFile=None, inheritTemplateRotations=False, controlShapes=None,
		oglControlShapes=None, fbx=False, scale=1, radius=1, numTwistJoints=4,
		ikShape="cube"):

	template(filepath=templateFile, scale=scale)

	root.main(name="assembly", position="spine1", fbx=fbx, radius=radius)

	#
	# spine and head
	#

	spine.main(positions=["spine1","spine2","spine3","spine4","spine5","spine6"],
		radius=radius)

	mc.parent("spine", "pelvis_ctrl")
	mc.parentConstraint("body_ctrl", "spine_ik2_ctrl_grp", mo=True)
	mc.setAttr("spine_ik1_ctrlShape.lodVisibility", False)
	mc.connectAttr("assembly.joints", "spine_ik1_ctrl.joints")
	mc.setAttr("spine_ik1_ctrl.joints", k=False)
	mc.connectAttr("assembly.editJoints", "spine_ik1_ctrl.editJoints")
	mc.setAttr("spine_ik1_ctrl.editJoints", k=False)

	head.main(control="spine_ik6_ctrl", parent="spine_jnt6",
		positions=["jaw","eye_lf","eye_rt"], radius=radius, ikShape=ikShape)

	mc.connectAttr("assembly.joints", "spine_ik6_ctrl.joints")
	mc.setAttr("spine_ik6_ctrl.joints", k=False)
	mc.connectAttr("assembly.editJoints", "spine_ik6_ctrl.editJoints")
	mc.setAttr("spine_ik6_ctrl.editJoints", k=False)

	#
	# legs
	#

	leg.main(name="leg_lf", positions=["leg_lf1","leg_lf2","leg_lf3",
		"leg_lf4","leg_lf5","leg_lf6"], radius=radius, ikShape=ikShape,
		inheritTemplateRotations=inheritTemplateRotations)

	mc.parent("leg_lf", "cog_ctrl")
	mc.parentConstraint("pelvis_ctrl", "leg_lf_ik1_grp", mo=True)
	mc.connectAttr("assembly.joints", "leg_lf_ik1_ctrl.joints")
	mc.setAttr("leg_lf_ik1_ctrl.joints", k=False)
	mc.connectAttr("assembly.editJoints", "leg_lf_ik1_ctrl.editJoints")
	mc.setAttr("leg_lf_ik1_ctrl.editJoints", k=False)
	mc.setAttr("leg_lf_ik1_ctrl.fkControls", False)

	leg.main(name="leg_rt", positions=["leg_rt1","leg_rt2","leg_rt3",
		"leg_rt4","leg_rt5","leg_rt6"], radius=radius, ikShape=ikShape,
		inheritTemplateRotations=inheritTemplateRotations)

	mc.parent("leg_rt", "cog_ctrl")
	mc.parentConstraint("pelvis_ctrl", "leg_rt_ik1_grp", mo=True)
	mc.connectAttr("assembly.joints", "leg_rt_ik1_ctrl.joints")
	mc.setAttr("leg_rt_ik1_ctrl.joints", k=False)
	mc.connectAttr("assembly.editJoints", "leg_rt_ik1_ctrl.editJoints")
	mc.setAttr("leg_rt_ik1_ctrl.editJoints", k=False)
	mc.setAttr("leg_rt_ik1_ctrl.fkControls", False)

	#
	# arms
	#

	arm.main(name="arm_lf", positions=["arm_lf1","arm_lf2","arm_lf3","arm_lf4"],
		radius=radius, ikShape=ikShape, inheritTemplateRotations=inheritTemplateRotations)

	mc.parent("arm_lf", "body_ctrl")
	mc.parentConstraint("spine_jnt3", "arm_lf", mo=True)
	mc.connectAttr("assembly.joints", "arm_lf_ik2_ctrl.joints")
	mc.setAttr("arm_lf_ik2_ctrl.joints", k=False)
	mc.connectAttr("assembly.editJoints", "arm_lf_ik2_ctrl.editJoints")
	mc.setAttr("arm_lf_ik2_ctrl.editJoints", k=False)
	mc.setAttr("arm_lf_ik2_ctrl.fkControls", False)

	arm.main(name="arm_rt", positions=["arm_rt1","arm_rt2","arm_rt3","arm_rt4"],
		radius=radius, ikShape=ikShape, inheritTemplateRotations=inheritTemplateRotations)

	mc.parent("arm_rt", "body_ctrl")
	mc.parentConstraint("spine_jnt3", "arm_rt", mo=True)
	mc.connectAttr("assembly.joints", "arm_rt_ik2_ctrl.joints")
	mc.setAttr("arm_rt_ik2_ctrl.joints", k=False)
	mc.connectAttr("assembly.editJoints", "arm_rt_ik2_ctrl.editJoints")
	mc.setAttr("arm_rt_ik2_ctrl.editJoints", k=False)
	mc.setAttr("arm_rt_ik2_ctrl.fkControls", False)

	#
	# hands and fingers
	#

	positions = []
	l = mc.ls("finger_lf*_1", typ="joint") or []
	for n in l:
		l2 = mc.listRelatives(n, pa=True, ad=True) or []
		positions.append(sorted([n]+l2))

	hand.main(name="hand", side="lf", control="arm_lf_ik2_ctrl",
		parent="arm_lf_fk4_ctrl", radius=radius, positions=positions,
		inheritTemplateRotations=inheritTemplateRotations)
	mc.setAttr("arm_lf_ik2_ctrl.fingerControls", False)

	positions = []
	l = mc.ls("finger_rt*_1", typ="joint") or []
	for n in l:
		l2 = mc.listRelatives(n, pa=True, ad=True) or []
		positions.append(sorted([n]+l2))

	hand.main(name="hand", side="rt", control="arm_rt_ik2_ctrl",
		parent="arm_rt_fk4_ctrl", radius=radius, positions=positions,
		inheritTemplateRotations=inheritTemplateRotations)
	mc.setAttr("arm_rt_ik2_ctrl.fingerControls", False)

	#
	# delete template
	#

	mc.delete("template")

	#
	# twist joints
	#

	if numTwistJoints:
		twist.main(name="leg_lf_up", control="leg_lf_ik1_ctrl", parent="leg_lf_ik1_grp",
			count=numTwistJoints, stable="leg_lf_fk1_ctrl", _twist="leg_lf_fk2_ctrl",
			scale="leg_lf_ik1", wu=(1,0,0), wuo="leg_lf")
		mc.delete("leg_lf_jnt1")
		twist.main(name="leg_rt_up", control="leg_rt_ik1_ctrl", parent="leg_rt_ik1_grp",
			count=numTwistJoints, stable="leg_rt_fk1_ctrl", _twist="leg_rt_fk2_ctrl",
			scale="leg_rt_ik1", wu=(1,0,0), wuo="leg_rt")
		mc.delete("leg_rt_jnt1")
		twist.main(name="leg_lf_lo", control="leg_lf_ik1_ctrl", parent="leg_lf_fk2_ctrl",
			count=numTwistJoints, stable="leg_lf_fk2_ctrl", _twist="leg_lf_fk3_ctrl",
			scale="leg_lf_ik1")
		mc.delete("leg_lf_jnt2")
		twist.main(name="leg_rt_lo", control="leg_rt_ik1_ctrl", parent="leg_rt_fk2_ctrl",
			count=numTwistJoints, stable="leg_rt_fk2_ctrl", _twist="leg_rt_fk3_ctrl",
			scale="leg_rt_ik1")
		mc.delete("leg_rt_jnt2")

		twist.main(name="arm_lf_up", control="arm_lf_ik2_ctrl", parent="arm_lf_fk1_ctrl",
			count=numTwistJoints, stable="arm_lf_fk2_ctrl", _twist="arm_lf_fk3_ctrl",
			scale="arm_lf_ik2")
		mc.delete("arm_lf_jnt2")
		twist.main(name="arm_rt_up", control="arm_rt_ik2_ctrl", parent="arm_rt_fk1_ctrl",
			count=numTwistJoints, stable="arm_rt_fk2_ctrl", _twist="arm_rt_fk3_ctrl",
			scale="arm_rt_ik2", aim=(-1,0,0))
		mc.delete("arm_rt_jnt2")
		twist.main(name="arm_lf_lo", control="arm_lf_ik2_ctrl", parent="arm_lf_fk3_ctrl",
			count=numTwistJoints, stable="arm_lf_fk3_ctrl", _twist="arm_lf_fk4_ctrl",
			scale="arm_lf_ik2")
		mc.delete("arm_lf_jnt3")
		twist.main(name="arm_rt_lo", control="arm_rt_ik2_ctrl", parent="arm_rt_fk3_ctrl",
			count=numTwistJoints, stable="arm_rt_fk3_ctrl", _twist="arm_rt_fk4_ctrl",
			scale="arm_rt_ik2", aim=(-1,0,0))
		mc.delete("arm_rt_jnt3")

	#
	# transformation spaces for some controls
	#

	common.space("leg_lf_ik1_ctrl", "leg_lf_ik1_ctrl_grp", constraint="parent", name="local")
	common.space("leg_lf_ik1_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("leg_lf_ik1_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("leg_lf_ik1_ctrl", "world_ctrl", constraint="parent", name="world")

	common.space("leg_rt_ik1_ctrl", "leg_rt_ik1_ctrl_grp", constraint="parent", name="local")
	common.space("leg_rt_ik1_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("leg_rt_ik1_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("leg_rt_ik1_ctrl", "world_ctrl", constraint="parent", name="world")

	common.space("leg_lf_pv_ctrl", "leg_lf_pv_ctrl_grp", constraint="parent", name="local")
	common.space("leg_lf_pv_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("leg_lf_pv_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("leg_lf_pv_ctrl", "world_ctrl", constraint="parent", name="world")

	common.space("leg_rt_pv_ctrl", "leg_rt_pv_ctrl_grp", constraint="parent", name="local")
	common.space("leg_rt_pv_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("leg_rt_pv_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("leg_rt_pv_ctrl", "world_ctrl", constraint="parent", name="world")

	common.space("spine_ik3_ctrl", "spine_ik3_ctrl_grp", constraint="parent", name="local")
	common.space("spine_ik3_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("spine_ik3_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("spine_ik3_ctrl", "world_ctrl", constraint="parent", name="world")

	common.space("arm_lf_pv_ctrl", "arm_lf_pv_ctrl_grp", constraint="parent", name="local")
	common.space("arm_lf_pv_ctrl", "spine_jnt3", constraint="parent", name="chest")
	common.space("arm_lf_pv_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("arm_lf_pv_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("arm_lf_pv_ctrl", "world_ctrl", constraint="parent", name="world")
	mc.setAttr("arm_lf_pv_ctrl.space", 3)

	common.space("arm_rt_pv_ctrl", "arm_rt_pv_ctrl_grp", constraint="parent", name="local")
	common.space("arm_rt_pv_ctrl", "spine_jnt3", constraint="parent", name="chest")
	common.space("arm_rt_pv_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("arm_rt_pv_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("arm_rt_pv_ctrl", "world_ctrl", constraint="parent", name="world")
	mc.setAttr("arm_rt_pv_ctrl.space", 3)

	common.space("arm_lf_ik2_ctrl", "arm_lf_ik2_ctrl_grp", constraint="parent", name="local")
	common.space("arm_lf_ik2_ctrl", "spine_jnt6", constraint="parent", name="head")
	common.space("arm_lf_ik2_ctrl", "spine_jnt3", constraint="parent", name="chest")
	common.space("arm_lf_ik2_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("arm_lf_ik2_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("arm_lf_ik2_ctrl", "world_ctrl", constraint="parent", name="world")
	mc.setAttr("arm_lf_ik2_ctrl.space", 4)

	common.space("arm_rt_ik2_ctrl", "arm_rt_ik2_ctrl_grp", constraint="parent", name="local")
	common.space("arm_rt_ik2_ctrl", "spine_jnt6", constraint="parent", name="head")
	common.space("arm_rt_ik2_ctrl", "spine_jnt3", constraint="parent", name="chest")
	common.space("arm_rt_ik2_ctrl", "body_ctrl", constraint="parent", name="body")
	common.space("arm_rt_ik2_ctrl", "cog_ctrl", constraint="parent", name="cog")
	common.space("arm_rt_ik2_ctrl", "world_ctrl", constraint="parent", name="world")
	mc.setAttr("arm_rt_ik2_ctrl.space", 4)

	common.space("spine_ik6_ctrl", "spine_ik6_ctrl_grp", constraint="orient", name="local")
	common.space("spine_ik6_ctrl", "spine_jnt3", constraint="orient", name="chest")
	common.space("spine_ik6_ctrl", "body_ctrl", constraint="orient", name="body")
	common.space("spine_ik6_ctrl", "cog_ctrl", constraint="orient", name="cog")
	common.space("spine_ik6_ctrl", "world_ctrl", constraint="orient", name="world")
	mc.setAttr("spine_ik6_ctrl.space", 3)

	common.space("head_eyes_ik_ctrl", "spine_ik6_ctrl", constraint="parent", name="local")
	common.space("head_eyes_ik_ctrl", "world_ctrl", constraint="parent", name="world")
	mc.setAttr("head_eyes_ik_ctrl.space", 1)

	#
	# global switch for control visibility
	#

	for n in ["fk_controls_set", "ik_controls_set"]:
		for n2 in mc.sets(n, q=True):
			if mc.nodeType(n2) == "objectSet": l = mc.sets(n2, q=True)
			else: l = [n2]
			for n3 in l:
				n3 = mc.listRelatives(n3, pa=True, s=True)[0]
				mc.setAttr(n3+".overrideEnabled", True)
				try: mc.connectAttr("assembly.controls", n3+".overrideVisibility")
				except: pass

	#
	# fbx skeleton
	#

	if fbx:
		mc.createNode("joint", n="root_fbx", p="skeleton_fbx")
		mc.setAttr("root_fbx.radius", radius*0.25)
		c = mc.pointConstraint("pelvis_ctrl", "root_fbx", sk=["y"])[0]
		mc.parent(c, "constraints_fbx")
		c = mc.orientConstraint("pelvis_ctrl", "root_fbx", sk=["x","z"])[0]
		mc.parent(c, "constraints_fbx")
		c = mc.scaleConstraint("pelvis_ctrl", "root_fbx")[0]
		mc.parent(c, "constraints_fbx")

		l = [None, "pelvis_ctrl","spine_jnt1","spine_jnt2","spine_jnt3","spine_jnt4","spine_jnt5","spine_jnt6","jaw_jnt"]
		l2 = ["root_fbx","pelvis_fbx","spine_fbx1","spine_fbx2","spine_fbx3","spine_fbx4","spine_fbx5","spine_fbx6","jaw_fbx"]
		for i in range(1,len(l)):
			mc.createNode("joint", n=l2[i], p=l2[i-1])
			mc.setAttr(l2[i]+".radius", radius*0.25)
			mc.delete(mc.parentConstraint(l[i], l2[i]))
			r = mc.getAttr(l2[i]+".r")[0]
			mc.setAttr(l2[i]+".jo", r[0], r[1], r[2])
			mc.setAttr(l2[i]+".r", 0,0,0)
			c = mc.pointConstraint(l[i], l2[i], mo=True)[0]
			mc.parent(c, "constraints_fbx")
			c = mc.orientConstraint(l[i], l2[i], mo=True)[0]
			r = mc.getAttr(l2[i]+".r")[0]
			mc.setAttr(c+".o", -r[0], -r[1], -r[2])
			mc.parent(c, "constraints_fbx")

		for side in ["lf","rt"]:
			mc.createNode("joint", n="eye_"+side+"_fbx", p="spine_fbx6")
			mc.setAttr("eye_"+side+"_fbx"+".radius", radius*0.25)
			mc.delete(mc.parentConstraint("eye_"+side+"_jnt", "eye_"+side+"_fbx"))
			r = mc.getAttr("eye_"+side+"_fbx.r")[0]
			mc.setAttr("eye_"+side+"_fbx.jo", r[0], r[1], r[2])
			mc.setAttr("eye_"+side+"_fbx.r", 0,0,0)
			c = mc.parentConstraint("eye_"+side+"_jnt", "eye_"+side+"_fbx", mo=True)[0]
			mc.parent(c, "constraints_fbx")
			mc.duplicate("eye_"+side+"_fbx")
			mc.parent("eye_"+side+"_fbx1", "eye_"+side+"_fbx")
			mc.duplicate("eye_"+side+"_fbx1")
			mc.parent("eye_"+side+"_fbx2", "eye_"+side+"_fbx1")
		
			if numTwistJoints:
				l = ["leg_"+side+"_up_twr1","leg_"+side+"_up_tw1","leg_"+side+"_up_tw2","leg_"+side+"_up_tw3","leg_"+side+"_lo_twr1","leg_"+side+"_lo_tw1","leg_"+side+"_lo_tw2","leg_"+side+"_lo_tw3","leg_"+side+"_jnt3","leg_"+side+"_jnt4"]
				l2 = ["leg_"+side+"_tw_fbx1","leg_"+side+"_tw_fbx2","leg_"+side+"_tw_fbx3","leg_"+side+"_tw_fbx4","leg_"+side+"_tw_fbx5","leg_"+side+"_tw_fbx6","leg_"+side+"_tw_fbx7","leg_"+side+"_tw_fbx8","leg_"+side+"_fbx1","leg_"+side+"_fbx4"]
				last_good = "pelvis_fbx"
				for i in range(0,len(l)):
					if not mc.objExists(l[i]): continue
					mc.createNode("joint", n=l2[i], p=last_good)
					last_good = l2[i]
					mc.setAttr(l2[i]+".radius", radius*0.25)
					mc.delete(mc.parentConstraint(l[i], l2[i]))
					r = mc.getAttr(l2[i]+".r")[0]
					mc.setAttr(l2[i]+".jo", r[0], r[1], r[2])
					mc.setAttr(l2[i]+".r", 0,0,0)
					c = mc.parentConstraint(l[i], l2[i], mo=True)[0]
					mc.parent(c, "constraints_fbx")

				l = ["arm_"+side+"_jnt1","arm_"+side+"_up_twr1","arm_"+side+"_up_tw1","arm_"+side+"_up_tw2","arm_"+side+"_up_tw3","arm_"+side+"_lo_twr1","arm_"+side+"_lo_tw1","arm_"+side+"_lo_tw2","arm_"+side+"_lo_tw3","arm_"+side+"_jnt4"]
				l2 = ["arm_"+side+"_fbx1","arm_"+side+"_tw_fbx1","arm_"+side+"_tw_fbx2","arm_"+side+"_tw_fbx3","arm_"+side+"_tw_fbx4","arm_"+side+"_tw_fbx5","arm_"+side+"_tw_fbx6","arm_"+side+"_tw_fbx7","arm_"+side+"_tw_fbx8","arm_"+side+"_fbx4"]
				last_good = "spine_fbx3"
				for i in range(0,len(l)):
					if not mc.objExists(l[i]): continue
					mc.createNode("joint", n=l2[i], p=last_good)
					last_good = l2[i]
					mc.setAttr(l2[i]+".radius", radius*0.25)
					mc.delete(mc.parentConstraint(l[i], l2[i]))
					r = mc.getAttr(l2[i]+".r")[0]
					mc.setAttr(l2[i]+".jo", r[0], r[1], r[2])
					mc.setAttr(l2[i]+".r", 0,0,0)
					c = mc.parentConstraint(l[i], l2[i], mo=True)[0]
					mc.parent(c, "constraints_fbx")
			else:
				l = ["leg_"+side+"_jnt1","leg_"+side+"_jnt2","leg_"+side+"_jnt3","leg_"+side+"_jnt4"]
				l2 = ["leg_"+side+"_fbx1","leg_"+side+"_fbx2","leg_"+side+"_fbx3","leg_"+side+"_fbx4"]
				last_good = "pelvis_fbx"
				for i in range(0,len(l)):
					if not mc.objExists(l[i]): continue
					mc.createNode("joint", n=l2[i], p=last_good)
					last_good = l2[i]
					mc.setAttr(l2[i]+".radius", radius*0.25)
					mc.delete(mc.parentConstraint(l[i], l2[i]))
					r = mc.getAttr(l2[i]+".r")[0]
					mc.setAttr(l2[i]+".jo", r[0], r[1], r[2])
					mc.setAttr(l2[i]+".r", 0,0,0)
					c = mc.parentConstraint(l[i], l2[i], mo=True)[0]
					mc.parent(c, "constraints_fbx")

				l = ["arm_"+side+"_jnt1","arm_"+side+"_jnt2","arm_"+side+"_jnt3","arm_"+side+"_jnt4"]
				l2 = ["arm_"+side+"_fbx1","arm_"+side+"_fbx2","arm_"+side+"_fbx3","arm_"+side+"_fbx4"]
				last_good = "spine_fbx3"
				for i in range(0,len(l)):
					if not mc.objExists(l[i]): continue
					mc.createNode("joint", n=l2[i], p=last_good)
					last_good = l2[i]
					mc.setAttr(l2[i]+".radius", radius*0.25)
					mc.delete(mc.parentConstraint(l[i], l2[i]))
					r = mc.getAttr(l2[i]+".r")[0]
					mc.setAttr(l2[i]+".jo", r[0], r[1], r[2])
					mc.setAttr(l2[i]+".r", 0,0,0)
					c = mc.parentConstraint(l[i], l2[i], mo=True)[0]
					mc.parent(c, "constraints_fbx")

			for i in range(1,6):
				l = [None] + mc.ls("finger_"+side+str(i)+"_jnt*", typ="joint") or []
				l2 = ["arm_"+side+"_fbx4"] + ["finger_"+side+str(i)+"_fbx"+str(j+1) for j in range(len(l)-1)]
				for j in range(1,len(l)):
					mc.createNode("joint", n=l2[j], p=l2[j-1])
					mc.setAttr(l2[j]+".radius", radius*0.25)
					mc.delete(mc.parentConstraint(l[j], l2[j]))
					r = mc.getAttr(l2[j]+".r")[0]
					mc.setAttr(l2[j]+".jo", r[0], r[1], r[2])
					mc.setAttr(l2[j]+".r", 0,0,0)
					c = mc.parentConstraint(l[j], l2[j], mo=True)[0]
					mc.parent(c, "constraints_fbx")

			mc.createNode("joint", n="props_"+side+"_fbx", p="arm_"+side+"_fbx4")
			mc.setAttr("props_"+side+"_fbx.radius", radius*0.25)
			if side == "lf": mc.setAttr("props_"+side+"_fbx.ty", scale)
			else: mc.setAttr("props_"+side+"_fbx.ty", -scale)

			common.control(name="props_"+side, parent="arm_"+side+"_fk4_ctrl", \
				position="props_"+side+"_fbx", rotation="props_"+side+"_fbx", \
				normal=(0,1,0), color=13, radius=radius*0.5, hideAttr=["v"])
			mc.addAttr("arm_"+side+"_ik2_ctrl", ln="propsControls", at="bool", k=True)
			mc.connectAttr("arm_"+side+"_ik2_ctrl.propsControls", "props_"+side+"_ctrl.v")
			mc.delete(mc.parentConstraint("props_"+side+"_ctrl", "props_"+side+"_fbx"))
			r = mc.getAttr("props_"+side+"_fbx.r")[0]
			mc.setAttr("props_"+side+"_fbx.jo", r[0], r[1], r[2])
			mc.setAttr("props_"+side+"_fbx.r", 0,0,0)
			c = mc.parentConstraint("props_"+side+"_ctrl", "props_"+side+"_fbx", mo=True)[0]
			c = mc.rename(c, "props_"+side+"_fbx_parcon")
			mc.parent(c, "constraints_fbx")

	#
	# rename controls for nice
	#

	mc.rename("leg_lf_ik1_ctrl", "leg_lf_ik_ctrl")
	mc.rename("leg_lf_fk1_ctrl", "leg_up_lf_fk_ctrl")
	mc.rename("leg_lf_fk2_ctrl", "leg_lo_lf_fk_ctrl")
	mc.rename("leg_lf_fk3_ctrl", "ankle_lf_fk_ctrl")
	mc.rename("leg_lf_fk4_ctrl", "toes_lf_fk_ctrl")

	mc.rename("leg_rt_ik1_ctrl", "leg_rt_ik_ctrl")
	mc.rename("leg_rt_fk1_ctrl", "leg_up_rt_fk_ctrl")
	mc.rename("leg_rt_fk2_ctrl", "leg_lo_rt_fk_ctrl")
	mc.rename("leg_rt_fk3_ctrl", "ankle_rt_fk_ctrl")
	mc.rename("leg_rt_fk4_ctrl", "toes_rt_fk_ctrl")

	mc.rename("spine_ik2_ctrl", "waist_ctrl")
	mc.rename("spine_ik3_ctrl", "chest_ctrl")
	mc.rename("spine_ik5_ctrl", "neck_ctrl")
	mc.rename("spine_ik6_ctrl", "head_ctrl")

	mc.rename("arm_lf_ik1_ctrl", "shoulder_lf_ik_ctrl")
	mc.rename("arm_lf_ik2_ctrl", "arm_lf_ik_ctrl")
	mc.rename("arm_lf_fk1_ctrl", "shoulder_lf_fk_ctrl")
	mc.rename("arm_lf_fk2_ctrl", "arm_up_lf_fk_ctrl")
	mc.rename("arm_lf_fk3_ctrl", "arm_lo_lf_fk_ctrl")
	mc.rename("arm_lf_fk4_ctrl", "wrist_lf_fk_ctrl")

	mc.rename("arm_rt_ik1_ctrl", "shoulder_rt_ik_ctrl")
	mc.rename("arm_rt_ik2_ctrl", "arm_rt_ik_ctrl")
	mc.rename("arm_rt_fk1_ctrl", "shoulder_rt_fk_ctrl")
	mc.rename("arm_rt_fk2_ctrl", "arm_up_rt_fk_ctrl")
	mc.rename("arm_rt_fk3_ctrl", "arm_lo_rt_fk_ctrl")
	mc.rename("arm_rt_fk4_ctrl", "wrist_rt_fk_ctrl")

	#
	# load control shapes
	#

	if controlShapes:
		if os.path.isfile(THIS_DIR+"/"+controlShapes):
			common.loadControlShapes(THIS_DIR+"/"+controlShapes)
		elif os.path.isfile(controlShapes):
			common.loadControlShapes(controlShapes)

	#
	# load OpenGL shapes
	#

	if oglControlShapes:
		f = None
		if os.path.isfile(THIS_DIR+"/"+oglControlShapes):
			f = THIS_DIR+"/"+oglControlShapes
		elif os.path.isfile(oglControlShapes):
			f = oglControlShapes
		if f:
			# delete wire control shapes
			l = []
			for t in ["fk","ik"]:
				for n in mc.sets(t+"_controls_set", q=True):
					if mc.nodeType(n) != "objectSet": l.append(n)
					else: l += mc.sets(n, q=True)
			for n in l: mc.delete(mc.listRelatives(n, pa=True, s=True))

			# create OpenGL control shapes
			f2 = open(f)
			s = f2.read()
			f2.close()
			mm.eval(s)

			# connect OpenGL shape visibility attributes to rig parameters
			f = mc.internalVar(userScriptDir=True)+"/icons.cfg"
			for n in l:
				try: n2 = mc.listRelatives(n, pa=True, s=True)[0]
				except:continue
				mc.setAttr(n2+".overrideEnabled", True)
				mc.connectAttr("assembly.controls", n2+".overrideVisibility")
				mc.setAttr(n+".iconsConfigFile", f, typ="string")
				mc.setAttr(n+".reloadIconsData", True)
			for side in ["lf","rt"]:
				for n in ["shoulder_"+side+"_fk_ctrl","arm_up_"+side+"_fk_ctrl","arm_lo_"+side+"_fk_ctrl","wrist_"+side+"_fk_ctrl"]:
					mc.connectAttr("arm_"+side+"_ik_ctrl.fkControls", n+"Shape.v")
				for n in ["shoulder_"+side+"_ik_ctrl","arm_"+side+"_pv_ctrl","lines_arm_"+side]:
					mc.connectAttr("arm_"+side+"_ik_ctrl.ikControls", n+"Shape.v")
				for i in ["1","2","3","4","5"]:
					for j in ["1","2","3"]:
						mc.connectAttr("arm_"+side+"_ik_ctrl.fingerControls", "finger_"+side+i+"_fk"+j+"_ctrlShape.v")
				for n in ["leg_up_"+side+"_fk_ctrl","leg_lo_"+side+"_fk_ctrl","ankle_"+side+"_fk_ctrl","toes_"+side+"_fk_ctrl"]:
					mc.connectAttr("leg_"+side+"_ik_ctrl.fkControls", n+"Shape.v")
				for n in ["leg_"+side+"_pv_ctrl","lines_leg_"+side]:
					mc.connectAttr("leg_"+side+"_ik_ctrl.ikControls", n+"Shape.v")
				for n in ["lines_arm_"+side,"lines_leg_"+side]:
					mc.connectAttr("assembly.controls", n+"Shape.overrideVisibility")
			for n in ["head_jaw_fk_ctrl","head_eye_rt_fk_ctrl","head_eye_lf_fk_ctrl"]:
				mc.connectAttr("head_ctrl.fkControls", n+"Shape.v")
			mc.connectAttr("head_ctrl.ikControls", "head_eyes_ik_ctrlShape.v")
			mc.connectAttr("head_ctrl.ikControls", "lines_eyesShape.v")
			mc.connectAttr("assembly.controls", "lines_eyesShape.overrideVisibility")
			mc.connectAttr("assembly.controls", "lines_spineShape.overrideVisibility")

			mc.parent("lines","lines_arm_lf","lines_arm_rt","lines_leg_lf","lines_leg_rt","lines_eyes","lines_spine", "assembly")
			mc.setAttr("assembly.joints", False)
			try: mc.setAttr("assembly.fbxJoints", False)
			except: pass

	mc.select(cl=True)
	mc.dgdirty(a=True)

def template(filepath=None, scale=1):

	if not filepath: filepath = THIS_DIR+"/"+THIS_FILE.split(".")[0]+".ma"
	if not os.path.isfile(filepath): filepath = THIS_DIR+"/"+filepath
	common.loadTemplate(filepath=filepath, scale=scale)
		
