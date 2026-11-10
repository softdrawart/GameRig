import bpy
from rigify.rigs.limbs.rear_paw import Rig as PawRig
from rigify.base_rig import stage

class Rig(PawRig):
    """Custom Paw rig shifting IK to 2nd/3rd bones and removing the heel."""

    def initialize(self):
        super().initialize()
        # Disable the secondary heel logic inherited from rear_paw
        self.use_heel2 = False

    # ----------------------------------------------------
    # 1. SHIFT IK TO 2ND AND 3RD BONES
    # ----------------------------------------------------
    
    def rig_org_bone(self, i: int, org: str, fk: str, ik: str | None):
        """Override to prevent the IK constraint from affecting the 1st bone."""
        # Index 0 is the first bone (e.g., thigh). We force it to be FK only.
        if i == 0:
            ik = None
        super().rig_org_bone(i, org, fk, ik)
        
    @stage.rig_bones
    def rig_custom_ik_adjustments(self):
        """Post-rigging step to adjust the IK solver's chain length."""
        # Locate the IK constraint on the IK end MCH bone and change chain_count to 2
        if hasattr(self.bones.mch, 'ik_end'):
            ik_end_bone = self.obj.pose.bones.get(self.bones.mch.ik_end)
            if ik_end_bone:
                for con in ik_end_bone.constraints:
                    if con.type == 'IK':
                        con.chain_count = 2

    # ----------------------------------------------------
    # 2. REMOVE HEEL IK
    # ----------------------------------------------------
    
    # By overriding the following stage methods with 'pass', 
    # we prevent the generation of the heel_ik controls and widgets.
    @stage.generate_bones
    def make_heel_control_bone(self):
        pass

    def get_ik_input_bone(self):
        pass

    def parent_ik_mch_chain(self):
        if self.use_mch_ik_base:
            self.set_bone_parent(self.bones.mch.ik_swing, self.bones.ctrl.ik_base, inherit_scale='AVERAGE')
            self.set_bone_parent(self.bones.mch.ik_base, self.bones.mch.ik_swing)
        else:
            self.set_bone_parent(self.bones.mch.ik_swing, self.bones.mch.follow)

        self.set_bone_parent(self.bones.mch.ik_target, self.get_ik_input_bone())
        self.set_bone_parent(self.bones.mch.ik_end, self.get_ik_chain_base())

        self.set_bone_parent(self.bones.mch.ik_target, self.bones.org.main[-3])

    def get_extra_ik_controls(self):
        extra = [self.bones.ctrl.heel2] if self.use_heel2 else []
        if self.component_ik_pivot:
            extra_ik_controls = [self.component_ik_pivot.control]
        else:
            extra_ik_controls = []
        return extra_ik_controls + extra

    @stage.parent_bones
    def parent_heel_control_bone(self):
        pass
        
    @stage.configure_bones
    def configure_heel_control_bone(self):
        pass
        
    @stage.generate_widgets
    def generate_heel_control_widget(self):
        pass
        
    # Omit heel controls from the UI selection/keyframing lists
    def get_middle_ik_controls(self):
        return []

        
def create_sample(obj):
    # Optionally call the parent sample generator or write a custom metarig structure here
    pass