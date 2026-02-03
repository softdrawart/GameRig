import bpy
from bpy.props import StringProperty
from mathutils import Vector
from rigify.base_rig import BaseRig, stage
from rigify.utils.naming import make_derived_name, strip_org
from rigify.utils.bones import put_bone, align_chain_x_axis
from rigify.utils.widgets_basic import create_sphere_widget
from rigify.utils.misc import map_list

class Rig(BaseRig):
    """
    A custom chain rig with tweaks, a master stretch bone, and 
    Armature-constrained middle mechanisms.
    """
    
    def initialize(self):
        super().initialize()
        # Validate chain length
        if len(self.bones.org) < 1:
            self.raise_error("Input to rig type must be a chain of at least 1 bone.")

    # --------------------------------------------------------------------------
    # 1. Define Parameters
    # --------------------------------------------------------------------------
    @classmethod
    def add_parameters(cls, params):
        """ Add custom parent parameters to the Rigify UI. """
        params.start_tweak_parent = StringProperty(
            name="Start Parent",
            description="Name of the bone to parent the start tweak to (default: root/parent)",
            default=""
        )
        params.end_tweak_parent = StringProperty(
            name="End Parent",
            description="Name of the bone to parent the end tweak to (default: root/parent)",
            default=""
        )

    @classmethod
    def parameters_ui(cls, layout, params):
        """ Draw the parameters in the UI. """
        layout.prop(params, "start_tweak_parent")
        layout.prop(params, "end_tweak_parent")

    # --------------------------------------------------------------------------
    # 2. Define Bone Collections
    # --------------------------------------------------------------------------
    class CtrlBones(BaseRig.CtrlBones):
        tweaks: list[str]  # Visible tweak controls

    class MchBones(BaseRig.MchBones):
        str_bone: str      # The main stretch bone
        mid_mchs: list[str] # Mechanism parents for middle tweaks

    bones: BaseRig.ToplevelBones[
        list[str],
        'Rig.CtrlBones',
        'Rig.MchBones',
        list[str]
    ]

    # --------------------------------------------------------------------------
    # 3. Generate Bones
    # --------------------------------------------------------------------------
    @stage.generate_bones
    def generate_all_bones(self):
        orgs = self.bones.org
        
        # --- A. Generate Tweak Bones (Head + Tail of chain) ---
        # We need tweaks at every joint. Count = len(orgs) + 1
        self.bones.ctrl.tweaks = []
        
        for i, org_bone in enumerate(orgs):
            # Create tweak at Head of current bone
            tweak_name = self.copy_bone(org_bone, make_derived_name(org_bone, 'ctrl', '_tweak'), parent=False)
            tweak_edit = self.get_bone(tweak_name)
            tweak_edit.length /= 4  # Make visual size smaller
            self.bones.ctrl.tweaks.append(tweak_name)
            
            # If this is the last bone, create the final tail tweak
            if i == len(orgs) - 1:
                tail_tweak_name = self.copy_bone(org_bone, make_derived_name(org_bone, 'ctrl', '_tweak_end'), parent=False)
                tail_tweak_edit = self.get_bone(tail_tweak_name)
                # Position at tail
                tail_tweak_edit.head = self.get_bone(org_bone).tail
                tail_tweak_edit.tail = tail_tweak_edit.head + Vector((0, 0, tail_tweak_edit.length/4))
                self.bones.ctrl.tweaks.append(tail_tweak_name)

        # --- B. Generate MCH STR Bone ---
        # One bone spanning the length of the whole chain
        str_name = self.copy_bone(orgs, make_derived_name(orgs, 'mch', '_STR'), parent=False)
        str_bone = self.get_bone(str_name)
        str_bone.tail = self.get_bone(orgs[-1]).tail # Span to end
        
        # Enable B-Bones on STR so the Armature constraint distributes MCHs along it smoothly [1]
        str_bone.bbone_segments = len(orgs) * 4 
        self.bones.mch.str_bone = str_name

        # --- C. Generate MCH Bones for Middle Tweaks ---
        # Only for indices 1 to -1 (excluding first and last)
        self.bones.mch.mid_mchs = []
        
        # We zip the orgs to finding joint positions corresponding to middle tweaks
        middle_indices = range(1, len(self.bones.ctrl.tweaks) - 1)
        
        for i in middle_indices:
            tweak_name = self.bones.ctrl.tweaks[i]
            # Create MCH at the same position as the tweak
            mch_name = self.copy_bone(tweak_name, make_derived_name(tweak_name, 'mch'), parent=False)
            self.get_bone(mch_name).length /= 2 # Slightly different size to distinguish
            self.bones.mch.mid_mchs.append(mch_name)

    # --------------------------------------------------------------------------
    # 4. Parenting
    # --------------------------------------------------------------------------
    @stage.parent_bones
    def parent_structure(self):
        ctrls = self.bones.ctrl.tweaks
        mchs = self.bones.mch.mid_mchs
        str_bone = self.bones.mch.str_bone
        
        # Default rig parent (root or previous bone)
        rig_parent = self.get_bone_parent(self.bones.org)

        # --- A. Parent Start Tweak ---
        start_tweak = ctrls
        # Check if user specified a custom parent in params [2]
        if self.params.start_tweak_parent:
             # Logic to find the bone by name (simplified)
             self.set_bone_parent(start_tweak, self.params.start_tweak_parent)
        else:
             self.set_bone_parent(start_tweak, rig_parent)

        # --- B. Parent End Tweak ---
        end_tweak = ctrls[-1]
        if self.params.end_tweak_parent:
             self.set_bone_parent(end_tweak, self.params.end_tweak_parent)
        else:
             self.set_bone_parent(end_tweak, rig_parent)

        # --- C. Parent MCH STR Bone ---
        # "parented to first tweak bone"
        self.set_bone_parent(str_bone, start_tweak)

        # --- D. Parent Middle MCH Bones ---
        # They must follow the rig generally, but their transform is driven by constraint.
        # Parenting to Root/Rig Parent prevents double transformations.
        for mch in mchs:
            self.set_bone_parent(mch, rig_parent)

        # --- E. Parent Middle Tweaks to Middle MCHs ---
        # "parent those middle tweak bones to their respectful MCHs"
        # The first and last tweaks are NOT in mchs list, so we map indices carefully.
        # ctrls[3] matches mchs, ctrls[4] matches mchs[3], etc.
        for i, mch in enumerate(mchs):
            tweak_idx = i + 1
            self.set_bone_parent(ctrls[tweak_idx], mch)

    # --------------------------------------------------------------------------
    # 5. Constraints & Rigging
    # --------------------------------------------------------------------------
    @stage.rig_bones
    def apply_constraints(self):
        ctrls = self.bones.ctrl.tweaks
        mchs = self.bones.mch.mid_mchs
        str_bone = self.bones.mch.str_bone

        # --- A. Stretch Constraint on STR Bone ---
        # "add stretch to constraint that stretch to last tweak bone"
        self.make_constraint(
            str_bone, 
            'STRETCH_TO', 
            ctrls[-1], 
            volume='VOLUME_XZ'
        )

        # --- B. Armature Constraint on Middle MCH Bones ---
        # "add Armature to MCH bones constrained to STR MCH"
        for mch in mchs:
            # We use the Armature constraint. For this to work well on a single bone target,
            # Rigify usually expects B-Bones (enabled in step 3B). 
            # This binds the MCH to the closest envelope of the STR bone.
            self.make_constraint(
                mch, 
                'ARMATURE', 
                targets=[(str_bone, 1.0)], 
                use_deform_preserve_volume=True
            )

    # --------------------------------------------------------------------------
    # 6. Widgets
    # --------------------------------------------------------------------------
    @stage.generate_widgets
    def create_widgets(self):
        for tweak in self.bones.ctrl.tweaks:
            create_sphere_widget(self.obj, tweak, radius=0.5)