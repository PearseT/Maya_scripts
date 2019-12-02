"""
komodo_rig rig setup
main module
"""
import maya.cmds as cmds
from rigLib.base import control, module

scene_scale = 1.0

main_project_path = 'C:/Users/pears/Desktop/'
model_file_path = '%s/%s/model/%s_model.mb'
builder_file_path = '%s/%s/builder/%s_builder.mb'


def build(
        character_name
    ):
    """
    function to build Komodo rig

    :param character_name: name of character to rig
    :return:
    """
    # make new scene
    cmds.file(new=True, force=True)

    # make base group
    base_rig = module.Base(character_name='character_name', scale=scene_scale)

    # import model
    model_file = model_file_path % (main_project_path, character_name, character_name)
    cmds.file(model_file, i=True)

    # import builder scene
    builder_file = builder_file_path % (main_project_path, character_name, character_name)
    cmds.file(builder_file, i=True)

    module.Module(prefix='arm', base_object=base_rig)
