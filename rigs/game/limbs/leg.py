import bpy
import math

from rigify.rigs.limbs.leg import Rig as leg
from rigify.rigs.limbs.leg import create_sample as orig_create_sample
from rigify.base_rig import stage
from rigify.utils.naming import make_derived_name
from rigify.utils.bones import put_bone
from rigify.rigs.widgets import create_ball_socket_widget
from rigify.utils.widgets import adjust_widget_transform_mesh
from mathutils import Matrix

from .limb_rigs import BaseLimbRig

class Rig(BaseLimbRig, leg):
    ik_toe_spin: str

    @stage.generate_bones
    def make_heel_control_bone(self):
        super().make_heel_control_bone()
        self.ik_toe_spin = self.make_ik_toe_spin_bone(self.bones.org.main)
        
    def make_ik_toe_spin_bone(self, orgs: list[str]):
        org = orgs[3]
        name = self.copy_bone(org, make_derived_name(org, 'ctrl', '_spin_ik'))
        put_bone(self.obj, name, self.get_bone(org).tail, scale=0.5)
        return name
        
    @stage.parent_bones
    def parent_heel_control_bone(self):
        super().parent_heel_control_bone()
        self.parent_ik_toe_spin_bone()

    def parent_ik_toe_spin_bone(self):
        if self.pivot_type == 'ANKLE_TOE':
            self.set_bone_parent(self.ik_toe_spin, self.get_ik_control_output())
            self.set_bone_parent(self.bones.ctrl.ik_spin, self.ik_toe_spin)
        else:
            self.set_bone_parent(self.ik_toe_spin, self.get_ik_control_output())
            self.set_bone_parent(self.bones.ctrl.heel, self.ik_toe_spin)

    @stage.generate_widgets
    def make_ik_spin_control_widget(self):
        obj = create_ball_socket_widget(self.obj, self.ik_toe_spin, size=0.75)
        #rot_fix = Matrix.Rotation(math.pi/2, 4, self.main_axis.upper())
        #adjust_widget_transform_mesh(obj, rot_fix, local=True)
def create_sample(obj):
    bones = orig_create_sample(obj)

    pbone = obj.pose.bones[bones['thigh.L']]
    pbone.rigify_type = 'game.leg'
