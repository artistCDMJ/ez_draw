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

import bpy, platform
from bpy.props import *
from bpy.types import Operator

from .props import main_canvas_data, get_addon_preferences
from .utils import *

PLATFORM = platform.system()


##############################
#       OPS UI Class         #
##############################
#----------------------------------------------------------------DISPLAY MESSAGE
class MessageOperator(Operator):
    bl_idname = "error.message"
    bl_label = "Warning Message"

    message = StringProperty()
    confirm = StringProperty()
    
    def check(self, context):
        return True    
    
    def execute(self, context):
        scene = context.scene
        scene.maincanvas_is_deleted = False
        print('INIT')
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200, height=300)

    def draw(self, context):
        layout = self.layout
        
        layout.label("**** WARNING! ****")
        message = "   " + self.message
        line = int(round(float(len(message))/32)) + 1
        n=1
        while (n <= line):
            X = (n-1)*32
            Z = n*32
            content = message[X:Z]
            row = layout.row(align=True)
            row.label(content)
            n += 1
        else:
            print("Written warning!")
        layout.separator() #---------------------------Empty line
        row = layout.row(align=True)
        row.operator(self.confirm)

#----------------------------------------------THE OK BUTTON IN THE ERROR DIALOG
class OkOperator(Operator):
    bl_idname = "error.ok0"
    bl_label = "OK"

    def execute(self, context):
        print('Ok!')
        return {'FINISHED'}

#----------------------------------------------THE OK BUTTON IN THE ERROR DIALOG
class OkOperator(Operator):
    bl_idname = "error.ok1"
    bl_label = "OK"

    def execute(self, context):
        scene = context.scene                                              #init
        main_canvas = main_canvas_data(self, context)
        #if main canvas exist and camera is not setup
        if main_canvas[0] != '':
            for obj in scene.objects:
                if obj.name == main_canvas[0] :   #if mainCanvas Mat exist
                    scene.objects.active = obj
                    break
        else:
            scene.ezdraw.clear()
            return {'FINISHED'}

        obj = context.active_object                       #obj is the mainCanvas
        if obj.mode != 'OBJECT':
            bpy.ops.paint.texture_paint_toggle()          #return in object mode

        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        bpy.ops.object.delete(use_global=True)
        for cam  in bpy.data.objects:
            if cam.name == "Camera_" + main_canvas[0]:
                cam.select = True
                context.scene.objects.active = cam
                bpy.ops.object.delete(use_global=True)

        scene.camera_is_setup = False
        scene.ezdraw.clear()
        scene.maincanvas_is_empty = True
        message = 'The canvas: "' + main_canvas[0] + \
                    '" is  removed in memory and deleted with his hierarchy.'
        self.report({'INFO'}, message)

        return {'FINISHED'}
