import bpy
import os
from os import listdir
from os.path import isfile, join
import pickle
from bpy.types import Operator
from . utils import *

class AutoMatcapCollectionGroup(bpy.types.PropertyGroup):
    multi_remove = bpy.props.BoolProperty(
        name="Multi remove",
        default=False, 
        description="Active multi selection to remove a list of selected matcaps")
        
    options = bpy.props.BoolProperty(
        name="Options",
        default=False,
        description="Display the options")
        
    new_name = bpy.props.StringProperty(
        name="Change name",
        default="")
        
    is_visible = bpy.props.BoolProperty(
        name="",
        default=False)
        
    remove_list = []
     

class SetupMatcap(Operator):
    bl_idname = "material.setup_matcap"
    bl_label = "Create new Matcap"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
    
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[current_dir].preferences
        thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")                         
        automatcap_settings = context.window_manager.automatcap_settings
        
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.space_data.viewport_shade = 'TEXTURED'
        
        if automatcap_settings.multi_remove:
            img_name = bpy.data.window_managers["WinMan"].matcap_previews
            
            if img_name in automatcap_settings.remove_list:
                pass
            
            else:
                automatcap_settings.remove_list.append(img_name)
                
            return {'FINISHED'}
        
        else:       
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
    

class RemoveMatcap(Operator):
    '''Remove the matcap and his thumbnail from your matcap library'''
    bl_idname = "material.remove_matcap"
    bl_label = "Remove matcap"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
                
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[current_dir].preferences
        thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
        automatcap_settings = context.window_manager.automatcap_settings
        images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]           
        matcaps_name = [f.split(".")[0] for f in automatcap_settings.remove_list]
        
        
        if automatcap_settings.multi_remove:
            thumbnails = (item for item in automatcap_settings.remove_list)
            matcaps = (item for item in images_matcaps if item.split(".")[0] in matcaps_name)
            
            for item in thumbnails:
                os.remove(join(thumbnails_path, item))
                
            for item in matcaps:
                os.remove(join(addon_prefs.matcaps_path, item))
                
            del(automatcap_settings.remove_list[:])
            automatcap_settings.multi_remove = False
            update_matcap_preview()
            
            return {'FINISHED'} 
        
        else:                   
            matcap_selected = bpy.data.window_managers["WinMan"].matcap_previews
            images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
            
            # We get back the matcap corresponding to the choice in preview
            matcap = [item for item in images_matcaps if item.split(".")[0] == matcap_selected.split(".")[0]]
            os.remove(join(addon_prefs.matcaps_path, matcap[0]))
            os.remove(join(addon_prefs.matcaps_path, "Thumbnails", matcap_selected))
            update_matcap_preview()
            
            return {'FINISHED'}        
        

class DeleteFromList(Operator):
    '''Remove the matcap from the list'''
    bl_idname = "material.remove_from_list"
    bl_label = "Remove from list"
    bl_options = {'REGISTER'}
    
    matcap = bpy.props.StringProperty(default = "")
    
    def execute(self, context):                
        automatcap_settings = context.window_manager.automatcap_settings
        
        if self.matcap in automatcap_settings.remove_list:
            automatcap_settings.remove_list.remove(self.matcap)            
        
        return {'FINISHED'}                
        

class ShowMatcap(Operator):
    '''Show the matcap in the preview'''
    bl_idname = "material.show_matcap"
    bl_label = "Show matcap"
    bl_options = {'REGISTER'}
    
    show_matcap = bpy.props.StringProperty(default = "")
    
    def execute(self, context):
        automatcap_settings = context.window_manager.automatcap_settings
        bpy.data.window_managers["WinMan"].matcap_previews = self.show_matcap
        automatcap_settings.is_visible = False
         
        return{'FINISHED'}
        
    
class ChangeMatcapName(Operator):
    ''' Change the matcap and thumbnail's name '''
    bl_idname = "material.change_matcap_name"
    bl_label = "Change matcap name"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[current_dir].preferences
        thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
        automatcap_settings = context.window_manager.automatcap_settings
        new_name = automatcap_settings.new_name
        
        images_matcaps = [f for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f))]
        thumbnails_matcaps = [f for f in listdir(thumbnails_path) if isfile(join(thumbnails_path, f))]         
        selected_matcap = bpy.data.window_managers["WinMan"].matcap_previews
        
        thumbnail = [item for item in thumbnails_matcaps if item == selected_matcap]
        os.rename(join(thumbnails_path, thumbnail[0]), join(thumbnails_path, new_name + ".png"))
        
        matcap = [item for item in images_matcaps if item.split(".")[0] == selected_matcap.split(".")[0]]
        matcap_extention = matcap[0].split(".")[-1]
        os.rename(join(addon_prefs.matcaps_path, matcap[0]), join(addon_prefs.matcaps_path, new_name + "." + matcap_extention))
        update_matcap_preview()
        bpy.data.window_managers["WinMan"].matcap_previews = new_name + ".png"
        
        automatcap_settings.new_name = ""
        
        return {'FINISHED'}
        
        
                    
class RefreshMatcapsFolder(Operator):
    ''' Refresh the preview manually after addition or deletion of matcap '''
    bl_idname = "material.refresh_preview_manually"
    bl_label = "Refresh preview"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[current_dir].preferences 
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
    
    
class RestoreSetup(Operator):
    ''' Back to setup before created Matcap'''
    bl_idname = "object.restore_setup"
    bl_label = "Restore setup"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        
        current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[current_dir].preferences 
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