# -*- coding: utf8 -*-
# python
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

bl_info = {"name": "EZ_Draw",
           "author": "CDMJ, Spirou4D, proxe, Jason van Gumster (Fweeb)",
           "version": (2, 30),
           "blender": (2, 78, 0),
           "location": "Toolbar > Misc Tab > EZ Draw",
           "description": "2D Paint Tools for 3D view",
           "warning": "Run only in BI now",
           "wiki_url": "",
           "category": "Paint"}

if "bpy" in locals():
    import imp
    imp.reload(props)
    imp.reload(utils)
    imp.reload(ops)
    imp.reload(io_import_canvas)
    imp.reload(ui_ops)
    imp.reload(ui_user)
else:
    from . import props
    from . import utils
    from . import ops
    from . import io_import_canvas
    from . import ui_ops
    from . import ui_user

import bpy, os, platform, math, _cycles
from bpy.props import *
from bpy.types import   AddonPreferences,\
                        PropertyGroup,\
                        Menu,\
                        Panel,\
                        UIList,\
                        Operator

from .ui_user import *
PLATFORM = platform.system()
SEP = os.sep


def update_panel(self, context):
    #author: Thks mano-wii
    cat = context.user_preferences.addons[__name__].preferences.category
    try:
        bpy.utils.unregister_class(CanvasIncreasePanel)
        bpy.utils.unregister_class(ArtistPanel)
        bpy.utils.unregister_class(ArtistTips)
    except:
        pass
    CanvasIncreasePanel.bl_category = cat
    ArtistPanel.bl_category = cat
    ArtistTips.bl_category = cat

    bpy.utils.register_class(CanvasIncreasePanel)
    bpy.utils.register_class(ArtistPanel)
    bpy.utils.register_class(ArtistTips)

#-----------------------------------------------Preferences of add-on
class EasyDrawPrefs(AddonPreferences):
    """Creates the 3D view > TOOLS > Artist Paint Panel"""
    bl_idname = __name__

    enable_Tab_APP_01 = bpy.props.BoolProperty(name = "Defaults", \
                                               default=False)
    bordercrop = bpy.props.BoolProperty(name = "Bordercrop", \
                                        default=False)
    guides = bpy.props.BoolProperty(name="Guides", \
                                    default=False)
    customAngle = bpy.props.FloatProperty(name="Angle of rotation", \
                                          default=5.00, \
                                          min=1)
    category = bpy.props.StringProperty(name="Category", \
                                        description="Choose a name for the category of the panel", \
                                        default="EZ Draw", \
                                        update=update_panel)

    def check(context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enable_Tab_APP_01", icon="QUESTION")

        if self.enable_Tab_APP_01:
            row = layout.row()
            row.prop(self,"bordercrop")
            row.prop(self,"guides")
            row.prop(self, "customAngle")
            row = layout.row(align=True)
            row.label(text="Panel's location (category): ")
            row.prop(self, "category", text="")


def register():
    bpy.utils.register_class(EasyDrawPrefs)
    bpy.utils.register_module(__name__)
    update_panel(None, bpy.context)

def unregister():
    bpy.utils.unregister_class(EasyDrawPrefs)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
