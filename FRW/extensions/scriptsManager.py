import os, __main__
import maya.cmds as mc

def main():

	mc.text(l="Use SOuP's scriptsManager as an alternative browser for the FRW codebase.")
	mc.button(l="scripts manager", w=440, c=doit)

def doit(*arg):

	try: __main__.scriptsManager.Gui()._Gui__setDir(__main__.FRW_DIR)
	except: pass
