import bpy
from bpy.types import PoseBone
from itertools import count
from rigify.utils.naming import make_derived_name, strip_org
from rigify.base_rig import BaseRig, stage
from rigify.utils.widgets_basic import create_sphere_widget
from rigify.utils.misc import map_list
from rigify.utils.bones import put_bone
from rigify.utils.rig import connected_children_names
from ....utils.bones import BoneUtilityMixin

class Rig(BaseRig, BoneUtilityMixin):
    """A rig that connects tweak to stretchy bone parented to Start and End bones set in params."""

    ##############################
    # BONES
    rig_parent_bone: str  # Bone to be used as parent of the whole rig
    head_tweak_parent: str
    tail_tweak_parent: str

    class CtrlBones(BaseRig.CtrlBones):
        tweak: list[str]               # Tweak control chain

    class MchBones(BaseRig.MchBones):
        tweak: list[str]               # Tweak mch chain
        stretch: str

    bones: BaseRig.ToplevelBones[
        list[str],
        'Rig.CtrlBones',
        'Rig.MchBones',
        list[str]
    ]

    def initialize(self):
        super().initialize()
        # Initialize lists to ensure they persist across stages
        self.bones.ctrl.tweak = []
        self.bones.mch.tweak = []
        
        self.head_tweak_parent = self.params.head_tweak_parent
        self.tail_tweak_parent = self.params.tail_tweak_parent

    def parent_bones(self):
        self.rig_parent_bone = self.get_bone_parent(self.bones.org[0])

    def find_org_bones(self, bone: PoseBone):
        return [bone.name] + connected_children_names(self.obj, bone.name)
    
    ##############################
    # Tweak chain

    @stage.generate_bones
    def make_tweak_chain(self):
        orgs = self.bones.org
        self.bones.ctrl.tweak = map_list(self.make_tweak_bone, count(0), orgs + orgs[-1:])

    def make_tweak_bone(self, i: int, org: str):
        name = self.copy_bone(org, 'tweak_' + strip_org(org), parent=False, scale=0.5)

        if i == len(self.bones.org):
            put_bone(self.obj, name, self.get_bone(org).tail)

        return name

    @stage.parent_bones
    def parent_tweak_chain(self):
        ctrl = self.bones.ctrl
        for tweak, mch in zip(ctrl.tweak[1:-1], self.bones.mch.tweak):
            self.set_bone_parent(tweak, mch)

        #parent first and last tweak bones
        start_tweak = ctrl.tweak[0]
        end_tweak = ctrl.tweak[-1]

        if self.head_tweak_parent:
             self.set_bone_parent(start_tweak, self.head_tweak_parent)
        else:
             self.set_bone_parent(start_tweak, self.rig_parent_bone)

        if self.tail_tweak_parent:
             self.set_bone_parent(end_tweak, self.tail_tweak_parent)
        else:
             self.set_bone_parent(end_tweak, self.rig_parent_bone) 



    @stage.generate_widgets
    def make_tweak_widgets(self):
        for tweak in self.bones.ctrl.tweak:
            self.make_tweak_widget(tweak)

    def make_tweak_widget(self, tweak: str):
        create_sphere_widget(self.obj, tweak)

    ##############################
    # Extra MCH

    @stage.generate_bones
    def make_stretch_mch(self):
        orgs = self.bones.org
        self.bones.mch.stretch = str_name = self.copy_bone(orgs[0], make_derived_name(orgs[0], 'mch', '_STR'), parent=False)
        str_bone = self.get_bone(str_name)
        str_bone.tail = self.get_bone(orgs[-1]).tail # Span to end
    
    @stage.parent_bones
    def parent_mch_stretch(self):
        self.set_bone_parent(self.bones.mch.stretch, self.rig_parent_bone)

    @stage.rig_bones
    def rig_mch_stretch(self):
        self.make_constraint(self.bones.mch.stretch, 'COPY_LOCATION', self.bones.ctrl.tweak[0])
        self.make_constraint(self.bones.mch.stretch, 'STRETCH_TO', self.bones.ctrl.tweak[-1])
        

    
    ##############################
    # Tweak MCH chain

    @stage.generate_bones
    def make_mch_tweak_chain(self):
        tweaks = self.bones.ctrl.tweak
        self.bones.mch.tweak = map_list(self.make_mch_tweak_bone, count(0), tweaks[1:-1])

    def make_mch_tweak_bone(self, i: int, org: str):
        name = self.copy_bone(org, make_derived_name(org, 'mch'), parent=False, scale=0.5)
        return name
    
    @stage.rig_bones
    def rig_mch_tweak_bones(self):
        mchs = self.bones.mch.tweak
        for mch in mchs:
            self.make_constraint(mch, 'ARMATURE', targets=[self.bones.mch.stretch])
            self.make_constraint(mch, 'COPY_SCALE', 'root')

    ##############################
    # ORG chain (that moves with tweaks)

    @stage.parent_bones
    def parent_org_bones(self):
        bones = self.bones
        for org, tweak in zip(bones.org, bones.ctrl.tweak[:-1]):
            self.set_bone_parent(org, tweak)

    @stage.rig_bones
    def rig_org_bones(self):
        self.make_constraint(self.bones.org[0], 'DAMPED_TRACK', self.bones.ctrl.tweak[1])
    ##############################
    # DEF chain (that copy transforms of org bones)

    @stage.generate_bones
    def make_deform_bones(self):
        orgs = self.bones.org
        self.bones.deform = map_list(self.make_deform_bone, count(0), orgs)
        
    def make_deform_bone(self, i: int, bone: str):
        return self.copy_bone(bone, make_derived_name(bone, 'def'), parent=True)
    
    @stage.parent_bones
    def parent_deform_bones(self):
        self.parent_bone_chain(self.bones.deform, use_connect=False)
        # This puts the deformation bones into the def hierarchy of its parent rig
        self.clean_def_hierarchy(self.bones.deform[0])
    
    @stage.rig_bones
    def rig_deform_bone(self):
        for deform, org in zip(self.bones.deform, self.bones.org):
            self.make_constraint(deform, 'COPY_LOCATION', org)
            self.make_constraint(deform, 'COPY_ROTATION', org)
            self.make_constraint(deform, 'COPY_SCALE', org)
        
        
    @classmethod
    def add_parameters(cls, params):
        """ Add custom parent parameters to the Rigify UI. """
        params.head_tweak_parent = bpy.props.StringProperty(
            name="Head Parent",
            description="Name of the bone to parent the tweak at head to (default: root/parent)",
            default=""
        )
        params.tail_tweak_parent = bpy.props.StringProperty(
            name="Tail Parent",
            description="Name of the bone to parent the tweak at the tail to (default: root/parent)",
            default=""
        )

    @classmethod
    def parameters_ui(cls, layout, params):
        """ Draw the parameters in the UI. """
        layout.prop(params, "head_tweak_parent")
        layout.prop(params, "tail_tweak_parent")
