import bpy
import sys
import pickle
sys.path.append('.')
from lib.renderer.blenderCommon import Object
import os

serial = os.getenv('genomeSerial')
cwd = os.getcwd()+os.sep
populationPath = cwd+'population_ram'+os.sep
currentBlendPath = populationPath+serial+'.blend'
print('blenderCreateMesh.py start')

meshData = pickle.load(open(populationPath+serial+'_data.obj', 'rb'))

first = Object('First')
for object in meshData:
    clone = first.clone()
    clone.mesh.setVertices(object)

first.remove()

bpy.context.scene.render.resolution_x = 320
bpy.context.scene.render.resolution_y = 240
try:
    bpy.ops.wm.save_mainfile(filepath=currentBlendPath, check_existing=False)
except Exception as e:
    print('save failed: '+str(e))
print('blenderCreateMesh.py end')
#bpy.ops.wm.quit_blender()
