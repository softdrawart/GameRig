# SPDX-FileCopyrightText: 2014-2022 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

import bpy

from itertools import count
from typing import Optional

from rigify.utils.bones import align_chain_x_axis, align_bone_orientation
from rigify.base_rig import stage
from rigify.utils.widgets_basic import create_circle_widget
from rigify.utils.widgets import layout_widget_dropdown, create_registered_widget
from ...chain_rigs import TweakChainRig
from rigify.utils.layers import ControlLayersOption
from rigify.utils.naming import make_derived_name, strip_org
from rigify.utils.misc import map_list
from rigify.rigs.basic.raw_copy import RelinkConstraintsMixin
from rigify.rigs.limbs.simple_tentacle import Rig as old_simple_tentacle


class Rig(TweakChainRig, RelinkConstraintsMixin):
    copy_rotation_axes: tuple[bool, bool, bool]
    automate: bool
    separate_rotation: bool
    separate_rotation_axes: tuple[bool, bool, bool]
    prop_bone: str
    min_chain_length = 1
    create_ctrl: bool

    class MchBones(TweakChainRig.MchBones):
        rot: str

    bones: TweakChainRig.ToplevelBones[
        list[str],
        'TweakChainRig.CtrlBones',
        'Rig.MchBones',
        list[str]
    ]

    def initialize(self):
        super().initialize()
        self.enable_scale = self.params.enable_scale
        self.relink = self.params.relink_constraints

    
    def rig_deform_bone(self, i, deform, org):
        if self.enable_scale:
            self.make_constraint(deform, 'COPY_TRANSFORMS', org)
        else:
            self.make_constraint(deform, 'COPY_LOCATION', org)
            self.make_constraint(deform, 'COPY_ROTATION', org)

    ##############################
    # Control chain

    @stage.generate_bones
    def make_control_chain(self):
        super().make_control_chain()
    
    @stage.configure_bones
    def configure_control_chain(self):
        super().configure_control_chain()
    
    @stage.generate_widgets
    def make_control_widgets(self):
        super().make_control_widgets()

    def make_control_widget(self, i: int, ctrl: str):
        create_registered_widget(self.obj, ctrl, self.params.fk_widget, radius=0.3, head_tail=0.5)
    ##############################
    # Tweak chain

    @stage.generate_bones
    def make_tweak_chain(self):
        super().make_tweak_chain()

    @stage.parent_bones
    def parent_tweak_chain(self):
        super().parent_tweak_chain()

    @stage.generate_widgets
    def make_tweak_widgets(self):
        super().make_tweak_widgets()

    ##############################
    # ORG chain

    # Parent
    @stage.parent_bones
    def parent_control_chain(self):
        # use_connect=False for backward compatibility
        self.parent_bone_chain(self.bones.ctrl.fk, use_connect=False)
        if self.relink:
            new_parent = self.relink_bone_parent(self.bones.org[0])
            if new_parent:
                self.set_bone_parent(self.bones.ctrl.fk[0], new_parent)

    # Configure
    @stage.configure_bones
    def configure_tweak_chain(self):
        super().configure_tweak_chain()

        ControlLayersOption.TWEAK.assign(self.params, self.obj, self.bones.ctrl.tweak)

    def configure_tweak_bone(self, i, tweak):
        super().configure_tweak_bone(i, tweak)

        # Backward compatibility
        self.get_bone(tweak).rotation_mode = 'QUATERNION'

    
    ##############################
    #ORG bones RIG
    @stage.rig_bones
    def rig_org_chain(self):
        tweaks = self.bones.ctrl.tweak
        for args in zip(count(0), self.bones.org, tweaks, tweaks[1:]):
            self.rig_org_bone_tweak(*args)
        

    def rig_org_bone_ctrl(self, i: int, org: str, ctrl: str):
        self.make_constraint(org, 'COPY_TRANSFORMS', ctrl)

    def rig_org_bone_tweak(self, i: int, org: str, tweak: str, next_tweak: Optional[str]):
            if self.enable_scale:
                self.make_constraint(org, 'COPY_SCALE', tweak)
            if next_tweak:
                self.make_constraint(org, 'DAMPED_TRACK', next_tweak)

    @classmethod
    def add_parameters(cls, params):
        """ Add the parameters of this rig type to the
            RigifyParameters PropertyGroup
        """
        
        ControlLayersOption.TWEAK.add_parameters(params)

        params.fk_widget = bpy.props.StringProperty(
            name='widget fk select',
            description='select fk widget',
            default='circle'
        )

        cls.add_relink_constraints_params(params)
        
    @classmethod
    def parameters_ui(cls, layout, params):
        """ Create the ui for the rig parameters.
        """

        
        layout_widget_dropdown(layout, params, 'fk_widget')
        ControlLayersOption.TWEAK.parameters_ui(layout, params)
        #relink to extra ctrl
        cls.add_relink_constraints_ui(layout, params)

        r = layout.row()
        r.prop(params, "enable_scale")
        
