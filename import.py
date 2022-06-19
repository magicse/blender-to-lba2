bl_info = {
    'name': 'TEST' ,
    'blender': (2, 80, 0),
    'author': 'Vegard Nossum <vegard.nossum@gmail.com>',
    'version': (0, 0, 1),
    'location': 'File > Import-Export',
    'description': 'MY Import Little Big Adventure 3D models and animations',
    'category': 'Import-Export',
}

import bpy
import bpy_extras.io_utils
import io
import math
import struct
import bmesh
import mathutils
import copy

#WORLD_SCALE = 1
WORLD_SCALE = 0.005


class HQRReader(object):
    def __init__(self, path):
        self.path = path

    def __getitem__(self, index):
        with open(self.path, 'rb') as f:
            def u8():
                return struct.unpack('<B', f.read(1))[0]
            def u16():
                return struct.unpack('<H', f.read(2))[0]
            def u32():
                return struct.unpack('<I', f.read(4))[0]

            f.seek(4 * index)
            print('index', index)
            offset = u32()
            print('offset = ', offset)
            f.seek(offset)

            size_full = u32()
            print('size_full = ', size_full)
            size_compressed = u32()
            print('size_compressed = ', size_compressed)
            compression_type = u16()
            print('compression_type = ', compression_type)

            if compression_type == 0:
                # No compression
                return io.BytesIO(f.read(size_compressed))

            decompressed = bytearray()
            while True:
                flags = u8()
                for i in range(8):
                    if (flags >> i) & 1:
                        decompressed.append(u8())
                        if len(decompressed) == size_full:
                            return io.BytesIO(decompressed)
                    else:
                        header = u16()
                        offset = 1 + (header >> 4)
                        length = 1 + compression_type + (header & 15)

                        for i in range(length):
                            decompressed.append(decompressed[-offset])

                        if len(decompressed) >= size_full:
                            return io.BytesIO(decompressed[:size_full])


class LBABone(object):
    def __init__(self):
        pass


class OriginalBone(object):
    parent = 0
    vertex = 0
    unknown1 = 0
    unknown2 = 0
    def __init__(self):
        pass
        
class GeneratedBone(object):
    parent = 0
    pos = []
    created = False
    def __init__(self):
        pass

class Vertex(object):
    index = 0
    x = 0
    y = 0
    z = 0
    bone = 0

    def __init__(self):
        pass

class Sphere(object):
    unknown1 = 0
    colour = 0
    vertex = 0
    size = 0

    def __init__(self):
        pass

class LBAModel(object):
    def __init__(self):
        pass
        
class LBA2Model(object):
    def __init__(self):
        self.normals = None
        self.vertices = None
        self.bones = None
        self.lines = None
        self.spheres = None
        self.polygons = None        

class LBAPolygon(object):
    def __init__(self):
        pass

class Polygon(object):
    renderType = 0
    vertex = []
    colour = 0
    intensity = 0
    u = []
    v = []
    tex = 0
    numVertex = 0
    hasTex = False
    hasExtra = False
    hasTransparency = False

    def __init__(self):
        pass

def transorm_orientation(x, y, z):
    pass
    return z, x, y

def read_lba_model(f):
    def goto(offset):
        f.seek(offset)
    def skip(n):
        f.read(n)
    def u8():
        return struct.unpack('<B', f.read(1))[0]
    def u16():
        return struct.unpack('<H', f.read(2))[0]
    def u16_div(n):
        x = u16()
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16_div(n):
        x = s16()
        if x == -1:
            return x
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16():
        return struct.unpack('<h', f.read(2))[0]
    def u32():
        return struct.unpack('<I', f.read(4))[0]
    def s32():
        return struct.unpack('<i', f.read(4))[0]


    body_flag = s32()  # 0x00
    unknown = s32()  # 0x04
    x_min = s32()  # 0x08
    x_max = s32()  # 0x0C
    y_min = s32()  # 0x10
    y_max = s32()  # 0x14
    z_min = s32()  # 0x18
    z_max = s32()  # 0x1C
    bones_count = u32()  # 0x20
    bones_offset = u32()  # 0x24
    vertices_count = u32()  # 0x28
    vertices_offset = u32()  # 0x2C
    normals_count = u32()  # 0x30
    normals_offset = u32()  # 0x34
    unknown_count = u32()  # 0x38
    unknown_offset = u32()  # 0x3C
    polygons_count = u32()  # 0x40
    polygons_offset = u32()  # 0x44
    lines_count = u32()  # 0x48
    lines_offset = u32()  # 0x4C
    spheres_count = u32()  # 0x50
    spheres_offset = u32()  # 0x54
    uv_groups_size = u32()  # 0x58
    uv_groups_offset = u32()  # 0x5C

    print ('body_flag', body_flag)
    
    # # BONE # #
    goto(bones_offset)
    bones = []
    for i in range(bones_count):
        print ('bones_count ==========', i)
        bone = OriginalBone()
        bone.parent = u16()
        print ('bone.parent', bone.parent)
        bone.vertex = u16()
        print ('bone.vertex', bone.vertex)
        bone.unknown1 = u16()
        print ('bone.unknown1', bone.unknown1)
        bone.unknown2 = u16()
        print ('bone.unknown2', bone.unknown2)
        """
        print(
            "Bone" + str(i) +
            ", parent: " + str(bone.parent) +
            ", vertex: " + str(bone.vertex) +
            ", unk1: " + str(bone.unk1) +
            ", unk2: " + str(bone.unk2))
        """
        bones.append(bone)
    
    # # VERTEX # #
    goto(vertices_offset)
    print ('vertices_offset', vertices_offset)
    vertices = []
    for i in range(vertices_count):
        vertex = Vertex()
        vertex.index = i
        print ('vertices_count', i)
        vertex.x = s16() * WORLD_SCALE
        vertex.y = s16() * WORLD_SCALE
        vertex.z = s16() * WORLD_SCALE
        vertex.bone = u16()
        print ('bone', vertex.bone)
        #vertices.append((x, y, z))
        vertices.append(vertex)
    old_vertices = copy.deepcopy(vertices)
 
    for i in range(vertices_count):
        vertex = vertices[i]
        found_root = False
        next_bone = bones[vertex.bone]
        while found_root is False:
            vertex.x += old_vertices[next_bone.vertex].x
            vertex.y += old_vertices[next_bone.vertex].y
            vertex.z += old_vertices[next_bone.vertex].z
            if next_bone.parent > 1000:
                found_root = True
            else:
                next_bone = bones[next_bone.parent]


    vert_groups = []
    for i in range(len(bones)):
        group = []
        for j in range(len(vertices)):
            if vertices[j].bone == i:
                group.append(j)
        vert_groups.append(group)

    
    vertices_test = []
    for i in range(vertices_count):
        x = old_vertices[i].x
        y = old_vertices[i].y
        z = old_vertices[i].z
        vertices_test.append((x, y, z))
    
    # # POLYGON # #
    goto(polygons_offset)
    polygons = []
    #offset = r.currentIndex
    #start_point = r.currentIndex
    offset = polygons_offset
    start_point = polygons_offset
    print (offset)
    while offset < start_point + (lines_offset - polygons_offset):
        render_type = u16()
        num_polygons = u16()
        section_size = u16()
        unknown1 = u16()
        offset += 8
        print ('offset',offset)
        print ('render_type',render_type)
        print ('num_polygons',num_polygons)
        print ('section_size',section_size)

        if section_size == 0:
            break

        block_size = ((section_size - 8) // num_polygons)
        print ('block_size', block_size)
        for i in range(num_polygons):
            poly = load_polygon(f, offset, render_type, block_size)
            polygons.append(poly)
            offset += block_size
    
    
    """goto(bones_offset)
    bones = []
    for i in range(bones_count):
        print ('bones_count', i)
        bone = LBABone()
        bone.first_point = u16_div(6)
        bone.nr_points = u16()
        bone.parent_point = u16_div(6)
        bone.parent_bone = s16_div(38)
        bone.bone_type = u16()
        # unknown
        bone.z = s16()
        bone.y = s16()
        bone.x = s16()
        nr_normals = u16()
        skip(2)
        skip(4)
        skip(4)
        skip(4)
        skip(4)
        skip(2)

        bones.append(bone)
    return {'FINISHED'}
    
    normals = []
    for i in range(u16()):
        x = s16()
        y = s16()
        z = s16()
        # unknown
        w = s16()

        normals.append((x, y, z, w))

    polygons = []
    for i in range(u16()):
        render_type = u8()
        nr_vertices = u8()
        color_index = u8()
        # unknown
        skip(1)

        polygon_vertices = []

        if render_type >= 9:
            # each vertex has a normal
            for j in range(nr_vertices):
                normal = u16()
                v = u16_div(6)
                polygon_vertices.append((v, normal))
        elif render_type >= 7:
            # one normal for the whole polygon
            normal = u16()
            for j in range(nr_vertices):
                v = u16_div(6)
                polygon_vertices.append((v, normal))
        else:
            # no normal (?)
            for j in range(nr_vertices):
                v = u16_div(6)
                polygon_vertices.append((v, ))

        polygon = LBAPolygon()
        polygon.render_type = render_type
        polygon.color_index = color_index
        polygon.vertices = polygon_vertices
        polygons.append(polygon)

    lines = []
    for i in range(u16()):
        data = u32()
        v1 = u16_div(6)
        v2 = u16_div(6)

        lines.append((v1, v2))"""
    
    # # SPHERE # #
    goto(spheres_offset)
    spheres = []
    for i in range(spheres_count):
        sphere = Sphere()
        sphere.unknown1 = u16()
        sphere.colour = int(math.floor((u16() & 0x00FF) / 16))
        sphere.vertex = u16()
        sphere.size = u16()
        """
        print ('+++++++++ sphere colour', hex(colour))
        print ('+++++++++ sphere colour', str(colour))
        print ('+++++++++ sphere size', size)
        """
        #spheres.append((colour, vertex, size))
        #spheres.append((v, color, size))
        spheres.append(sphere)
        

    #lba_model = LBAModel()
    #lba_model.vertices = vertices_test
    #lba_model.bones = bones
    #lba_model.normals = normals
    #lba_model.polygons = polygons
    #lba_model.lines = lines
    #lba_model.spheres = spheres
    #return lba_model
    
    lba2_model = LBA2Model()
    lba2_model.vertices = vertices
    lba2_model.bones = bones
    #lba2_model.normals = normals
    lba2_model.polygons = polygons
    #lba2_model.lines = lines
    lba2_model.spheres = spheres
    #lba2_model.uvgroups = uvgroups
    lba2_model.vertgroups = vert_groups
    return lba2_model
    

def load_polygon(data, offset, render_type, block_size):
    def goto(offset):
        data.seek(offset)
    def skip(n):
        data.read(n)
    def u8():
        return struct.unpack('<B', data.read(1))[0]
    def u16():
        return struct.unpack('<H', data.read(2))[0]
    def u16_div(n):
        x = u16()
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16_div(n):
        x = s16()
        if x == -1:
            return x
        if x % n != 0:
            raise RuntimeError("%u is not divisible by %u" % (x, n))
        return x // n
    def s16():
        return struct.unpack('<h', data.read(2))[0]
    def u32():
        return struct.unpack('<I', data.read(4))[0]
    def s32():
        return struct.unpack('<i', data.read(4))[0]
 
    goto(offset)  # is it needed?
    poly = Polygon()
    poly.numVertex = 4 if (render_type & 0x8000) else 3
    poly.hasExtra = (render_type & 0x4000) is True
    poly.hasTex = (render_type & 0x8 and block_size > 16) is True
    poly.hasTransparency = (render_type == 2)
    
    print(
        "numVertex: " + str(poly.numVertex) +
        ", hasExtra: " + str(poly.hasExtra) +
        ", hasTex: " + str(poly.hasTex) +
        ", hasTransparency: " + str(poly.hasTransparency))
    
    poly.vertex = []
    for i in range(poly.numVertex):
        poly.vertex.append(u16())

    if poly.hasTex and poly.numVertex == 3:
        poly.tex = u8()

    goto(offset + 8)
    poly.colour = int(math.floor((u16() & 0x00FF) / 16))

    poly.intensity = s16()
    goto(offset + 12)
    if poly.hasTex:
        for i in range(poly.numVertex):
            skip(1)
            poly.u.append(u8())
            skip(1)
            poly.v.append(u8())

        if poly.numVertex == 4:
            goto(offset + 27)
            poly.tex = u8()
    return poly    


class LBABodyImporter_MY(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):

    bl_idname = 'object.mylbabody'
    bl_label = 'MY Import LBA body'
    filename_ext = '.hqr'
    filter_glob : bpy.props.StringProperty(
        default='*.hqr;*.HQR',
        options={'HIDDEN'},
    )
    
    entry : bpy.props.IntProperty(
        name='Select Entry number',
        subtype='UNSIGNED',
    )
    
    def execute(self, context):
        lba_model = read_lba_model(HQRReader(self.filepath)[self.entry])
        print ('SCRIPT EXECUTING PYTHON IMPORTER')
        print('My string:', self.entry)
        
        #bones = bone_generator(lba_model.bones, lba_model.vertices)
        
        # create new armature
        amt = bpy.data.armatures.new('Armature')
        amt.show_names = True
        
        rig = bpy.data.objects.new('Rig', amt)
        rig.location = bpy.context.scene.cursor.location
        
        bpy.context.collection.objects.link(rig)
        bpy.context.view_layer.objects.active = rig
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        model_bones = {}
        #=========================
        bone_count = len(lba_model.bones)
        blender_bones = []
        bones = [None] * bone_count
        #for i, lba_bone in enumerate(lba_model.bones):
        filepath = 'L:\\LBA\\LBA_EDITS\\Topology\\3d_models\\LBA_utils\\Test_Extraction\\test.bin'
        myfile = open(filepath, 'w')

        for i in range(bone_count):
            
            g_bone = GeneratedBone()
            bone = lba_model.bones[i]
            vert = lba_model.vertices[bone.vertex]
            g_bone.parent = bone.parent
            #=============  changes y and z axes =================
            #g_bone.pos = (vert.x, vert.y, vert.z)
            #g_bone.pos = (vert.z, vert.x, vert.y)
            g_bone.pos = transorm_orientation(vert.x, vert.y, vert.z)
            
            blender_bones.append(g_bone)
            myfile.write('bone '+str(i)+' '+'parent bone '+str(bone.parent)+' x= '+str(vert.x)+' y= '+str(vert.y)+' z= '+str(vert.z)+'\n')
            #bone = amt.edit_bones.new('Bone {}'.format(i))
            # Must give bone a non-zero length, otherwise it will be
            # invalid and disappear.
            #bone.head = (0, 0, 0)
            #bone.tail = (0, 1, 0)
            #bone.tail = (g_bone.pos)
        created_bones = 0
        while created_bones != bone_count:
            for i in range(bone_count):
                bone = blender_bones[i]
                if bone.created is True:
                    continue
                if bone.parent > 1000:
                    bone_cr = amt.edit_bones.new('Bone {}'.format(i))
                    
                    #bone_cr.head = (0, 0, 0)
                    bone_cr.head = (bone.pos)
                    bone_cr.tail = (0, 1, 0)
                    model_bones[0] = bone_cr
                    bone.created = True
                    created_bones += 1
                else:
                    parent_bone = blender_bones[bone.parent]
                    if parent_bone.created is True:
                        bone_cr = amt.edit_bones.new('Bone {}'.format(i))
                        #bone_cr.head = (0, 0, 0)
                        bone_cr.head = (blender_bones[bone.parent].pos)
                        #bone_cr.tail = (0, 1, 0)
                        bone_cr.tail = (bone.pos)
                        bone_cr.parent = model_bones[bone.parent]
                        model_bones[i] = bone_cr
                        bone.created = True
                        created_bones += 1
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Move bones into place                
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='POSE')
        for i in range(bone_count):
            bone = blender_bones[i]
            bone_cr = rig.pose.bones['Bone {}'.format(i)]
            bone_cr.rotation_mode = 'ZYX'
            if bone.parent < 1000:
 
                x1, y1, z1 = blender_bones[bone.parent].pos
                #bone_cr.location = (x1, y1, z1)
                #bone_cr.location = bone.pos
            #parent_bone = blender_bones[bone_cur.parent]
            #bone.head = (blender_bones.pos)
            #bone.tail = (parent_bone.pos)

        
            #if lba_bone.parent_bone != -1:
            #    bone.parent = model_bones[lba_bone.parent_bone]

            #model_bones[i] = bone
            
        #scale = 1. / (1 << 7)
        scale = 1
        rig.pose.bones['Bone 0'].scale = (scale, scale, scale)
        bpy.ops.object.mode_set(mode='OBJECT')
        #=========================
        
        #myfile.write(struct.pack('<i',len(blender_bones)))
        #myfile.write(g_bone)
        myfile.flush()
        myfile.close()
        
        
        # Make an empty mesh and use “from_pydata” to add your verts and edges to it        
        me = bpy.data.meshes.new('Mesh')
        
        vertices_test = []
        for i in range(bone_count):
            bone = blender_bones[i]
            x2, y2, z2 = bone.pos
            vertices_test.append((x2, y2, z2))
        
        vertices_test2 = []
        vertices_count = len(lba_model.vertices)
        for i in range(vertices_count):
            vertex = lba_model.vertices[i]
            x2, y2, z2 = transorm_orientation(vertex.x, vertex.y, vertex.z)
            vertices_test2.append((x2, y2, z2))
        
        # from_pydata(vertices, edges, faces)
        #me.from_pydata(vertices_test2, [], [])
        #me.from_pydata(lba_model.vertices, [], [tuple(y[0] for y in polygon.vertices) for polygon in lba_model.polygons])
        me.from_pydata(vertices_test2, [], [tuple(y[0] for y in polygon.vertices) for polygon in lba_model.polygons])
        
        # Make an object out of the mesh, and add the object to the scene
        ob = bpy.data.objects.new('Body', me)
        ob.location = bpy.context.scene.cursor.location
        bpy.context.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        
        
        # Spere creation
        spheres_count = len(lba_model.spheres)
        for i in range(spheres_count):
            sph_sphere = lba_model.spheres[i]
            print (sph_sphere)
            sph_radius = sph_sphere.size * WORLD_SCALE
            vertex = lba_model.vertices[i]
            # Create an empty mesh and the object.
            mesh = bpy.data.meshes.new('Basic_Sphere')
            basic_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
            # Add the object into the scene.
            bpy.context.collection.objects.link(basic_sphere)
            # Select the newly created object
            bpy.context.view_layer.objects.active = basic_sphere
            basic_sphere.select_set(True)
            # Construct the bmesh sphere and assign it to the blender mesh.
        
            #current_point = (5, 5, 5)
            vertex = lba_model.vertices[sph_sphere.vertex]
            current_point = transorm_orientation(vertex.x, vertex.y, vertex.z)
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, diameter=sph_radius, matrix=mathutils.Matrix.Translation(current_point))
            bm.to_mesh(mesh)
            bm.free()
            #bpy.ops.object.modifier_add(type='SUBSURF')
            #bpy.ops.object.shade_smooth()
        
        return {'FINISHED'}
    

def bone_generator(source_bones, source_verts):
    bone_count = len(source_bones)
    maya_bones = []
    bones = [None] * bone_count
    # setup bones
    for i in range(bone_count):
        g_bone = GeneratedBone()
        bone = source_bones[i]
        vert = source_verts[bone.vertex]
        g_bone.parent = bone.parent
        g_bone.pos = (vert.x, vert.y, vert.z)
        maya_bones.append(g_bone)

    created_bones = 0
    while created_bones != bone_count:
        for i in range(bone_count):
            bone = maya_bones[i]
            if bone.created is True:
                continue
            if bone.parent > 1000:
                root_bone = pm.joint(p=bone.pos, name='joint0', rad=0.2)
                root_bone.setRotationOrder('YZX', True)
                bones[0] = root_bone
                bone.created = True
                created_bones += 1
            else:
                # look if parent has been already created
                parent_bone = maya_bones[bone.parent]
                if parent_bone.created is True:
                    # has bone parent
                    pm.select(bones[bone.parent])
                    bn = pm.joint(p=bone.pos, name='joint' + str(i), rad=0.2)
                    bn.setRotationOrder('YZX', True)
                    bones[i] = bn
                    bone.created = True
                    created_bones += 1
    return bones


def menu_func(self, context):
    self.layout.operator(LBABodyImporter_MY.bl_idname, text='LBA2 Body (.HQR)')

    
def register():
    bpy.utils.register_class(LBABodyImporter_MY)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_class(LBABodyImporter_MY)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)

if __name__ == '__main__':
    register()
