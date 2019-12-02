# TODO:
# importDeformerWeights to perform auto-binding for some of the more common deformers like skinCluster, cluster, etc.
# quadruped

import sys, os, imp, inspect, shutil, glob, platform, __main__
from functools import partial
import maya.cmds as mc

THIS_DIR, THIS_FILE = os.path.split(__file__)
sys.path.append(THIS_DIR)
THIS_FILE_NAME = os.path.splitext(THIS_FILE)[0]

def __initialize():

	global STAGING_DIR, ASSET_TYPES, EDITOR, CACHE
	STAGING_DIR = ASSET_TYPES = EDITOR = None
	CACHE = {}
	LIB_CACHE = {}

def main(force=False):

	if force:
		if mc.dockControl("dc_FRW", ex=True) == True:
			mc.deleteUI("dc_FRW")
		if mc.window("w_FRW", ex=True):
			mc.deleteUI("w_FRW")

	if not mc.window("w_FRW", ex=True):
		a = mc.window("w_FRW", t="the Fastest Rig in the West")
		tl = mc.tabLayout()
		tab1 = mc.paneLayout(cn="horizontal3", st=1, shp=1, ps=[(1,1,1),(2,1,99),(3,1,1)])
		mc.columnLayout(adj=True)
		mc.rowLayout(nc=5, adj=4)
		mc.iconTextButton(st="iconOnly", i1="QR_add.png", ann="create new asset", c=__createAsset_ui)
		mc.iconTextButton(st="iconOnly", i1="QR_delete.png", ann="delete selected asset", c=__deleteAsset)
		mc.iconTextButton(st="iconOnly", i1="CN_refresh.png", ann="update assets list", c=__update)
		mc.text(l="")
		mc.iconTextButton(st="iconOnly", i1="UVEditorSnapshot.png", ann="update icon", c=__icon)
		mc.setParent("..")
		mc.rowLayout(nc=3, adj=2)
		mc.textScrollList("tsl_type_FRW", w=100, h=200, sc=__updateNames)
		mc.textScrollList("tsl_name_FRW", w=170, h=200, sc=__updateIconAndPath)
		mc.image("img_FRW", w=200, h=200)
		mc.setParent("..")
		mc.rowLayout(nc=2, adj=1)
		mc.textField("tf_path_FRW", ed=False)
		mc.iconTextButton(st="iconOnly", i1="passSetRelationEditor.png", ann="edit", c=__edit)
		mc.setParent("..")
		mc.setParent("..")
		mc.scrollLayout("sl_inspector_FRW", bv=True)
		mc.setParent("..")
		mc.button("b_execute_FRW", l="execute", c=__execute)
		mc.setParent("..")
		tab2 = mc.scrollLayout(bv=True)
		mc.columnLayout("cl_library_FRW", adj=True, rs=5)
		mc.setParent("..")
		mc.setParent("..")
		tab3 = mc.scrollLayout(bv=True)
		mc.columnLayout("cl_extensions_FRW", adj=True, rs=5)
		mc.setParent("..")
		mc.setParent("..")
		mc.tabLayout(tl, e=True, tl=[(tab1, "builder"), (tab2, "library"), (tab3, "extensions")])

	if not mc.dockControl("dc_FRW", ex=True):
		mc.dockControl("dc_FRW", l="the Fastest Rig in the West", con="w_FRW", aa=["left","right"], a="left", w=1)
		mc.dockControl("dc_FRW", e=True, fl=True)
	else:
		mc.dockControl("dc_FRW", e=True, vis=True)

	__initialize()
	__update()
	__library()
	__extensions()
	
def __update(*arg):

	__config()

	si = None
	if mc.textScrollList("tsl_type_FRW", q=True, nsi=True):
		si = mc.textScrollList("tsl_type_FRW", q=True, si=True)[0]

	mc.textScrollList("tsl_type_FRW", e=True, ra=True)
	if os.path.isdir(STAGING_DIR):
		for d in os.listdir(STAGING_DIR):
			mc.textScrollList("tsl_type_FRW", e=True, a=d)
			if d == si:
				mc.textScrollList("tsl_type_FRW", e=True, si=d)

	__updateNames()

def __config():

	if not os.path.isfile(THIS_DIR+"/"+THIS_FILE_NAME+".cfg"): return
	f = open(THIS_DIR+"/"+THIS_FILE_NAME+".cfg")
	l = f.readlines()
	f.close()
	for line in l:
		line = line.strip()
		if "=" not in line: continue
		line = line.split("=")
		if len(line) != 2: continue
		key = line[0].strip()
		if key == "STAGING_DIR":
			global STAGING_DIR
			STAGING_DIR = THIS_DIR+"/staging/"
			value = eval(line[1].strip())
			if type(value) == str or type(value) == unicode:
				if value[-1] != "/": value += "/"
				STAGING_DIR = value
		elif key == "ASSET_TYPES":
			global ASSET_TYPES
			ASSET_TYPES = eval(line[1].strip())
		elif key == "EDITOR":
			global EDITOR
			EDITOR = line[1].strip()

def __updateNames():

	si = None
	if mc.textScrollList("tsl_name_FRW", q=True, nsi=True):
		si = mc.textScrollList("tsl_name_FRW", q=True, si=True)[0]
	mc.textScrollList("tsl_name_FRW", e=True, ra=True)
	if mc.textScrollList("tsl_type_FRW", q=True, nsi=True):
		t = mc.textScrollList("tsl_type_FRW", q=True, si=True)[0]
		if os.path.isdir(STAGING_DIR):
			for d in os.listdir(STAGING_DIR+"/"+t):
				mc.textScrollList("tsl_name_FRW", e=True, a=d)
				if d == si:
					mc.textScrollList("tsl_name_FRW", e=True, si=d)

	__updateIconAndPath()

def __updateIconAndPath():

	mc.textField("tf_path_FRW", e=True, tx="")
	mc.image("img_FRW", e=True, i=THIS_DIR+"/frw.png")
	if mc.textScrollList("tsl_type_FRW", q=True, nsi=True):
		t = mc.textScrollList("tsl_type_FRW", q=True, si=True)[0]
		if mc.textScrollList("tsl_name_FRW", q=True, nsi=True):
			n = mc.textScrollList("tsl_name_FRW", q=True, si=True)[0]
			f = STAGING_DIR+"/"+t+"/"+n+"/"+n+".py"
			if os.path.isfile(f):
				mc.textField("tf_path_FRW", e=True, tx=f)
				f = f[:-3]+".png"
				if os.path.isfile(f):
					mc.image("img_FRW", e=True, i=f)

	__updateInspector()

# Updates the inspector according to the contents (functions and signatures) of the template script.
# Stores useful information in a global cache, accessible from everywhere in the code.
def __updateInspector():

	global CACHE
	CACHE = {"index":{}, "function":{}, "execute":{}}

	mc.button("b_execute_FRW", e=True, en=False)
	l = mc.scrollLayout("sl_inspector_FRW", q=True, ca=True) or []
	if len(l): mc.deleteUI(l)
	if mc.textScrollList("tsl_type_FRW", q=True, nsi=True):
		t = mc.textScrollList("tsl_type_FRW", q=True, si=True)[0]
		if mc.textScrollList("tsl_name_FRW", q=True, nsi=True):
			CACHE["name"] = mc.textScrollList("tsl_name_FRW", q=True, si=True)[0]
			CACHE["file"] = STAGING_DIR+t+"/"+CACHE["name"]+"/"+CACHE["name"]+".py"
			if os.path.isfile(CACHE["file"]):
				m = imp.load_source(CACHE["name"], CACHE["file"])
				for n, o in inspect.getmembers(m, inspect.isfunction):
					CACHE["index"][o.__code__.co_firstlineno] = [n, inspect.getargspec(o)]
				ids = sorted(CACHE["index"].viewkeys()); c = len(ids)
				for i in range(c):
					if i == 0: mc.button("b_execute_FRW", e=True, en=True)
					fn = CACHE["index"][ids[i]][0]
					CACHE["function"][fn] = {"checkbox":None, "arguments":{}, "presets":{}}
					mc.rowLayout(nc=10, adj=2, p="sl_inspector_FRW")
					cb = mc.iconTextCheckBox(i="checkboxOff.png", si="checkboxOn.png",
						v=__loadStatePreset(fn), cc=partial(__saveStatePreset, ids[i]))
					CACHE["function"][fn]["checkbox"] = cb
					mc.text(l=CACHE["index"][ids[i]][0], w=250, al="left", fn="fixedWidthFont")
					ab = mc.iconTextButton(st="iconOnly", i1="fileOpen.png", ann="load preset", vis=False, c=partial(__loadAllArgPresets, ids[i]))
					eb = mc.iconTextButton(st="iconOnly", i1="fileSave.png", ann="save preset", vis=False, c=partial(__saveAllArgPresets, ids[i]))
					db = mc.iconTextButton(st="iconOnly", i1="QR_delete.png", ann="delete preset", vis=False, c=partial(__deleteAllArgPresets, ids[i]))
					rv = mc.iconTextButton(st="iconOnly", i1="RS_disable.png", ann="reset value", vis=False, c=partial(__resetAllArgValues, ids[i]))
					mc.text(l="", w=5)
					CACHE["function"][fn]["error"] = mc.image(i="RS_WarningOldCollection", vis=False)
					e = mc.iconTextButton(st="iconOnly", i1="timeplay.png", c=partial(__execute, ids[i]))
					CACHE["execute"][e] = CACHE["index"][ids[i]][0]
					mc.setParent("..")
					arg_nms = CACHE["index"][ids[i]][1][0];       c_nms = len(arg_nms)
					arg_val = CACHE["index"][ids[i]][1][3] or []; c_val = len(arg_val)
					offset = c_nms - c_val
					# arguments
					for j in range(offset):
						if j == 0:
							for s in [ab, eb, db, rv]: mc.iconTextButton(s, e=True, vis=True)
						tfg, img = __argumentWidget(j, ids[i], CACHE["index"][ids[i]][0], arg_nms[j], None)
						CACHE["function"][fn]["arguments"][arg_nms[j]] = tfg
						CACHE["function"][fn]["presets"][arg_nms[j]] = img
					# keyword arguments
					for j in range(c_val):
						if j == 0:
							for s in [ab, eb, db, rv]: mc.iconTextButton(s, e=True, vis=True)
						jj = j+offset
						tfg, img = __argumentWidget(jj, ids[i], CACHE["index"][ids[i]][0], arg_nms[jj], arg_val[j])
						CACHE["function"][fn]["arguments"][arg_nms[jj]] = tfg
						CACHE["function"][fn]["presets"][arg_nms[jj]] = img
					if i < c-1: mc.separator(st="in", w=435, h=10, p="sl_inspector_FRW")
					# Load at once any available presets for the arguments of the inspected function.
					__loadArgPreset(ids[i], arg_nms)

def __argumentWidget(i, idx, fn, arg_nam, arg_val, presets=True):

	mc.rowLayout(nc=2, adj=True)
	tfg = mc.textFieldGrp(l=arg_nam, tx=str(arg_val))
	if presets:
		mc.popupMenu()
		mc.menuItem("load preset", i="folder-open.png", c=partial(__loadArgPreset, idx, [arg_nam]))
		mc.menuItem("save preset", i="UVTkSaveValue.png", c=partial(__saveArgPreset, idx, fn+"."+arg_nam))
		mc.menuItem("delete preset", i="RS_delete.png", c=partial(__deleteArgPreset, idx, fn+"."+arg_nam))
		mc.menuItem(d=True)
		mc.menuItem("reset value", i="RS_disable.png", c=partial(__resetArgValue, idx, arg_nam))
		img = mc.image(i="Bookmark.png", vis=False)
	else: img = None
	mc.setParent("..")

	return tfg, img

def __icon(*arg):

	if "file" not in CACHE.viewkeys(): return
	mc.select(cl=True)
	for e in mc.lsUI(ed=True):
		try: mc.viewFit(p=e)
		except: pass
	f = CACHE["file"][:-3]+".png"
	if os.path.isfile(f): os.remove(f)
	fmt = mc.getAttr("defaultRenderGlobals.imageFormat")
	mc.setAttr("defaultRenderGlobals.imageFormat", 32)
	i = mc.playblast(cf=f, fmt="image", cc=False, fr=1, v=False, orn=False, os=True, p=100, wh=[200,200], qlt=100)
	mc.setAttr("defaultRenderGlobals.imageFormat", fmt)
	mc.image("img_FRW", e=True, i=f)

# edit build template
def __edit(*arg):

	if "file" not in CACHE.viewkeys(): return

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	if platform.system() == "Windows": os.system("start "+EDITOR+" "+CACHE["file"])
	else: os.system(EDITOR+" "+CACHE["file"]+"&")

# edit library
def __edit2(*arg):

	if not os.path.isfile(arg[0]):
		mc.confirmDialog(t=" ", m="File not found: "+arg[0], b="ok")
		return

	if platform.system() == "Windows": os.system("start "+EDITOR+" "+arg[0])
	else: os.system(EDITOR+" "+arg[0]+"&")

def __extensions():

	l = mc.columnLayout("cl_extensions_FRW", q=True, ca=True) or []
	if len(l) > 0: mc.deleteUI(l)

	mc.columnLayout(p="cl_extensions_FRW")
	mc.iconTextButton(st="iconOnly", i1="CN_refresh.png", ann="update", c=__extensions)
	mc.setParent("..")

	__main__.FRW_DIR = THIS_DIR
	d = THIS_DIR+"/extensions/"
	if not os.path.isdir(d): return
	for f in glob.glob(d+"*.py"):
		try:
			n = os.path.splitext(os.path.split(f)[1])[0]
			m = imp.load_source(n, f)
			fl = mc.frameLayout(l=n, bv=True, cll=True, mw=5, mh=5, p="cl_extensions_FRW")
			m.main()
			mc.setParent("..")
			mc.frameLayout(fl, e=True, cl=False)
			mc.frameLayout(fl, e=True, cl=True)
		except Exception as e:
			print("Extension: "+f)
			print("    Error: "+str(e))

def __library():

	l = mc.columnLayout("cl_library_FRW", q=True, ca=True) or []
	if len(l) > 0: mc.deleteUI(l)

	mc.columnLayout(p="cl_library_FRW")
	mc.iconTextButton(st="iconOnly", i1="CN_refresh.png", ann="update", c=__library)
	mc.setParent("..")

	if not os.path.isdir(THIS_DIR): return
	global LIB_CACHE
	LIB_CACHE = {}
	for f in glob.glob(THIS_DIR+"/*.py"):
		f = f.replace("\\", "/")
		n = os.path.splitext(os.path.split(f)[1])[0]
		try: m = imp.load_source(n, f)
		except Exception as e:
			print("Library: "+f)
			print("  Error: "+str(e))
			continue
		fl = mc.frameLayout(l=n, bv=True, cll=True, cl=True, mw=15, mh=15, p="cl_library_FRW")
		mc.rowLayout(nc=2, adj=1)
		mc.textField(tx=f, ed=False)
		mc.iconTextButton(st="iconOnly", i1="passSetRelationEditor.png", ann="edit", c=partial(__edit2, f))
		mc.setParent("..")
		mc.separator(st="in", w=420, h=10)
		LIB_CACHE[f] = {}
		for n, o in inspect.getmembers(m, inspect.isfunction):
			LIB_CACHE[f][o.__code__.co_firstlineno] = [n, inspect.getargspec(o)]
		ids = sorted(LIB_CACHE[f].viewkeys()); c = len(ids)
		for i in range(c):
			fn = LIB_CACHE[f][ids[i]][0]
			arg_nms = LIB_CACHE[f][ids[i]][1][0];       c_nms = len(arg_nms)
			arg_val = LIB_CACHE[f][ids[i]][1][3] or []; c_val = len(arg_val)
			mc.frameLayout(l=fn, bv=True, cll=True, cl=True, mw=5, mh=5, fn="smallPlainLabelFont")
			mc.rowLayout(nc=2, adj=1)
			mc.text(l="")#fn, al="left", fn="fixedWidthFont")
			e = mc.iconTextButton(st="iconOnly", i1="timeplay.png", c=partial(__execute2, f, ids[i]))
			mc.setParent("..")
			if c_nms > 0:
				LIB_CACHE[f][ids[i]].append({})
				offset = c_nms - c_val
				# arguments
				for j in range(offset):
					LIB_CACHE[f][ids[i]][2][arg_nms[j]] = __argumentWidget(j, ids[i], LIB_CACHE[f][ids[i]][1][0], arg_nms[j], None, presets=False)[0]
				# keyword arguments
				for j in range(c_val):
					jj = j+offset
					LIB_CACHE[f][ids[i]][2][arg_nms[jj]] = __argumentWidget(jj, ids[i], LIB_CACHE[f][ids[i]][1][0], arg_nms[jj], arg_val[j], presets=False)[0]
			# if i < c-1: mc.separator(st="in", h=10)
			mc.setParent("..")
		mc.frameLayout(fl, e=True, cl=False)
		mc.frameLayout(fl, e=True, cl=True)

#
# argument presets
#

def __loadAllArgPresets(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	f = CACHE["file"][:-3]+".pre"
	if os.path.isfile(f):
		fn = CACHE["index"][arg[0]][0]
		f = open(f); lines = f.readlines(); f.close()
		for line in lines:
			line = line.strip()
			if "=" not in line: continue
			l = line.split("=")
			if not "." in l[0]: continue
			fn2, arg2 = l[0].strip().split(".")
			if fn != fn2: continue
			for arg in CACHE["function"][fn]["arguments"].viewkeys():
				if arg != arg2: continue
				tfg = CACHE["function"][fn]["arguments"][arg]
				mc.textFieldGrp(tfg, e=True, tx=l[1].strip())
				img = CACHE["function"][fn]["presets"][arg]
				mc.image(img, e=True, vis=True)

def __saveAllArgPresets(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	fn = CACHE["index"][arg[0]][0]
	filepath = CACHE["file"][:-3]+".pre"
	if os.path.isfile(filepath):
		f = open(filepath); l = f.readlines(); f.close()
		for arg in CACHE["function"][fn]["arguments"].viewkeys():
			add = False
			for i in range(len(l)):
				s = l[i].strip()
				if "=" not in s: continue
				l2 = s.split("=")
				if "." not in l2[0]: continue
				if fn+"."+arg != l2[0].strip(): continue
				add = True
				tfg = CACHE["function"][fn]["arguments"][arg]
				val = mc.textFieldGrp(tfg, q=True, tx=True)
				l[i] = fn+"."+arg+" = "+str(val)+"\n"
				img = CACHE["function"][fn]["presets"][arg]
				mc.image(img, e=True, vis=True)
				break
			if not add:
				tfg = CACHE["function"][fn]["arguments"][arg]
				val = mc.textFieldGrp(tfg, q=True, tx=True)
				l.append(fn+"."+arg+" = "+str(val)+"\n")
				img = CACHE["function"][fn]["presets"][arg]
				mc.image(img, e=True, vis=True)
	else:
		l = []
		for arg in CACHE["function"][fn]["arguments"].viewkeys():
			tfg = CACHE["function"][fn]["arguments"][arg]
			val = mc.textFieldGrp(tfg, q=True, tx=True)
			l.append(fn+"."+arg+" = "+str(val)+"\n")
			img = CACHE["function"][fn]["presets"][arg]
			mc.image(img, e=True, vis=True)
	f = open(filepath, "w"); f.writelines(l); f.close()

def __deleteAllArgPresets(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	idx = arg[0]
	fn = CACHE["index"][idx][0]
	filepath = CACHE["file"][:-3]+".pre"
	if os.path.isfile(filepath):
		f = open(filepath); l = f.readlines(); f.close()
		for arg in CACHE["function"][fn]["arguments"].viewkeys():
			for i in range(len(l)):
				s = l[i].strip()
				if "=" not in s: continue
				l2 = s.split("=")
				if "." not in l2[0]: continue
				if fn+"."+arg != l2[0].strip(): continue
				__resetArgValue(idx, arg)
				l.pop(i)
				img = CACHE["function"][fn]["presets"][arg]
				mc.image(img, e=True, vis=False)
				break
		f = open(filepath, "w"); f.writelines(l); f.close()

def __resetAllArgValues(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	for arg2 in CACHE["function"][CACHE["index"][arg[0]][0]]["arguments"].viewkeys():
		__resetArgValue(arg[0], arg2)

def __loadStatePreset(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return True

	f = CACHE["file"][:-3]+".pre"
	if os.path.isfile(f):
		f = open(f); lines = f.readlines(); f.close()
		for line in lines:
			line = line.strip()
			if "=" not in line: continue
			l = line.split("=")
			if "." in l[0]: continue
			if arg[0] != l[0].strip(): continue
			return eval(l[1])

	return True

def __saveStatePreset(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	cb = CACHE["function"][CACHE["index"][arg[0]][0]]["checkbox"]
	val = str(mc.iconTextCheckBox(cb, q=True, v=True))
	fn = CACHE["index"][arg[0]][0]
	filepath = CACHE["file"][:-3]+".pre"
	if os.path.isfile(filepath):
		add = False
		f = open(filepath); l = f.readlines(); f.close()
		for i in range(len(l)):
			s = l[i].strip()
			if "=" not in s: continue
			l2 = s.split("=")
			if "." in l2[0]: continue
			if fn != l2[0].strip(): continue
			add = True
			l[i] = fn+" = "+val+"\n"
			break
		if not add: l.append(fn+" = "+val+"\n")
		f = open(filepath, "w"); f.writelines(l); f.close()
	else:
		s = fn+" = "+val+"\n"
		f = open(filepath, "w"); f.write(s); f.close()

def __loadArgPreset(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	f = CACHE["file"][:-3]+".pre"
	if not os.path.isfile(f): lines = []
	else:
		f = open(f); lines = f.readlines(); f.close()

	idx = arg[0]
	fn = CACHE["index"][idx][0]
	args = arg[1]
	for arg in args:
		img = CACHE["function"][CACHE["index"][idx][0]]["presets"][arg]
		mc.image(img, e=True, vis=False)

		for line in lines:
			line = line.strip()
			if "=" not in line: continue
			l = line.split("=")
			if "." not in l[0]: continue
			fn2, arg2 = l[0].strip().split(".")
			if fn != fn2 or arg != arg2: continue
			tfg = CACHE["function"][CACHE["index"][idx][0]]["arguments"][arg]
			mc.textFieldGrp(tfg, e=True, tx=("=".join(s for s in l[1:])).strip())
			mc.image(img, e=True, vis=True)

def __saveArgPreset(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	idx = arg[0]
	fn, arg = arg[1].split(".")

	filepath = CACHE["file"][:-3]+".pre"
	if os.path.isfile(filepath):
		add = False
		f = open(filepath); l = f.readlines(); f.close()
		for i in range(len(l)):
			s = l[i].strip()
			if "=" not in s: continue
			l2 = s.split("=")
			if "." not in l2[0]: continue
			if fn+"."+arg != l2[0].strip(): continue
			add = True
			tfg = CACHE["function"][CACHE["index"][idx][0]]["arguments"][arg]
			val = mc.textFieldGrp(tfg, q=True, tx=True)
			l[i] = fn+"."+arg+" = "+str(val)+"\n"
			break
		if not add:
			tfg = CACHE["function"][CACHE["index"][idx][0]]["arguments"][arg]
			val = mc.textFieldGrp(tfg, q=True, tx=True)
			l.append(fn+"."+arg+" = "+str(val)+"\n")
		f = open(filepath, "w"); f.writelines(l); f.close()
	else:
		tfg = CACHE["function"][CACHE["index"][idx][0]]["arguments"][arg]
		val = mc.textFieldGrp(tfg, q=True, tx=True)
		s = fn+"."+arg+" = "+str(val)+"\n"
		f = open(filepath, "w"); f.write(s); f.close()

	img = CACHE["function"][CACHE["index"][idx][0]]["presets"][arg]
	mc.image(img, e=True, vis=True)

def __deleteArgPreset(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	idx = arg[0]
	fn, arg = arg[1].split(".")

	filepath = CACHE["file"][:-3]+".pre"
	if os.path.isfile(filepath):
		f = open(filepath); l = f.readlines(); f.close()
		for i in range(len(l)):
			s = l[i].strip()
			if "=" not in s: continue
			l2 = s.split("=")
			if "." not in l2[0]: continue
			if fn+"."+arg == l2[0].strip():
				l.pop(i)
				f = open(filepath, "w"); f.writelines(l); f.close()
				__resetArgValue(idx, arg)
				break

	img = CACHE["function"][CACHE["index"][idx][0]]["presets"][arg]
	mc.image(img, e=True, vis=False)

def __resetArgValue(*arg):

	nms = CACHE["index"][arg[0]][1][0];       c_nms = len(nms)
	val = CACHE["index"][arg[0]][1][3] or []; c_val = len(val)
	offset = c_nms - c_val
	for i in range(c_nms):
		if arg[1] == nms[i]: break
	tfg = CACHE["function"][CACHE["index"][arg[0]][0]]["arguments"][arg[1]]
	if c_nms != c_val:
		if i < offset: mc.textFieldGrp(tfg, e=True, tx="None")
		else: mc.textFieldGrp(tfg, e=True, tx=str(val[i-offset]))
	else: mc.textFieldGrp(tfg, e=True, tx=str(val[i]))

#
# execute code from inspector
#

def __execute(*arg):

	if not os.path.isfile(CACHE["file"]):
		mc.confirmDialog(t=" ", m="File not found: "+CACHE["file"], b="ok")
		return

	cmd = CACHE["name"]+'=imp.load_source("'+CACHE["name"]+'", "'+CACHE["file"]+'")'
	print("import imp\n"+cmd); exec(cmd)

	for idx in sorted(CACHE["index"].viewkeys()):
		fn = CACHE["index"][idx][0]
		mc.image(CACHE["function"][fn]["error"], e=True, vis=False)
		if type(arg[0]) != int:
			if not mc.iconTextCheckBox(CACHE["function"][fn]["checkbox"], q=True, v=True):
				continue
		elif idx != arg[0]:
			continue
		cmd = CACHE["name"]+"."+fn+"("+__arguments(idx)+")"
		print(cmd)
		try: exec(cmd)
		except Exception as e:
			mc.image(CACHE["function"][fn]["error"], e=True, vis=True)
			raise Exception(e)

	if type(arg[0]) == bool: __icon()

def __arguments(idx):

	arg = ""
	nms = CACHE["index"][idx][1][0];       cnt_nms = len(nms)
	val = CACHE["index"][idx][1][3] or []; cnt_val = len(val)
	off = cnt_nms-cnt_val
	for i in range(off):
		tfg = CACHE["function"][CACHE["index"][idx][0]]["arguments"][nms[i]]
		val = mc.textFieldGrp(tfg, q=True, tx=True)
		try: val = eval(val)
		except: val = '"'+val+'"'
		arg += str(val)
		if cnt_nms != cnt_val: arg += ", "
	for i in range(cnt_val):
		tfg = CACHE["function"][CACHE["index"][idx][0]]["arguments"][nms[i+off]]
		val = mc.textFieldGrp(tfg, q=True, tx=True)
		try: val = eval(val)
		except: val = '"'+val+'"'
		arg += nms[i+off]+"="+str(val)
		if i < cnt_val-1: arg += ", "

	return arg

#
# execute code from library
#

def __execute2(*arg):

	if not os.path.isfile(arg[0]):
		mc.confirmDialog(t=" ", m="File not found: "+arg[0], b="ok")
		return

	n = os.path.split(os.path.splitext(arg[0])[0])[1]
	cmd = n+'=imp.load_source("'+n+'", "'+arg[0]+'")'
	print("import imp\n"+cmd); exec(cmd)

	cmd = n+"."+LIB_CACHE[arg[0]][arg[1]][0]+"("+__arguments2(arg[0], arg[1])+")"
	print(cmd); exec(cmd)

def __arguments2(f, idx):

	arg = ""
	nms = LIB_CACHE[f][idx][1][0];       cnt_nms = len(nms)
	val = LIB_CACHE[f][idx][1][3] or []; cnt_val = len(val)
	off = cnt_nms-cnt_val
	for i in range(off):
		tfg = LIB_CACHE[f][idx][2][nms[i]]
		val = mc.textFieldGrp(tfg, q=True, tx=True)
		try: val = eval(val)
		except: val = '"'+val+'"'
		arg += str(val)
		if cnt_nms != cnt_val: arg += ", "
	for i in range(cnt_val):
		tfg = LIB_CACHE[f][idx][2][nms[i+off]]
		val = mc.textFieldGrp(tfg, q=True, tx=True)
		try: val = eval(val)
		except: val = '"'+val+'"'
		arg += nms[i+off]+"="+str(val)
		if i < cnt_val-1: arg += ", "

	return arg

#
# create/delete assets
#

def __createAsset_ui(*arg):

	mc.layoutDialog(ui=__createAsset_dlg, t="create new asset")

def __createAsset_dlg():

	mc.columnLayout(adj=True)
	mc.rowLayout(nc=2, adj=2)
	mc.text(l="rig type", al="right", w=80)
	mc.optionMenu("om_rigType_FRW")
	for f in glob.glob(THIS_DIR+"/*.ma"):
		mc.menuItem(l=os.path.splitext(os.path.split(f)[1])[0])
	mc.setParent("..")
	mc.rowLayout(nc=2, adj=2)
	mc.text(l="asset type", al="right", w=80)
	mc.optionMenu("om_assetType_FRW")
	for t in ASSET_TYPES: mc.menuItem(l=t)
	mc.setParent("..")
	mc.rowLayout(nc=2, adj=2)
	mc.text(l="asset name", al="right", w=80)
	mc.textField("tf_assetName_FRW")
	mc.setParent("..")
	mc.text(l="")
	mc.rowColumnLayout(nc=2, cw=[(1,148),(2,148)])
	mc.button(l="create", c=__createAsset_stage)
	mc.button(l="cancel", c=__createAsset_cancel)
	mc.setParent("..")
	mc.setParent("..")

def __createAsset_cancel(*arg): mc.layoutDialog(dis="cancel")

def __createAsset_stage(*arg):

	n = mc.textField("tf_assetName_FRW", q=True, tx=True).strip()
	if not n:
		mc.confirmDialog(t=" ", m="Incorrect asset name.", b="ok")
		return
	rt = mc.optionMenu("om_rigType_FRW", q=True, v=True)
	at = mc.optionMenu("om_assetType_FRW", q=True, v=True)
	f = STAGING_DIR+at+"/"+n+"/"+n+".py"
	if os.path.isfile(f):
		result = mc.confirmDialog(t="overwrite existing asset",
					m="Asset with this name already exists. Do you want to overwrite it ?",
					b=["yes","no"], cb="no", ds="no", db="no")
		if result == "no": return
	createAsset(rt, at, n)
	mc.layoutDialog(dis="cancel")
	__update()
	mc.textScrollList("tsl_type_FRW", e=True, si=at)
	__updateNames()
	mc.textScrollList("tsl_name_FRW", e=True, si=n)
	__update()

def createAsset(rigType, assetType, assetName):

	directory = STAGING_DIR+assetType+"/"+assetName+"/"
	try: os.makedirs(directory)
	except: pass
	if not os.path.isdir(directory):
		raise Exception("Cannot create directory: "+directory)

	filepath = directory+assetName+".py"
	try: shutil.copy(THIS_DIR+"/template.py", filepath)
	except: raise Exception("Cannot create file: "+filepath)
	try: os.makedirs(directory+"/weights")
	except: pass
	try: os.remove(filepath[:-3]+".pre")
	except: pass

	if not os.path.isfile(THIS_DIR+"/"+rigType+".py"): rigType = "generic"
	for f in glob.glob(THIS_DIR+"/"+rigType+".*"):
		ext = os.path.splitext(f)[1]
		if ext == ".py" or ext == ".pyc": continue
		shutil.copy(f, directory+assetName+ext)

	m = imp.load_source(rigType, THIS_DIR+"/"+rigType+".py")
	for n, o in inspect.getmembers(m, inspect.isfunction):
		if n == "main":
			args = inspect.getargspec(o)
			args1 = ", ".join((a+"="+str(b), a+'="'+str(b)+'"')[type(b) == str] for a,b in zip(args[0],args[3]))
			args2 = ", ".join(a+"="+a for a in args[0])

			f = open(filepath); s = f.read(); f.close()
			s = s.replace("FRW_DIR", THIS_DIR).replace("FRW_RIG", rigType)
			s = s.replace("FRW_ARG2", args2).replace("FRW_ARG", args1)
			f = open(filepath, "w"); f.write(s); f.close()

			break

	print("Result: "+filepath)
	return filepath

def __deleteAsset(*arg):

	if "file" not in CACHE.viewkeys(): return

	d = os.path.split(CACHE["file"])[0]
	if not os.path.isdir(d):
		mc.confirmDialog(t=" ", m="Invalid asset.", b="ok")
		return

	result = mc.confirmDialog(t="delete asset",
					m="Do you want to delete the selected asset ?",
					b=["yes","no"], cb="no", ds="no", db="no")
	if result == "no": return

	try: shutil.rmtree(d)
	except: raise Exception("Cannot delete directory: "+d)

	__update()
