import bpy
import os
from os import listdir
from os.path import isfile, join
      

def display_auto_matcap_panel(self, context):
    layout = self.layout
    wm = context.window_manager
    automatcap_settings = context.window_manager.automatcap_settings
    
    layout.prop(wm, "auto_matcap_enabled")
    if wm.auto_matcap_enabled: 
        if not context.selected_objects:
            layout.label("No mesh selected", icon='ERROR')
        else:
            current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
            user_preferences = bpy.context.user_preferences
            addon_prefs = user_preferences.addons[current_dir].preferences
            thumbnails_path = join(addon_prefs.matcaps_path, "Thumbnails")
            extentions = (".jpeg", ".jpg", ".png", ".tiff")

            images_matcaps = [f.split(".")[0] for f in listdir(addon_prefs.matcaps_path) if isfile(join(addon_prefs.matcaps_path, f)) and f .endswith(extentions)]
            thumbnails_matcaps = [f.split(".")[0] for f in listdir(thumbnails_path) if isfile(join(thumbnails_path, f)) and f .endswith(extentions)]         
            matcap_is_updated = [item for item in images_matcaps if item not in thumbnails_matcaps]
            thumbnail_is_updated = [item for item in thumbnails_matcaps if item not in images_matcaps]
            
            if len(matcap_is_updated) or len(thumbnail_is_updated):
                layout.label("Changes were made in the matcap folder", icon='ERROR')
                layout.operator("material.refresh_preview_manually", text="Refresh preview", icon='FILE_REFRESH')  
            else:                                                                     
                layout.template_icon_view(wm, "matcap_previews", show_labels=True)
                layout.label(text=bpy.data.window_managers["WinMan"].matcap_previews.split(".")[0])
                layout.prop(automatcap_settings, "options", icon='TRIA_DOWN' if automatcap_settings.options else 'TRIA_RIGHT')
                if automatcap_settings.options:
                    layout.label("Change matcap's name")
                    row = layout.row(align=True)
                    row.prop(automatcap_settings, "new_name", text="")
                    if automatcap_settings.new_name:
                        if automatcap_settings.new_name in thumbnails_matcaps:
                            row = layout.row(align=True)
                            row.label("\" " + automatcap_settings.new_name + " \" already exist", icon='ERROR')
                        else:  
                            row.operator("material.change_matcap_name", text="", icon='FILE_TICK')
                    row = layout.row(align=True)
                    row.operator("material.remove_matcap", text="Remove matcap", icon='X')                 
                    row.prop(automatcap_settings, "multi_remove", text = "", icon='FILE_TEXT') 
                    if automatcap_settings.multi_remove:                    
                        box = layout.box().column()
                        row = box.row(align=True)
                        for item in automatcap_settings.remove_list:
                            op = row.operator("material.remove_from_list", text=item, emboss=False)
                            op.matcap = item
                            op = row.operator("material.show_matcap", text="", emboss=False, icon='RESTRICT_VIEW_OFF')
                            op.show_matcap = item
                            row = box.row(align=True)
                            
                        
