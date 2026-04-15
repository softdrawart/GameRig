import bpy
from itertools import count
from bpy.types import PoseBone
from rigify.utils.rig import connected_children_names
from rigify.utils.bones import put_bone
from rigify.utils.naming import make_derived_name
from rigify.utils.misc import map_list
from rigify.utils.widgets_basic import create_sphere_widget, create_circle_widget
from rigify.utils.layers import ControlLayersOption
from rigify.base_rig import BaseRig, stage
from ....utils.bones import BoneUtilityMixin

def _lerp_bone_pos(obj, org_name: str, t: float):
    bone = obj.data.edit_bones[org_name]
    return bone.head.lerp(bone.tail, t)

class Rig(BaseRig, BoneUtilityMixin):
    class CtrlBones(BaseRig.CtrlBones):
        main: list[str]
        tweak: list[str]

    class MchBones(BaseRig.MchBones):
        pass

    bones: BaseRig.ToplevelBones[
        list[str],
        'Rig.CtrlBones',
        'Rig.MchBones',
        list[str],
    ]

    segments:    int
    seg_orgs:    list[str]
    seg_indices: list[int]
    tweak_count: int

    def find_org_bones(self, bone: PoseBone) -> list[str]:
        return [bone.name] + connected_children_names(self.obj, bone.name)

    def initialize(self) -> None:
        if len(self.bones.org) < 1:
            self.raise_error("Input must be at least 1 bone.")

        self.segments = self.params.segments
        self.seg_orgs    = []
        self.seg_indices = []
        for org in self.bones.org:
            for s in range(self.segments):
                self.seg_orgs.append(org)
                self.seg_indices.append(s)

        self.tweak_count = len(self.seg_orgs) + 1

    @stage.generate_bones
    def make_main_controls(self) -> None:
        self.bones.ctrl.main = []
        if self.params.create_main_bones:
            for org in self.bones.org:
                name = make_derived_name(org, 'ctrl')
                name = self.copy_bone(org, name)
                self.bones.ctrl.main.append(name)

    @stage.generate_bones
    def make_tweak_chain(self) -> None:
        self.bones.ctrl.tweak = []
        total = len(self.seg_orgs)

        for idx in range(self.tweak_count):
            if idx < total:
                org = self.seg_orgs[idx]
                t   = self.seg_indices[idx] / self.segments
            else:
                org = self.seg_orgs[-1]
                t   = 1.0

            name = make_derived_name(org, 'ctrl', '_tweak')
            name = self.copy_bone(org, name, parent=False, scale=0.5 / self.segments)
            put_bone(self.obj, name, _lerp_bone_pos(self.obj, org, t))
            self.bones.ctrl.tweak.append(name)

    @stage.generate_bones
    def make_deform_chain(self) -> None:
        self.bones.deform = []
        for idx in range(len(self.seg_orgs)):
            org = self.seg_orgs[idx]
            t   = self.seg_indices[idx] / self.segments
            name = make_derived_name(org, 'def')
            name = self.copy_bone(org, name, parent=False, scale=1.0 / self.segments)
            put_bone(self.obj, name, _lerp_bone_pos(self.obj, org, t))
            self.bones.deform.append(name)

    @stage.parent_bones
    def parent_main_controls(self) -> None:
        if self.params.create_main_bones:
            self.parent_bone_chain(self.bones.ctrl.main, use_connect=False)

    @stage.parent_bones
    def parent_tweak_chain(self) -> None:
        if self.params.create_main_bones:
            for i, tweak in enumerate(self.bones.ctrl.tweak):
                if i < len(self.seg_orgs):
                    org_name = self.seg_orgs[i]
                    org_idx = self.bones.org.index(org_name)
                    parent_ctrl = self.bones.ctrl.main[org_idx]
                else:
                    parent_ctrl = self.bones.ctrl.main[-1]
                
                self.set_bone_parent(tweak, parent_ctrl)
        else:
            root = self.get_bone_parent(self.bones.org[0])
            for tweak in self.bones.ctrl.tweak:
                self.set_bone_parent(tweak, root)

    @stage.parent_bones
    def parent_deform_chain(self) -> None:
        self.parent_bone_chain(self.bones.deform, use_connect=False)
        self.clean_def_hierarchy(self.bones.deform[0])

    @stage.configure_bones
    def configure_tweak_chain(self) -> None:
        total = len(self.bones.ctrl.tweak)
        for i, tweak in enumerate(self.bones.ctrl.tweak):
            pb = self.get_bone(tweak)
            pb.rotation_mode = 'ZXY'
            if i == total - 1:
                pb.lock_rotation_w = True
                pb.lock_rotation   = (True, True, True)
                pb.lock_scale      = (True, True, True)
            else:
                pb.lock_rotation_w = False
                pb.lock_rotation   = (True, False, True)
                pb.lock_scale      = (False, True, False)

        ControlLayersOption.TWEAK.assign_rig(self, self.bones.ctrl.tweak)

    @stage.rig_bones
    def rig_deform_chain(self) -> None:
        tweaks = self.bones.ctrl.tweak
        for deform, head_tw, tail_tw in zip(self.bones.deform, tweaks, tweaks[1:]):
            self.make_constraint(deform, 'COPY_TRANSFORMS', head_tw)
            self.make_constraint(deform, 'DAMPED_TRACK', tail_tw, track_axis='TRACK_Y')

    @stage.generate_widgets
    def make_widgets(self) -> None:
        if self.params.create_main_bones:
            for main_ctrl in self.bones.ctrl.main:
                create_circle_widget(self.obj, main_ctrl, radius=1.0)
        for tweak in self.bones.ctrl.tweak:
            create_sphere_widget(self.obj, tweak)

    @classmethod
    def add_parameters(cls, params) -> None:
        params.segments = bpy.props.IntProperty(
            name        = 'Segments',
            default     = 4,
            min         = 1,
            max         = 32,
            description = 'Number of tweak segments per ORG bone',
        )
        params.create_main_bones = bpy.props.BoolProperty(
            name        = 'Create Main Controls',
            default     = True,
            description = 'Create parent control bones for each ORG bone'
        )
        ControlLayersOption.TWEAK.add_parameters(params)

    @classmethod
    def parameters_ui(cls, layout, params) -> None:
        layout.row().prop(params, 'segments', slider=True)
        layout.row().prop(params, 'create_main_bones')
        ControlLayersOption.TWEAK.parameters_ui(layout, params)