import bpy
import os
from os import listdir
from os.path import isfile, join
import pickle
from bpy.types import Operator


matcap_preview_collections = {}


def convert_as_icons():
    
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons["auto_matcap"].preferences 
    thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
    
    images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
        
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

    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons["auto_matcap"].preferences 
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


class RestoreSetup(Operator):
    ''' Back to setup before created Matcap'''
    bl_idname = "object.restore_setup"
    bl_label = "Restore setup"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["auto_matcap"].preferences 
        pickle_path = join(addon_prefs.matcaps_path, "Backup_of_scene")
        # read python dict back from the file
        pickle_file = open(join(pickle_path, "backup_setup"), "rb")
        my_dict = pickle.load(pickle_file) 
        
        bpy.context.scene.render.engine = my_dict["render_engine"]
        bpy.context.scene.game_settings.material_mode = my_dict["material_mode"]
        bpy.context.space_data.viewport_shade = my_dict["viewport_shade"] 
        
        if bpy.context.object.mode == 'EDIT': 
            bpy.ops.object.mode_set(mode='OBJECT')
            if my_dict["materials"] == "No material":                
                for mat in context.active_object.material_slots:
                    bpy.ops.object.material_slot_remove()
                    
            else:
                for mat in context.active_object.material_slots:
                    bpy.ops.object.material_slot_remove()
                ob = bpy.context.active_object
                me = ob.data
                my_mat = my_dict["materials"]
                for mat in my_mat:
                    mat_list = bpy.data.materials[mat]
                    me.materials.append(mat_list)
                    
            bpy.ops.object.mode_set(mode='EDIT')
            
        else: 
            if my_dict["materials"] == "No material":                
                for mat in context.active_object.material_slots:
                    bpy.ops.object.material_slot_remove()
                    
            else:
                for mat in context.active_object.material_slots:
                    bpy.ops.object.material_slot_remove()
                ob = bpy.context.active_object
                me = ob.data
                my_mat = my_dict["materials"]
                for mat in my_mat:
                    mat_list = bpy.data.materials[mat]
                    me.materials.append(mat_list) 
                                     
        pickle_file.close()
        os.remove(join(pickle_path, "backup_setup"))
        
        return {'FINISHED'}   


class SetupMatcap(Operator):
    bl_idname = "material.setup_matcap"
    bl_label = "Create new Matcap"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
    
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["auto_matcap"].preferences 
        thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
        
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.space_data.viewport_shade = 'TEXTURED' 
        
        if bpy.data.materials:
            
            img_name = bpy.data.window_managers["WinMan"].matcap_previews.split(".")[0]
            images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
            
            # We get back the matcap corresponding to the choice in preview
            matcap = [item for item in images_matcaps if item.split(".")[0] == img_name]
            
            try:
                img = bpy.data.images.load(join(addon_prefs.matcaps_path, matcap[0]))
            except:
                raise NameError("Cannot load image %s" % join(addon_prefs.matcaps_path, matcap[0]))
            
            if "Matcap" in bpy.data.materials: 
                
                if context.active_object.material_slots:
                    if context.object.material_slots[0].name == "Matcap":
                        if matcap[0] in bpy.data.textures:
                            bpy.data.materials["Matcap"].active_texture = bpy.data.textures[matcap[0]]
                            bpy.context.object.active_material.texture_slots[0].texture_coords = 'NORMAL'
                            
                        else:
                            matTex = bpy.data.textures.new(matcap[0], type = 'IMAGE')
                            matTex.image = img
                            bpy.data.materials["Matcap"].active_texture = bpy.data.textures[matcap[0]]
                            bpy.context.object.active_material.texture_slots[0].texture_coords = 'NORMAL'
                            
                    else:
                        if context.object.mode == 'EDIT':
                            bpy.ops.object.mode_set(mode='OBJECT')
                            for mat in context.active_object.material_slots:
                                bpy.ops.object.material_slot_remove()
                            bpy.ops.object.mode_set(mode='EDIT')
                            
                        elif context.object.mode == 'OBJECT':                       
                            for mat in context.active_object.material_slots:
                                bpy.ops.object.material_slot_remove()
                
                        bpy.context.active_object.active_material = bpy.data.materials["Matcap"]
                        
                        if matcap[0] in bpy.data.textures:
                            bpy.data.materials["Matcap"].active_texture = bpy.data.textures[matcap[0]]
                            bpy.context.object.active_material.texture_slots[0].texture_coords = 'NORMAL'

                            
                        else:
                            matTex = bpy.data.textures.new(matcap[0], type = 'IMAGE')
                            matTex.image = img
                            bpy.data.materials["Matcap"].active_texture = bpy.data.textures[matcap[0]]
                            bpy.context.object.active_material.texture_slots[0].texture_coords = 'NORMAL'

                        
                else:
                    if context.object.mode == 'EDIT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for mat in context.active_object.material_slots:
                            bpy.ops.object.material_slot_remove()
                        bpy.ops.object.mode_set(mode='EDIT')
                        
                    elif context.object.mode == 'OBJECT':                       
                        for mat in context.active_object.material_slots:
                            bpy.ops.object.material_slot_remove()
            
                    bpy.context.active_object.active_material = bpy.data.materials["Matcap"]
                    
                    if matcap[0] in bpy.data.textures:
                        bpy.data.materials["Matcap"].active_texture = bpy.data.textures[matcap[0]]
                        bpy.context.object.active_material.texture_slots[0].texture_coords = 'NORMAL'

                        
                    else:
                        matTex = bpy.data.textures.new(matcap[0], type = 'IMAGE')
                        matTex.image = img
                        bpy.data.materials["Matcap"].active_texture = bpy.data.textures[matcap[0]]  
                        bpy.context.object.active_material.texture_slots[0].texture_coords = 'NORMAL'
             
                
                return {'FINISHED'}
            
            elif not "Matcap" in bpy.data.materials:                 
                
                if context.active_object.material_slots:
                    if context.object.mode == 'EDIT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for mat in context.active_object.material_slots:
                            bpy.ops.object.material_slot_remove()
                        bpy.ops.object.mode_set(mode='EDIT')
                        
                    elif context.object.mode == 'OBJECT':                       
                        for mat in context.active_object.material_slots:
                            bpy.ops.object.material_slot_remove()               
                            
                # create new material        
                mat = bpy.data.materials.new("Matcap")
                mat.diffuse_color = (0.8, 0.8, 0.8)
                mat.use_shadeless = True
                
                # Create image texture from image
                matTex = bpy.data.textures.new(matcap[0], type = 'IMAGE')
                matTex.image = img 
                
                # Add texture slot for color texture
                mtex = mat.texture_slots.add()
                mtex.texture = matTex
                mtex.texture_coords = 'NORMAL'
                mtex.use_map_color_diffuse = True 
                mtex.mapping = 'FLAT'
                
                # assign material
                ob = bpy.context.active_object
                me = ob.data
                me.materials.append(mat)
                
                return {'FINISHED'}                
        
        else: # no material        
            
            img_name = bpy.data.window_managers["WinMan"].matcap_previews.split(".")[0]
            images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
            matcap = [item for item in images_matcaps if item.split(".")[0] == img_name]
            
            try:
                img = bpy.data.images.load(join(addon_prefs.matcaps_path, matcap[0]))
            except:
                raise NameError("Cannot load image %s" % join(addon_prefs.matcaps_path, matcap[0]))
                       
            mat = bpy.data.materials.new("Matcap")
            mat.diffuse_color = (0.8, 0.8, 0.8)
            mat.use_shadeless = True
            
            matTex = bpy.data.textures.new(matcap[0], type = 'IMAGE')
            matTex.image = img 
            
            mtex = mat.texture_slots.add()
            mtex.texture = matTex
            mtex.texture_coords = 'NORMAL'
            mtex.use_map_color_diffuse = True 
            mtex.mapping = 'FLAT'
            
            ob = bpy.context.active_object
            me = ob.data
            me.materials.append(mat)            
                   
            return {'FINISHED'}


class RefreshMatcapsFolder(Operator):
    ''' Refresh the preview manually after addition or deletion of matcap '''
    bl_idname = "material.refresh_preview_manually"
    bl_label = "Refresh preview"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["auto_matcap"].preferences 
        thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")

        images_matcaps = [f.split(".")[0] for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]

        thumbnails_matcaps = [f.split(".")[0] for f in listdir(thumbnails_path) if isfile(join(thumbnails_path, f))] 
        
        for images in images_matcaps:
            if images not in thumbnails_matcaps:
                convert_as_icons()
                update_matcap_preview()
                
        for images in thumbnails_matcaps:
            if images not in images_matcaps:
                os.remove(join(thumbnails_path, images + ".png"))
                update_matcap_preview()
                
        return {'FINISHED'}
    
    
def update_matcap_folder(self, context):
    if self.auto_matcap_enabled:
        
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["auto_matcap"].preferences 
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

    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons["auto_matcap"].preferences    
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
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.matcap_previews = enum_items
    pcoll.matcap_previews_dir = directory
    return pcoll.matcap_previews


def display_auto_matcap_panel(self, context):
    layout = self.layout
    wm = context.window_manager
    
    layout.prop(wm, "auto_matcap_enabled")
    if wm.auto_matcap_enabled: 
        if not context.selected_objects:
            layout.label("No mesh selected", icon='ERROR')
        else:
            user_preferences = bpy.context.user_preferences
            addon_prefs = user_preferences.addons["auto_matcap"].preferences 
            thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")

            images_matcaps = [f.split(".")[0] for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
            thumbnails_matcaps = [f.split(".")[0] for f in listdir(thumbnails_path) if isfile(join(thumbnails_path, f))]         
            matcap_is_updated = [item for item in images_matcaps if item not in thumbnails_matcaps]
            thumbnail_is_updated = [item for item in thumbnails_matcaps if item not in images_matcaps]
            
            if len(matcap_is_updated) or len(thumbnail_is_updated):
                layout.label("Changes were made in the matcap folder", icon='ERROR')
                layout.operator("material.refresh_preview_manually", text="Refresh preview", icon='FILE_REFRESH')  
            else:                       
                layout.template_icon_view(wm, "matcap_previews")

            


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

    del WindowManager.my_previews

    for pcoll in matcap_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    matcap_preview_collections.clear()