# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api.root


class TestCreateEntity(test.bootstrap.IFC4):
    def test_creating_a_simple_entity_with_automatic_global_id(self):
        wall = ifcopenshell.api.root.create_entity(
            self.file, ifc_class="IfcRailing", predefined_type="HANDRAIL", name="Foo"
        )
        assert wall.is_a() == "IfcRailing"
        assert len(wall.GlobalId) == 22
        assert wall.Name == "Foo"
        assert wall.PredefinedType == "HANDRAIL"

    def test_handling_predefined_types(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcRailing", name="Foo")
        assert element.PredefinedType is None
        element = ifcopenshell.api.root.create_entity(
            self.file, ifc_class="IfcRailing", predefined_type="HANDRAIL", name="Foo"
        )
        assert element.PredefinedType == "HANDRAIL"
        element = ifcopenshell.api.root.create_entity(
            self.file, ifc_class="IfcRailing", predefined_type="Foobar", name="Foo"
        )
        assert element.PredefinedType == "USERDEFINED"
        assert element.ObjectType == "Foobar"
        element = ifcopenshell.api.root.create_entity(
            self.file, ifc_class="IfcWallType", predefined_type="Foobar", name="Foo"
        )
        assert element.PredefinedType == "USERDEFINED"
        assert element.ElementType == "Foobar"
        if self.file.schema != "IFC2X3":
            element = ifcopenshell.api.root.create_entity(
                self.file, ifc_class="IfcTaskType", predefined_type="Foobar", name="Foo"
            )
            assert element.PredefinedType == "USERDEFINED"
            assert element.ProcessType == "Foobar"

    def test_setting_default_values_for_validity(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="Foo")
        assert element.PredefinedType == "NOTDEFINED"
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoorStyle", name="Foo")
        assert element.OperationType == "NOTDEFINED"
        assert element.ConstructionType == "NOTDEFINED"
        assert element.ParameterTakesPrecedence == False
        assert element.Sizeable == False
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindowStyle", name="Foo")
        assert element.OperationType == "NOTDEFINED"
        assert element.ConstructionType == "NOTDEFINED"
        assert element.ParameterTakesPrecedence == False
        assert element.Sizeable == False
        if self.file.schema != "IFC2X3":
            element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoorType", name="Foo")
            assert element.OperationType == "NOTDEFINED"
            element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindowType", name="Foo")
            assert element.PartitioningType == "NOTDEFINED"
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFurnitureType", name="Foo")
        assert element.AssemblyPlace == "NOTDEFINED"


class TestCreateEntityIFC2X3(test.bootstrap.IFC2X3, TestCreateEntity):
    pass
