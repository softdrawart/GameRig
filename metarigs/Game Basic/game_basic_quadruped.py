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
    arm.rigify_colors[0].select = Color((0.3137, 0.7843, 1.0000))
    arm.rigify_colors[0].standard_colors_lock = True
    arm.rigify_colors[1].name = "IK"
    arm.rigify_colors[1].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[1].normal = Color((0.6039, 0.0000, 0.0000))
    arm.rigify_colors[1].select = Color((0.3137, 0.7843, 1.0000))
    arm.rigify_colors[1].standard_colors_lock = True
    arm.rigify_colors[2].name = "Special"
    arm.rigify_colors[2].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[2].normal = Color((0.9569, 0.7882, 0.0471))
    arm.rigify_colors[2].select = Color((0.3137, 0.7843, 1.0000))
    arm.rigify_colors[2].standard_colors_lock = True
    arm.rigify_colors[3].name = "Tweak"
    arm.rigify_colors[3].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[3].normal = Color((0.0392, 0.2118, 0.5804))
    arm.rigify_colors[3].select = Color((0.3137, 0.7843, 1.0000))
    arm.rigify_colors[3].standard_colors_lock = True
    arm.rigify_colors[4].name = "FK"
    arm.rigify_colors[4].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[4].normal = Color((0.1176, 0.5686, 0.0353))
    arm.rigify_colors[4].select = Color((0.3137, 0.7843, 1.0000))
    arm.rigify_colors[4].standard_colors_lock = True
    arm.rigify_colors[5].name = "Extra"
    arm.rigify_colors[5].active = Color((0.5490, 1.0000, 1.0000))
    arm.rigify_colors[5].normal = Color((0.9686, 0.2510, 0.0941))
    arm.rigify_colors[5].select = Color((0.3137, 0.7843, 1.0000))
    arm.rigify_colors[5].standard_colors_lock = True

    bone_collections = {}

    for bcoll in list(arm.collections):
        arm.collections.remove(bcoll)

    def add_bone_collection(name, *, ui_row=0, ui_title='', sel_set=False, color_set_id=0):
        new_bcoll = arm.collections.new(name)
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

    add_bone_collection('Spine', ui_row=1, color_set_id=3)
    add_bone_collection('Spine (Tweak)', ui_row=2, ui_title='(Tweak)', color_set_id=4)
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
    add_bone_collection('Tail', ui_row=12, color_set_id=6)
    add_bone_collection('Root', ui_row=15, color_set_id=1)

    bones = {}

    bone = arm.edit_bones.new('spine.004')
    bone.head = 0.0000, 0.4418, 0.7954
    bone.tail = 0.0000, 0.3546, 0.8059
    bone.roll = 0.0000
    bone.use_connect = False
    bones['spine.004'] = bone.name
    bone = arm.edit_bones.new('spine.003')
    bone.head = 0.0000, 0.4418, 0.7954
    bone.tail = 0.0000, 0.5547, 0.7568
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.004']]
    bones['spine.003'] = bone.name
    bone = arm.edit_bones.new('spine.005')
    bone.head = 0.0000, 0.3546, 0.8059
    bone.tail = 0.0000, 0.1803, 0.7782
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.004']]
    bones['spine.005'] = bone.name
    bone = arm.edit_bones.new('spine.002')
    bone.head = 0.0000, 0.5547, 0.7568
    bone.tail = 0.0000, 0.7755, 0.7418
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.003']]
    bones['spine.002'] = bone.name
    bone = arm.edit_bones.new('spine.006')
    bone.head = 0.0000, 0.1803, 0.7782
    bone.tail = 0.0000, 0.0319, 0.7731
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.005']]
    bones['spine.006'] = bone.name
    bone = arm.edit_bones.new('thigh.L')
    bone.head = 0.1249, 0.3419, 0.7379
    bone.tail = 0.1249, 0.2712, 0.4731
    bone.roll = -0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.005']]
    bones['thigh.L'] = bone.name
    bone = arm.edit_bones.new('thigh.R')
    bone.head = -0.1249, 0.3419, 0.7379
    bone.tail = -0.1249, 0.2712, 0.4731
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.005']]
    bones['thigh.R'] = bone.name
    bone = arm.edit_bones.new('spine.001')
    bone.head = 0.0000, 0.7755, 0.7418
    bone.tail = 0.0000, 0.9624, 0.7412
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.002']]
    bones['spine.001'] = bone.name
    bone = arm.edit_bones.new('spine.007')
    bone.head = 0.0000, 0.0319, 0.7731
    bone.tail = 0.0000, -0.0980, 0.7945
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.006']]
    bones['spine.007'] = bone.name
    bone = arm.edit_bones.new('shin.L')
    bone.head = 0.1249, 0.2712, 0.4731
    bone.tail = 0.1114, 0.4766, 0.2473
    bone.roll = 0.0195
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['thigh.L']]
    bones['shin.L'] = bone.name
    bone = arm.edit_bones.new('shin.R')
    bone.head = -0.1249, 0.2712, 0.4731
    bone.tail = -0.1114, 0.4766, 0.2473
    bone.roll = -0.0195
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['thigh.R']]
    bones['shin.R'] = bone.name
    bone = arm.edit_bones.new('spine')
    bone.head = 0.0000, 0.9624, 0.7412
    bone.tail = 0.0000, 1.1044, 0.7633
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.001']]
    bones['spine'] = bone.name
    bone = arm.edit_bones.new('spine.008')
    bone.head = 0.0000, -0.0980, 0.7945
    bone.tail = 0.0000, -0.3618, 0.8375
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.007']]
    bones['spine.008'] = bone.name
    bone = arm.edit_bones.new('foot.L')
    bone.head = 0.1114, 0.4766, 0.2473
    bone.tail = 0.1088, 0.4138, 0.0411
    bone.roll = 0.0165
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['shin.L']]
    bones['foot.L'] = bone.name
    bone = arm.edit_bones.new('foot.R')
    bone.head = -0.1114, 0.4766, 0.2473
    bone.tail = -0.1088, 0.4138, 0.0411
    bone.roll = -0.0165
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['shin.R']]
    bones['foot.R'] = bone.name
    bone = arm.edit_bones.new('spine.009')
    bone.head = 0.0000, -0.3618, 0.8375
    bone.tail = 0.0000, -0.4253, 0.8585
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.008']]
    bones['spine.009'] = bone.name
    bone = arm.edit_bones.new('shoulder.L')
    bone.head = 0.0596, -0.2578, 0.8876
    bone.tail = 0.1249, -0.3418, 0.7153
    bone.roll = -0.3526
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.008']]
    bones['shoulder.L'] = bone.name
    bone = arm.edit_bones.new('shoulder.R')
    bone.head = -0.0596, -0.2578, 0.8876
    bone.tail = -0.1249, -0.3418, 0.7153
    bone.roll = 0.3526
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['spine.008']]
    bones['shoulder.R'] = bone.name
    bone = arm.edit_bones.new('toe.L')
    bone.head = 0.1088, 0.4138, 0.0411
    bone.tail = 0.1088, 0.2808, 0.0000
    bone.roll = 3.1416
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['foot.L']]
    bones['toe.L'] = bone.name
    bone = arm.edit_bones.new('toe.R')
    bone.head = -0.1088, 0.4138, 0.0411
    bone.tail = -0.1088, 0.2808, 0.0000
    bone.roll = -3.1416
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['foot.R']]
    bones['toe.R'] = bone.name
    bone = arm.edit_bones.new('spine.010')
    bone.head = 0.0000, -0.4253, 0.8585
    bone.tail = 0.0000, -0.4888, 0.8796
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.009']]
    bones['spine.010'] = bone.name
    bone = arm.edit_bones.new('front_thigh.L')
    bone.head = 0.1249, -0.3161, 0.6902
    bone.tail = 0.1249, -0.2245, 0.4418
    bone.roll = -0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['shoulder.L']]
    bones['front_thigh.L'] = bone.name
    bone = arm.edit_bones.new('front_thigh.R')
    bone.head = -0.1249, -0.3161, 0.6902
    bone.tail = -0.1249, -0.2245, 0.4418
    bone.roll = 0.0000
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['shoulder.R']]
    bones['front_thigh.R'] = bone.name
    bone = arm.edit_bones.new('spine.011')
    bone.head = 0.0000, -0.4888, 0.8796
    bone.tail = 0.0000, -0.6590, 0.9809
    bone.roll = 0.0000
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['spine.010']]
    bones['spine.011'] = bone.name
    bone = arm.edit_bones.new('front_shin.L')
    bone.head = 0.1249, -0.2245, 0.4418
    bone.tail = 0.1114, -0.2147, 0.1698
    bone.roll = 0.0098
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['front_thigh.L']]
    bones['front_shin.L'] = bone.name
    bone = arm.edit_bones.new('front_shin.R')
    bone.head = -0.1249, -0.2245, 0.4418
    bone.tail = -0.1114, -0.2147, 0.1698
    bone.roll = -0.0098
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['front_thigh.R']]
    bones['front_shin.R'] = bone.name
    bone = arm.edit_bones.new('front_foot.L')
    bone.head = 0.1114, -0.2147, 0.1698
    bone.tail = 0.1088, -0.2462, 0.0411
    bone.roll = 0.0272
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['front_shin.L']]
    bones['front_foot.L'] = bone.name
    bone = arm.edit_bones.new('front_foot.R')
    bone.head = -0.1114, -0.2147, 0.1698
    bone.tail = -0.1088, -0.2462, 0.0411
    bone.roll = -0.0272
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['front_shin.R']]
    bones['front_foot.R'] = bone.name
    bone = arm.edit_bones.new('front_toe.L')
    bone.head = 0.1088, -0.2462, 0.0411
    bone.tail = 0.1088, -0.3707, 0.0000
    bone.roll = 3.1416
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['front_foot.L']]
    bones['front_toe.L'] = bone.name
    bone = arm.edit_bones.new('front_toe.R')
    bone.head = -0.1088, -0.2462, 0.0411
    bone.tail = -0.1088, -0.3707, 0.0000
    bone.roll = -3.1416
    bone.use_connect = True
    bone.parent = arm.edit_bones[bones['front_foot.R']]
    bones['front_toe.R'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['spine.004']]
    pbone.rigify_type = 'game.spines.basic_spine'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
    try:
        pbone.rigify_parameters.pivot_pos = 4
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Spine (Tweak)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Spine (Tweak)')
    pbone = obj.pose.bones[bones['spine.003']]
    pbone.rigify_type = 'game.spines.basic_tail'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Tail')
    try:
        pbone.rigify_parameters.connect_chain = True
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Spine (Tweak)')
    pbone = obj.pose.bones[bones['spine.005']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
    pbone = obj.pose.bones[bones['spine.002']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Tail')
    pbone = obj.pose.bones[bones['spine.006']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
    pbone = obj.pose.bones[bones['thigh.L']]
    pbone.rigify_type = 'game.limbs.rear_paw'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.L (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Leg.L (FK)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Leg.L (Tweak)')
    pbone = obj.pose.bones[bones['thigh.R']]
    pbone.rigify_type = 'game.limbs.rear_paw'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Leg.R (FK)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Leg.R (Tweak)')
    pbone = obj.pose.bones[bones['spine.001']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Tail')
    pbone = obj.pose.bones[bones['spine.007']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
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
    pbone = obj.pose.bones[bones['spine']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Tail')
    pbone = obj.pose.bones[bones['spine.008']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
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
    pbone = obj.pose.bones[bones['spine.009']]
    pbone.rigify_type = 'game.spines.super_head'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
    try:
        pbone.rigify_parameters.connect_chain = True
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Spine (Tweak)')
    pbone = obj.pose.bones[bones['shoulder.L']]
    pbone.rigify_type = 'game.basic.super_copy'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    try:
        pbone.rigify_parameters.make_widget = False
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['shoulder.R']]
    pbone.rigify_type = 'game.basic.super_copy'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    try:
        pbone.rigify_parameters.make_widget = False
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
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['toe.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Leg.R (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['spine.010']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
    pbone = obj.pose.bones[bones['front_thigh.L']]
    pbone.rigify_type = 'game.limbs.front_paw'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Arm.L (FK)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Arm.L (Tweak)')
    pbone = obj.pose.bones[bones['front_thigh.R']]
    pbone.rigify_type = 'game.limbs.front_paw'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.ik_local_location = False
    except AttributeError:
        pass
    assign_bone_collection_refs(pbone.rigify_parameters, 'fk', 'Arm.R (FK)')
    assign_bone_collection_refs(pbone.rigify_parameters, 'tweak', 'Arm.R (Tweak)')
    pbone = obj.pose.bones[bones['spine.011']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Spine')
    pbone = obj.pose.bones[bones['front_shin.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    pbone = obj.pose.bones[bones['front_shin.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    pbone = obj.pose.bones[bones['front_foot.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    pbone = obj.pose.bones[bones['front_foot.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    pbone = obj.pose.bones[bones['front_toe.L']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.L (IK)')
    try:
        pbone.rigify_parameters.limb_type = 'paw'
    except AttributeError:
        pass
    pbone = obj.pose.bones[bones['front_toe.R']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    assign_bone_collections(pbone, 'Arm.R (IK)')
    try:
        pbone.rigify_parameters.rotation_axis = 'x'
    except AttributeError:
        pass
    try:
        pbone.rigify_parameters.limb_type = 'paw'
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

    arm.collections.active_index = 0

    return bones


if __name__ == "__main__":
    create(bpy.context.active_object)
