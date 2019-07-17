# -*- coding: utf8 -*-
#
# ##### BEGIN GPL LICENSE BLOCK #####
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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy, _cycles
from bpy.props import *
from bpy.types import Panel

from .props import main_canvas_data, get_addon_preferences
from .utils import *




######################################################################## PANEL 1
class UI_PT_CanvasIncreasePanel(Panel):
    """Increase Canvas Dimension"""
    bl_label = "EZ Draw - Increase Canvas"
    bl_idname = "UI_PT_CanvasIncreasePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Draw"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, cls):
        return bpy.context.scene.render.engine == 'BLENDER_RENDER'

    def draw(self, context):
        scene = context.scene
        render = context.scene.render

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        if scene.camera != None:
            #----------------------------
            row = col.row()
            row.prop(scene, "camera")
            row.operator("ez_draw.canvas_resetrot",
                                 text = "", icon = 'LOAD_FACTORY')
            cam = scene.camera
            #----------------------------
            row = col.row(align=True)
            row.prop(cam.data, "ortho_scale")
            #----------------------------
            row = col.row(align=True)
            row.prop(cam.data, "shift_x")
            row.prop(cam.data, "shift_y")
        else:
            col.label("The scene havn't a camera, please?")
        #----------------------------
        row = box.row(align=True)
        row1 = row.split()
        row1.label(text="Render Scale")
        row1.scale_x = 0.60
        row.prop(render, "resolution_percentage")


######################################################################## PANEL 2
class UI_PT_ArtistPanel(Panel):
    bl_label = "EZ Draw - 2D in a 3D View"
    bl_idnmae = "UI_PT_ArtistPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Draw"

    @classmethod
    def poll(self, cls):
        return bpy.context.scene.render.engine == 'BLENDER_RENDER'

    @staticmethod
    def draw_header(self, context):
        self.layout.prop(context.scene, 'ui_is_activated' , text= "")

    def draw(self, context):
        scene = context.scene
        rs = scene.render
        addon_prefs = get_addon_preferences()
        buttName_1 = str(addon_prefs.customAngle) +"°"
        buttName_2 = str(addon_prefs.customAngle) +"°"

        #layout.active
        layout = self.layout
        layout.active = layout.enabled = scene.ui_is_activated

        #change variables with prefs
        #------------------------------------------
        empty = scene.maincanvas_is_empty
        bordercrop_is_activated = scene.bordercrop_is_activated
        guides_are_activated =  scene.guides_are_activated
        PAL = scene.prefs_are_locked
        mask_V_align = scene.mask_V_align
        main_canvas = main_canvas_data(self, context)

        GAA = BIA = False
        if main_canvas[0] != '':                    #if main canvas isn't erased
            _camName = "Camera_" + main_canvas[0]
            for cam in bpy.data.objects:
                if cam.name == _camName:              #True = guides not visible
                    GAA = False if cam.data.show_guide == set() else True
            BIA = True if rs.use_border or rs.use_crop_to_border else False

        if PAL:
            BIA = addon_prefs.bordercrop
            GAA = addon_prefs.guides

        toolsettings = context.tool_settings
        ipaint = toolsettings.image_paint

        stencil_text = ""
        if context.active_object is not None :
            ob = context.active_object
            if ob.type == 'MESH' and ob.data.uv_texture_stencil is not None :
                stencil_text = ob.data.uv_texture_stencil.name

        #UI Design
        row = layout.row(align = True)
        box = row.box()
        col = box.column(align = True)
        row = col.row(align = True)
        row1 = row.split(align=True)
        row1.label(text="SAVING & RENDER")                          #IMAGE STATE
        row2 = row.split(align=True)

        if scene.game_settings.material_mode == 'GLSL':
            row2.operator("ez_draw.multitexture",
                          text='Shading', icon="RADIO")
        else:
            row2.operator("ez_draw.glsl",
                          text='Shading', icon="RENDERLAYERS")
        row2.scale_x = 0.40

        col.separator() #--------------------------------empty line

        row = col.row(align = True)
        row.operator("ez_draw.image_load",
                    text = "Import canvas", icon = 'IMAGE_COL')
        row.operator("ez_draw.reload_saved_state",
                                        icon = 'LOAD_FACTORY')

        row = col.row(align = True)                              #Camera buttons

        row1 = row.split(align=True)
        row1.operator("ez_draw.cameraview_paint",
                    text = "Set Camera",
                    icon = 'RENDER_REGION')

        row2 = row.split(align=True)
        row2.prop(context.space_data.region_3d, 'lock_rotation',\
                    text= "",\
                    icon = 'KEY_HLT')
        Icon = 'CLIPUV_DEHLT' if BIA else 'BORDER_RECT'
        row2.operator("ez_draw.border_toggle",
                    text = "",
                    icon = Icon)
        Icun = 'CLIPUV_DEHLT' if GAA else 'MOD_LATTICE'
        row2.operator("ez_draw.guides_toggle",
                    text = "",
                    icon = Icun)
        Ican = 'LOCKED' if PAL else 'UNLOCKED'
        row2.operator("ez_draw.prefs_lock_toggle",
                    text = "",
                    icon = Ican)

        if BIA:
            col.separator() #---------------------------Empty line
            row = col.row()
            row.label(text="Crop Adjust")
            row.prop(scene.render, "border_max_y", text="Y Max", slider=True)
            row.label(text="")
            #----------------------------
            row = col.row(align=True)
            row.prop(scene.render, "border_min_x", text="X Min", slider=True)
            row.prop(scene.render, "border_max_x", text="X Max", slider=True)
            #----------------------------
            row = col.row()
            row.label(text="")
            row.prop(scene.render, "border_min_y", text="Y Min", slider=True)
            row.label(text="")
            col.separator() #---------------------------Empty line

        row = col.row(align = True)
        row.operator("ez_draw.save_current",
                    text = "Save/Overwrite", icon = 'IMAGEFILE')
        row.operator("ez_draw.save_increm",
                    text = "Incremental Save", icon = 'SAVE_COPY')

        for A in (_cycles.get_device_types()):                       #If not CPU
            if A :
                col.operator("render.opengl", \
                             text = "Snapshot", icon = 'RENDER_STILL')
                break

        box = layout.box()                                                #MACRO
        col = box.column(align = True)
        col.label(text="SPECIAL SETUP MACROS")                           #?
        col.operator("ez_draw.create_brush_scene",
                text="Create Brush Maker Scene",
                icon='OUTLINER_OB_CAMERA')

        row = col.row(align = True)
        row1 = row.split(align=True)
        row1.operator("ez_draw.frontof_ccw",
                text="-"+buttName_1, icon = 'TRIA_LEFT')
        row1.scale_x = 0.40
        row2 = row.split(align=True)
        row2.operator("ez_draw.frontof_paint",
                text = "View Align 3D",
                icon = 'ERROR')
        row3 = row.split(align=True)
        row3.operator("ez_draw.frontof_cw",
                 text= "+"+buttName_2, icon = 'TRIA_RIGHT')
        row3.scale_x = 0.40

        col.separator() #---------------------------Empty line

        ########reference maker scene#########
        row = col.row(align = True)
        row1 = row.split(align=True)
        row1.label(text="Ref Tool")
        row1.scale_x = 0.50
        row2 = row.split(align=True)
        row2.operator("object.create_reference_scene", text = "Refmaker Scene", icon = 'OUTLINER_OB_LAMP')
        row3 = row.split(align=True)
        row3.operator("ez_draw.image_to_canvas", text="", icon='NODE_SEL')

        col.separator() #---------------------------Empty line

        ########sculpt camera and lock toggle#####
        row = col.row(align = True)
        row1 = row.split(align=True)
        row1.label(text="Sculpt/Paint View")
        row1.scale_x = 0.50
        row2 = row.split(align=True)
        row2.operator("object.sculpt_camera", text = "Sculpt Ref View", icon = 'RENDER_REGION')
        row2.scale_x = .50
        row3 = row.split(align=True)

        if context.space_data.lock_camera == True:
            row3.operator("object.lock_screen", text="", icon='LOCKED')
        if context.space_data.lock_camera == False:
            row3.operator("object.lock_screen", text="", icon='UNLOCKED')
        row4 = row.split(align=True)
        if context.scene.render.fps > 1:
            row4.operator("object.slow_play", text="", icon='CLIP')
        if context.scene.render.fps == 1:
            row4.operator("object.slow_play", text="", icon='CAMERA_DATA')

        col.separator() #---------------------------Empty line

        box = layout.box()
        col = box.column(align = True)
        col.label(text="CANVAS MASKS TOOLS")               #CANVAS MASKING TOOLS
        col.prop(ipaint, "use_stencil_layer", text="Stencil Mask")
        if ipaint.use_stencil_layer:
            col.menu("VIEW3D_MT_tools_projectpaint_stencil", text=stencil_text, translate=False)
            col.template_ID(ipaint, "stencil_image", open="image.open")
            col.operator("image.new", text="New stencil").gen_context = 'PAINT_STENCIL'
            row = col.row(align = True)
            row.prop(ipaint, "stencil_color", text="")
            row.prop(ipaint, "invert_stencil",
                        text="Invert the mask",
                        icon='IMAGE_ALPHA')

        col.separator() #---------------------------Empty line

        row = col.row(align = True)
        row.operator("ez_draw.sculpt_duplicate",
                     text = "New Dupli. Sculpt Mask",
                     icon = 'COPY_ID')
        row.operator("ez_draw.sculpt_liquid",
                     text = "Liquid Sculpt",
                     icon = 'MOD_WAVE')

        col.separator() #---------------------------Empty line

        col.operator("ez_draw.trace_selection",
                    text = "Mesh Mask from Gpencil",
                    icon = 'OUTLINER_OB_MESH')

        col.separator() #---------------------------Empty line

        col.operator("ez_draw.curve_2dpoly",
                    text = "Make Vector Contour",
                    icon = 'PARTICLE_POINT')

        row = col.row(align = True)
        row.operator("ez_draw.curve_unwrap",
                    text = "To Mesh Mask",
                    icon = 'OUTLINER_OB_MESH')
        row.operator("ez_draw.inverted_mask",
                    text = "To Inverted Mesh Mask",
                    icon = 'MOD_TRIANGULATE')

        col.separator() #---------------------------Empty line

        row = col.row(align = True)                         #BOOL MASK AND REUSE
        row1 = row.split(align=True)
        row1.label(text="Bool")
        row1.scale_x = 0.30
        row2 = row.split(align=True)
        row2.operator("ez_draw.solidfy_difference", text=" Difference", icon = 'ROTACTIVE')
        row2.operator("ez_draw.solidfy_union", text=" Union", icon = 'ROTATECOLLECTION')
        row2.scale_x = 1.00
        row.separator() #---------------------------Empty line
        row3 = row.split(align=True)
        row3.operator("ez_draw.reproject_mask",
                    text=" Reproject", icon = 'NODE_SEL')
        row3.scale_x = 1.10
        row4 = row.split(align=True)
        row4.operator("ez_draw.remove_modifiers", icon='RECOVER_LAST')

        col.separator() #---------------------------Empty line
        col.label("Masks Alignment")                                 #ALIGNEMENT
        row = col.row(align = True)                                     #TABLEAU

        row1 = row.split(align = True)                                 #Column 1
        row1.scale_x = 1.00
        col1 = row1.column(align = True)
        col1.label("")
        col1.operator("object.align_left",
                    text="Left", icon = 'TRIA_LEFT_BAR')
        col1.label("")


        row2 = row.split(align = True)                                 #column 2
        row2.scale_x = 1.00
        col2 = row2.column(align = True)
        col2.operator("object.align_top", text="Top", icon = 'TRIA_UP_BAR')
        if mask_V_align:
            col2.operator("object.align_hcenter",
                    text="Center V", icon = 'GRIP')
        else:
            col2.operator("object.align_center",
                    text="Center H", icon = 'PAUSE')
        col2.operator("object.align_bottom",
                    text="Bottom", icon = 'TRIA_DOWN_BAR')
        col2.operator("object.center_align_reset", icon='RECOVER_LAST')


        row3 = row.split(align = True)                                 #column 3
        row3.scale_x = 1.00
        col3 = row3.column(align = True)
        col3.label("")
        col3.operator("object.align_right",
                    text="Right", icon = 'TRIA_RIGHT_BAR')
        col3.label("")

        col.separator() #---------------------------Empty line

        box = layout.box()                              #CANVAS FRAME CONSTRAINT
        col = box.column(align = True)
        row = col.row(align=True)
        row.label(text="CANVAS MOVEMENT")
        row = col.row(align=True)
        row1 = row.split()
        row1.label(text="Mirror")
        row2 = row.split(align=True)
        row2.prop(ipaint, "use_symmetry_x", text=" Horizontal", toggle=True)
        row2.prop(ipaint, "use_symmetry_y", text=" Vertical", toggle=True)
        row2.scale_x = 1.50
        row.separator() #---------------------------Empty line
        row3 = row.split(align=True)
        row3.operator("ez_draw.set_symmetry_origin",
                    text=" New", icon='ERROR') #MUST BE SETUP AFTER.....ICONS PROBLEM WITH BLENDER2.79!!!!!
        row4 = row.split(align=True)
        row4.operator("ez_draw.reset_origin", icon='RECOVER_AUTO')

        col.separator() #---------------------------Empty line

        row = col.row(align = True)                                        #FLIP
        row.operator("ez_draw.canvas_horizontal",
                    text="Canvas Flip Horizontal",
                    icon='ARROW_LEFTRIGHT')
        row.operator("ez_draw.canvas_vertical",
                    text = "Canvas Flip Vertical",
                    icon = 'FILE_PARENT')


        row = col.row(align = True)                                    #ROTATION
        row.label(text="Rotation")
        row.prop(context.scene, "canvas_in_frame" ,
                                    text="Frame Constraint")
        row.enabled = poll_apt(self, context)
        row = col.row(align = True)

        row.operator("ez_draw.rotate_ccw_15",
                    text = "Rotate -" + buttName_1, icon = 'TRIA_LEFT')
        row.operator("ez_draw.rotate_cw_15",
                    text = "Rotate +" + buttName_2, icon = 'TRIA_RIGHT')

        row = col.row(align = True)
        row.operator("ez_draw.rotate_ccw_90",
                    text = "Rotate 90° CCW", icon = 'PREV_KEYFRAME')
        row.operator("ez_draw.rotate_cw_90",
                    text = "Rotate 90° CW", icon = 'NEXT_KEYFRAME')

        col.operator("ez_draw.canvas_resetrot",
                    text = "Reset Rotation", icon = 'CANCEL')


######################################################################## PANEL 3
class UI_PT_ArtistTips(Panel):
    bl_label = "EZ Tools Tips"
    bl_idname = "UI_PT_ArtistTips"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "EZ Draw"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, cls):
        return bpy.context.scene.render.engine == 'BLENDER_RENDER'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="EZ Draw______________")
        col.label(text="        Pie => F7")

        col.separator() #---------------------------Empty line

        col.label(text="EZ Paint______________")
        col.label(text="        Brush Popup => W")
        col.label(text="        Slots & VGroups Popup => Shift + W")
        col.label(text="        Paint Texture/Mask Popup => Alt + W")
        col.label(text-"        Image Editor Popup => Shift + Alt + W")

        col.separator() #---------------------------Empty line

        col.label(text="EZ Sculpt______________")
