import sys, os
import maya.cmds as mc
import maya.mel as mm

sys.path.append("C:/Users/pears/PycharmProjects/Maya_scripts/FRW")
import common; reload(common)
import biped; reload(biped)

THIS_DIR, THIS_FILE = os.path.split(__file__)
sys.path.append(THIS_DIR)
THIS_FILE_NAME = os.path.splitext(THIS_FILE)[0]

def new(): mc.file(new=True, f=True)

def preRig(): pass

def rig(templateFile=None, inheritTemplateRotations=False, controlShapes=None, oglControlShapes=None, fbx=False, scale=1, radius=1, numTwistJoints=4, ikShape="cube"):

	# consider local file paths, if no absolute ones provided
	try: templateFile = THIS_DIR+"/"+THIS_FILE_NAME+".ma" if not templateFile else templateFile
	except: pass
	try: controlShapes = THIS_DIR+"/"+controlShapes if not os.path.isfile(controlShapes) else controlShapes
	except: pass
	try: oglControlShapes = THIS_DIR+"/"+oglControlShapes if not os.path.isfile(oglControlShapes) else oglControlShapes
	except: pass

	biped.main(templateFile=templateFile, inheritTemplateRotations=inheritTemplateRotations, controlShapes=controlShapes, oglControlShapes=oglControlShapes, fbx=fbx, scale=scale, radius=radius, numTwistJoints=numTwistJoints, ikShape=ikShape)

def postRig(): pass

def model(filepath=[]): common.loadModel(filepath)

def preBind(): pass

# Keyword argument "method" can be "index", "nearest", "barycentric", or "bilinear".
def bind(method="index"): common.bind(THIS_DIR+"/weights/", method=method)

def postBind(): pass

def finalize(): pass
