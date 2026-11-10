import bpy
from rigify.base_rig import BaseRig, stage
from rigify.rigs.spines.super_head import Rig as HeadRig
from math import radians

from bpy.types import PoseBone
from rigify.utils.misc import map_list, ArmatureObject
from rigify.utils.rig import is_rig_base_bone, connected_children_names
from rigify.utils.bones import is_same_position, put_bone, flip_bone, align_bone_orientation
from rigify.utils.naming import make_derived_name
from rigify.utils.widgets_basic import create_sphere_widget

from itertools import count

def bone_siblings(obj: ArmatureObject, bone: str) -> list[str]:
    """ Returns a list of the siblings of the given bone.
        This requires that the bones has a parent.
    """
    parent = obj.data.bones[bone].parent
    connected_siblings = connected_children_names(obj, parent.name)

    if parent is None:
        return []

    bones = []

    for b in parent.children:
        if b.name != bone and not is_rig_base_bone(obj, b.name) and b.name not in connected_siblings:
            bones += [b.name]

    return bones

class Rig(BaseRig):
    """ A "chain_skin" rig.  A set of sibling bones that move based on the parent chain rig.
        This is a control and deformation rig.
    """
    class MchBones(BaseRig.MchBones):
        tip: list[str]
        main: list[str]
        mid: list[str]  # Changed to list to support multiple middle bones
        direction: list[str] # Changed to list

    class CtrlBones(BaseRig.CtrlBones):
        tip: list[str]

    bones: BaseRig.ToplevelBones[
        list[str],
        'Rig.CtrlBones',
        'Rig.MchBones',
        list[str]
    ]

    def find_org_bones(self, bone: PoseBone) -> list[str]:
        base_head = bone.bone.head
        siblings = bone_siblings(self.obj, bone.name)

        # Sort list by name and distance
        siblings.sort()
        siblings.sort(key=lambda b: (self.get_bone(b).bone.head - base_head).length)

        return [bone.name] + siblings
        
    def initialize(self):
        #test
        print(f"initialise: bone {self.bones.org[1]} position {self.get_bone(self.bones.org[1]).tail}")
        org = self.bones.org
        if not isinstance(self.rigify_parent, HeadRig):
            self.raise_error('Parent rig of the {} must be Super Head Rig Type', org[0])
        parent_org = self.rigify_parent.bones.org
        
        # Now requires at least 2 bones
        if len(org) < 2:
            self.raise_error('Amount of bones for {} must be at least 2', org[0])
            
        for org_bone, parent_org_bone in zip(org, parent_org):
            if not is_same_position(self.obj, org_bone, parent_org_bone):
                self.raise_error('Bone {} and {} should be in the same position', org_bone, parent_org_bone)

    def prepare_bones(self):
        #parent org bones temporary
        parent_org = self.rigify_parent.bones.org
        for org_bone, parent_org_bone in zip(self.bones.org, parent_org):
            self.set_bone_parent(org_bone, parent_org_bone)

    def parent_bones(self):
        self.rig_parent_bone = parent = self.get_bone_parent(self.bones.org[0])
        self.rig_parent_parent_bone = self.get_bone_parent(parent) 
        #parent org bones temporary
        parent_org = self.rigify_parent.bones.deform
        for org_bone, parent_org_bone in zip(self.bones.org, parent_org):
            self.set_bone_parent(org_bone, parent_org_bone)
        
    ##############################
    # Tip bones MCH and CTRL
    @stage.generate_bones
    def make_tip_controls(self):
        self.bones.ctrl.tip = map_list(self.make_tip_contorol, self.bones.org)

    def make_tip_contorol(self, org:str):
        bone = self.copy_bone(org, make_derived_name(org, 'ctrl', '_tip'), scale=0.2)
        pos = self.get_bone(org).tail
        put_bone(self.obj, bone, pos)
        return bone

    @stage.generate_bones
    def make_tip_mchs(self):
        self.bones.mch.tip = map_list(self.make_tip_mch, self.bones.ctrl.tip, self.rigify_parent.bones.org)
        
        self.bones.mch.mid = []
        if len(self.bones.org) > 2:
            for i in range(1, len(self.bones.ctrl.tip) - 1):
                mid_ctrl = self.bones.ctrl.tip[i]
                mid_mch = self.copy_bone(mid_ctrl, make_derived_name(mid_ctrl, 'mch', '_mid'), parent=True, scale=.5)
                self.bones.mch.mid.append(mid_mch)

    def make_tip_mch(self, ctrl:str, align_bone:str):
        bone = self.copy_bone(ctrl, make_derived_name(ctrl, 'mch'), scale=1.2)
        align_bone_orientation(self.obj, bone, align_bone)
        return bone

    @stage.parent_bones
    def parent_tip_controlers(self):
        for i, ctrl, mch in zip(count(0), self.bones.ctrl.tip, self.bones.mch.tip):
            self.set_bone_parent(ctrl, mch)

    @stage.parent_bones
    def parent_tip_mch(self):
            mch = self.bones.mch.tip
            parent = self.rigify_parent.bones.ctrl
            
            # 1. Parent the first bone
            self.set_bone_parent(mch[0], self.rig_parent_parent_bone)
            
            # 2. Parent the last bone
            self.set_bone_parent(mch[-1], parent.head)
            
            # 3. Only parent the second-to-last bone to 'neck' if it's NOT the first bone
            if len(mch) > 2:
                self.set_bone_parent(mch[-2], parent.neck)

    @stage.rig_bones
    def rig_tip_mch_bones(self):

        def find_distance(a:str, b:str):
            pos_a = self.get_bone(a).head
            pos_b = self.get_bone(b).head
            return (pos_b - pos_a).length   

        mch = self.bones.mch.tip
        ctrl = self.bones.ctrl.tip
        parent_org = self.rigify_parent.bones.org
        
        # First bone transform
        co = self.make_constraint(mch[0], 'TRANSFORM', parent_org[0], space='LOCAL', map_from='ROTATION', map_to='LOCATION')
        co.from_max_x_rot = radians(150)
        co.to_max_y = -.35
        co.to_max_z = -.09
        co.map_to_y_from = 'X'
        co.map_to_z_from = 'X'
        co = self.make_constraint(mch[0], 'LIMIT_DISTANCE', parent_org[0], distance=find_distance(mch[0], parent_org[0]),
                        limit_mode='LIMITDIST_OUTSIDE', use_transform_limit=True,)

        # Last bone transform (uses index -1 instead of hardcoded 2)
        co = self.make_constraint(mch[-1], 'TRANSFORM', parent_org[-1], space='LOCAL', map_from='ROTATION', map_to='LOCATION')
        co.from_min_x_rot = radians(-100)
        co.from_max_x_rot = radians(100)
        co.to_min_y = -.2
        co.to_max_y = .2
        co.map_to_y_from = 'X'
        co = self.make_constraint(mch[-1], 'LIMIT_DISTANCE', parent_org[-1], distance=find_distance(mch[-1], parent_org[-1]),
                                limit_mode='LIMITDIST_OUTSIDE', use_transform_limit=True,)

        # Mid bones logic (skips if only 2 bones)
        if len(self.bones.org) > 2:
            start_pos = self.get_bone(self.bones.org[0]).tail
            end_pos = self.get_bone(self.bones.org[-1]).tail
            total_dist = (end_pos - start_pos).length
            #test
            print(f"initialise: bone {self.bones.org[1]} position {self.get_bone(self.bones.org[1]).tail}")
            for i, mid_mch in enumerate(self.bones.mch.mid):
                org_idx = i + 1
                curr_pos = self.get_bone(self.bones.org[org_idx]).tail
                
                # Calculate dynamic influence based on distance
                dist_from_start = (curr_pos - start_pos).length
                influence = 1.0 - (dist_from_start / total_dist) if total_dist > 0 else 0.5
                
                self.make_constraint(mid_mch, 'COPY_LOCATION', ctrl[0], space='WORLD', influence=1.0)
                self.make_constraint(mid_mch, 'COPY_LOCATION', ctrl[-1], space='WORLD', influence=1.0 - influence)

    @stage.generate_widgets
    def make_tip_widgets(self):
        for tip in self.bones.ctrl.tip:
            create_sphere_widget(self.obj, tip)

    ##############################
    # Main MCHs
    @stage.generate_bones
    def make_mch_bones(self):
        self.bones.mch.main = map_list(self.make_mch_bone, self.bones.org)

    def make_mch_bone(self, org:str):
        bone = self.copy_bone(org, make_derived_name(org, 'mch'))
        flip_bone(self.obj, bone)
        return bone

    @stage.parent_bones
    def parent_mch_main_bones(self): # Renamed to avoid duplicate stage name
        for child, parent in zip(self.bones.mch.main, self.rigify_parent.bones.deform):
            self.set_bone_parent(child, parent)

    @stage.rig_bones
    def rig_mch_bones(self):
        for mch, tip_ctrl, parent_org_bone in zip(self.bones.mch.main, self.bones.ctrl.tip, self.rigify_parent.bones.org):
            self.make_constraint(mch, 'COPY_LOCATION', tip_ctrl)
            self.make_constraint(mch, 'DAMPED_TRACK', parent_org_bone)

    ##############################
    # Direction mid MCH
    @stage.generate_bones
    def make_mid_direction_mch(self):
        self.bones.mch.direction = []
        if len(self.bones.org) > 2:
            for i in range(1, len(self.bones.org) - 1):
                mid_bone = self.bones.org[i]
                dir_mch = self.copy_bone(mid_bone, make_derived_name(mid_bone, 'mch', '_direction'))
                self.bones.mch.direction.append(dir_mch)

    @stage.parent_bones
    def parent_mid_direction_mch(self):
            if len(self.bones.org) > 2:
                for i, dir_mch in enumerate(self.bones.mch.direction):
                    org_idx = i + 1
                    # Parent to the parent rig's ORG bone to break the dependency cycle
                    self.set_bone_parent(dir_mch, self.rigify_parent.bones.deform[org_idx])

    @stage.rig_bones
    def rig_mid_direction_mch(self):
        if len(self.bones.org) > 2:
            for i, direction in enumerate(self.bones.mch.direction):
                org_idx = i + 1
                self.make_constraint(direction, 'COPY_LOCATION', self.rigify_parent.bones.org[org_idx])
                self.make_constraint(direction, 'DAMPED_TRACK', self.bones.mch.mid[i])
                self.make_constraint(self.bones.mch.tip[org_idx], 'COPY_LOCATION', direction, head_tail=1)

    ##############################
    # DEF bones
    @stage.generate_bones
    def make_def_bones(self):
        self.bones.deform = map_list(lambda b: self.copy_bone(b, make_derived_name(b, 'def'), parent=True), self.bones.org)

    @stage.rig_bones
    def rig_def_bones(self):
        for b, b2 in zip(self.bones.deform, self.bones.org):
            self.make_constraint(b, 'COPY_LOCATION', b2)
            self.make_constraint(b, 'COPY_ROTATION', b2)

    @stage.parent_bones
    def parent_def_bones(self):
        children = self.bones.deform
        parents = self.rigify_parent.bones.deform
        for i, child, parent in zip(count(0), children, parents):
            if i == 0:
                parent = self.rigify_parent.rigify_parent.bones.org[-1]
                self.set_bone_parent(children[0], make_derived_name(parent,'def'))
            else:
                self.set_bone_parent(child, parent)

    ##############################
    # ORG bones
    @stage.parent_bones
    def parent_org_bones(self): # Renamed to avoid duplicate stage name
        for child, parent in zip(self.bones.org, self.bones.mch.main):
            self.set_bone_parent(child, parent)


def create_sample(obj):  # noqa
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('neck')
    bone.head = -0.0000, 0.2287, 0.1410
    bone.tail = -0.0000, 0.1653, 0.1599
    bone.roll = 0.0000
    bone.use_connect = False
    bones['neck'] = bone.name
    bone = arm.edit_bones.new('neck.001')
    bone.head = -0.0000, 0.1653, 0.1599
    bone.tail = -0.0000, 0.1140, 0.1910
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['neck']]
    bones['neck.001'] = bone.name
    bone = arm.edit_bones.new('skin3')
    bone.head = -0.0000, 0.1140, 0.1910
    bone.tail = -0.0000, 0.0210, 0.0390
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['neck']]
    bones['skin3'] = bone.name
    bone = arm.edit_bones.new('skin2')
    bone.head = -0.0000, 0.1653, 0.1599
    bone.tail = -0.0000, 0.1016, 0.0158
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['neck']]
    bones['skin2'] = bone.name
    bone = arm.edit_bones.new('skin1')
    bone.head = -0.0000, 0.2287, 0.1410
    bone.tail = -0.0000, 0.1960, -0.0122
    bone.roll = -3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['neck']]
    bones['skin1'] = bone.name
    bone = arm.edit_bones.new('head')
    bone.head = -0.0000, 0.1140, 0.1910
    bone.tail = -0.0000, 0.0227, 0.3671
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['neck.001']]
    bones['head'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['neck']]
    pbone.rigify_type = 'game.spines.super_head'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.connect_chain = False
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.enable_scale = False
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['neck.001']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['skin3']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['skin2']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['skin1']]
    pbone.rigify_type = 'vizor.spines.chain_skin'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['head']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in arm.edit_bones:
        bone.select = False
        bone.select_head = False
        bone.select_tail = False
    for b in bones:
        bone = arm.edit_bones[bones[b]]
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        bone.bbone_x = bone.bbone_z = bone.length * 0.05
        arm.edit_bones.active = bone
        if bcoll := arm.collections.active:
            bcoll.assign(bone)

    return bones
