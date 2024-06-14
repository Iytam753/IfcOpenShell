# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import blenderbim.tool as tool


def add_style(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material) -> ifcopenshell.entity_instance:
    element = ifc.run("style.add_style", name=style.get_name(obj))
    ifc.link(element, obj)
    if style.can_support_rendering_style(obj):
        attributes = style.get_surface_rendering_attributes(obj)
        ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleRendering", attributes=attributes)
    else:
        attributes = style.get_surface_shading_attributes(obj)
        ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleShading", attributes=attributes)

    material = ifc.get_entity(obj)
    if material:
        ifc.run("style.assign_material_style", material=material, style=element, context=style.get_context())
    return element


def add_external_style(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material, attributes: dict[str, Any]) -> None:
    element = style.get_style(obj)
    ifc.run(
        "style.add_surface_style", style=element, ifc_class="IfcExternallyDefinedSurfaceStyle", attributes=attributes
    )


# TODO: unused `style` argument?
def update_external_style(
    ifc: tool.Ifc,
    style: ifcopenshell.entity_instance,
    external_style: ifcopenshell.entity_instance,
    attributes: dict[str, Any],
) -> None:
    ifc.run("style.edit_surface_style", style=external_style, attributes=attributes)


def remove_style(
    ifc: tool.Ifc, style_tool: tool.Style, style: ifcopenshell.entity_instance
) -> None:
    obj = ifc.get_object(style)
    ifc.unlink(element=style)
    ifc.run("style.remove_style", style=style)
    style_tool.delete_object(obj)
    if style_tool.is_editing_styles():
        style_tool.import_presentation_styles(style_tool.get_active_style_type())


def update_style_colours(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material, verbose: bool = False) -> None:
    element = style.get_style(obj)

    if style.can_support_rendering_style(obj):
        rendering_style = style.get_surface_rendering_style(obj)
        texture_style = style.get_texture_style(obj)
        attributes = style.get_surface_rendering_attributes(obj, verbose)
        if rendering_style:
            ifc.run("style.edit_surface_style", style=rendering_style, attributes=attributes)
        else:
            ifc.run(
                "style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleRendering", attributes=attributes
            )

        # TODO: uvs?
        textures = ifc.run("style.add_surface_textures", material=obj)
        if not texture_style and textures:
            ifc.run(
                "style.add_surface_style",
                style=element,
                ifc_class="IfcSurfaceStyleWithTextures",
                attributes={"Textures": textures},
            )
        elif texture_style:
            # TODO: should we remove blender images and IFCIMAGETEXTURE here if they're not used by other objects?
            ifc.run("style.edit_surface_style", style=texture_style, attributes={"Textures": textures})
    else:
        shading_style = style.get_surface_shading_style(obj)
        attributes = style.get_surface_shading_attributes(obj)
        if shading_style:
            ifc.run("style.edit_surface_style", style=shading_style, attributes=attributes)
        else:
            ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleShading", attributes=attributes)

    style.record_shading(obj)


def update_style_textures(
    ifc: tool.Ifc, style: tool.Style, obj: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
) -> None:
    element = style.get_style(obj)

    uv_maps = style.get_uv_maps(representation)
    textures = ifc.run("style.add_surface_textures", material=obj, uv_maps=uv_maps)
    texture_style = style.get_surface_texture_style(obj)

    if textures:
        if texture_style:
            ifc.run("style.remove_surface_style", style=texture_style)
        ifc.run(
            "style.add_surface_style",
            style=element,
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": textures},
        )
    elif texture_style:
        ifc.run("style.remove_surface_style", style=texture_style)


def unlink_style(ifc: tool.Ifc, style: ifcopenshell.entity_instance) -> None:
    ifc.unlink(element=style)


def enable_editing_style(style: tool.Style, obj: bpy.types.Material) -> None:
    style.enable_editing(obj)
    style.import_surface_attributes(style.get_style(obj), obj)


def disable_editing_style(style: tool.Style, obj: bpy.types.Material) -> None:
    style.disable_editing(obj)


def edit_style(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material) -> None:
    attributes = style.export_surface_attributes(obj)
    ifc.run("style.edit_presentation_style", style=style.get_style(obj), attributes=attributes)
    style.disable_editing(obj)


def load_styles(style: tool.Style, style_type: str) -> None:
    style.import_presentation_styles(style_type)
    style.enable_editing_styles()


def disable_editing_styles(style: tool.Style) -> None:
    style.disable_editing_styles()


def select_by_style(style_tool: tool.Style, spatial: tool.Spatial, style: ifcopenshell.entity_instance) -> None:
    spatial.select_products(style_tool.get_elements_by_style(style))
