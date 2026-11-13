from rigify.base_rig import stage

from .rear_paw import Rig as RearPawRig
from rigify.rigs.limbs.limb_rigs import BaseLimbRig, SegmentEntry
from rigify.utils.naming import make_derived_name
from rigify.utils.widgets_basic import create_limb_widget, create_circle_widget
from rigify.utils.bones import align_bone_x_axis, align_bone_z_axis, compute_chain_x_axis, flip_bone, put_bone
from rigify.utils.widgets import create_registered_widget
from rigify.utils.bones import align_bone_to_axis

class Rig(RearPawRig):
    """3-bone linkage wing rig based on the rear_paw mechanics. Digit is omitted."""
    
    # Add this line to override paw's 3-segment assumption
    segmented_orgs = 2 
    
    # Constrain the rig to exactly 3 bones (Thigh, Shin, Heel)
    min_valid_orgs = 3
    max_valid_orgs = 3

    bones: RearPawRig.ToplevelBones[
        'RearPawRig.OrgBones',
        'Rig.CtrlBones',
        'RearPawRig.MchBones',
        list[str]
    ]

    class CtrlBones(RearPawRig.CtrlBones):
        extra_palm: str
    
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
        return self.copy_bone(orgs[2], make_derived_name(orgs[0], 'mch', '_ik2_target'), scale=1 / 2)
    
    def align_ik_control_bone(self, name: str):
        #align_bone_to_axis(self.obj, name, 'y', flip=True)
        bone = self.get_bone(name)
        put_bone(self.obj, name, bone.tail)
        #bone.tail[2] = bone.head[2]
        #bone.roll = 0

    def make_ik_ctrl_widget(self, ctrl):
        create_registered_widget(self.obj, ctrl, 'cube', size=0.5)
    #######
    #extra palm rotation control for wing tip
    @stage.generate_bones
    def make_palm_extra_rotation_bone(self):
        org = self.bones.org.main[2]
        self.bones.ctrl.extra_palm = self.copy_bone(org, make_derived_name(org, 'ctrl', '_extra_rotation'))

    @stage.parent_bones
    def parent_palm_extra_rotation_bone(self):
        self.set_bone_parent(self.bones.ctrl.extra_palm, self.bones.ctrl.heel)

    def parent_tweak_mch_bone(self, i: int, mch: str, entry: SegmentEntry):
        if i == 0:
            self.set_bone_parent(mch, self.rig_parent_bone, inherit_scale='FIX_SHEAR')
        else:
            if entry.org == self.bones.org.main[2]:
                # Parent the 3rd tweak bone to the extra palm rotation control for proper wing tip rotation
                self.set_bone_parent(mch, self.bones.ctrl.extra_palm)
            else:
                self.set_bone_parent(mch, entry.org)

    @stage.rig_bones
    def rig_tweak_mch_chain(self):
        #copy local rotation from main ik
        co = self.make_constraint(self.bones.ctrl.extra_palm, 'COPY_ROTATION', self.bones.ctrl.ik, use_offset=True, target_space='LOCAL', owner_space='LOCAL')
                
    def rig_tweak_mch_bone(self, i: int, tweak: str, entry: SegmentEntry):
            if entry.seg_idx:
                prev_tweak, next_tweak, fac = self.get_tweak_blend(i, entry)
    
                self.make_constraint(tweak, 'COPY_TRANSFORMS', prev_tweak)
                self.make_constraint(tweak, 'COPY_TRANSFORMS', next_tweak, influence=fac)
                self.make_constraint(tweak, 'DAMPED_TRACK', next_tweak)
    
            elif entry.seg_idx is not None or entry.org == self.bones.org.main[2]:
                self.make_constraint(tweak, 'COPY_SCALE', self.bones.mch.follow, use_make_uniform=True)
    
            if i == 0:
                self.make_constraint(tweak, 'COPY_LOCATION', entry.org)
                self.make_constraint(tweak, 'DAMPED_TRACK', entry.org, head_tail=1)

    def rig_org_bone(self, i: int, org: str, fk: str, ik: str | None):
        #overide MCH ik target (3rd bone) hand to our custom to control rotation of the wing tip
        if ik == self.bones.mch.ik_target:
            ik = self.bones.ctrl.extra_palm

        self.make_constraint(org, 'COPY_TRANSFORMS', fk)

        if ik:
            con = self.make_constraint(org, 'COPY_TRANSFORMS', ik)

            self.make_driver(con, 'influence',
                             variables=[(self.prop_bone, 'IK_FK')], polynomial=[1.0, -1.0])
    @stage.configure_bones
    def configure_palm_extra_rotation_bone(self):
        self.make_fk_control_widget(1, self.bones.ctrl.extra_palm)
        bone = self.get_bone(self.bones.ctrl.extra_palm)
        bone.lock_location = (False, False, False)
        bone.lock_rotation = (False, False, False)
        bone.lock_scale = (True, True, True)
