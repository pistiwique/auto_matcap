import bpy
import os
from os import listdir
from os.path import isfile, join
import pickle
from bpy.types import Operator

matcap_preview_collections = {}


def convert_as_icons():

    current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[current_dir].preferences
    thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
    extentions = (".jpeg", ".jpg", ".png", ".tiff")
    
    images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f)) and f.endswith(extentions)]
        
    thumbnails_matcaps = [f for f in listdir(thumbnails_path) if isfile(join(thumbnails_path, f))]  

    settings = bpy.context.scene.render.image_settings

    settings.file_format = 'PNG'
    settings.color_mode = 'RGBA'
    settings.color_depth = '8'
    
    for images in images_matcaps:                
        if images not in thumbnails_matcaps:
            img_name = (images.split("."))[0]
            img = bpy.data.images.load(join(addon_prefs.matcaps_path, images))
            img.scale(256, 256)
            img.save_render(join(thumbnails_path,img_name + ".png")) 


def save_current_setup():

    current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[current_dir].preferences
    pickle_path = join(addon_prefs.matcaps_path, "Backup_of_scene")
    
    if not os.path.exists(pickle_path):
            os.makedirs(pickle_path)
    
    my_dict = {}
    key = "materials"
      
    my_dict["render_engine"] = bpy.context.scene.render.engine 
    my_dict["material_mode"] = bpy.context.scene.game_settings.material_mode
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    myViewport_shade = space.viewport_shade
                    
    my_dict["viewport_shade"] = myViewport_shade
    
    if bpy.context.active_object.active_material:        
        for mat in bpy.context.active_object.material_slots:
            list_mat = mat.name
            my_dict.setdefault(key, [])
            my_dict[key].append(list_mat) 
                                   
    else:        
        my_dict["materials"] = "No material"
            
    output = open(join(pickle_path, "backup_setup"), "wb")
    pickle.dump(my_dict, output)
    output.close()
    
    
def update_matcap_folder(self, context):
    if self.auto_matcap_enabled:
        
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[current_dir].preferences
        thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
    
        # Test if "Thumbnails" folder exist. If not, we create it
        if not os.path.exists(thumbnails_path):
            os.makedirs(thumbnails_path)
        
        # We get back the list of the names of matcaps without the extension of file 
        images_matcaps = [f.split(".")[0] for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
        
        # Same as matcaps but for the thumbanils
        thumbnails_matcaps = [f.split(".")[0] for f in listdir(thumbnails_path) if isfile(join(thumbnails_path, f))] 
        
        for images in images_matcaps:
            if images not in thumbnails_matcaps:
                convert_as_icons()
                update_matcap_preview()
                
        for images in thumbnails_matcaps:
            if images not in images_matcaps:
                os.remove(join(thumbnails_path, images + ".png"))
                update_matcap_preview()
        
        save_current_setup()
        bpy.ops.material.setup_matcap()
        
    else:
        bpy.ops.object.restore_setup()
        
def update_matcap_preview():
    global matcap_preview_collections
    matcap_preview_collections = {}
    register_matcap_pcoll()
    

def update_matcap(self, context):
    bpy.ops.material.setup_matcap()
    

def enumPreviewsFromDirectoryItems(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items

    current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[current_dir].preferences    
    directory = join(addon_prefs.matcaps_path, "Thumbnails")
    # Get the preview collection (defined in register func).
    pcoll = matcap_preview_collections["main"]

    if directory == pcoll.matcap_previews_dir:
        return pcoll.matcap_previews

    # print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name.split(".png")[0], "", thumb.icon_id, i))

    pcoll.matcap_previews = enum_items
    pcoll.matcap_previews_dir = directory
    
    return pcoll.matcap_previews


def register_matcap_pcoll():  
    from bpy.types import WindowManager
    from bpy.props import (
            EnumProperty,
            BoolProperty)

    WindowManager.matcap_previews = EnumProperty(
            items=enumPreviewsFromDirectoryItems,
            update=update_matcap)
                    
    WindowManager.auto_matcap_enabled = BoolProperty(
            name="Auto matcap",
            description="Configure automatically the scene for using custom matcaps",
            default=False,
            update=update_matcap_folder)
                               
    import bpy.utils.previews
    wm = bpy.context.window_manager
    pcoll = bpy.utils.previews.new()
    pcoll.matcap_previews_dir = ""
    pcoll.matcap_previews = ()

    matcap_preview_collections["main"] = pcoll


def unregister_matcap_pcoll():
    from bpy.types import WindowManager

    del WindowManager.matcap_previews

    for pcoll in matcap_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    matcap_preview_collections.clear()
