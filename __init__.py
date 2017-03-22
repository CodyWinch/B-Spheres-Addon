#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>

bl_info = {
    "name": "B-Spheres",
    "version": (1, 0),
    "author": "Cody Winchester",
    "blender": (2, 78, 0),
    "description": "Base mesh creation",
    "location": "Create Tab in 3D View",
    "category": "Create"}

import bpy
import math
import mathutils
import bmesh
from bpy.props import *

class BSpherePanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_category = 'Create'
    bl_label = "B-Spheres"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    
    #Creates the properties under the toolbar
    object = bpy.types.Object
    scn = bpy.types.Scene
    
    object.BS_segment_end = BoolProperty(name = "Segment End Sphere", description = "", default = False)
    scn.BS_resolution = IntProperty(name = "Segment Resolution", description = "Amount of spheres for segment", default = 1, min = 1, max = 5)
    
    def draw(self, context):
        layout = self.layout
        aobj = context.active_object
        scn = context.scene
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.prop(scn, "BS_resolution")
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.operator("scene.bsphere_new_segment")
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.operator("scene.bsphere_extrude")
        
        if aobj == None or aobj.BS_segment_end == False:
            row.enabled = False
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.operator("scene.bsphere_to_metaballs")
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.operator("scene.bsphere_make_selectable")
        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.scale_y = 1.5
#        row.label(text = "CREATE REPOSER OBJECTS")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.prop(scn, "RP_seperation_dist")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.prop(aobj, "RP_remesh_level")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.prop(aobj, "RP_decimate_ratio")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.prop(scn, "RP_res_method", text="")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.scale_y = 1.5
#        row.operator("object.create_lowres_poser")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.scale_y = 1.5
#        row.label(text = "REPOSE SCULPT")
#            
#        row = layout.row()
#        row.prop_search(aobj, "RP_pose_ob", context.scene, "objects", text="Posed Sculpt Object")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.prop(aobj, "RP_limit_selected")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.prop(aobj, "RP_smooth_iterations")
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.label(icon = 'ERROR')
#        row.label(text = 'Adding a subsurf modifier to your poser object')
#        row.label(icon = 'ERROR')
#        
#        row = layout.row()
#        row.alignment = 'CENTER'
#        row.label(icon = 'ERROR')
#        row.label(text = 'improves results of the repose')
#        row.label(icon = 'ERROR')

class AddNewSegment(bpy.types.Operator):
    bl_idname = "scene.bsphere_new_segment"
    bl_label = "Add New B-Sphere Segment"
    
    def execute(self, context):
        data = bpy.data
        con = bpy.context
        scn = context.scene
        aobj = context.active_object
        
        
        if 'B-Sphere_Dark' not in data.materials:
            dark_mat = data.materials.new('B-Sphere_Dark')
            dark_mat.diffuse_color = (0.2, 0.2, 0.2)
            
        dark_mat = data.materials['B-Sphere_Dark']
        
        if 'B-Sphere_Light' not in data.materials:
            light_mat = data.materials.new('B-Sphere_Light')
            light_mat.diffuse_color = (0.5, 0.5, 0.5)
            
        light_mat = data.materials['B-Sphere_Light']
        
        found = False
        new_suffix = '.000'
        suffix = '.000'
        while found == False:
            for ob in data.objects:
                if ob.name.startswith('B-Sphere_Ctrl'):
                    end = ob.name[13:]
                    
                    if end == suffix:
                        num = int(ob.name[14:]) + 1
                        if len(str(num)) == 1:
                            new_suffix = '.00' + str(num)
                        elif len(str(num)) == 2:
                            new_suffix = '.0' + str(num)
                        else:
                            new_suffix = '.' + str(num)
                        
            if suffix != new_suffix:
                suffix = new_suffix
            else:
                found = True
        
        
        dist = 0.0
        for i in range((10*scn.BS_resolution) + 1):
            if i < 2:
                bs_name = 'B-Sphere_Ctrl' + suffix
            else:
                bs_name = 'B-Sphere'
            
            bpy.ops.mesh.primitive_uv_sphere_add(size=1, location=(0.0,0.0,0.0))
            ob = con.active_object
            ob.name = bs_name
            bpy.ops.object.material_slot_add()
            
            ob.location[2] -= dist
            
            bpy.ops.object.shade_smooth()
            
            if i == 0:
                first_ob = ob
                ob.material_slots[0].material = light_mat
                ob.BS_segment_end = True
            elif i == 1:
                last_ob = ob
                ob.material_slots[0].material = light_mat
                ob.location[2] -= 2.0
                dist += (0.2/scn.BS_resolution)
                ob.BS_segment_end = True
            else:
                ob.material_slots[0].material = dark_mat
                ob.constraints.new('COPY_LOCATION')
                ob.constraints.new('COPY_SCALE')
                ob.constraints[0].target = first_ob
                ob.constraints[1].target = first_ob
                ob.constraints.new('COPY_LOCATION')
                ob.constraints.new('COPY_SCALE')
                ob.constraints[2].target = last_ob
                ob.constraints[3].target = last_ob
                
                ob.constraints[0].influence = 1.0
                ob.constraints[1].influence = 1.0 - ((i-1) * (0.1/scn.BS_resolution))
                
                ob.constraints[2].influence = (i-1) * (0.1/scn.BS_resolution)
                ob.constraints[3].influence = (i-1) * (0.1/scn.BS_resolution)
                ob.constraints[3].use_offset = True
                
                dist += (0.2/scn.BS_resolution)
                ob.hide_select = True
        
        bpy.ops.object.select_all(action='DESELECT')
        last_ob.select = True
        scn.objects.active=last_ob
        
        return {'FINISHED'}

class ExtrudeBSphere(bpy.types.Operator):
    bl_idname = "scene.bsphere_extrude"
    bl_label = "Extrude B-Sphere Segment"
    
    def execute(self, context):
        data = bpy.data
        con = bpy.context
        scn = context.scene
        aobj = context.active_object
        
        if 'B-Sphere_Dark' not in data.materials:
            dark_mat = data.materials.new('B-Sphere_Dark')
            dark_mat.diffuse_color = (0.2, 0.2, 0.2)
            
        dark_mat = data.materials['B-Sphere_Dark']

        if 'B-Sphere_Light' not in data.materials:
            light_mat = data.materials.new('B-Sphere_Light')
            light_mat.diffuse_color = (0.5, 0.5, 0.5)
            
        light_mat = data.materials['B-Sphere_Light']

        first_ob = con.active_object


        found = False
        new_suffix = '.000'
        suffix = '.000'
        while found == False:
            for ob in data.objects:
                if ob.name.startswith('B-Sphere_Ctrl'):
                    end = ob.name[13:]
                    
                    if end == suffix:
                        num = int(ob.name[14:]) + 1
                        if len(str(num)) == 1:
                            new_suffix = '.00' + str(num)
                        elif len(str(num)) == 2:
                            new_suffix = '.0' + str(num)
                        else:
                            new_suffix = '.' + str(num)
                        
            if suffix != new_suffix:
                suffix = new_suffix
            else:
                found = True


        dist = 0.5
        for i in range(10*scn.BS_resolution):
            if i < 1:
                bs_name = 'B-Sphere_Ctrl' + suffix
            else:
                bs_name = 'B-Sphere'
            
            bpy.ops.mesh.primitive_uv_sphere_add(size=1, location=first_ob.location)
            ob = con.active_object
            ob.name = bs_name
            bpy.ops.object.material_slot_add()
            
            ob.location[2] -= dist
            
            bpy.ops.object.shade_smooth()
            
            if i == 0:
                last_ob = ob
                ob.material_slots[0].material = light_mat
                ob.location = first_ob.location
                ob.location[2] -= 2.0
                dist += (0.2/scn.BS_resolution)
                ob.BS_segment_end = True
            else:
                ob.material_slots[0].material = dark_mat
                ob.constraints.new('COPY_LOCATION')
                ob.constraints.new('COPY_SCALE')
                ob.constraints[0].target = first_ob
                ob.constraints[1].target = first_ob
                ob.constraints.new('COPY_LOCATION')
                ob.constraints.new('COPY_SCALE')
                ob.constraints[2].target = last_ob
                ob.constraints[3].target = last_ob
                
                ob.constraints[0].influence = 1.0
                ob.constraints[1].influence = 1.0 - ((i) * (0.1/scn.BS_resolution))
                
                ob.constraints[2].influence = (i) * (0.1/scn.BS_resolution)
                ob.constraints[3].influence = (i) * (0.1/scn.BS_resolution)
                ob.constraints[3].use_offset = True
                
                dist += (0.2/scn.BS_resolution)
                ob.hide_select = True

        bpy.ops.object.select_all(action='DESELECT')
        last_ob.select = True
        scn.objects.active=last_ob
        
        return {'FINISHED'}

class ConvertMetaballs(bpy.types.Operator):
    bl_idname = "scene.bsphere_to_metaballs"
    bl_label = "B-Spheres to Metaballs"
    
    def execute(self, context):
        data = bpy.data
        con = bpy.context
        scn = context.scene
        aobj = context.active_object
        
        bpy.ops.object.select_all(action = 'DESELECT')
        
        for ob in data.objects:
            if ob.name.startswith('B-Sphere'):
                mball_name = 'B-Sphere_MB'
                mball = data.metaballs.new(mball_name)
                mb_ob = data.objects.new('B-Sphere_MB', mball)
                scn.objects.link(mb_ob)
                
                mball.resolution = 0.2
                mball.render_resolution = 0.1
                
                ele = mball.elements.new()
                ele.co = (0.0,0.0,0.0)
                ele.radius = 2.0
                
                mb_ob.matrix_world = ob.matrix_world
                mb_ob.select = True
                scn.objects.active = mb_ob
        
        return {'FINISHED'}

class MakeSelectable(bpy.types.Operator):
    bl_idname = "scene.bsphere_make_selectable"
    bl_label = "Make B-Sphere Selectable"
    
    def execute(self, context):
        data = bpy.data
        con = bpy.context
        scn = context.scene
        aobj = context.active_object
        

        for ob in bpy.data.objects:
            if ob.name.startswith('B-Sphere'):
                ob.hide_select = False
        
        return {'FINISHED'}
    


def register():
    bpy.utils.register_class(AddNewSegment)
    bpy.utils.register_class(ExtrudeBSphere)
    bpy.utils.register_class(ConvertMetaballs)
    bpy.utils.register_class(MakeSelectable)
    bpy.utils.register_class(BSpherePanel)

def unregister():
    bpy.utils.unregister_class(AddNewSegment)
    bpy.utils.unregister_class(ExtrudeBSphere)
    bpy.utils.unregister_class(ConvertMetaballs)
    bpy.utils.unregister_class(MakeSelectable)
    bpy.utils.unregister_class(BSpherePanel)
    
if __name__ == "__main__":
    register()