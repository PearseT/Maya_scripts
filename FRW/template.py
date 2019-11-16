import sys, os
import maya.cmds as mc
import maya.mel as mm

sys.path.append("FRW_DIR")
import common; reload(common)
import FRW_RIG; reload(FRW_RIG)

THIS_DIR, THIS_FILE = os.path.split(__file__)
sys.path.append(THIS_DIR)
THIS_FILE_NAME = os.path.splitext(THIS_FILE)[0]

def new(): mc.file(new=True, f=True)

def preRig(): pass

def rig(FRW_ARG):

	# consider local file paths, if no absolute ones provided
	try: templateFile = THIS_DIR+"/"+THIS_FILE_NAME+".ma" if not templateFile else templateFile
	except: pass
	try: controlShapes = THIS_DIR+"/"+controlShapes if not os.path.isfile(controlShapes) else controlShapes
	except: pass
	try: oglControlShapes = THIS_DIR+"/"+oglControlShapes if not os.path.isfile(oglControlShapes) else oglControlShapes
	except: pass

	FRW_RIG.main(FRW_ARG2)

def postRig(): pass

def model(filepath=[]): common.loadModel(filepath)

def preBind(): pass

# Keyword argument "method" can be "index", "nearest", "barycentric", or "bilinear".
def bind(method="index"): common.bind(THIS_DIR+"/weights/", method=method)

def postBind(): pass

def finalize(): pass
