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

import bpy, os, platform, math
from bpy.props import *
from bpy.types import   Operator

from .props import main_canvas_data, get_addon_preferences
from .utils import *

MASK_MESSAGE = "Name the mask, please..."
CURVE_MESSAGE = "Name the curve, please..."

#######################
#       Classes       #
#######################
#-------------------------------------------------------CHANGE TO GLSL VIEW MODE
class GLSLViewMode(Operator):
    bl_description = "GLSL Mode"
    bl_idname = "ez_draw.glsl"
    bl_label = "GLSL View Mode"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        A = context.scene.viewmode_toggle
        return not A

    def execute(self, context):
        context.scene.game_settings.material_mode = 'GLSL'
        A = context.scene.viewmode_toggle

        context.scene.viewmode_toggle = False if A else True
        
        return {'FINISHED'}



#-----------------------------------------------CHANGE TO MULTITEXTURE VIEW MODE
class MTViewMode(Operator):
    bl_description = "Multitexture Mode"
    bl_idname = "ez_draw.multitexture"
    bl_label = "Multi-Texture View Mode - Single Texture View"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        A = context.scene.viewmode_toggle
        return A

    def execute(self, context):
        context.scene.game_settings.material_mode = 'MULTITEXTURE'
        A = context.scene.viewmode_toggle

        context.scene.viewmode_toggle = False if A else False
        
        return {'FINISHED'}



#---------------------------------------------------------------LOAD MAIN CANVAS
class ImageLoad(Operator):
    bl_description = "Load the Main Canvas to Paint"
    bl_idname = "ez_draw.image_load"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        OBJ = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        filePATH = self.filepath
        fileName = os.path.split(filePATH)[-1]
        fileDIR = os.path.dirname(filePATH) 
        #os.path.realpath
        #Init
        scene.ezdraw.clear()
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.ez_draw.image_to_canvas(\
                        files=[{"name":fileName,"name":fileName}],
                        directory=fileDIR,
                        filter_image=True,
                        filter_movie=True,
                        use_transparency=True)
        data = context.active_object.data
        select_mat = data.materials[0].texture_slots[0].texture.image.size[:]

        main_canvas = scene.ezdraw.add()
        main_canvas.filename = fileName
        main_canvas.path = fileDIR
        main_canvas.dimX = select_mat[0]
        main_canvas.dimY = select_mat[1]
        scene.maincanvas_is_empty = False

        for main_canvas in scene.ezdraw:
            print(main_canvas.filename)
            print(main_canvas.path)
            print(str(main_canvas.dimX))
            print(str(main_canvas.dimY))

        #set the cursor snap on object faces
        userpref = context.user_preferences
        userpref.view.use_mouse_depth_cursor = True
        return {'FINISHED'}


#-------------------------------------------------------------------RELOAD IMAGE
class ImageReload(Operator):
    """Reload Image Last Saved State"""
    bl_description = "Reload selected slot's image"
    bl_idname = "ez_draw.reload_saved_state"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        A = obj is not None
        if A:
            B = obj.type == 'MESH'
            return B

    def execute(self, context):
        original_type = context.area.type
        context.area.type = 'IMAGE_EDITOR'
        
        obdat =  context.active_object.data
        ima = obdat.materials[0].texture_slots[0].texture.image
        context.space_data.image = ima
        bpy.ops.image.reload()                 #return image to last saved state
        
        context.area.type = original_type
        return {'FINISHED'}

#---------------------------------------------------------------------IMAGE SAVE
class SaveImage(Operator):
    """Overwrite Image to Disk"""
    bl_description = ""
    bl_idname = "ez_draw.save_current"
    bl_label = "Save Image Current"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        A = obj is not None
        if A:
            B = obj.type == 'MESH'
            return B

    def execute(self, context):
        obj =  context.active_object
        #save the original state
        original_type = context.area.type
        
        context.area.type = 'IMAGE_EDITOR'
        ima = obj.data.materials[0].texture_slots[0].texture.image
        context.space_data.image = ima
        bpy.ops.image.save_as()                                         #save as
        
        #reinstall the original state
        context.area.type = original_type
        return {'FINISHED'}


#---------------------------------------------------------------------IMAGE SAVE
class SaveIncremImage(Operator):
    """Save Incremential Images - MUST SAVE SESSION FILE FIRST"""
    bl_description = ""
    bl_idname = "ez_draw.save_increm"
    bl_label = "Save incremential Image Current"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        A = obj is not None
        if A:
            B = obj.type == 'MESH'
            return B

    def execute(self, context):
        scene =context.scene
        main_canvas = main_canvas_data(self, context)
        
        if main_canvas[0] != '':                    #if main canvas isn't erased
            for obj in scene.objects:
                if obj.name == main_canvas[0] :         #if mainCanvas Mat exist
                    scene.objects.active = obj
                    break
        else:
            return {'FINISHED'}
        
        #init
        obj = context.active_object
        original_type = context.area.type
        context.area.type = 'IMAGE_EDITOR'
        """
        ~/.config/blender/Brushes/13_Tâche_de_café/Cafeina (1).png
        /media/patrinux/Autre/VISTA/Patrick/Pictures/1_CAPTURES
        
        realpath corrige the path à la racine!
        /home/patrinux/.config/blender/Brushes/13_Tâche_de_café/Cafeina (1).png
        /media/patrinux/Autre/VISTA/Patrick/Pictures/1_CAPTURES
        """
        #verify the brushname
        _tempName = [main_canvas[0] + '_001' + main_canvas[1]]
        _Dir = os.path.realpath(main_canvas[2])
        l = os.listdir(_Dir)
        brushesName = [ f for f in l if os.path.isfile(os.path.join(_Dir,f)) ]
        brushesName = sorted(brushesName)

        i = 1
        for x in _tempName:
            for ob in brushesName:
                if ob == _tempName[-1]:
                    i += 1
                    _tempName = _tempName + [main_canvas[0] + '_' + \
                                    '{:03d}'.format(i) + main_canvas[1]]

        #return image to last saved state
        filepath = os.path.join(_Dir,_tempName[-1])
        ima = obj.data.materials[0].texture_slots[0].texture.image
        context.space_data.image = ima
        bpy.ops.image.save_as(filepath = filepath,
                                check_existing=False,
                                relative_path=True)

        context.area.type = original_type
        return {'FINISHED'}


#-------------------------------------------------------------------CREATE BRUSH
class BrushMakerScene(Operator):
    """Create Brush Scene"""
    bl_description = ""
    bl_idname = "ez_draw.create_brush_scene"
    bl_label = "Create Scene for Image Brush Maker"
    bl_options = {'REGISTER', 'UNDO'}
    
    scene_name = bpy.props.StringProperty(name="Scene Name", default="Brush")
    
    @classmethod
    def poll(self, context):
        for sc in bpy.data.scenes:
            if sc.name == self.scene_name:
                return False
        return context.area.type=='VIEW_3D'

    def execute(self, context):
        for sc in bpy.data.scenes:
            if sc.name == self.scene_name:
                return {'FINISHED'}
        bpy.ops.scene.new(type='NEW')           #add new scene & name it 'Brush'
        context.scene.name = self.scene_name

        #add lamp and move up 4 units in z
        bpy.ops.object.lamp_add(
                    type = 'POINT',
                    radius = 1,
                    view_align = False,
                    location = (0, 0, 4)
                    )

        #add camera to center and move up 4 units in Z
        bpy.ops.object.camera_add(
                    view_align=False,
                    enter_editmode=False,
                    location=(0, 0, 4),
                    rotation=(0, 0, 0)
                    )

        context.object.name="Tex Camera"                 #rename selected camera

        #change scene size to 1K
        _RenderScene = context.scene.render
        _RenderScene.resolution_x=1024
        _RenderScene.resolution_y=1024
        _RenderScene.resolution_percentage = 100

        #save scene size as preset
        bpy.ops.render.preset_add(name = "1K Texture")

        #change to camera view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.copy()
                override['area'] = area
                bpy.ops.view3d.viewnumpad(override, type = 'CAMERA')
                break             # this will break the loop after the first ran
        return {'FINISHED'}


#-------------------------------------------------------------FRONT OF CCW15 ROT
class FrontOfCCW(Operator):
    """front of face CCW15 rotate"""
    bl_description = ""
    bl_idname = "ez_draw.frontof_ccw"
    bl_label = "Front Of CCW15 rotation"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.mode == 'PAINT_TEXTURE'
            B = obj.type == 'MESH'
            return A and B

    def execute(self, context):
        #init
        paint = bpy.ops.paint
        addon_prefs = get_addon_preferences()
        CustomAngle = math.radians(addon_prefs.customAngle)

        paint.texture_paint_toggle()                      #return in object mode
        bpy.ops.transform.rotate(value=-CustomAngle,
                                constraint_orientation='NORMAL')
        paint.texture_paint_toggle()                       #return in paint mode
        return {'FINISHED'}


#-----------------------------------------------------------------FRONT OF PAINT
class FrontOfPaint(Operator):
    """fast front of face view paint"""
    bl_description = ""
    bl_idname = "ez_draw.frontof_paint"
    bl_label = "Front Of Paint"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.mode == 'PAINT_TEXTURE'
            B = obj.type == 'MESH'
            return A and B

    def execute(self, context):
        #init
        paint = bpy.ops.paint
        object = bpy.ops.object
        contextObj = context.object

        context.space_data.viewport_shade = 'TEXTURED'             #texture draw
        paint.texture_paint_toggle()
        object.editmode_toggle()
        bpy.ops.view3d.viewnumpad(type='TOP', align_active=True)
        object.editmode_toggle()
        paint.texture_paint_toggle()
        contextObj.data.use_paint_mask = True
        return {'FINISHED'}


#--------------------------------------------------------------FRONT OF CW15 ROT
class FrontOfCW(Operator):
    """fast front of face CW15 rotate"""
    bl_description = ""
    bl_idname = "ez_draw.frontof_cw"
    bl_label = "Front Of CW15 rotation"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.mode == 'PAINT_TEXTURE'
            B = obj.type == 'MESH'
            return A and B

    def execute(self, context):
        #init
        paint = bpy.ops.paint
        addon_prefs = get_addon_preferences()
        CustomAngle = math.radians(addon_prefs.customAngle)

        paint.texture_paint_toggle()                      #return in object mode
        bpy.ops.transform.rotate(value=+CustomAngle,
                            constraint_orientation='NORMAL')
        paint.texture_paint_toggle()                       #return in paint mode
        return {'FINISHED'}


#---------------------------------------------------------------CAMERAVIEW PAINT
class CameraviewPaint(Operator):
    """Create a front-of camera in painting mode"""
    bl_description = ""
    bl_idname = "ez_draw.cameraview_paint"
    bl_label = "Cameraview Paint"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        scene = context.scene
        #Init
        obj =  context.active_object
        empty = scene.maincanvas_is_empty
        main_canvas = main_canvas_data(self, context)
    
        if empty or main_canvas[0] == '':                        #if no main canvas!
            return False
    
        if obj is None:                                        #If no active object!
            return False
        
        return obj.name == main_canvas[0]

    def execute(self, context):
        scene = context.scene
        #init
        main_canvas = main_canvas_data(self, context)
        
        if main_canvas[0] != '' and scene.camera_is_setup == False: 
            _camName = "Camera_" + main_canvas[0]
            for obj in scene.objects:
                if obj.name == main_canvas[0] :
                    scene.objects.active = obj
                    break
        else:
            scene.camera_is_setup = False
            return {'FINISHED'}

        obj = context.active_object
        context.space_data.viewport_shade = 'TEXTURED'      #texture draw option
        context.object.active_material.use_shadeless = True    #shadeless option

        for cam  in bpy.data.objects:
            if cam.name == _camName:
                prefix = 'Already found a camera for this image : '
                bpy.ops.error.message('INVOKE_DEFAULT',
                                    message =  prefix + _camName,
                                    confirm ="error.ok0" )
                return {'FINISHED'}

        bpy.ops.view3d.snap_cursor_to_center()        #Cursor to center of world
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        #add camera
        bpy.ops.object.camera_add(view_align=False,\
                        enter_editmode=False,\
                        location=(0, 0, 0),\
                        rotation=(0, 0, 0),\
                        layers=(True, False, False, False, False,\
                                False, False, False, False, False,\
                                False, False, False, False, False,\
                                False, False, False, False, False))

        context.scene.render.resolution_percentage = 100             #ratio full
        context.object.name = _camName                                  #name it
        bpy.ops.view3d.object_as_camera()                 #switch to camera view

        context.object.data.type = 'ORTHO'                     #ortho view 4 cam
        context.object.data.dof_object= obj

        #move cam up in Z by 1 unit
        bpy.ops.transform.translate(value=(0, 0, 1),
                    constraint_axis=(False, False, True),
                    constraint_orientation='GLOBAL',
                    mirror=False,
                    proportional='DISABLED',
                    proportional_edit_falloff='SMOOTH',
                    proportional_size=1)

        #resolution
        rnd = scene.render
        rndx = rnd.resolution_x = main_canvas[3]
        rndy = rnd.resolution_y = main_canvas[4]
        print(rndx)
        print(rndy)
        #orthoscale
        orthoscale =  (rndx / rndy) if (rndx >= rndy) else 1
        context.object.data.ortho_scale = orthoscale
        scene.camera_is_setup = True  #Camera is setup & movement are authorized

        bpy.ops.object.select_all(action='TOGGLE')
        bpy.ops.object.select_all(action='DESELECT')             #init Selection

        #select canvas
        obj.select = True
        context.scene.objects.active = obj
        bpy.ops.paint.texture_paint_toggle()
        scene.game_settings.material_mode = 'GLSL'
        context.space_data.lock_camera = False
        return {'FINISHED'}


#-----------------------------------------------------------------BORDER CROP ON
class BorderCrop(Operator):
    """Turn on Border Crop in Render Settings"""
    bl_description = "Border Crop ON"
    bl_idname = "ez_draw.border_crop"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        rs = context.scene.render
        rs.use_border = True
        rs.use_crop_to_border = True
        return {'FINISHED'}


#----------------------------------------------------------------BORDER CROP OFF
class BorderUnCrop(Operator):
    """Turn off Border Crop in Render Settings"""
    bl_description = "Border Crop OFF"
    bl_idname = "ez_draw.border_uncrop"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        rs = context.scene.render
        rs.use_border = False
        rs.use_crop_to_border = False
        return {'FINISHED'}


#-------------------------------------------------------------BORDER CROP TOGGLE
class BorderCropToggle(Operator):
    """Set Border Crop in Render Settings"""
    bl_description = "Border Crop On/Off TOGGLE"
    bl_idname = "ez_draw.border_toggle"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        return poll_apt(self, context)

    def execute(self, context):
        scene = context.scene
        rs = context.scene.render

        if not(scene.prefs_are_locked):
            if rs.use_border and rs.use_crop_to_border:
                bpy.ops.ez_draw.border_uncrop()
                scene.bordercrop_is_activated = False
            else:
                bpy.ops.ez_draw.border_crop()
                scene.bordercrop_is_activated = True
        return {'FINISHED'}



#------------------------------------------------------------------CAMERA GUIDES
class CamGuides(Operator):
    """Turn on Camera Guides"""
    bl_description = "Camera Guides On/Off Toggle"
    bl_idname = "ez_draw.guides_toggle"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        return poll_apt(self, context)

    def execute(self, context):
        scene = context.scene
        _bool03 = scene.prefs_are_locked
        main_canvas = main_canvas_data(self, context)
        
        if main_canvas[0] != '':                    #if main canvas isn't erased
            _camName = "Camera_" + main_canvas[0]
        else:
            return {'FINISHED'}

        for cam in bpy.data.objects :
            if cam.name == _camName:
                if not(_bool03):
                    if not(scene.guides_are_activated):      #True= if no guides
                        cam.data.show_guide = {'CENTER', 'THIRDS', 'CENTER_DIAGONAL'}
                        scene.guides_are_activated = True
                    else:
                        cam.data.show_guide = set()           #False=> if guides
                        scene.guides_are_activated = False

        return {'FINISHED'}


#------------------------------------------------------------PREFS TOOGLE BUTTON
class PrefsLockToggle(Operator):
    """Lock bordercrop & guides preferences in viewport"""
    bl_description = "Prefs lock On/Off TOGGLE"
    bl_idname = "ez_draw.prefs_lock_toggle"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        return poll_apt(self, context)

    def execute(self, context):
        addon_prefs = get_addon_preferences()
        scene = context.scene
        A = scene.prefs_are_locked
        bordercrop_is_activated = scene.bordercrop_is_activated
        guides_are_activated = scene.guides_are_activated
        main_canvas = main_canvas_data(self, context)

        if main_canvas[0] != '':                    #if main canvas isn't erased
            _camName = "Camera_" + main_canvas[0]
        else:
            return {'FINISHED'}


        if addon_prefs.bordercrop:
            bpy.ops.ez_draw.border_crop()
        else:
            bpy.ops.ez_draw.border_uncrop()

        for cam in bpy.data.objects :
            if cam.name == _camName:
                if not(guides_are_activated) and addon_prefs.guides:
                    cam.data.show_guide = {'CENTER', 'THIRDS', 'CENTER_DIAGONAL'}
                    scene.guides_are_activated = True
                else:
                    cam.data.show_guide = set()          #False = guides visible
                    scene.guides_are_activated = False
                    
                break

        scene.prefs_are_locked = False if A else True
        return {'FINISHED'}


#----------------------------------------------------GPENCIL TO MASK IN ONE STEP
class TraceSelection(Operator):
    """Mesh mask from gpencil lines"""
    bl_idname = "ez_draw.trace_selection"
    bl_label = "Make Mesh Mask from Gpencil's drawing"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.mode == 'PAINT_TEXTURE'
            B = obj.type == 'MESH'
            C = False
            GP = bpy.data.grease_pencil
            for lay0 in GP:
                if lay0.name == 'GPencil':
                    if GP['GPencil'].layers.find('GP_Layer')!= -1:
                        C = True
                        break
                break
            return A and B and C

    mask_name = StringProperty(name="Mask name")

    def invoke(self, context, event):
        global MASK_MESSAGE
        self.mask_name = MASK_MESSAGE
        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):
        scene = context.scene
        tool_settings = scene.tool_settings

        objOPS = bpy.ops.object
        gpencilOPS = bpy.ops.gpencil
        paintOPS = bpy.ops.paint
        meshOPS = bpy.ops.mesh
        cvOPS = bpy.ops.curve
        main_canvas = main_canvas_data(self, context)
        
        #----------------------------------------------INIT MAIN CANVAS
        if main_canvas[0] != '':      #if main canvas isn't erased
            for obj in scene.objects:
                if obj.name == main_canvas[0] :      #if mainCanvas Mat exist
                    scene.objects.active = obj
                    break
        else:
            return {'FINISHED'}
        _mkName = self.mask_name

        #----------------------------------------------CONVERT TO CURVE
        obj =  context.active_object             #save the main Canvas
        objRz = obj.rotation_euler[2]

        gpencilOPS.convert(type='CURVE', use_timing_data=True)
        gpencilOPS.data_unlink()
        paintOPS.texture_paint_toggle()          #return object mode
        lrs = []
        for cvP in bpy.data.objects:
            if cvP.name.find('GP_Layer') != -1:
                if cvP.type == "CURVE":
                    lrs.append(cvP)
        cv = lrs[-1]                             #select 'GP_Layer'curve

        scene.objects.active = cv                #active the curve
        cv.name = "msk_"+ _mkName                #name the curve here

        objOPS.editmode_toggle()                 #return in edit mode
        cvOPS.cyclic_toggle()                    #invert normals
        cv.data.dimensions = '2D'                #transform line to face
        objOPS.editmode_toggle()                 #return in Object mode

        #----------------------------------------DUPLICAT-PARENT 2x curves
        context.space_data.layers[19] = True     #layer20 temporary visible
        obj.select = False
        cv.select = True
        objOPS.duplicate_move()
        cvDupli = context.object
        cvDupli.name = 'cvs_' +  _mkName
        #parent curveDupli to Canvas
        cvDupli.select = True
        scene.objects.active = obj                              #select the Canvas
        objOPS.parent_set(type='OBJECT', keep_transform=False)  #parent Curve to Canvas
        objOPS.move_to_layer(layers=(False, False, False, False,\
                                False, False, False, False, False,\
                                False, False, False, False, False,\
                                False, False, False, False, False,\
                                True))           #move to layer20
        context.space_data.layers[19] = False    #layer20 stay invisible
        cvDupli.select = False
        #parent curve to Canvas
        cv.select = True
        scene.objects.active = obj               #select the Canvas
        objOPS.parent_set(type='OBJECT', keep_transform=False)#parent curve to Canvas


        #------------------------------------------------------MESH MASK UV
        scene.objects.active = cv
        objOPS.convert(target='MESH')            #convert to mesh

        scene.objects.active = obj               #select the canvas
        #init rotation
        bpy.ops.transform.rotate(value=-objRz,
                                 axis=(0, 0, 1),
                                 constraint_axis=(False, False, True),
                                 constraint_orientation='GLOBAL')

        scene.objects.active = cv                #select the Mask
        objOPS.editmode_toggle()                 #return in edit mode
        meshOPS.select_all(action='TOGGLE')      #select points
        meshOPS.dissolve_faces()                 #dissolve faces
        meshOPS.normals_make_consistent(inside=False)#Normals ouside
        bpy.ops.uv.project_from_view(camera_bounds=True,
                                    correct_aspect=False,
                                    scale_to_bounds=False)#uv cam unwrap
        for mat in bpy.data.materials:           #Material and texture
            if mat.name == main_canvas[0] :          #if mainCanvas Mat exist
                cv.data.materials.append(mat)    #add main canvas mat
                paintOPS.add_texture_paint_slot(type='DIFFUSE_COLOR',
                                            name=cv.name,
                                            width=main_canvas[3],
                                            height=main_canvas[4],
                                            color=(1, 1, 1, 0),
                                            alpha=True,
                                            generated_type='BLANK',
                                            float=False)
                break                            #add a texture
        objOPS.editmode_toggle()                 #return in object mode

        scene.objects.active = obj               #select the Canvas
        #return to rotation state
        bpy.ops.transform.rotate(value=objRz,
                                 axis=(0, 0, 1),
                                 constraint_axis=(False, False, True),
                                 constraint_orientation='GLOBAL')

        #----------------------------------------------------------------OPTIONS
        scene.objects.active = cv                            #return on the mask
        if context.mode != 'PAINT_TEXTURE':
            paintOPS.texture_paint_toggle()                #return in paint mode
        context.object.data.use_paint_mask = True
        tool_settings.image_paint.use_occlude = False
        tool_settings.image_paint.use_backface_culling = False
        tool_settings.image_paint.use_normal_falloff = False
        tool_settings.image_paint.seam_bleed = 0

        return {'FINISHED'}



#-----------------------------------------------------------CURVE BEZIER TO POLY
class CurvePoly2d(Operator):
    """Curve added and made poly 2d Macro"""
    bl_description = "Create 2D Poly Vector Mask"
    bl_idname = "ez_draw.curve_2dpoly"
    bl_label = "Create 2D Bezier Vector Mask"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        A = poll_apt(self, context)
        B = context.mode == 'PAINT_TEXTURE'
        return A and B

    curve_name = StringProperty(name="Curve name")

    def invoke(self, context, event):
        global CURVE_MESSAGE
        self.curve_name = CURVE_MESSAGE
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object                      #selected canvas object
        objRz = math.degrees(obj.rotation_euler[2])
        #Operators
        objOPS = bpy.ops.object
        cvOPS = bpy.ops.curve
        paintOPS = bpy.ops.paint

        paintOPS.texture_paint_toggle()                      #return object mode
        bpy.ops.view3d.snap_cursor_to_center()                #center the cursor
        cvOPS.primitive_bezier_curve_add(rotation=(0, 0, objRz),
                                layers=(True, False, False, False,
                                 False, False, False, False, False,
                                 False, False, False, False, False,
                                 False, False, False, False, False,
                                 False))                              #add curve
        cv = context.object                                 #save original curve

        objOPS.editmode_toggle()                              #toggle curve edit
        cvOPS.spline_type_set(type= 'POLY')               #change to poly spline
        cv.data.dimensions = '2D'                                  #change to 2d
        cvOPS.delete(type='VERT')                                #delete vertice
        objOPS.editmode_toggle()                         #return in  object mode

        context.scene.objects.active = obj                    #select mainCanvas
        objOPS.parent_set(type='OBJECT',
                          xmirror=False,
                          keep_transform=False)           #parent Mask to canvas

        #Name the curve with "+ Mask.xxx" or "+ Mask"(no mask)
        context.scene.objects.active = cv                   #return on the curve
        _cvName = self.curve_name
        cv.name = "cvs_" + _cvName                                      #name it

        objOPS.editmode_toggle()                              #toggle curve edit
        cvOPS.vertex_add()                                 #first: add a vertice
        cvOPS.handle_type_set(type='VECTOR')
        context.space_data.show_manipulator = True
        return {'FINISHED'}


#---------------------------------------------------------CLOSE, MESH AND UNWRAP
class CloseCurveUnwrap(Operator):
    """Close the curve, set to mesh and unwrap"""
    bl_description = "Close the curve, set to mesh and unwrap"
    bl_idname = "ez_draw.curve_unwrap"
    bl_label = ""
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None and obj.name is not None:
            A = obj.type == 'CURVE'
            B = obj.mode == 'EDIT'
            C = obj.name.find('cvs')!=-1
            return A and B and C
        return False


    def execute(self, context):
        scene = context.scene
        tool_settings = scene.tool_settings
        cv = context.active_object                             #the vector curve
        _cvName = cv.name[4:]                                 #type "cvs_xxxxxx"
        obj = cv.parent                                         #the main canvas
        objRz = obj.rotation_euler[2]                     #if mainCanvas rotated

        #Operators
        cvOPS = bpy.ops.curve
        objOPS = bpy.ops.object
        meshOPS = bpy.ops.mesh
        paintOPS = bpy.ops.paint
        main_canvas = main_canvas_data(self, context)

        #-------------------------------------------------------------------INIT 
        if main_canvas[0] == '':                       #if main canvas is erased
            return {'FINISHED'}

        #------------------------------------------------------------------CURVE
        cvOPS.select_all(action='TOGGLE')                        #Init selection
        cvOPS.select_all(action='TOGGLE')                         #select points
        cvOPS.cyclic_toggle()                        #close spline 'create faces
        cv.data.dimensions = '2D'                              #change the space
        objOPS.editmode_toggle()                          #return to object mode

        #---------------------------------------------DUPLICAT-PARENTt 2x curves
        obj.select = False
        cv.select = True
        if cv.layers[0]==False:
            objOPS.move_to_layer(layers=(True, False, False, False,
                                    False, False, False, False, False,
                                    False, False, False, False, False,
                                    False, False, False, False, False,
                                    False))                      #move to layer1
        objOPS.duplicate_move()
        cvDupli = context.object

        #parent curveDupli to Canvas
        cv.select = False
        cvDupli.select = True
        scene.objects.active = obj                            #select the Canvas
        objOPS.parent_set(type='OBJECT',
                            keep_transform=True)         #parent Curve to Canvas
        objOPS.move_to_layer(layers=(False, False, False, False,
                                False, False, False, False, False,
                                False, False, False, False, False,
                                False, False, False, False, False,
                                True))                          #move to layer20
        context.space_data.layers[19] = False                 #layer20 invisible
        cvDupli.select = False
        #parent curve to Canvas
        cv.select = True
        scene.objects.active = obj                            #select the Canvas
        objOPS.parent_set(type='OBJECT',
                            xmirror=False,
                            keep_transform=True)         #parent curve to Canvas

        #--------------------------------------------------        NEW MESH MASK
        scene.objects.active = cv
        objOPS.convert(target='MESH')                           #convert to mesh
        mk = context.object                          #overwrite cv with new mask
        mk.name = "msk_" + _cvName                    #name mask with curve name
        scene.objects.active = obj
        #init rotation
        bpy.ops.transform.rotate(value=-objRz,
                                 axis=(0, 0, 1),
                                 constraint_orientation='GLOBAL')

        scene.objects.active = mk
        objOPS.editmode_toggle()                              #mask in edit mode
        meshOPS.select_all(action='TOGGLE')                          #select all
        bpy.ops.mesh.edge_face_add()
        meshOPS.normals_make_consistent(inside=False)           #Normals outside
        bpy.ops.uv.project_from_view(camera_bounds=True,
                                    correct_aspect=False,
                                    scale_to_bounds=False)        #uv cam unwrap

        for mat in bpy.data.materials:
            if mat.name == main_canvas[0] :             #if mainCanvas Mat exist
                cv.data.materials.append(mat)               #add main canvas mat
                paintOPS.add_texture_paint_slot(type='DIFFUSE_COLOR',
                                            name=mk.name,
                                            width= main_canvas[3],
                                            height= main_canvas[4],
                                            color=(1, 1, 1, 0),
                                            alpha=True,
                                            generated_type='BLANK',
                                            float=False)
                break
        objOPS.editmode_toggle()                          #return in object mode

        scene.objects.active = obj                       #Select the  maincanvas
        #return to rotation state
        bpy.ops.transform.rotate(value=objRz,
                                 axis=(0, 0, 1),
                                 constraint_orientation='GLOBAL')

        #------------------------------------------------------          OPTIONS
        cvDupli.name = "cvs_" + _cvName

        scene.objects.active = mk
        if context.mode != 'PAINT_TEXTURE':
            paintOPS.texture_paint_toggle()                #return in Paint mode
        context.object.data.use_paint_mask = True
        tool_settings.image_paint.use_occlude = False
        tool_settings.image_paint.use_backface_culling = False
        tool_settings.image_paint.use_normal_falloff = False
        tool_settings.image_paint.seam_bleed = 0
        return {'FINISHED'}


#-------------------------------------------Invert all mesh mask
class CurvePolyInvert(Operator):
    """Invert Mesh Mask in Object mode only"""
    bl_idname = "ez_draw.inverted_mask"
    bl_description = "Invert Mesh Mask in Object mode only"
    bl_label = "Inverted mesh Mask"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None and obj.name is not None:
            A = obj.type == 'CURVE'
            B = obj.mode == 'EDIT'
            C = obj.name.find('cvs')!=-1
            return A and B and C
        return False

    def execute(self, context):
        scene = context.scene
        tool_settings = scene.tool_settings
        #Operators
        objOPS = bpy.ops.object
        meshOPS = bpy.ops.mesh
        paintOPS = bpy.ops.paint
        main_canvas = main_canvas_data(self, context)

        #----------------------------------------------------               INIT
        if main_canvas[0] == '':                           #the canvas is erased
            return {'FINISHED'}

        #---------------------------------------------------          INIT CURVE
        cv = context.active_object                            #save active curve
        _cvName = cv.name[4:]                             #Find the genuine name
        mainCanv = cv.parent                                      #Select canvas
        objRz = mainCanv.rotation_euler[2]                #if mainCanvas rotated

        #---------------------------------------------------         DUPLICATION
        objOPS.editmode_toggle()                          #return in object mode
        objOPS.duplicate_move()                             #duplicate the curve
        cvTemp = context.active_object                              #save cvTemp
        cvTemp.select = False                                   #deselect cvTemp

        cv.select = False                              #deselect the 'cvs' curve
        mainCanv.select = True
        scene.objects.active = mainCanv                  #active the main Canvas
        if mainCanv.mode == 'TEXTURE_PAINT':
            paintOPS.texture_paint_toggle()                  #return object mode
        objOPS.duplicate_move()                       #duplicate the main canvas
        objOPS.convert(target='CURVE')                  #convert active in curve
        canvTemp = context.active_object                          #save canvTemp

        canvTemp.select = True                          #select the canvas curve
        cvTemp.select = True
        scene.objects.active = cvTemp                         #active the cvTemp
        objOPS.join()                                          #join both curves
        objOPS.convert(target='MESH')                    #convert active in mesh
        objInv = context.active_object               #save the new Inverted Mask
        objOPS.move_to_layer(layers=(True, False, False, False,
                                False, False, False, False, False,
                                False, False, False, False, False,
                                False, False, False, False, False,
                                False))           #move to layer0

        #---------------------------------------------------          UV PROJECT
        objInv.select = True                           #select the inverted mask
        scene.objects.active = mainCanv                  #active the main Canvas
        objOPS.parent_set(type='OBJECT',
                          xmirror=False,
                          keep_transform=True)  #parent: Inverted mask to Canvas

        scene.objects.active = mainCanv                 #select again the Canvas
        bpy.ops.transform.rotate(value=-objRz,
                                 axis=(0, 0, 1),
                                 constraint_orientation='GLOBAL')

        scene.objects.active = objInv                  #Active the inverted mask
        objInv.name = "inv_" + _cvName                   #name the Inverted Mask
        objInv.location[2] = 0.01                   #Raise the Z level inv. mask
        objOPS.editmode_toggle()                                #go in edit mode
        bpy.ops.mesh.select_all(action='TOGGLE')             #select all vertice
        meshOPS.normals_make_consistent(inside=False)           #Normals outside
        bpy.ops.uv.project_from_view(camera_bounds=True,
                                    correct_aspect=False,
                                    scale_to_bounds=True)         #uv cam unwrap

        for mat in bpy.data.materials:
            if mat.name == main_canvas[0] :             #if mainCanvas Mat exist
                objInv.data.materials.append(mat)            #add mainCanvas mat
                paintOPS.add_texture_paint_slot(type='DIFFUSE_COLOR',
                                            name=objInv.name,
                                            width= main_canvas[3],
                                            height= main_canvas[4],
                                            color=(1, 1, 1, 0),
                                            alpha=True,
                                            generated_type='BLANK',
                                            float=False)
                break
        objOPS.editmode_toggle()                             #return object mode
        #return to rotation state
        scene.objects.active = mainCanv                       #select the Canvas
        bpy.ops.transform.rotate(value=objRz,
                                 axis=(0, 0, 1),
                                 constraint_orientation='GLOBAL')

        #--------------------------------------------------              OPTIONS
        scene.objects.active = objInv                  #active the Inverted Mask
        if context.mode != 'PAINT_TEXTURE':
            paintOPS.texture_paint_toggle()                #return in Paint mode
        context.object.data.use_paint_mask = True
        tool_settings.image_paint.use_occlude = False
        tool_settings.image_paint.use_backface_culling = False
        tool_settings.image_paint.use_normal_falloff = False
        tool_settings.image_paint.seam_bleed = 0
        return {'FINISHED'}


class SetSymmetryOrigin(Operator):
    """Set Symmetry Origin"""
    bl_idname = "ez_draw.set_symmetry_origin"
    bl_label = "Set Symmetry Origin"
    bl_description = "Move the symetry origin!"

    @classmethod
    def poll(self, context):
        A = poll_apt(self, context)
        B = context.mode == 'PAINT_TEXTURE'
        return A and B

    def execute(self, context):
        paintOPS = bpy.ops.paint
        
        paintOPS.texture_paint_toggle()                   #return in object mode
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        paintOPS.texture_paint_toggle()                    #return in paint mode
        
        return {'FINISHED'}


class ResetOrigin(Operator):
    """"Reset Canvas Origin"""
    bl_idname = "ez_draw.reset_origin"
    bl_label = ""
    bl_description = "Reset the canvas origin!"

    @classmethod
    def poll(self, context):
        A = poll_apt(self, context)
        B = context.mode == 'PAINT_TEXTURE'
        return A and B

    def execute(self, context):
        paintOPS = bpy.ops.paint
        
        paintOPS.texture_paint_toggle()                   #return in object mode
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        paintOPS.texture_paint_toggle()                    #return in paint mode
        
        return {'FINISHED'}


#--------------------------------------------------           flip  horiz. macro
class CanvasHoriz(Operator):
    """Canvas Flip Horizontal Macro"""
    bl_idname = "ez_draw.canvas_horizontal"
    bl_label = "Canvas horiz"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        bpy.ops.paint.texture_paint_toggle()                 #toggle Object mode
        # Horizontal mirror
        bpy.ops.transform.mirror(constraint_axis=(True, False, False))
        bpy.ops.paint.texture_paint_toggle()                  #return Paint mode
        
        return {'FINISHED'}


    #--------------------------------------------------      flip vertical macro
class CanvasVertical(Operator):
    """Canvas Flip Vertical Macro"""
    bl_idname = "ez_draw.canvas_vertical"
    bl_label = "Canvas Vertical"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        bpy.ops.paint.texture_paint_toggle()                 #toggle Object mode
        # Vertical mirror
        bpy.ops.transform.mirror(constraint_axis=(False, True, False))
        bpy.ops.paint.texture_paint_toggle()                  #toggle Paint mode
        
        return {'FINISHED'}


#-------------------------------------------------ccw15
class RotateCanvasCCW15(Operator):
    """Image Rotate CounterClockwise 15 Macro"""
    bl_description = "Rotate from prefs. custom angle, default=15°."
    bl_idname = "ez_draw.rotate_ccw_15"
    bl_label = "Canvas Rotate CounterClockwise 15°"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        scene = context.scene
        addon_prefs = get_addon_preferences()
        
        guides_are_activated =  scene.guides_are_activated
        CustomAngle = math.radians(addon_prefs.customAngle)
        _bool01 = scene.canvas_in_frame
        _bool02 = scene.ezdraw_bool02
        _bool03 = scene.prefs_are_locked
        _bool04 = scene.locking_are_desactived

        #init
        obj = context.active_object
        _obName = obj.name
        _camName = "Camera_" + _obName

        if guides_are_activated:                                  #remove guides
            if scene.prefs_are_locked:                             #prefs locked
                scene.prefs_are_locked = False             #desactivate the lock
                scene.locking_are_desactived = True            #prefs_was_locked
            bpy.ops.ez_draw.guides_toggle()
            scene.ezdraw_bool02 = True                      #rotation sans guide

        #toggle texture mode/object mode
        bpy.ops.paint.texture_paint_toggle()

        #rotate canvas 15 degrees left
        bpy.ops.transform.rotate(value=CustomAngle,
                        axis=(0, 0, 1),
                        constraint_axis=(False, False, True))

        if _bool01:                                      #option Frame contraint
            bpy.ops.view3d.camera_to_view_selected()

        for cam  in bpy.data.objects:
            if cam.name == _camName:
                cam.select = True
                context.scene.objects.active = cam


        bpy.ops.object.select_all(action='DESELECT')
        ob = bpy.data.objects[_obName]
        ob.select = True
        context.scene.objects.active = ob

        #toggle texture mode / object mode
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}


#-------------------------------------------------cw15
class RotateCanvasCW15(Operator):
    """Image Rotate Clockwise 15 Macro"""
    bl_description = "Rotate from prefs. custom angle, default=15°."
    bl_idname = "ez_draw.rotate_cw_15"
    bl_label = "Canvas Rotate Clockwise 15°"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        scene = context.scene
        addon_prefs = get_addon_preferences()
        
        guides_are_activated =  scene.guides_are_activated
        CustomAngle = math.radians(addon_prefs.customAngle)
        _bool01 = context.scene.canvas_in_frame
        _bool02 = context.scene.ezdraw_bool02

        #init
        obj = context.active_object
        _obName = obj.name
        _camName = "Camera_" + _obName

        if guides_are_activated:                                  #remove guides
            if scene.prefs_are_locked:                             #prefs locked
                scene.prefs_are_locked = False             #desactivate the lock
                scene.locking_are_desactived = True            #prefs_was_locked
            bpy.ops.ez_draw.guides_toggle()
            scene.ezdraw_bool02 = True                      #rotation sans guide

        #toggle texture mode / object mode
        bpy.ops.paint.texture_paint_toggle()

        #rotate canvas 15 degrees left
        bpy.ops.transform.rotate(value=-(CustomAngle),
                                axis=(0, 0, 1),
                                constraint_axis=(False, False, True))

        if _bool01:                                      #option Frame contraint
            bpy.ops.view3d.camera_to_view_selected()

        for cam  in bpy.data.objects:
            if cam.name == _camName:
                cam.select = True
                context.scene.objects.active = cam

        bpy.ops.object.select_all(action='DESELECT')
        ob = bpy.data.objects[_obName]
        ob.select = True
        context.scene.objects.active = ob

        #toggle texture mode/object mode
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}


#-------------------------------------------------ccw 90
class RotateCanvasCCW(Operator):
    """Image Rotate CounterClockwise 90 Macro"""
    bl_idname = "ez_draw.rotate_ccw_90"
    bl_label = "Canvas Rotate CounterClockwise 90"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        _bool01 = context.scene.canvas_in_frame
        obj = context.active_object
        
        _obName = obj.name
        _camName = "Camera_" + _obName

        select_mat = obj.data.materials[0].texture_slots[0].\
                                            texture.image.size[:]
        if select_mat[0] >= select_mat[1]:
            camRatio = select_mat[0]/select_mat[1]
        else:
            camRatio = select_mat[1]/select_mat[0]
        #(988, 761) X select_mat[0] Y select_mat[1]

        #resolution
        rnd = context.scene.render
        if rnd.resolution_x==select_mat[0]:
            rnd.resolution_x= select_mat[1]
            rnd.resolution_y= select_mat[0]
        elif rnd.resolution_x==select_mat[1]:
            rnd.resolution_x= select_mat[0]
            rnd.resolution_y= select_mat[1]

        #toggle texture mode / object mode
        bpy.ops.paint.texture_paint_toggle()

        #rotate canvas 90 degrees left
        bpy.ops.transform.rotate(value=1.5708,
                                axis=(0, 0, 1),
                                constraint_axis=(False, False, True),
                                constraint_orientation='GLOBAL',
                                mirror=False,
                                proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=1)
        if _bool01:
            bpy.ops.view3d.camera_to_view_selected()

        #Init Selection
        bpy.ops.object.select_all(action='TOGGLE')
        bpy.ops.object.select_all(action='DESELECT')

        #select plane
        ob = bpy.data.objects[_obName]
        ob.select = True
        context.scene.objects.active = ob

        #toggle texture mode / object mode
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}


#-------------------------------------------------cw 90
class RotateCanvasCW(Operator):
    """Image Rotate Clockwise 90 Macro"""
    bl_idname = "ez_draw.rotate_cw_90"
    bl_label = "Canvas Rotate Clockwise 90"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        obj = context.active_object
        _obName = obj.name
        _camName = "Camera_" + _obName
        _bool01 = context.scene.canvas_in_frame

        select_mat = obj.data.materials[0].texture_slots[0].\
                                            texture.image.size[:]

        if select_mat[0] >= select_mat[1]:
            camRatio = select_mat[0]/select_mat[1]
        else:
            camRatio = select_mat[1]/select_mat[0]

        #resolution
        rnd = context.scene.render
        if rnd.resolution_x==select_mat[0]:
            rnd.resolution_x= select_mat[1]
            rnd.resolution_y= select_mat[0]
        elif rnd.resolution_x==select_mat[1]:
            rnd.resolution_x= select_mat[0]
            rnd.resolution_y= select_mat[1]

        #toggle texture mode / object mode
        bpy.ops.paint.texture_paint_toggle()

        #rotate canvas 90 degrees left
        bpy.ops.transform.rotate(value=-1.5708,
                    axis=(0, 0, 1),
                    constraint_axis=(False, False, True),
                    constraint_orientation='GLOBAL',
                    mirror=False,
                    proportional='DISABLED',
                    proportional_edit_falloff='SMOOTH',
                    proportional_size=1)

        if _bool01 == True:
            bpy.ops.view3d.camera_to_view_selected()

        #Init Selection
        bpy.ops.object.select_all(action='TOGGLE')
        bpy.ops.object.select_all(action='DESELECT')

        #select plane
        ob = bpy.data.objects[_obName]
        ob.select = True
        context.scene.objects.active = ob

        #toggle texture mode / object mode
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}


#-------------------------------------------------          image rotation reset
class CanvasResetrot(Operator):
    """Canvas Rotation Reset Macro"""
    bl_idname = "ez_draw.canvas_resetrot"
    bl_label = "Canvas Reset Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        scene = context.scene
        #init
        tool_settings = scene.tool_settings
        _bool2 = context.scene.ezdraw_bool02
        main_canvas = main_canvas_data(self, context)

        if main_canvas[0] != '':                    #if main canvas isn't erased
            for obj in scene.objects:
                if obj.name == main_canvas[0] :         #if mainCanvas Mat exist
                    _camName = 'Camera_' + main_canvas[0]
                    scene.objects.active = obj
                    break
        else:
            return {'FINISHED'}

        #changing
        obj = context.active_object
        if main_canvas[3] >= main_canvas[4]:
            camRatio = main_canvas[3]/main_canvas[4]
        else:
            camRatio = 1

        #resolution
        rnd = context.scene.render
        rnd.resolution_x= main_canvas[3]
        rnd.resolution_y= main_canvas[4]

        #reset canvas rotation
        bpy.ops.object.rotation_clear()
        bpy.ops.view3d.camera_to_view_selected()

        for cam  in bpy.data.objects:
            if cam.name == _camName:
                cam.select = True
                scene.objects.active = cam
        context.object.data.ortho_scale = camRatio

        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj

        if _bool2:                                                  #if rotation
            bpy.ops.ez_draw.guides_toggle()                          #add guides
            scene.ezdraw_bool02 = False                 #init the rotation state

        if scene.locking_are_desactived:                       #prefs_was_locked
            bpy.ops.ez_draw.prefs_lock_toggle()                  #lock the prefs
            scene.locking_are_desactived = False         #init the locking state
        return {'FINISHED'}

######################################################## EXPERIMENTAL OPERATIONs
class SculptDuplicate(Operator):
    """Duplicate Selected Image Plane, Single User for Eraser Paint"""
    bl_idname = "ez_draw.sculpt_duplicate"
    bl_label = "Sculpt Liquid Duplicate"
    bl_options = { 'REGISTER', 'UNDO' }
    
    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = poll_apt(self, context)
            return A and B

    def execute(self, context):
        scene = context.scene

        bpy.ops.paint.texture_paint_toggle()
        bpy.ops.object.duplicate_move(
                    OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, \
                    TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":\
                    (False, False, False), "constraint_orientation":'GLOBAL', \
                    "mirror":False, "proportional":'DISABLED', \
                    "proportional_edit_falloff":'SMOOTH', "proportional_size":1,\
                    "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0),\
                    "snap_align":False, "snap_normal":(0, 0, 0), \
                    "gpencil_strokes":False, "texture_space":False, \
                    "remove_on_cancel":False, "release_confirm":False})
        bpy.ops.transform.translate(value=(0, 0, 0.1), \
                                    constraint_axis=(False, False, True), \
                                    constraint_orientation='GLOBAL', 
                                    mirror=False, \
                                    proportional='DISABLED', 
                                    proportional_edit_falloff='SMOOTH', \
                                    proportional_size=1)
        context.object.active_material.use_shadeless = True
        context.object.active_material.use_transparency = True
        context.object.active_material.transparency_method = 'Z_TRANSPARENCY'
        bpy.ops.view3d.localview()
        bpy.ops.paint.texture_paint_toggle()

        #make ERASER brush or use exisitng
        try:
            context.tool_settings.image_paint.brush = bpy.data.brushes["Eraser"]
            pass
        except:
            context.tool_settings.image_paint.brush = bpy.data.brushes["TexDraw"]
            bpy.ops.brush.add()
            bpy.data.brushes["TexDraw.001"].name="Eraser"
            context.scene.tool_settings.unified_paint_settings.use_pressure_size = False
            bpy.data.brushes["Eraser"].use_pressure_strength = False
            bpy.data.brushes["Eraser"].blend = 'ERASE_ALPHA'

        #make individual
        sel = bpy.context.selected_objects
        for ob in sel:
            mat = ob.active_material
            if mat:
                ob.active_material = mat.copy()

                for ts in mat.texture_slots:
                    try:
                        ts.texture = ts.texture.copy()

                        if ts.texture.image:
                            ts.texture.image = ts.texture.image.copy()
                    except:
                        pass

        return {'FINISHED'}


class SculptLiquid(Operator):
    """Convert to Subdivided Plane & Sculpt Liquid"""
    bl_idname = "ez_draw.sculpt_liquid"
    bl_label = "Sculpt like Liquid"
    bl_options = { 'REGISTER', 'UNDO' }
    
    @classmethod
    def poll(self, context):
        obj =  context.active_object
        main_canvas = main_canvas_data(self, context)
         
        if obj is not None:
            A = context.active_object.type == 'MESH'
            B = context.active_object.name == main_canvas[0]+ '.001'
            return A and B

    def execute(self, context):
        scene = context.scene

        bpy.ops.paint.texture_paint_toggle()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=100, smoothness=0)
        bpy.ops.mesh.subdivide(number_cuts=2, smoothness=0)
        bpy.ops.sculpt.sculptmode_toggle()
        bpy.ops.paint.brush_select(paint_mode='SCULPT', sculpt_tool='GRAB')
        scene.tool_settings.sculpt.use_symmetry_x = False
        bpy.ops.view3d.localview()

        return {'FINISHED'}


class ReprojectMask(Operator):
    """Reproject Mask"""
    bl_idname = "ez_draw.reproject_mask"
    bl_label = "Reproject Mask by View"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.editmode_toggle()                    #toggle edit mode
        bpy.ops.uv.project_from_view(camera_bounds=True, \
                                     correct_aspect=False, \
                                     scale_to_bounds=False) #project from view
        bpy.ops.object.editmode_toggle()                    #toggle back from edit mode
        #in obj mode, convert to mesh for correction on Artist Panel Vector Masks/Gpencil Masks
        bpy.ops.object.convert(target='MESH')               
        bpy.ops.paint.texture_paint_toggle()                #toggle texpaint
        
        return {'FINISHED'}


class SolidfyDifference(Operator):
    """Solidify and Difference Mask"""
    bl_idname = "ez_draw.solidfy_difference"
    bl_label = "Add Solidy and Difference Bool"
    bl_options = { 'REGISTER','UNDO' }

    def execute(self, context):
        scene = context.scene
        #init
        sel = context.selected_objects
        act = context.scene.objects.active

        for obj in sel:
            scene.objects.active = obj                   #set active to selected
            
            bpy.ops.object.editmode_toggle()
            #to get a clean single face for paint projection
            bpy.ops.mesh.dissolve_faces()  
            bpy.ops.object.editmode_toggle()

            bpy.ops.object.modifier_add(type='SOLIDIFY')  #set soldifiy for bool
            #thicker than active
            context.object.modifiers["Solidify"].thickness = 0.3
            #attempt to only move bool brush up in Z
            bpy.ops.transform.translate(value=(0, 0, 0.01), \
                        constraint_axis=(False, False, True), \
                        constraint_orientation='GLOBAL', \
                        mirror=False, proportional='DISABLED', \
                        proportional_edit_falloff='SMOOTH', \
                        proportional_size=1, \
                        release_confirm=True) 

            context.scene.objects.active = act                     #reset active
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.dissolve_faces()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.modifier_add(type='SOLIDIFY')    #soldify for boolean
            #to move active 0 in Z
            bpy.ops.transform.translate(value=(0, 0, 0), \
                    constraint_axis=(False, False, True), \
                    constraint_orientation='GLOBAL', mirror=False, \
                    proportional='DISABLED', \
                    proportional_edit_falloff='SMOOTH', \
                    proportional_size=1, release_confirm=True)  
            bpy.ops.btool.boolean_diff()                          #call booltool
            
            return {'FINISHED'}


class SolidfyUnion(Operator):
    """Solidify and Union Mask"""
    bl_idname = "ez_draw.solidfy_union"
    bl_label = "Add Solidy and Union Bool"
    bl_options = { 'REGISTER','UNDO' }

    def execute(self, context):
        scene = context.scene
        #init
        sel = context.selected_objects
        act = context.scene.objects.active

        for obj in sel:
            scene.objects.active = obj                             #set active to selected

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.dissolve_faces()                          #to get a single face for paint projection
            bpy.ops.object.editmode_toggle()

            bpy.ops.object.modifier_add(type='SOLIDIFY')           #set soldifiy for bool
            context.object.modifiers["Solidify"].thickness = 0.3   #thicker than active

            scene.objects.active = act                             #reset active

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.dissolve_faces()
            bpy.ops.object.editmode_toggle()

            bpy.ops.object.modifier_add(type='SOLIDIFY')           #basic soldify for boolean
            context.object.modifiers["Solidify"].thickness = 0.3   #thicker than active

            bpy.ops.btool.boolean_union()                          #call booltool

            return {'FINISHED'}


class RemoveMods(Operator):
    """Remove Modifiers"""
    bl_idname = "ez_draw.remove_modifiers"
    bl_label = "Remove modifiers"
    bl_options = { 'REGISTER','UNDO' }

    def execute(self, context):
        scene = context.scene
        #init
        obj = context.object
        old_mesh = obj.data             #get a reference to the current obj.data
        
        apply_modifiers = False                            #settings for to_mesh
        new_mesh = obj.to_mesh(scene, apply_modifiers, 'PREVIEW')
        obj.modifiers.clear()     #object will still have modifiers, remove them
        obj.data = new_mesh                     #assign the new mesh to obj.data
        bpy.data.meshes.remove(old_mesh)    #remove the old mesh from the .blend
        context.object.draw_type = 'TEXTURED'

        return {'FINISHED'}

#-------------------------------------------------------------------ALIGN LAYERS
class AlignLeft(Operator):
    """Left Align"""
    bl_idname = "object.align_left"
    bl_label = "Align Objects Left"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.align(align_mode='OPT_1', \
                             relative_to='OPT_4', align_axis={'X'})
        return {'FINISHED'}

class AlignCenter(Operator):
    """Center Align"""
    bl_idname = "object.align_center"
    bl_label = "Align Objects Center"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.align(align_mode='OPT_2', \
                             relative_to='OPT_4', align_axis={'X'})
        scene.mask_V_align = True
        return {'FINISHED'}

class AlignRight(Operator):
    """Center Align"""
    bl_idname = "object.align_right"
    bl_label = "Align Objects Right"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.align(align_mode='OPT_3', \
                             relative_to='OPT_4', align_axis={'X'})
        return {'FINISHED'}

class AlignTop(Operator):
    """Top Align"""
    bl_idname = "object.align_top"
    bl_label = "Align Objects Top"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.align(align_mode='OPT_3', \
                             relative_to='OPT_4', align_axis={'Y'})
        return {'FINISHED'}

class AlignHcenter(Operator):
    """Horizontal Center Align"""
    bl_idname = "object.align_hcenter"
    bl_label = "Align Objects Horizontal Center"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.align(align_mode='OPT_2', \
                             relative_to='OPT_4', align_axis={'Y'})
        scene.mask_V_align = False
        return {'FINISHED'}

class CenterAlignReset(Operator):
    """Center Alignment Reset"""
    bl_idname = "object.center_align_reset"
    bl_label = "Reset center alignment"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene
        mva =scene.mask_V_align
        
        scene.mask_V_align = False if mva else True
        return {'FINISHED'}

class AlignBottom(Operator):
    """Horizontal Bottom Align"""
    bl_idname = "object.align_bottom"
    bl_label = "Align Objects Horizontal Bottom"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.align(align_mode='OPT_1', \
                             relative_to='OPT_4', align_axis={'Y'})
        return {'FINISHED'}



###################################################### SCULPT & PAINT REFERENCE+
#Create reference scene
class RefMakerScene(Operator):
    """Create Reference Scene"""
    bl_description = "Create Scene for Composing Reference Slides"
    bl_idname = "object.create_reference_scene"
    bl_label = "Create Scene for Image Reference"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        for sc in bpy.data.scenes:
            if sc.name == "Refmaker":
                return False
        return context.area.type=='VIEW_3D'

    def execute(self, context):
        _name="Refmaker"
        for sc in bpy.data.scenes:
            if sc.name == _name:
                return {'FINISHED'}
        
        bpy.ops.scene.new(type='NEW')
        context.scene.name = _name
        #add camera to center and move up 4 units in Z
        bpy.ops.object.camera_add(view_align=False,
                                  enter_editmode=False,
                                  location=(0, 0, 4),
                                  rotation=(0, 0, 0)
                                  )

        context.object.name = _name + " Camera"          #rename selected camera

        #change scene size to HD
        _RenderScene = context.scene.render
        _RenderScene.resolution_x=1920
        _RenderScene.resolution_y=1080
        _RenderScene.resolution_percentage = 100

        #save scene size as preset
        bpy.ops.render.preset_add(name = _name)

        #change to camera view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.copy()
                override['area'] = area
                bpy.ops.view3d.viewnumpad(override, type = 'CAMERA')
                break
        
        return {'FINISHED'}

#sculpt the new duplicated canvas
class SculptView(Operator):
    """Sculpt View Reference Camera"""
    bl_idname = "object.sculpt_camera"
    bl_label = "Sculpt Camera"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.camera_add(view_align=False,
                                  enter_editmode=False,
                                  location=(0, -4, 0),
                                  rotation=(1.5708, 0, 0)
                                  )
        context.object.name = "Reference Cam"          #add camera to front view
        context.object.data.show_passepartout = False
        context.object.data.lens = 80

        #change to camera view
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.copy()
                override['area'] = area
                bpy.ops.view3d.viewnumpad(override, type = 'CAMERA')
                break
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080

        return {'FINISHED'}


class ToggleLock(Operator):
    """Lock Screen"""
    bl_idname = "object.lock_screen"
    bl_label = "Lock Screen Toggle"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        data = context.space_data
        A = data.lock_camera
        B = data.show_only_render
        
        if A and B:
            data.lock_camera = False
            data.show_only_render = False
        else:
            data.lock_camera = True
            data.show_only_render = True
        
        return {'FINISHED'}


class CustomFps(Operator):
    """Slow Play FPS"""
    bl_idname = "object.slow_play"
    bl_label = "Slow Play FPS Toggle"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        scene = context.scene
        F = scene.render.fps
        
        if F == 1:
            scene.render.fps = 30
            scene.render.fps_base = 1
        else:
            scene.render.fps = 1
            scene.render.fps_base = 12

        return {'FINISHED'}
