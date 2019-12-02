import os, __main__
from functools import partial
import maya.cmds as mc

def main():

	sf = mc.scrollField(w=440)
	mc.paneLayout(cn="vertical2", st=1, shp=1)
	mc.button(l="save", c=partial(save, sf))
	mc.button(l="reload", c=partial(update, sf))
	mc.setParent("..")

	update(sf)

def update(*arg):

	s = ""
	filepath = __main__.FRW_DIR+"/manager.cfg"
	if os.path.isfile(filepath):
		f = open(filepath); s = f.read(); f.close()
	mc.scrollField(arg[0], e=True, tx=s)

def save(*arg):

	filepath = __main__.FRW_DIR+"/manager.cfg"
	if os.path.isfile(filepath):
		result = mc.confirmDialog(t="overwrite config",
			m="Do you want to overwrite the existing configuration ?",
			b=["yes","no"], cb="no", ds="no", db="no")
		if result == "no": return
	s = mc.scrollField(arg[0], q=True, tx=True)
	f = open(filepath, "w"); f.write(s); f.close()
	result = mc.confirmDialog(t="restart",
		m="You must restart the UI for the updates to take place.",
		b=["ok"], cb="ok", ds="ok", db="ok")
