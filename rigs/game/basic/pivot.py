import bpy, re

from rigify.rigs.basic.pivot import Rig as pivot
from rigify.rigs.basic.pivot import create_sample as orig_create_sample
from rigify.utils.naming import make_derived_name
from ....utils.bones import BoneUtilityMixin
from rigify.utils.switch_parent import SwitchParentBuilder


class Rig(BoneUtilityMixin, pivot):

    def initialize(self):
        super().initialize()

        """ Gather and validate data about the rig.
        """
        self.enable_scale = self.params.enable_scale
        self.parent_bones_names = self.build_list()
        self.default_parent = self.find_default_parent()
    
    #forms a list of bone names from parameter
    def build_list(self):
        string = self.params.parents
        if isinstance(string, str):
            parents = [stripped for item in string.split(',') if (stripped := item.strip())]
            return parents
        return []
    
    def find_default_parent(self):
        string = self.params.default_parent
        if isinstance(string, str):
            parent = string.replace(" ", "")
            if self.parent_bones_names:
                if parent in self.parent_bones_names:
                    return parent
        return 'root'


    def generate_bones(self):
        org = self.bones.org

        if self.make_control:
            self.bones.ctrl.master = name = self.copy_bone(org, make_derived_name(org, 'ctrl'), parent=True)

            if self.make_pivot:
                self.bones.ctrl.pivot = self.copy_bone(org, make_derived_name(org, 'ctrl', '_pivot'))

            if self.params.make_parent_switch:
                self.build_parent_switch(name)

            if self.params.register_parent:
                self.register_parent(name, self.get_parent_tags())



        else:
            self.bones.ctrl.pivot = self.copy_bone(org, make_derived_name(org, 'ctrl'), parent=True)

        if self.make_deform:
            self.bones.deform = self.copy_bone(org, make_derived_name(org, 'def'), parent = True, bbone=True)

    def build_parent_switch(self, master_name: str):
        pbuilder = SwitchParentBuilder(self.generator)

        org_parent = self.get_bone_parent(self.bones.org)
        parents = [org_parent] if org_parent else []
        if len(self.parent_bones_names) > 0:
            parents += self.parent_bones_names

        pbuilder.build_child(
            self, master_name,
            context_rig=self.rigify_parent, allow_self=True,
            prop_name="Parent ({})".format(master_name),
            extra_parents=parents, select_parent=self.default_parent or org_parent, exclude_self=True,
            controls=lambda: self.bones.ctrl.flatten()
        )

    def parent_bones(self):
        ctrl = self.bones.ctrl

        if self.make_pivot:
            if self.make_control:
                self.set_bone_parent(ctrl.pivot, ctrl.master, use_connect=False)

            self.set_bone_parent(self.bones.org, ctrl.pivot, use_connect=False)

        else:
            self.set_bone_parent(self.bones.org, ctrl.master, use_connect=False)

        if self.make_deform:
            self.clean_def_hierarchy(self.bones.deform)


    def configure_bones(self):
        super().configure_bones()
        #self.remove_quat_rot_mode(self.bones.ctrl)



    def rig_bones(self):
        super().rig_bones()
        if self.make_deform:
            if self.enable_scale:
                self.make_constraint(self.bones.deform, 'COPY_TRANSFORMS', self.bones.org)
            else:
                self.make_constraint(self.bones.deform, 'COPY_LOCATION', self.bones.org)
                self.make_constraint(self.bones.deform, 'COPY_ROTATION', self.bones.org)
   
   
    @classmethod
    def add_parameters(self, params):
        """ Add the parameters of this rig type to the
            RigifyParameters PropertyGroup
        """
        super().add_parameters(params)

        params.parents = bpy.props.StringProperty("Parents", description="Parents for switching separated by , ")
        params.default_parent = bpy.props.StringProperty("Default Parent", description="bone name selected as default parent")

        params.enable_scale = bpy.props.BoolProperty(
            name="Scale",
            default=True,
            description="Deformation bones will inherit the scale of their ORG bones. Enable this only if you know what you are doing because scale can break your rig in the game engine"
        )

    @classmethod
    def parameters_ui(self, layout, params):
        """ Create the ui for the rig parameters.
        """
        super().parameters_ui(layout, params)
        

        if params.make_extra_control:
            r = layout.column()
            r.active = params.make_parent_switch
            r.prop(params, 'parents', text="Extra Parents")
            r.prop(params, 'default_parent', text="Default Parent")

        r = layout.row()
        r.prop(params, "enable_scale")
        

def create_sample(obj):
    """ Create a sample metarig for this rig type.
    """
    bones = orig_create_sample(obj)

    pbone = obj.pose.bones[bones['pivot']]
    pbone.rigify_type = 'game.basic.pivot'

    return bones
