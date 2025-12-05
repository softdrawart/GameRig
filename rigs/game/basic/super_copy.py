import bpy
from math import degrees

from rigify.rigs.basic.super_copy import Rig as super_copy
from rigify.rigs.basic.super_copy import create_sample as orig_create_sample
from rigify.utils.naming import strip_org, make_deformer_name
from rigify.utils.widgets import create_registered_widget
from rigify.utils.widgets_basic import create_bone_widget

#from rigify.utils.widgets import widget_generator
from ....utils.bones import BoneUtilityMixin
from ....utils.space_switch import gameRig_switch_parents

class Rig(BoneUtilityMixin, super_copy):
    """ A "copy" rig.  All it does is duplicate the original bone and
        constrain it.
        This is a control and deformation rig.

    """

    def initialize(self):
        super().initialize()

        """ Gather and validate data about the rig.
        """
        self.enable_scale = self.params.enable_scale

    def generate_bones(self):
        bones = self.bones

        # Make a control bone (copy of original).
        if self.make_control:
            bones.ctrl = self.copy_bone(bones.org, self.org_name, parent=True)

        # Make a deformation bone (copy of original, child of original).
        if self.make_deform:
            bones.deform = self.copy_bone(bones.org, make_deformer_name(self.org_name), parent = True, bbone=False)
    

    def parent_bones(self):
        bones = self.bones

        new_parent = self.relink_bone_parent(bones.org)

        if self.make_control and new_parent:
            self.set_bone_parent(bones.ctrl, new_parent)
        # This puts the deformation bones into the def hierarchy of its parent rig
        if self.make_deform:
            self.clean_def_hierarchy(self.bones.deform)


    def rig_bones(self):
        bones = self.bones

        self.relink_bone_constraints(bones.org)

        if self.make_control:
            self.relink_move_constraints(bones.org, bones.ctrl, prefix='CTRL:')

            # Constrain the original bone.
            self.make_constraint(bones.org, 'COPY_TRANSFORMS', bones.ctrl, insert_index=0)

        if self.make_deform:
            if self.enable_scale:
                self.make_constraint(bones.deform, 'COPY_TRANSFORMS', bones.org)
            else:
                self.make_constraint(bones.deform, 'COPY_LOCATION', bones.org)
                self.make_constraint(bones.deform, 'COPY_ROTATION', bones.org)

    def configure_bones(self):
        if self.bones.ctrl:
            controls = {'ctrl': [self.bones.ctrl]}
            #self.remove_quat_rot_mode(controls)
        
    def generate_widgets(self):
        bones = self.bones

        if self.make_control:
            # Create control widget
            if self.make_widget:
                create_registered_widget(self.obj, bones.ctrl,
                                            self.params.super_copy_widget_type or 'circle')
                if self.params.super_copy_widget_type == 'shoulder':
                    pbone = self.get_bone(bones.ctrl)
                    if pbone.x_axis.z > 0:
                        pbone.custom_shape_rotation_euler[1] = degrees(-90)
                    else:
                        pbone.custom_shape_rotation_euler[1] = degrees(90)
            else:
                create_bone_widget(self.obj, bones.ctrl)

    @classmethod
    def add_parameters(self, params):
        """ Add the parameters of this rig type to the
            RigifyParameters PropertyGroup
        """
        super().add_parameters(params)
        params.enable_scale = bpy.props.BoolProperty(
            name="Scale",
            default=True,
            description="Deformation bones will inherit the scale of their ORG bones. Enable this only if you know what you are doing because scale can break your rig in the game engine"
        )

        params.switch_parents = bpy.props.CollectionProperty(type=gameRig_switch_parents)

    @classmethod
    def parameters_ui(self, layout, params):
        """ Create the ui for the rig parameters.
        """
        super().parameters_ui(layout, params)

        r = layout.row()
        r.prop(params, "enable_scale")
        # WIP of a new space switch system test, ignore it
        # col = layout.column()
        # for parent in params.switch_parents:
        #     col.label(text=parent.name)


    @classmethod
    def get_space_switch_children(self):
        """ Return list of names of bones for space switching
        """
        return ["bone"]

""" @widget_generator(register="shoulder_game")
def create_custom_widget(geom, *, radius=0.5):
    # Typically Rigify widgets treat 'radius' as the visual thickness.
    # We apply it to X and Z, but keep Y (length) constant at 1.0.
    r = radius 

    geom.verts = [(-5.960464477539063e-08, 0.0, -5.960464477539063e-08),
	 (-8.195638656616211e-08, 1.0, -3.632158041000366e-08),
	 (-0.2821650505065918, 0.27611100673675537, 0.4121399223804474),
	 (-0.16804707050323486, 0.31435999274253845, 0.4690059423446655),
	 (-0.07400184869766235, 0.37070798873901367, 0.4927109181880951),
	 (-0.01605677604675293, 0.4405969977378845, 0.4984188973903656),
	 (-1.1920928955078125e-07, 0.5, 0.49999991059303284),
	 (-0.016056418418884277, 0.5594019889831543, 0.4984188973903656),
	 (-0.07400110363960266, 0.6292909979820251, 0.4927119016647339),
	 (-0.16804605722427368, 0.6856399774551392, 0.4690059423446655),
	 (-0.282164067029953, 0.7238889932632446, 0.41214093565940857),
	 (-0.38359105587005615, 0.7423350214958191, 0.3169519305229187),
	 (-0.4534890651702881, 0.7477099895477295, 0.20715191960334778),
	 (-0.4896490275859833, 0.7494900226593018, 0.09999752044677734),
	 (-0.5, 0.75, -5.960464477539063e-08),
	 (-0.4896489977836609, 0.7494900226593018, -0.09999704360961914),
	 (-0.4534890353679657, 0.7477099895477295, -0.20715206861495972),
	 (-0.38359203934669495, 0.7423350214958191, -0.31695103645324707),
	 (-0.2821650207042694, 0.7238889932632446, -0.41214102506637573),
	 (-0.16804605722427368, 0.6856399774551392, -0.4690060019493103),
	 (-0.07400113344192505, 0.6292909979820251, -0.49271103739738464),
	 (-0.016056358814239502, 0.5594019889831543, -0.49841904640197754),
	 (-5.960464477539063e-08, 0.5, -0.5),
	 (-0.016056358814239502, 0.4405980110168457, -0.49841904640197754),
	 (-0.0740012526512146, 0.37070900201797485, -0.49271106719970703),
	 (-0.1680470108985901, 0.31435999274253845, -0.4690060019493103),
	 (-0.2821650207042694, 0.27611100673675537, -0.4121400713920593),
	 (-0.38359203934669495, 0.2576650083065033, -0.31695103645324707),
	 (-0.4534890353679657, 0.2522900104522705, -0.20715105533599854),
	 (-0.4896490275859833, 0.25051000714302063, -0.09999597072601318),
	 (-0.5, 0.25, -5.960464477539063e-08),
	 (-0.4896480441093445, 0.25051000714302063, 0.09999853372573853),
	 (-0.45348799228668213, 0.2522900104522705, 0.20715291798114777),
	 (-0.38359004259109497, 0.2576650083065033, 0.3169529139995575)]

    geom.edges = [[0, 1],
	 [2, 3],
	 [4, 3],
	 [5, 4],
	 [5, 6],
	 [6, 7],
	 [8, 7],
	 [8, 9],
	 [10, 9],
	 [10, 11],
	 [11, 12],
	 [13, 12],
	 [14, 13],
	 [14, 15],
	 [16, 15],
	 [16, 17],
	 [17, 18],
	 [19, 18],
	 [19, 20],
	 [21, 20],
	 [21, 22],
	 [22, 23],
	 [24, 23],
	 [25, 24],
	 [25, 26],
	 [27, 26],
	 [27, 28],
	 [29, 28],
	 [29, 30],
	 [30, 31],
	 [32, 31],
	 [32, 33],
	 [2, 33]]
 """
def create_sample(obj):
    """ Create a sample metarig for this rig type.
    """
    bones = orig_create_sample(obj)

    pbone = obj.pose.bones[bones['Bone']]
    pbone.rigify_type = 'game.basic.super_copy'

    return bones