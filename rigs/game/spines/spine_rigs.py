import bpy

from ...chain_rigs import TweakChainRig, ConnectingChainRig

class BaseSpineRig(TweakChainRig):

    bbone_segments = None

    def initialize(self):
        super().initialize()



    def rig_deform_bone(self, i, deform, tweak, next_tweak):
        self.make_constraint(deform, 'COPY_LOCATION', tweak)
        self.make_constraint(deform, 'COPY_ROTATION', tweak)
        if next_tweak:
            self.make_constraint(deform, 'DAMPED_TRACK', next_tweak)


    @classmethod
    def parameters_ui(self, layout, params):
        """ Create the ui for the rig parameters.
        """
        super().parameters_ui(layout, params)


class BaseHeadTailRig(ConnectingChainRig):

    def initialize(self):
        super().initialize()


    def rig_deform_bone(self, i, deform, org):
        self.make_constraint(deform, 'COPY_LOCATION', org)
        self.make_constraint(deform, 'COPY_ROTATION', org)

    @classmethod
    def parameters_ui(self, layout, params):
        """ Create the ui for the rig parameters.
        """
        super().parameters_ui(layout, params)

