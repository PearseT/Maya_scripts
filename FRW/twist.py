import sys, os
import maya.cmds as mc
sys.path.append(os.path.split(__file__)[0])
import common; reload(common)

def main(name="twist", control=None, parent=None, stable=None, _twist=None,
		scale=None, aim=(1,0,0), up=(0,1,0), wu=(0,0,0), wuo=None, count=4):

	if not control:
		control = common.control(name=name, color=13)[1]
		addControlToSets = True
	else:
		addControlToSets = False

	if not mc.objExists(control+".joints"):
		mc.addAttr(control, ln="joints", at="bool", dv=True, k=True)
	if not mc.objExists(control+".editJoints"):
		mc.addAttr(control, ln="editJoints", at="bool", k=True)

	if count < 1: count = 1
	elif count > 4: count = 4
	count += 1
		
	tw = [None]*count
	tw[0] = mc.duplicate(stable)[0]
	try: mc.delete(mc.listRelatives(tw[0], pa=True, c=True))
	except: pass
	l = mc.listConnections(tw[0]+".message", s=False, d=True, p=True) or []
	for na in l: mc.disconnectAttr(tw[0]+".message", na)
	for a in ["t","tx","ty","tz","r","rx","ry","rz","s","sx","sy","sz","v","radius","template"]:
		mc.setAttr(tw[0]+"."+a, l=False, k=True)
	mc.setAttr(tw[0]+".radius", mc.getAttr(tw[0]+".radius"))
	mc.setAttr(tw[0]+".drawStyle", 0)
	mc.setAttr(tw[0]+".template", False)
	tw[0] = mc.rename(tw[0], name+"_twr#")
	try: tw[0] = mc.parent(tw[0], parent)[0]
	except: pass
	tw[1] = mc.duplicate(tw[0])[0]
	mc.setAttr(tw[1]+".drawStyle", 2)
	for i in range(2,count): tw[i] = mc.duplicate(tw[0])[0]

	if not wuo: c = mc.aimConstraint(_twist, tw[0], aim=aim, u=up, wut="vector", wu=wu, mo=True)[0]
	else: c = mc.aimConstraint(_twist, tw[0], aim=aim, u=up, wut="objectrotation", wu=wu, wuo=wuo, mo=True)[0]
	mc.rename(c, tw[0]+"_aimcon")
	c = mc.aimConstraint(_twist, tw[1], aim=aim, u=up, wut="objectrotation", wu=(0,1,0), wuo=_twist, mo=True)[0]
	mc.rename(c, tw[0]+"_aimcon")

	if count == 5:
		wgt = [0.75,0.5,0.25]
	elif count == 4:
		wgt = [0.6666,0.3333]
	else: # count == 3
		wgt = [0.5]
	
	for i in range(2,count):
		tw[i] = mc.rename(tw[i], name+"_tw#")
		c = mc.pointConstraint(tw[0], _twist, tw[i])[0]
		mc.setAttr(c+"."+tw[0].split("|")[-1]+"W0", wgt[i-2])
		mc.setAttr(c+"."+_twist.split("|")[-1]+"W1", 1-wgt[i-2])
		mc.delete(c)
		c = mc.orientConstraint(tw[0], tw[1], tw[i])[0]
		mc.setAttr(c+"."+tw[0].split("|")[-1]+"W0", wgt[i-2])
		mc.setAttr(c+"."+tw[1].split("|")[-1]+"W1", 1-wgt[i-2])
		mc.setAttr(c+".interpType", 2)
		mc.rename(c, tw[i]+"_oricon")

	if count > 2: mc.parent(tw[2:],tw[1])
	mc.select(tw[0], tw[1])

	mc.connectAttr(scale+".s", tw[1]+".s")

	mc.connectAttr(control+".joints", tw[0]+".v")
	mc.connectAttr(control+".joints", tw[1]+".v")

	tw.pop(1)

	# selection sets
	if addControlToSets: common.sets(name, tw, [control], None)
	else: common.sets(name, tw, None, None)

	# selectable joints
	common.selectable(control+".editJoints", tw)

	mc.select(control)
	mc.dgdirty(a=True)

	return control
