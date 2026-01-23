import bpy

from ....utils.bones import BoneUtilityMixin

from rigify.base_rig import stage
from rigify.rigs.limbs.limb_rigs import BaseLimbRig as old_BaseLimbRig
from rigify.rigs.limbs.limb_rigs import SegmentEntry
from rigify.utils.naming import choose_derived_bone


class BaseLimbRig(BoneUtilityMixin, old_BaseLimbRig):

    def initialize(self):
        super().initialize()
        self.bbone_segments = 1
        self.leaf_hierarchy = self.params.leaf_hierarchy


    @stage.parent_bones
    def parent_deform_chain(self):
        self.set_bone_parent(self.bones.deform[0], self.rig_parent_bone)
        self.parent_bone_chain(self.bones.deform, use_connect=True)

        # This puts the deformation bones into the def hierarchy of its parent rig
        self.clean_def_hierarchy(self.bones.deform[0])

        for bone in self.bones.deform:
            self.get_bone(bone).use_connect = False

        # Create leaf hierarchy
        if self.leaf_hierarchy:
            limb_segments = []
            for bone in self.bones.org['main']:
                limb_segments.append(choose_derived_bone(self.generator, bone, 'def'))
            self.set_bone_parent(limb_segments[1], limb_segments[0])
            self.set_bone_parent(limb_segments[2], limb_segments[1])

            for bone in self.bones.deform:
                if bone not in limb_segments:
                    for segment in limb_segments:
                        if segment in bone:
                            self.set_bone_parent(bone, segment)

    def rig_deform_bone(self, i, deform, entry, next_entry, tweak, next_tweak):
        if tweak:
            self.make_constraint(deform, 'COPY_LOCATION', tweak)
            self.make_constraint(deform, 'COPY_ROTATION', tweak)

            if next_tweak:
                self.make_constraint(deform, 'DAMPED_TRACK', next_tweak)

                # self.rig_deform_easing(i, deform, tweak, next_tweak) #bbone stuff, not relevant here.

            elif next_entry:
                self.make_constraint(deform, 'DAMPED_TRACK', next_entry.org)

        else:
            self.make_constraint(deform, 'COPY_LOCATION', entry.org)
            self.make_constraint(deform, 'COPY_ROTATION', entry.org)

    def rig_ik_mch_end_bone(self, mch_ik: str, mch_target: str, ctrl_pole: str, chain=2):
        con = self.make_constraint(
            mch_ik, 'IK', mch_target, chain_count=chain,
        )

        self.make_driver(con, "mute",
                         variables=[(self.prop_bone, 'pole_vector')], polynomial=[0.0, 1.0])
        self.make_driver(con, "use_stretch",
                         variables=[(self.prop_bone, 'IK_Stretch')])

        con_pole = self.make_constraint(
            mch_ik, 'IK', mch_target, chain_count=chain,
            pole_target=self.obj, pole_subtarget=ctrl_pole, pole_angle=self.pole_angle,
        )

        self.make_driver(con_pole, "mute",
                         variables=[(self.prop_bone, 'pole_vector')], polynomial=[1.0, -1.0])
        self.make_driver(con_pole, "use_stretch",
                         variables=[(self.prop_bone, 'IK_Stretch')])

    @stage.configure_bones
    def set_control_orientations(self):
        pass
        #self.remove_quat_rot_mode(self.bones.ctrl)

    
    def rig_tweak_mch_bone(self, i: int, tweak: str, entry: SegmentEntry):
        super().rig_tweak_mch_bone(i, tweak, entry) #call existing super function
        #then add copy rotation constraint
        if i == 0:
            con = self.make_constraint(tweak, 'COPY_ROTATION', entry.org)
            controls = self.bones.ctrl.flatten() #all controllers will open parameters
            panel = self.generator.script.panel_with_selected_check(self, controls)
            self.make_property(self.prop_bone, 'Tweak_Follow', default=1.0, description="Vizor Tweak Follow ORG Bone")
            panel.custom_prop(self.prop_bone, 'Tweak_Follow')
            self.make_driver(con, 'influence', variables={(self.prop_bone, 'Tweak_Follow')})

    @stage.rig_bones
    def rig_ik_mch_chain(self):
        mch = self.bones.mch
        input_bone = self.get_ik_input_bone()

        self.make_constraint(mch.ik_swing, 'DAMPED_TRACK', mch.ik_target)

        """ self.rig_ik_mch_stretch_limit(
            mch.ik_target, mch.follow, input_bone, self.ik_input_head_tail, 2) """
        self.rig_ik_mch_end_bone(mch.ik_end, mch.ik_target, self.bones.ctrl.ik_pole)
    
    @stage.rig_bones
    def rig_org_chain(self):
        super().rig_org_chain()
        #last ORG bone is copy location from previous ORG bone to mantain correct
        self.make_constraint(self.bones.org.main[-1], 'COPY_LOCATION', self.bones.org.main[-2], head_tail=1)
    ##############################
    # Parameter UI

    @classmethod
    def add_parameters(self, params):
        """ Add the parameters of this rig type to the
            RigifyParameters PropertyGroup
        """
        super().add_parameters(params)
        params.leaf_hierarchy = bpy.props.BoolProperty(
            name="Leaf Hierarchy",
            default=False,
            description="False means limb segments and tweak bones will create a single chain. True means limb segments will be parented to each other directly and the tweak bones will be parented to their respective segment."
        )

    @classmethod
    def parameters_ui(self, layout, params):
        """ Create the ui for the rig parameters.
        """
        super().parameters_ui(layout, params)

        c = layout.column()
        c.prop(params, "leaf_hierarchy")
