import bpy
from mathutils import Vector

class Object():
    def __init__(self, name):
        self.name = name
        self.object = bpy.data.objects[name]
        self.mesh = Mesh(bpy.data.meshes[name])

    def randomize(self):
        self.mesh.randomize()

    def clone(self):
        newObj = self.object.copy()
        newObj.data = self.mesh.clone()
        bpy.context.scene.objects.link(newObj)
        return Object(newObj.name)

    def remove(self):
        bpy.context.scene.objects.unlink(self.object)

class Mesh():
    def __init__(self, mesh):
        self.mesh = mesh

    def clone(self):
        new = self.mesh.copy()
        return new

    def setVertices(self, co=[]):
        for i in range(0,3):
            self.mesh.vertices[i].co = Vector((co[i][0], co[i][1], co[i][2]))