import bpy

from rigify.rigs.spines.basic_spine import Rig as basic_spine
from rigify.rigs.spines.basic_spine import create_sample as orig_create_sample
from rigify.utils.bones import align_bone_orientation
from .spine_rigs import BaseSpineRig


class Rig(BaseSpineRig, basic_spine):
    """
    Spine rig with fixed pivot, hip/chest controls and tweaks.
    """
    move_pivot: bool

    def initialize(self):
        super().initialize()
        #if pivot_pos is at the last bone then put it on prev bone
        self.move_pivot = (self.pivot_pos == len(self.bones.org)-1)

    def get_master_control_pos(self, orgs: list[str]):
        return self.get_bone(orgs[0]).head
    
    def make_mch_pivot_bone(self, org: str, name: str):
        # Move pivot bone down if True
        if self.move_pivot:
            org = self.bones.org[self.pivot_pos - 1]
        name = super().make_mch_pivot_bone(org, name)
        return name
    
    def parent_mch_control_bones(self):
        super().parent_mch_control_bones()
        if self.move_pivot:
            mch = self.bones.mch
            fk = self.fk_result
            self.set_bone_parent(mch.pivot, fk.hips[-1])
            align_bone_orientation(self.obj, mch.pivot, fk.hips[-2])

    def parent_tweak_chain(self):
        if self.move_pivot:
            mch = self.bones.mch
            chain = self.fk_result
            parents = [chain.hips[0], *chain.hips[0:-2], mch.pivot, *chain.chest, chain.chest[-1]]
            for args in zip(self.bones.ctrl.tweak, parents):
                self.set_bone_parent(*args)
        else:
            super().parent_tweak_chain()
    
    def rig_mch_control_bones(self):
        if self.move_pivot:
            mch = self.bones.mch
            self.make_constraint(mch.pivot, 'COPY_TRANSFORMS', self.fk_result.hips[-2], influence=0.5)
        else:
            super().rig_mch_control_bones()



def create_sample(obj):
    """ Create a sample metarig for this rig type.
    """
    bones = orig_create_sample(obj)

    pbone = obj.pose.bones[bones['spine']]
    pbone.rigify_type = 'game.spines.basic_spine'

    return bones