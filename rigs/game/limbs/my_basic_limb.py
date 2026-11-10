import bpy
from rigify.rigs.limbs.limb_rigs import BaseLimbRig
from mathutils import Matrix, Vector
from rigify.utils.widgets import adjust_widget_transform_mesh
from rigify.utils.bones import align_chain_x_axis, align_bone_x_axis, align_bone_z_axis, put_bone
from rigify.utils.misc import matrix_from_axis_roll, matrix_from_axis_pair
from rigify.rigs.widgets import create_foot_widget
from rigify.utils.naming import make_derived_name


class Rig(BaseLimbRig):
    """Basic 3 bones limb rig with a single IK system."""
    def prepare_bones(self):
            orgs = self.bones.org.main
            foot = self.get_bone(orgs[2])
    
            ik_y_axis = (0, 1, 0)
            foot_y_axis = -self.vector_without_z(foot.y_axis)
            foot_x = foot_y_axis.cross((0, 0, 1))
    
            if self.params.rotation_axis == 'automatic':
                align_chain_x_axis(self.obj, orgs[0:2])
    
                # Orient foot and toe
                align_bone_x_axis(self.obj, orgs[2], foot_x)
    
                align_bone_x_axis(self.obj, self.bones.org.heel, Vector((0, 0, 1)))
    
            elif self.params.auto_align_extremity:
                if self.main_axis == 'x':
                    align_bone_x_axis(self.obj, orgs[2], foot_x)
                else:
                    align_bone_z_axis(self.obj, orgs[2], foot_x)
    
            else:
                ik_y_axis = foot_y_axis
    
            # Orientation of the IK main and roll control bones
            self.ik_matrix = matrix_from_axis_roll(ik_y_axis, 0)
            self.roll_matrix = matrix_from_axis_pair(ik_y_axis, foot_x, self.main_axis)

    def make_ik_control_bone(self, orgs):
            name = self.copy_bone(orgs[2], make_derived_name(orgs[2], 'ctrl', '_ik'))
            put_bone(self.obj, name, None, matrix=self.ik_matrix)
            return name

    def make_ik_ctrl_widget(self, ctrl):
        # Create the basic foot widget mesh
        obj = create_foot_widget(self.obj, ctrl)

        ctrl_pbone = self.get_bone(ctrl)
        org_bone = self.get_bone(self.bones.org.main[-1]) 
        shape_pbone = ctrl_pbone.custom_shape_transform or ctrl_pbone

        offset_vector = org_bone.tail - shape_pbone.head
        offset_vector.z = offset_vector.z - org_bone.tail.z
        matrix = Matrix.Translation(offset_vector)
        
        adjust_widget_transform_mesh(obj, matrix, local=False)

        scale = 3.0

        scale_matrix = Matrix.Diagonal((scale, scale, 1.0, 1.0))
        adjust_widget_transform_mesh(obj, scale_matrix, local=True)