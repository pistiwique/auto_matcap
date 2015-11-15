'''
Copyright (C) 2015 Pistiwique

Created by Pistiwique

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Auto matcap",
    "author": "Pistiwique",
    "version": (0, 1, 5),
    "blender": (2, 75, 0),
    "description": "Setup matcap",
    "wiki_url": "https://www.youtube.com/watch?v=-uxy9irGr80",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=26&t=1064",
    "category": "Material"}
    
import bpy
from bpy.types import AddonPreferences
from . utils import register_matcap_pcoll, unregister_matcap_pcoll
from . ui import *
from . operators import AutoMatcapCollectionGroup

                           

class AutoMatcapPreferences(AddonPreferences):
    bl_idname = __name__
    matcaps_path = bpy.props.StringProperty(
            name="Your matcaps path",
            maxlen=1024,
            subtype='DIR_PATH') 
            
    def draw(self, context):
        layout = self.layout  
        
        split = layout.split(percentage=1)

        col = split.column()
        sub = col.column(align=True)
        sub.prop(self, "matcaps_path")
    
    
    
def register():
    bpy.utils.register_module(__name__)
    register_matcap_pcoll()
    bpy.types.VIEW3D_PT_view3d_shading.append(display_auto_matcap_panel)
    bpy.types.WindowManager.automatcap_settings = bpy.props.PointerProperty(type=AutoMatcapCollectionGroup)

def unregister():
    del bpy.types.WindowManager.automatcap_settings
    unregister_matcap_pcoll()
    bpy.types.VIEW3D_PT_view3d_shading.remove(display_auto_matcap_panel)
    bpy.utils.unregister_module(__name__)