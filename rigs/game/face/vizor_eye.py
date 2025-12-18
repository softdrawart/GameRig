import bpy
from mathutils import Vector
from bpy.types import PoseBone
from rigify.base_rig import BaseRig, stage, BaseRigMixin
from rigify.utils.naming import make_derived_name, change_name_side, Side
from rigify.utils.bones import TypedBoneDict, BaseBoneDict, put_bone, align_bone_roll
from rigify.base_generate import GeneratorPlugin, BaseGenerator
from rigify.utils.widgets import create_registered_widget
from math import degrees, radians

def calculate_alignment_rotation(obj, pb_a, pb_b):
    """Return result in radians"""
    if not obj or obj.type != 'ARMATURE':
        print(f"Error: Armature '{armature_name}' not found.")
    if not pb_a or not pb_b:
        print("Error: Could not find one or both bones.")
        return

    matrix_aligned_local = obj.convert_space(
        pose_bone=pb_a,
        matrix=pb_b.matrix,
        from_space='POSE',
        to_space='LOCAL'
    )

    rotation_needed = matrix_aligned_local.to_euler('XYZ')
    
    return rotation_needed

class Rig(BaseRig):

    ####################################################
    # BONES
    parent_bone: str

    class OrgBones(TypedBoneDict):
        eye: str
        eye_lid_top: str
        eye_lid_bottom: str

    class CtrlBones(TypedBoneDict):
        target: str
        eye_lid_top: str
        eye_lid_bottom: str

    bones: BaseRig.ToplevelBones[
        'Rig.OrgBones', #ORG bones are renamed and placed here as Def bones are here
        'Rig.CtrlBones', #lid controllers and target controller
        str, #empty
        str #empty
    ]

    def initialize(self):
        cluster_control = EyeClusterControl(self.generator)
        cluster_control.register_rig(self)
        #renames ORG to DEF and put it to ORG bones
    
    def find_org_bones(self, pose_bone: PoseBone) -> BaseBoneDict:
        self.parent_bone = pose_bone.parent.name
        bones = self.OrgBones()
        old_bones = [pose_bone.name] + [bone.name for bone in pose_bone.children]
        for i, old_name in enumerate(old_bones):
            if i == 0:
                bones.eye = self.generator.rename_org_bone(old_name, make_derived_name(old_name, 'def'))
            elif any(s in old_name.lower() for s in ('_top', '_up')):
                bones.eye_lid_top = self.generator.rename_org_bone(old_name, make_derived_name(old_name, 'def'))
            elif any(s in old_name.lower() for s in ('_bottom', '_down')):
                bones.eye_lid_bottom = self.generator.rename_org_bone(old_name, make_derived_name(old_name, 'def'))
        return bones
    
    ####################################################
    # target bone
    @stage.generate_bones
    def make_target_bone(self):
        bone_name = self.bones.org.eye
        self.bones.ctrl.target = bone = self.copy_bone(bone_name, make_derived_name(bone_name, 'ctrl', suffix='_C'), parent=True)
        org_bone = self.get_bone(bone_name)
        new_position = org_bone.head + ((org_bone.tail - org_bone.head) * 5)  #normalized()
        put_bone(self.obj, bone, new_position)
    @stage.rig_bones
    def rig_target_bone(self):
        target_bone_name = self.bones.ctrl.target
        owner_bone_name = self.bones.org.eye
        self.make_constraint(owner_bone_name, 'DAMPED_TRACK', target_bone_name, track_axis='Y')
    ####################################################
    # def/org bones   
    @stage.parent_bones
    def parent_def_bones(self):
        parent = self.parent_bone
        self.set_bone_parent(self.bones.org.eye_lid_top, parent)
        self.set_bone_parent(self.bones.org.eye_lid_bottom, parent)
    ####################################################
    # eye_lid bones 
    @stage.generate_bones
    def make_lid_bones(self):
        bone = self.bones.ctrl.eye_lid_top = self.copy_bone(self.bones.org.eye_lid_top, make_derived_name(self.bones.org.eye_lid_top, 'ctrl', suffix='_C'), parent=True)
        pbone = self.get_bone(bone)
        length = pbone.length
        new_position = pbone.tail
        put_bone(self.obj, bone, new_position)

        bone2 = self.bones.ctrl.eye_lid_bottom = self.copy_bone(self.bones.org.eye_lid_bottom, make_derived_name(self.bones.org.eye_lid_bottom, 'ctrl', suffix='_C'), parent=True)
        pbone2 = self.get_bone(bone2)
        new_position = pbone2.tail
        put_bone(self.obj, bone2, new_position)

        #move out and orient lid controllers in the direction
        vec = (pbone.tail - pbone.head).normalized()
        vec[2] = 0 #exclude z from direction
        axis_idx, axis_val = max(enumerate(vec), key=lambda i: abs(i[1]))
        move_offset = Vector((0, 0, 0))
        sign = 1 if axis_val >= 0 else -1
        move_offset[axis_idx] = length * sign

        #orient bones stright
        for bone in [pbone, pbone2]:
            bone.head += move_offset
            bone.tail = bone.head +  move_offset
            align_bone_roll(self.obj, bone.name, self.bones.org.eye_lid_top)
    @stage.parent_bones
    def parent_lid_bones(self):
        bones = self.bones.ctrl
        for bone in [bones.eye_lid_top, bones.eye_lid_bottom]:
            self.set_bone_parent(bone, self.parent_bone)
    @stage.rig_bones
    def rig_lid_bones(self):
        ctrl = self.bones.ctrl
        
        bone_pairs = zip(
            [ctrl.eye_lid_top, ctrl.eye_lid_bottom], 
            [self.bones.org.eye_lid_top, self.bones.org.eye_lid_bottom]
        )

        angleMin = calculate_alignment_rotation(self.obj, self.get_bone(self.bones.org.eye_lid_top), self.get_bone(self.bones.org.eye_lid_bottom))[0] #isolate X rotation value
        angleMin = degrees(angleMin)
        angleMax = 20
        targetMin = -0.04
        targetMax = (targetMin * angleMax)/(angleMin) #find max value using linear relationship Ratio Rule

        for i, (controller, owner_bone_name) in enumerate(bone_pairs):
            self.make_constraint(
                owner_bone_name, 
                'COPY_ROTATION', 
                self.bones.org.eye, 
                use_x=True, use_y=False, use_z=False,  # explicit axis locking
                owner_space='LOCAL', target_space='LOCAL'
            )
            min =-abs(targetMin) if i==0 else -abs(targetMax)
            max = abs(targetMax) if i==0 else abs(targetMin)
            self.make_constraint(
                owner_bone_name, 
                'TRANSFORM', 
                controller, 
                owner_space='LOCAL', target_space='LOCAL',
                map_from='LOCATION', map_to='ROTATION',
                map_to_x_from='Z',
                map_to_z_from='X',
                from_min_z=min, from_max_z=max,  # Input range
                to_min_x_rot=-abs(radians(angleMin)) if i==0 else -abs(radians(angleMax)), to_max_x_rot=abs(radians(angleMax)) if i==0 else abs(radians(angleMin)) # Output range
            )
            """ con = self.make_constraint(
                owner_bone_name, 
                'LIMIT_ROTATION', 
                owner_space='LOCAL',
                use_limit_x=True, min_x=radians(-50.2) if i==0 else radians(-6.2), max_x=radians(6.2) if i==0 else radians(50.2), # Lock Y
            )
            if con and con.use_legacy_behavior:
                con.use_legacy_behavior=False """
            #rig Target Bones
            self.make_constraint(
                controller, 
                'LIMIT_LOCATION', 
                min_z=min, max_z=max,
                owner_space='LOCAL'
            )
            
    def configure_bones(self):
        bones = self.bones.ctrl.eye_lid_top, self.bones.ctrl.eye_lid_bottom
        for bone in bones:
            pbone = self.get_bone(bone)
            pbone.lock_rotation = [True]*3
            pbone.lock_rotation_w = True
            pbone.lock_location = [True]*2 + [False]
            pbone.lock_scale = [True]*3

    def generate_widgets(self):
        bones = self.bones.ctrl.eye_lid_top, self.bones.ctrl.eye_lid_bottom, self.bones.ctrl.target
        for bone in bones:
            create_registered_widget(self.obj, bone, 'circle')


    

    
####################################################
# Cluster rig
class EyeClusterControl(GeneratorPlugin, BaseRigMixin):
    rig_list: list[Rig] = []
    master_bone: str


    def __init__(self, generator: BaseGenerator):
        super().__init__(generator)

    def register_rig(self,  rig: Rig):
        if isinstance(rig, Rig):
            self.rig_list.append(rig)
    ####################################################
    # master bone
    @stage.generate_bones
    def make_master_bone(self):
        if len(self.rig_list) > 1:
            new_position = Vector((0,0,0))
            for rig in self.rig_list:
                new_position += self.get_bone(rig.bones.ctrl.target).head
            new_position /= len(self.rig_list) #get avarage position for master control
            target_bone_name = self.rig_list[0].bones.ctrl.target
            self.master_bone = master_bone_name = self.copy_bone(target_bone_name, make_derived_name(change_name_side(target_bone_name, side=Side.MIDDLE), 'ctrl', suffix='_C'), parent=True)
            put_bone(self.obj, master_bone_name, new_position)
    @stage.parent_bones
    def parent_target_bones_to_master(self):
        for rig in self.rig_list:
            self.set_bone_parent(rig.bones.ctrl.target, self.master_bone)
    
    def generate_widgets(self):
        create_registered_widget(self.obj, self.master_bone, 'diamond')



def create_sample(obj):  # noqa
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('eye.R')
    bone.head = -0.0415, -0.0755, 1.3777
    bone.tail = -0.0415, -0.1030, 1.3776
    bone.roll = 3.1416
    bone.use_connect = False
    bones['eye.R'] = bone.name
    bone = arm.edit_bones.new('eye_up.R')
    bone.head = -0.0415, -0.0755, 1.3777
    bone.tail = -0.0459, -0.1104, 1.3882
    bone.roll = 2.3681
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['eye.R']]
    bones['eye_up.R'] = bone.name
    bone = arm.edit_bones.new('eye_down.R')
    bone.head = -0.0415, -0.0755, 1.3777
    bone.tail = -0.0472, -0.1047, 1.3601
    bone.roll = -2.5587
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['eye.R']]
    bones['eye_down.R'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['eye.R']]
    pbone.rigify_type = 'game.face.vizor_eye'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.enable_scale = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.make_widget = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.relink_constraints = True
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['eye_up.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.enable_scale = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.relink_constraints = True
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['eye_down.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    try:
        pbone.rigify_parameters.enable_scale = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.make_widget = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.relink_constraints = True
    except AttributeError:
        pass

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
