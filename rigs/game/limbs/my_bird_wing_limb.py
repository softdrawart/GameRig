from .rear_paw import Rig as RearPawRig
from rigify.rigs.limbs.limb_rigs import BaseLimbRig
from rigify.utils.naming import make_derived_name
from rigify.utils.widgets_basic import create_limb_widget, create_circle_widget
from rigify.utils.bones import align_bone_x_axis, align_bone_z_axis, compute_chain_x_axis, flip_bone
from rigify.utils.widgets import create_registered_widget
from rigify.utils.bones import align_bone_to_axis

class Rig(RearPawRig):
    """3-bone linkage wing rig based on the rear_paw mechanics. Digit is omitted."""
    
    # Add this line to override paw's 3-segment assumption
    segmented_orgs = 2 
    
    # Constrain the rig to exactly 3 bones (Thigh, Shin, Heel)
    min_valid_orgs = 3
    max_valid_orgs = 3
    
    def initialize(self):
        super().initialize()
        # Disable the second heel flag and bypass pawRig's digit dependency
        self.use_heel2 = False
        self.toe_bone_index = 999 
        
    def make_ik_control_bone(self, orgs: list[str]):
        # Place the main IK control at the tail of the 3rd bone (heel)
        name = self.copy_bone(orgs[2], make_derived_name(orgs[2], 'ctrl', '_ik'))
        self.align_ik_control_bone(name)
        
        # Match the length of the 3rd bone for a clean aesthetic
        vec = self.get_bone(orgs[2]).tail - self.get_bone(orgs[2]).head
        self.get_bone(name).length = max(vec.length, 0.01)
        
        return name

    def get_ik2_input_bone(self):
        # The secondary IK normally targets the toe socket. Since it is removed, 
        # we reroute it directly to the main IK control output.
        return self.get_ik_control_output()

    def make_toe_socket_bone(self):
        # Nullify the toe socket mechanism creation
        pass

    def parent_toe_socket_bone(self):
        # Nullify the toe socket parenting
        pass

    def register_switch_parents(self, pbuilder):
        # Explicitly skip pawRig's switch parent generation which hardcodes the 4th bone
        BaseLimbRig.register_switch_parents(self, pbuilder)
        
        # Safely register the 3rd bone (heel) as the limb end instead
        pbuilder.register_parent(self, self.bones.org.main[2], exclude_self=True, tags={'limb_end'})
        
    def make_fk_control_widget(self, i, ctrl):
        # Safely assign FK widgets without relying on the now-disabled toe_bone_index
        if i < 2:
            create_limb_widget(self.obj, ctrl)
        else:
            create_circle_widget(self.obj, ctrl, radius=0.4, head_tail=0.0)

    def prepare_bones(self):
        # Override to prevent pawRig from attempting to align a 4th bone
        orgs = self.bones.org.main
        foot_x = self.vector_without_z(self.get_bone(orgs[2]).y_axis).cross((0, 0, 1))

        if self.params.rotation_axis == 'automatic':
            axis = compute_chain_x_axis(self.obj, orgs[0:2])
            for bone in orgs:
                align_bone_x_axis(self.obj, bone, axis)
        elif self.params.auto_align_extremity:
            # Safely align only the 3rd bone (heel), ignoring the toe
            if getattr(self, 'main_axis', 'z') == 'x':
                align_bone_x_axis(self.obj, orgs[2], foot_x)
            else:
                align_bone_z_axis(self.obj, orgs[2], foot_x)

    def make_ik2_mch_target_bone(self, orgs: list[str]):
        # Override rear_paw's hardcoded 4th bone requirement for the IK2 stretch target.
        # Use the 3rd bone (heel/wing tip) instead of the missing toe (orgs[3]).
        return self.copy_bone(orgs[2], make_derived_name(orgs[0], 'mch', '_ik2_target'), scale=1 / 2)
    
    def align_ik_control_bone(self, name: str):
        align_bone_to_axis(self.obj, name, 'y', flip=True)
        bone = self.get_bone(name)
        bone.tail[2] = bone.head[2]
        bone.roll = 0

    def make_ik_ctrl_widget(self, ctrl):
        create_registered_widget(self.obj, ctrl, 'cube')