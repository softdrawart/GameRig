import bpy
from mathutils import Vector
from bpy.types import PoseBone
from rigify.base_rig import BaseRig, stage, RigComponent
from rigify.utils.naming import make_derived_name, change_name_side, Side
from rigify.utils.bones import TypedBoneDict, BaseBoneDict, put_bone



class Rig(BaseRig):
    cluster_control = None

    ####################################################
    # BONES
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
        if not self.cluster_control:
            EyeClusterControl(self)
    
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




    #renames ORG to DEF and put it to ORG bones
    def find_org_bones(self, pose_bone: PoseBone) -> BaseBoneDict:
        bones = self.OrgBones()
        old_bones = [pose_bone.name] + [bone.name for bone in pose_bone.children]
        for i, old_name in enumerate(old_bones):
            if i == 0:
                bones.eye = self.generator.rename_org_bone(old_name, make_derived_name(old_name, 'def'))
            elif '_top' or '_up' in old_name.lower():
                bones.eye_lid_top = self.generator.rename_org_bone(old_name, make_derived_name(old_name, 'def'))
            elif '_bottom' or '_down' in old_name.lower():
                bones.eye_lid_bottom = self.generator.rename_org_bone(old_name, make_derived_name(old_name, 'def'))
        return bones
    

    
####################################################
# Cluster rig
class EyeClusterControl(RigComponent):
    rigify_sub_object_run_late = True
    owner: Rig
    rig_list: list[Rig]
    master_bone: str


    def __init__(self, owner: Rig):
        super().__init__(owner)

        self.find_cluster_rigs()

    def find_cluster_rigs(self):
        owner = self.owner
        self.rig_list = [owner]

        parent_rig = owner.rigify_parent
        if parent_rig:
            for rig in parent_rig.rigify_children:
                if isinstance(rig, Rig) and rig != owner:
                    rig.cluster_control = self
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
            target_bone_name = self.owner.bones.ctrl.target
            self.master_bone = master_bone_name = self.copy_bone(target_bone_name, make_derived_name(change_name_side(target_bone_name, side=Side.MIDDLE), 'ctrl', suffix='_C'), parent=True)
            put_bone(self.obj, master_bone_name, new_position)



                    

