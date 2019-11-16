import maya.cmds as mc

def main(name=None, subdivisions=1, scale=1, parent=None):

	if name: name += "_terrain"
	else: name = "terrain"
	t = mc.polyPlane(w=scale, h=scale, sx=subdivisions, sy=subdivisions, ch=False, n=name)[0]
	mc.setAttr(t+".template", True)
	if parent: t = mc.parent(t, parent)[0]

	return t
