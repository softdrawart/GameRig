
import bpy
from rigify.base_rig import BaseRig, stage
from rigify.utils.naming import make_derived_name
from rigify.utils.bones import align_bone_orientation
from rigify.utils.widgets_basic import create_sphere_widget
from ..basic.super_copy import Rig as SuperCopyRig


class Rig(SuperCopyRig):
    """A split rotation mechanism rig that sits between two bones and splits their rotation."""
    
    target_bone: str # This is the bone for the copy rotation constraint
    parent_bone: str # This is the bone for parenting

    def initialize(self):
        super().initialize()
        
        self.org_bone = self.bones.org
        self.parent_bone = self.get_bone_parent(self.org_bone)
        
        if not self.parent_bone:
            self.raise_error(f"Bone '{self.org_bone}' must be parented to a base bone.")

        # If user explicitly defined a target in the UI, use it and skip distance math
        if self.params.rotation_target:
            self.target_bone = self.params.rotation_target
            if not self.get_bone(self.target_bone):
                self.raise_error(f"Manual rotation target '{self.target_bone}' not found in the metarig.")
            return

        # Get coordinates to determine placement intersection
        org_head = self.get_bone(self.org_bone).head
        parent_head = self.get_bone(self.parent_bone).head
        parent_tail = self.get_bone(self.parent_bone).tail

        # 1. ORG head is at the HEAD of the parent bone
        if (org_head - parent_head).length < (org_head - parent_tail).length:
            self.target_bone = self.get_bone_parent(self.parent_bone)
            if not self.target_bone:
                self.raise_error(f"Parent bone '{self.parent_bone}' must have its own parent to split rotation.")
        # 2. ORG head is at the TAIL of the parent bone
        elif (org_head - parent_tail).length < (org_head - parent_head).length:
            self.target_bone = None
            children = self.get_bone(self.parent_bone).children
            
            if not children:
                self.raise_error(f"Could not find a connected child of '{self.parent_bone}' at its tail to use as a target.")
            
            # Iterate through children to find the adjoining bone
            for child in children:
                if (child.head - parent_tail).length < 1e-4 and child.name != self.org_bone:
                    self.target_bone = child.name
                    break
            
            # Fallback: if distance tolerance failed but there's exactly one valid child
            if not self.target_bone and len(children) == 1 and children[0].name != self.org_bone:
                self.target_bone = children[0].name
                
            if not self.target_bone:
                self.raise_error(f"Could not find a valid target bone at the tail of '{self.parent_bone}'.")
        
        else:
            self.raise_error(f"Bone '{self.org_bone}' must be placed close to the head or tail of its parent.") 
        
    
    def rig_bones(self):
        bones = self.bones

        self.relink_bone_constraints(bones.org)
        self.relink_move_constraints(bones.org, bones.mch)

        if self.make_control:
            # Constrain the original bone.
            self.make_constraint(bones.org, 'COPY_TRANSFORMS', bones.ctrl, insert_index=0)

        if self.make_deform:
            if self.enable_scale:
                self.make_constraint(bones.deform, 'COPY_TRANSFORMS', bones.org)
            else:
                self.make_constraint(bones.deform, 'COPY_LOCATION', bones.org)
                self.make_constraint(bones.deform, 'COPY_ROTATION', bones.org)
    
    def parent_bones(self):
        bones = self.bones

        new_parent = self.relink_bone_parent(bones.org)

        self.set_bone_parent(bones.mch, new_parent)
        # This puts the deformation bones into the def hierarchy of its parent rig
        if self.make_deform:
            self.clean_def_hierarchy(self.bones.deform)   

    @stage.generate_bones
    def make_mechanism_bones(self):
        # Create the MCH split bone
        mch_name = make_derived_name(self.org_bone, 'mch', '_split')
        self.bones.mch = self.copy_bone(self.org_bone, mch_name, length = self.get_bone(self.target_bone).length/2)

        # Orient MCH to exactly match the target bone in world space
        align_bone_orientation(self.obj, self.bones.mch, self.target_bone)

    @stage.parent_bones
    def parent_bones_stage(self):
        # MCH remains parented to the original parent (e.g., Shin or Thigh)
        self.set_bone_parent(self.bones.mch, self.parent_bone)
        if self.make_control:
            # CTRL is parented to the new MCH bone
            self.set_bone_parent(self.bones.ctrl, self.bones.mch)

    @stage.rig_bones
    def rig_bones_stage(self):
        # MCH copies rotation from the target bone at 50% influence
        self.make_constraint(
            self.bones.mch,
            'COPY_ROTATION',
            self.target_bone,
            space='WORLD',
            influence=self.params.influence
        )

    @classmethod
    def add_parameters(cls, params):
        super().add_parameters(params)
        params.influence = bpy.props.FloatProperty(
            name="Rotation Constraint Influence",
            default=0.5,
            min=0.0,
            max=1.0,
            description="Adjust how close it will follow rotation"
        )
        params.rotation_target = bpy.props.StringProperty(
            name="Rotation Target",
            description="Set rotation target bone here otherwise it will use default nearby target"
        )
        params.enable_scale = bpy.props.BoolProperty(
            name="Scale",
            default=True,
            description="Deformation bones will inherit the scale of their ORG bones. Enable this only if you know what you are doing because scale can break your rig in the game engine"
        )
    @classmethod
    def parameters_ui(cls, layout, params):
        """ Create the ui for the rig parameters.
        """
        super().parameters_ui(layout, params)

        r = layout.row()
        r.prop(params, "influence")
        r = layout.row()
        r.prop(params, "rotation_target")
        r = layout.row()
        r.prop(params, "enable_scale")

