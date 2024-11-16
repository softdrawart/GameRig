import bpy

from rna_prop_ui import rna_idprop_ui_create

from mathutils import Color


def create(obj):  # noqa
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    for i in range(6):
        arm.rigify_colors.add()

    arm.rigify_colors[0].name = "Root"
    arm.rigify_colors[0].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[0].normal = Color((0.4353, 0.1843, 0.4157))
    arm.rigify_colors[0].select = Color((0.3140, 0.7840, 1.0000))
    arm.rigify_colors[0].standard_colors_lock = True
    arm.rigify_colors[1].name = "IK"
    arm.rigify_colors[1].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[1].normal = Color((0.6039, 0.0000, 0.0000))
    arm.rigify_colors[1].select = Color((0.3140, 0.7840, 1.0000))
    arm.rigify_colors[1].standard_colors_lock = True
    arm.rigify_colors[2].name = "Special"
    arm.rigify_colors[2].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[2].normal = Color((0.9569, 0.7882, 0.0471))
    arm.rigify_colors[2].select = Color((0.3140, 0.7840, 1.0000))
    arm.rigify_colors[2].standard_colors_lock = True
    arm.rigify_colors[3].name = "Tweak"
    arm.rigify_colors[3].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[3].normal = Color((0.0392, 0.2118, 0.5804))
    arm.rigify_colors[3].select = Color((0.3140, 0.7840, 1.0000))
    arm.rigify_colors[3].standard_colors_lock = True
    arm.rigify_colors[4].name = "FK"
    arm.rigify_colors[4].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[4].normal = Color((0.1176, 0.5686, 0.0353))
    arm.rigify_colors[4].select = Color((0.3140, 0.7840, 1.0000))
    arm.rigify_colors[4].standard_colors_lock = True
    arm.rigify_colors[5].name = "Extra"
    arm.rigify_colors[5].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[5].normal = Color((0.9686, 0.2510, 0.0941))
    arm.rigify_colors[5].select = Color((0.3140, 0.7840, 1.0000))
    arm.rigify_colors[5].standard_colors_lock = True

    bone_collections = {}

    for bcoll in list(arm.collections_all):
        arm.collections.remove(bcoll)

    def add_bone_collection(name, *, parent=None, ui_row=0, ui_title='', sel_set=False, color_set_id=0):
        new_bcoll = arm.collections.new(name, parent=bone_collections.get(parent))
        new_bcoll.rigify_ui_row = ui_row
        new_bcoll.rigify_ui_title = ui_title
        new_bcoll.rigify_sel_set = sel_set
        new_bcoll.rigify_color_set_id = color_set_id
        bone_collections[name] = new_bcoll

    def assign_bone_collections(pose_bone, *coll_names):
        assert not len(pose_bone.bone.collections)
        for name in coll_names:
            bone_collections[name].assign(pose_bone)

    def assign_bone_collection_refs(params, attr_name, *coll_names):
        ref_list = getattr(params, attr_name + '_coll_refs', None)
        if ref_list is not None:
            for name in coll_names:
                ref_list.add().set_collection(bone_collections[name])

    add_bone_collection('Torso', ui_row=1, color_set_id=3)
    add_bone_collection('Torso (Tweak)', ui_row=2, ui_title='(Tweak)', color_set_id=4)
    add_bone_collection('Arm.L (IK)', ui_row=4, color_set_id=2)
    add_bone_collection('Arm.L (FK)', ui_row=5, ui_title='(FK)', color_set_id=5)
    add_bone_collection('Arm.L (Tweak)', ui_row=6, ui_title='(Tweak)', color_set_id=4)
    add_bone_collection('Arm.R (IK)', ui_row=4, color_set_id=2)
    add_bone_collection('Arm.R (FK)', ui_row=5, ui_title='(FK)', color_set_id=5)
    add_bone_collection('Arm.R (Tweak)', ui_row=6, ui_title='(Tweak)', color_set_id=4)
    add_bone_collection('Leg.L (IK)', ui_row=8, color_set_id=2)
    add_bone_collection('Leg.L (FK)', ui_row=9, ui_title='(FK)', color_set_id=5)
    add_bone_collection('Leg.L (Tweak)', ui_row=10, ui_title='(Tweak)', color_set_id=4)
    add_bone_collection('Leg.R (IK)', ui_row=8, color_set_id=2)
    add_bone_collection('Leg.R (FK)', ui_row=9, ui_title='(FK)', color_set_id=5)
    add_bone_collection('Leg.R (Tweak)', ui_row=10, ui_title='(Tweak)', color_set_id=4)
    add_bone_collection('Root', ui_row=13, color_set_id=1)
    add_bone_collection('Face', ui_row=1, color_set_id=5)
    add_bone_collection('Face (Primary)', ui_row=2, ui_title='(Primary)', color_set_id=2)
    add_bone_collection('Face (Secondary)', ui_row=2, ui_title='(Secondary)', color_set_id=3)
    add_bone_collection('Fingers', ui_row=7, color_set_id=6)
    add_bone_collection('Fingers (Detail)', ui_row=8, ui_title='(Detail)', color_set_id=5)

    bones = {}

    bone = arm.edit_bones.new('char_root')
    bone.head = 0.0000, 0.0000, 0.0000
    bone.tail = 0.0000, 0.2500, 0.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bones['char_root'] = bone.name
    bone = arm.edit_bones.new('spine')
    bone.head = 0.0000, 0.0552, 1.0099
    bone.tail = 0.0000, 0.0172, 1.1573
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['char_root']]
    bones['spine'] = bone.name
    bone = arm.edit_bones.new('spine.001')
    bone.head = 0.0000, 0.0172, 1.1573
    bone.tail = 0.0000, 0.0004, 1.2929
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine']]
    bones['spine.001'] = bone.name
    bone = arm.edit_bones.new('thigh.L')
    bone.head = 0.0980, 0.0124, 1.0720
    bone.tail = 0.0980, -0.0286, 0.5372
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine']]
    bones['thigh.L'] = bone.name
    bone = arm.edit_bones.new('thigh.R')
    bone.head = -0.0980, 0.0124, 1.0720
    bone.tail = -0.0980, -0.0286, 0.5372
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine']]
    bones['thigh.R'] = bone.name
    bone = arm.edit_bones.new('spine.002')
    bone.head = 0.0000, 0.0004, 1.2929
    bone.tail = 0.0000, 0.0059, 1.4657
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.001']]
    bones['spine.002'] = bone.name
    bone = arm.edit_bones.new('shin.L')
    bone.head = 0.0980, -0.0286, 0.5372
    bone.tail = 0.0980, 0.0162, 0.0852
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['thigh.L']]
    bones['shin.L'] = bone.name
    bone = arm.edit_bones.new('shin.R')
    bone.head = -0.0980, -0.0286, 0.5372
    bone.tail = -0.0980, 0.0162, 0.0852
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['thigh.R']]
    bones['shin.R'] = bone.name
    bone = arm.edit_bones.new('spine.003')
    bone.head = 0.0000, 0.0059, 1.4657
    bone.tail = 0.0000, 0.0114, 1.6582
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.002']]
    bones['spine.003'] = bone.name
    bone = arm.edit_bones.new('foot.L')
    bone.head = 0.0980, 0.0162, 0.0852
    bone.tail = 0.0980, -0.0934, 0.0167
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['shin.L']]
    bones['foot.L'] = bone.name
    bone = arm.edit_bones.new('foot.R')
    bone.head = -0.0980, 0.0162, 0.0852
    bone.tail = -0.0980, -0.0934, 0.0167
    bone.roll = -0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['shin.R']]
    bones['foot.R'] = bone.name
    bone = arm.edit_bones.new('spine.004')
    bone.head = 0.0000, 0.0114, 1.6582
    bone.tail = 0.0000, -0.0130, 1.7197
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.003']]
    bones['spine.004'] = bone.name
    bone = arm.edit_bones.new('shoulder.L')
    bone.head = 0.0183, -0.0684, 1.6051
    bone.tail = 0.1694, 0.0205, 1.6050
    bone.roll = 0.0004
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.003']]
    bones['shoulder.L'] = bone.name
    bone = arm.edit_bones.new('shoulder.R')
    bone.head = -0.0183, -0.0684, 1.6051
    bone.tail = -0.1694, 0.0205, 1.6050
    bone.roll = -0.0004
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.003']]
    bones['shoulder.R'] = bone.name
    bone = arm.edit_bones.new('toe.L')
    bone.head = 0.0980, -0.0934, 0.0167
    bone.tail = 0.0980, -0.1606, 0.0167
    bone.roll = -0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['foot.L']]
    bones['toe.L'] = bone.name
    bone = arm.edit_bones.new('heel.L')
    bone.head = 0.0600, 0.0459, 0.0000
    bone.tail = 0.1400, 0.0459, 0.0000
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['foot.L']]
    bones['heel.L'] = bone.name
    bone = arm.edit_bones.new('toe.R')
    bone.head = -0.0980, -0.0934, 0.0167
    bone.tail = -0.0980, -0.1606, 0.0167
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['foot.R']]
    bones['toe.R'] = bone.name
    bone = arm.edit_bones.new('heel.R')
    bone.head = -0.0600, 0.0459, 0.0000
    bone.tail = -0.1400, 0.0459, 0.0000
    bone.roll = -0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['foot.R']]
    bones['heel.R'] = bone.name
    bone = arm.edit_bones.new('spine.005')
    bone.head = 0.0000, -0.0130, 1.7197
    bone.tail = 0.0000, -0.0247, 1.7813
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.004']]
    bones['spine.005'] = bone.name
    bone = arm.edit_bones.new('upper_arm.L')
    bone.head = 0.1953, 0.0267, 1.5846
    bone.tail = 0.4424, 0.0885, 1.4491
    bone.roll = 2.0724
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['shoulder.L']]
    bones['upper_arm.L'] = bone.name
    bone = arm.edit_bones.new('upper_arm.R')
    bone.head = -0.1953, 0.0267, 1.5846
    bone.tail = -0.4424, 0.0885, 1.4491
    bone.roll = -2.0724
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['shoulder.R']]
    bones['upper_arm.R'] = bone.name
    bone = arm.edit_bones.new('toe_roll.L')
    bone.head = 0.0980, -0.1880, -0.0020
    bone.tail = 0.0980, -0.1895, 0.0652
    bone.roll = -3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['toe.L']]
    bones['toe_roll.L'] = bone.name
    bone = arm.edit_bones.new('toe_roll.R')
    bone.head = -0.0980, -0.1880, -0.0020
    bone.tail = -0.0980, -0.1895, 0.0652
    bone.roll = 3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['toe.R']]
    bones['toe_roll.R'] = bone.name
    bone = arm.edit_bones.new('spine.006')
    bone.head = 0.0000, -0.0247, 1.7813
    bone.tail = 0.0000, -0.0247, 1.9796
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.005']]
    bones['spine.006'] = bone.name
    bone = arm.edit_bones.new('forearm.L')
    bone.head = 0.4424, 0.0885, 1.4491
    bone.tail = 0.6594, 0.0492, 1.3061
    bone.roll = 2.1535
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['upper_arm.L']]
    bones['forearm.L'] = bone.name
    bone = arm.edit_bones.new('forearm.R')
    bone.head = -0.4424, 0.0885, 1.4491
    bone.tail = -0.6594, 0.0492, 1.3061
    bone.roll = -2.1535
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['upper_arm.R']]
    bones['forearm.R'] = bone.name
    bone = arm.edit_bones.new('hand.L')
    bone.head = 0.6594, 0.0492, 1.3061
    bone.tail = 0.7234, 0.0412, 1.2585
    bone.roll = 2.2103
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['forearm.L']]
    bones['hand.L'] = bone.name
    bone = arm.edit_bones.new('hand.R')
    bone.head = -0.6594, 0.0492, 1.3061
    bone.tail = -0.7234, 0.0412, 1.2585
    bone.roll = -2.2103
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['forearm.R']]
    bones['hand.R'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['char_root']]
    pbone.rigify_type = 'game.basic.super_copy'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    try:
        pbone.rigify_parameters.super_copy_widget_type = 'diamond'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.make_control = False
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['spine']]
    pbone.rigify_type = 'game.spines.basic_spine'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Torso (Tweak)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Torso (Tweak)')
    pbone = obj.pose.bones[bones['spine.001']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    pbone = obj.pose.bones[bones['thigh.L']]
    pbone.rigify_type = 'game.limbs.leg'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'leg'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.extra_ik_toe = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Leg.L (FK)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Leg.L (Tweak)')
    pbone = obj.pose.bones[bones['thigh.R']]
    pbone.rigify_type = 'game.limbs.leg'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'leg'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.extra_ik_toe = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Leg.R (FK)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Leg.R (Tweak)')
    pbone = obj.pose.bones[bones['spine.002']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    pbone = obj.pose.bones[bones['shin.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    pbone = obj.pose.bones[bones['shin.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    pbone = obj.pose.bones[bones['spine.003']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    pbone = obj.pose.bones[bones['foot.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    pbone = obj.pose.bones[bones['foot.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    pbone = obj.pose.bones[bones['spine.004']]
    pbone.rigify_type = 'game.spines.super_head'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    try:
        pbone.rigify_parameters.connect_chain = True
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Torso (Tweak)')
    pbone = obj.pose.bones[bones['shoulder.L']]
    pbone.rigify_type = 'game.basic.super_copy'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    assign_bone_collections(pbone, 'Torso')
    try:
        pbone.rigify_parameters.make_widget = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.super_copy_widget_type = 'shoulder'
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['shoulder.R']]
    pbone.rigify_type = 'game.basic.super_copy'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    assign_bone_collections(pbone, 'Torso')
    try:
        pbone.rigify_parameters.make_widget = True
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.super_copy_widget_type = 'shoulder'
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['toe.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    pbone = obj.pose.bones[bones['heel.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    pbone = obj.pose.bones[bones['toe.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    pbone = obj.pose.bones[bones['heel.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    pbone = obj.pose.bones[bones['spine.005']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    pbone = obj.pose.bones[bones['upper_arm.L']]
    pbone.rigify_type = 'game.limbs.arm'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Arm.L (Tweak)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Arm.L (FK)')
    pbone = obj.pose.bones[bones['upper_arm.R']]
    pbone.rigify_type = 'game.limbs.arm'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Arm.R (Tweak)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Arm.R (FK)')
    pbone = obj.pose.bones[bones['toe_roll.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    pbone = obj.pose.bones[bones['toe_roll.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    pbone = obj.pose.bones[bones['spine.006']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Torso')
    pbone = obj.pose.bones[bones['forearm.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    pbone = obj.pose.bones[bones['forearm.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    pbone = obj.pose.bones[bones['hand.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    pbone = obj.pose.bones[bones['hand.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')

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

    arm.collections.active_index = 0

    return bones


if __name__ == "__main__":
    create(bpy.context.active_object)