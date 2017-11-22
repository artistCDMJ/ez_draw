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

import bpy, os, platform, math, _cycles
from bpy.props import *

from .props import main_canvas_data


########################
#      Functions       #
########################

def poll_apt(self, context):
    scene = context.scene
    #Init
    obj =  context.active_object
    empty = scene.maincanvas_is_empty
    main_canvas = main_canvas_data(self, context)

    if empty or main_canvas[0] == '':                        #if no main canvas!
        return False

    if obj is None:                                        #If no active object!
        return False
    
    if scene.camera_is_setup:                                #If camera is setup
        return obj.name == main_canvas[0]
    else:
        return False
