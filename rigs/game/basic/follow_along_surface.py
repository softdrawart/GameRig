import bpy
from rigify.base_rig import BaseRig, stage
from ..basic.super_copy import Rig as SuperCopyRig
from rigify.utils.naming import make_derived_name
from rigify.utils.widgets_basic import create_circle_widget

class Rig(SuperCopyRig):
    """A rig that creates a shrinkwrapped mechanism to slide across a specific masked area of a linked mesh."""

    class MchBones(BaseRig.MchBones):
        shrink: str

    bones: BaseRig.ToplevelBones[str, str, MchBones, str]

    def initialize(self):
        super().initialize()
        self.rig_parent_bone = self.get_bone(self.bones.org).parent.name
        self.target_mesh = None
        
        target_obj = self.params.target_object
        vgroup_name = self.params.vertex_group
        
        if target_obj:
            if vgroup_name:
                if vgroup_name in target_obj.vertex_groups:
                    self.target_mesh = self.create_helper_mesh(target_obj, vgroup_name)
                else:
                    self.raise_error(f"Vertex group '{vgroup_name}' not found on '{target_obj.name}'.")
            else:
                self.target_mesh = self.create_helper_mesh(target_obj, vgroup_name)
        else:
            self.raise_error("Target Object must be specified in rig parameters.")

    def create_helper_mesh(self, original_obj, vgroup_name):
        """Creates a linked duplicate, duplicates the required vertex group, and applies a Mask modifier."""
        mch_name = make_derived_name(self.bones.org, 'mch', '_shrink')
        vg_mask_name = f"surfaceDeform_mask_{mch_name}"
        if not original_obj:
            self.raise_error(f"No object is specified for {self.bones.org}")


        new_obj = original_obj.copy()
        self.generator.collection.objects.link(new_obj)
                
        new_obj.name = f"RIG_ShrinkTarget_{self.bones.org}"

        if vgroup_name:
            # 2. Handle Vertex Groups
            # Create a brand new vertex group to keep the original intact,
            # then copy the weights over vertex-by-vertex using the data API.
            if vgroup_name in new_obj.vertex_groups:
                old_vg = new_obj.vertex_groups[vgroup_name]
                new_vg = new_obj.vertex_groups.new(name=vg_mask_name)
                
                # Iterate through vertices and copy weights
                for v in new_obj.data.vertices:
                    try:
                        # .weight() raises a RuntimeError if the vertex isn't in the group
                        weight = old_vg.weight(v.index)
                        new_vg.add([v.index], weight, 'REPLACE')
                    except RuntimeError:
                        pass
            else:
                self.raise_error(f"Vertex group '{vgroup_name}' not found on duplicated object.")
            
            # 3. Add the Mask Modifier
            mask_mod = new_obj.modifiers.new(name="Mask", type='MASK')
            mask_mod.vertex_group = vg_mask_name
            mask_mod.show_in_editmode = True
            mask_mod.show_on_cage = True
            
        # Clean up object settings (Hide it from viewport and renders)
        new_obj.hide_viewport = True
        new_obj.hide_render = True
        new_obj.hide_select = True
        
        # Parent the helper mesh to the generated Rig armature to keep the scene clean
        new_obj.parent = self.generator.obj
        
        return new_obj

    @stage.generate_bones
    def make_mechanism_bones(self):
        # 1. Create the DEF bone
        def_name = make_derived_name(self.bones.org, 'def')
        self.bones.deform = self.copy_bone(self.bones.org, def_name)
        
        # 2. Create the MCH Shrinkwrap bone
        mch_name = make_derived_name(self.bones.org, 'mch', '_shrink')
        self.bones.mch.shrink = self.copy_bone(self.bones.org, mch_name)
        
    @stage.parent_bones
    def parent_bones_stage(self):
        # Parent both CTRL and MCH to the root/parent of this rig part
        self.set_bone_parent(self.bones.ctrl, self.rig_parent_bone)
        self.set_bone_parent(self.bones.mch.shrink, self.rig_parent_bone)
        self.set_bone_parent(self.bones.deform, self.rig_parent_bone)

    @stage.rig_bones
    def rig_bones_stage(self):
        # 1. MCH follows the CTRL bone
        self.make_constraint(self.bones.mch.shrink, 'COPY_TRANSFORMS', self.bones.ctrl)
        
        # 2. MCH Shrinkwraps to the generated helper mesh
        if self.target_mesh:
            sw_con = self.make_constraint(self.bones.mch.shrink, 'SHRINKWRAP')
            sw_con.target = self.target_mesh
            sw_con.wrap_mode = 'ABOVE_SURFACE'
            sw_con.use_track_normal = True
            sw_con.track_axis = 'TRACK_Y'
            sw_con.distance = self.params.shrinkwrap_distance
        
        # 3. ORG copies transformation from MCH
        self.make_constraint(self.bones.org, 'COPY_TRANSFORMS', self.bones.mch.shrink)
        
        # 4. DEF copies transformation from ORG
        self.make_constraint(self.bones.deform, 'COPY_TRANSFORMS', self.bones.org)

    @stage.generate_widgets
    def generate_widgets(self):
        # Assign a basic circle widget to the CTRL bone
        create_circle_widget(self.obj, self.bones.ctrl, radius=0.25)

    @classmethod
    def add_parameters(cls, params):
        """ Add the UI parameters for the rig setup """
        super().add_parameters(params)
        
        params.target_object = bpy.props.PointerProperty(
            type=bpy.types.Object,
            name="Source Mesh Object",
            description="The mesh object containing the vertex group (e.g. the body or face mesh)"
        )
        params.vertex_group = bpy.props.StringProperty(
            name="Vertex Group",
            description="The vertex group name that defines the separated target area (e.g. 'DEF-eye')"
        )
        params.shrinkwrap_distance = bpy.props.FloatProperty(
            name="Shrinkwrap Distance",
            default=0.1,
            description="Distance offset for the Above Surface Shrinkwrap constraint"
        )

    @classmethod
    def parameters_ui(cls, layout, params):
        """ Draw the parameters in the Rigify UI panel """
        super().parameters_ui(layout, params)
        
        layout.label(text="Helper Mesh Settings:")
        box = layout.box()
        box.prop(params, "target_object")
        box.prop(params, "vertex_group")
        
        layout.label(text="Constraint Settings:")
        box2 = layout.box()
        box2.prop(params, "shrinkwrap_distance")