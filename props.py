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

import bpy
from bpy.props import *
from bpy.types import   PropertyGroup



########################
#      Properties      #
########################
def ezdraw_init(self, context):
    scene = context.scene
    #Init
    empty = scene.maincanvas_is_empty
    main_canvas = main_canvas_data(self, context)

    if main_canvas[0] != '':
        warning = 'Do you really want to remove "'+ main_canvas[0] + \
                '" from memory and delete all his hierarchy?'
        state = bpy.ops.error.message('INVOKE_DEFAULT',\
                                        message = warning,\
                                        confirm ="error.ok1" )
    else:
        scene.camera_is_setup = False
        scene.maincanvas_is_empty = True
        scene.ezdraw.clear()

#--------------------------------------------------------CREATE SCENE PROPERTIES
#bool property to activation of UI
bpy.types.Scene.ui_is_activated = \
                   bpy.props.BoolProperty(default=False, update = ezdraw_init)
#bool property to togle viewmode
bpy.types.Scene.viewmode_toggle = \
                            bpy.props.BoolProperty(default=True)
#bool property when the main canvas is empty
bpy.types.Scene.maincanvas_is_empty = \
                            bpy.props.BoolProperty(default=True)
#bool property when the camra is setup
bpy.types.Scene.camera_is_setup = \
                            bpy.props.BoolProperty(default=False)
#bool property when the bordercrop is activated
bpy.types.Scene.bordercrop_is_activated = \
                            bpy.props.BoolProperty(default=False)
#bool property when the guides are activated
bpy.types.Scene.guides_are_activated = \
                            bpy.props.BoolProperty(default=False)
#bool property to use with resetrotation
bpy.types.Scene.canvas_in_frame = \
                                bpy.props.BoolProperty(default=False)
#bool property of ?
bpy.types.Scene.ezdraw_bool02 = \
                                bpy.props.BoolProperty(default=False)
#bool property to cadenas addon's prefs
bpy.types.Scene.mask_V_align = \
                            bpy.props.BoolProperty(default=False)
#bool property to addon's prefs lock
bpy.types.Scene.prefs_are_locked = \
                                bpy.props.BoolProperty(default=True)
#bool property when the lockpad is activated
bpy.types.Scene.locking_are_desactived = \
                                bpy.props.BoolProperty(default=False)

#Precise Render Border Adjust Properties by Lapineige :D
#Minimum X
bpy.types.Scene.x_min_pixels = bpy.props.IntProperty(min=0)
#Maximum X
bpy.types.Scene.x_max_pixels = bpy.props.IntProperty(min=0)
#Minimum Y
bpy.types.Scene.y_min_pixels = bpy.props.IntProperty(min=0)
#Maximum Y
bpy.types.Scene.y_max_pixels = bpy.props.IntProperty(min=0)


##############################
#       Ops Props Class      #
##############################
def main_canvas_data(self, context):
    scene = context.scene
    #default datas
    name = ext = filepath = dimX = dimY = ''
    
    if scene.ezdraw is not None:                          #if main canvas isn't erased
        if len(scene.ezdraw) > 0:
            for main_canvas in scene.ezdraw:          #look main canvas name
                name : (main_canvas.filename)[:-4]    #find the name of the maincanvas
                ext : (main_canvas.filename)[-4:]
                filepath : main_canvas.path
                dimX : main_canvas.dimX
                dimY :  main_canvas.dimY

    return [name, ext, filepath, dimX, dimY]

#---------------------------------------------------------MAIN_CANVAS COLLECTION
class MainCanvas(PropertyGroup):
    filename = bpy.props.StringProperty(name="Canvas Filename", default="")
    path = bpy.props.StringProperty(name="Canvas Path", default='')
    dimX = bpy.props.IntProperty(name="Canvas DimX", default=0)
    dimY = bpy.props.IntProperty(name="Canvas DimY", default=0)
bpy.utils.register_class(MainCanvas)
#Create "ezdraw" scene-object
bpy.types.Scene.ezdraw = bpy.props.CollectionProperty(type=MainCanvas)

#------------------------------------------------------GET THE ADDON PREFERENCES
def get_addon_preferences():
    bl_idname = __package__
    #bpy.context.user_preferences.addons["notify_after_render"].preferences['sent_sms']=1
    #Par exemple:
    # addon_prefs = get_addon_preferences()
    # addon_prefs.url_smsservice
    return bpy.context.user_preferences.addons[__package__].preferences
