import bpy
import os
import sys
import pickle
import json
sys.path.append('.')
from lib.renderer.blenderCommon import Object
print('blenderCreateMesh.py start')

params = json.loads(os.getenv('params'))
config = params['config']
serial = params['genomeSerial']

populationPath = config['main']['populationRamPath']
currentBlendPath = populationPath+serial+'.blend'
meshDataPath = populationPath+serial+'_data.obj'

meshData = pickle.load(open(meshDataPath, 'rb'))
if meshData == None:
	raise Exception('Failed to read meshData file '+meshDataPath)
	
first = Object('First')
for object in meshData:
    clone = first.clone()
    clone.mesh.setVertices(object)

first.remove()

# todo: render size should be taken from base image
bpy.context.scene.render.resolution_x = 320
bpy.context.scene.render.resolution_y = 240
try:
    bpy.ops.wm.save_mainfile(filepath=currentBlendPath, check_existing=False)
except Exception as e:
    print('save failed: '+str(e))
print('blenderCreateMesh.py end')
#bpy.ops.wm.quit_blender()
