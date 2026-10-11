"""Rebuild a photo-informed cafe study; all dimensions are inferred, not surveyed.
Run from any directory with Blender --background --python this_file.
Source priority and assumptions: ../asset-brief.md. Original photos never enter GLB.
"""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'models/EN_LittleDonkey'
OUT = ROOT / 'cafe/assets'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.world = bpy.data.worlds.new('Studio')
scene.world.color = (0.65, 0.7, 0.65)
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.studio_light = 'paint.sl'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.curvature_ridge_factor = 1.1
scene.display.shading.curvature_valley_factor = 1.2
scene.display.shading.show_object_outline = True
scene.display.shading.background_type = 'WORLD'
scene.world.color = (0.7, 0.76, 0.72)
scene.view_settings.view_transform = 'Standard'
low = bpy.data.collections.new('LOW'); scene.collection.children.link(low)
refcol = bpy.data.collections.new('REF'); scene.collection.children.link(refcol)
PALETTE = {
 'Plaster':'e5e1d4','Concrete':'acb3b0','Grout':'88918d','Oak':'c69a65',
 'OakLight':'dcc29a','Walnut':'78543f','Metal':'303c3e','Brass':'bb8352',
 'Porcelain':'f4f0df','Tile':'eaece4','Moss':'637e51','Leaf':'8ba765',
 'Red':'b34742','Cushion':'e5b84b','Blue':'72a9bb','Screen':'f9f4e9',
 'Coffee':'442c24','Silver':'93a3a6','Bulb':'ffe5ab','Glass':'d2e4df'
}
def linear(v): return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
mats={}
for name,color in PALETTE.items():
    rgba=tuple(linear(int(color[i:i+2],16)/255) for i in (0,2,4))+(1,)
    m=bpy.data.materials.new(name);m.diffuse_color=rgba;m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=rgba;p.inputs['Roughness'].default_value=.85
    mats[name]=m
objects=[]
def finish(o,name,mat,zone='main',bevel=0):
    o.name='EN_LittleDonkey_'+name
    o.data.name=o.name+'_Mesh'
    for c in list(o.users_collection): c.objects.unlink(o)
    low.objects.link(o)
    o.data.materials.append(mats[mat]);o['zone']=zone;o['evidence']='ZAPX spatial forms; inferred dimensions' if zone not in ['historic','patio'] else '2017-2018 historical reference; current layout unverified'
    o['dimensionsStatus']='inferred'
    if bevel:
        mod=o.modifiers.new('EdgeSoftening','BEVEL');mod.width=bevel;mod.segments=1
        mod=o.modifiers.new('WeightedNormals','WEIGHTED_NORMAL')
    objects.append(o);return o
serial=0
def box(name,loc,size,mat,zone='main',bevel=0):
    global serial
    serial+=1
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,f'{name}_{serial:04}',mat,zone,bevel)
def cyl(name,loc,r,depth,mat,zone='main',r2=None,verts=12):
    global serial
    serial+=1
    bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r,radius2=r if r2 is None else r2,depth=depth,location=loc)
    return finish(bpy.context.object,f'{name}_{serial:04}',mat,zone)
def rod(name,a,b,r,mat,zone='main',verts=8):
    a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,mat,zone,verts=verts)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def sphere(name,loc,scale,mat,zone='main'):
    global serial
    serial+=1
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=loc)
    o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,f'{name}_{serial:04}',mat,zone)
def cup(x,y,z,zone='main',mat='Porcelain'):
    cyl('Saucer',(x,y,z+.009),.092,.018,mat,zone,verts=16)
    cyl('Cup',(x,y,z+.065),.045,.10,mat,zone,r2=.06,verts=16)
    cyl('Coffee',(x,y,z+.117),.051,.003,'Coffee',zone,verts=16)
    # Small handle, modelled as three rods to avoid unnecessary subdivisions.
    for a,b in [((x+.05,y,z+.1),(x+.087,y,z+.1)),((x+.087,y,z+.1),(x+.087,y,z+.046)),((x+.087,y,z+.046),(x+.05,y,z+.046))]:rod('CupHandle',a,b,.009,mat,zone)
def chair(x,y,angle=0,zone='main',wood=False):
    start=len(objects)
    box('ChairSeat',(0,0,.465),(.44,.42,.055),'Oak',zone,.025)
    box('ChairBack',(0,.20,.80),(.44,.048,.25),'Oak',zone,.025)
    for sx in [-1,1]:
        rod('ChairBackRail',(sx*.20,.18,.43),(sx*.20,.20,.91),.016,'Walnut' if wood else 'Metal',zone)
        for sy in [-1,1]:rod('ChairLeg',(sx*.225,sy*.24,.04),(sx*.18,sy*.16,.45),.024 if wood else .014,'Walnut' if wood else 'Metal',zone)
        rod('ChairBrace',(sx*.225,-.22,.09),(sx*.225,.22,.09),.014,'Walnut' if wood else 'Metal',zone)
    for o in objects[start:]:
        p=o.location.copy();o.location.z += .22;o.location.x=x+p.x*math.cos(angle)-p.y*math.sin(angle);o.location.y=y+p.x*math.sin(angle)+p.y*math.cos(angle)
        o.rotation_euler.z+=angle

def pedestal(x,y,w,d,h=.74,zone='main',top='OakLight'):
    box('TableTop',(x,y,h),(w,d,.055),top,zone,.012)
    cyl('TableBase',(x,y,.045),.25,.055,'Metal',zone,verts=16)
    cyl('TableStem',(x,y,h/2),.037,h-.08,'Metal',zone)

def plant(x,y,h=.8,zone='patio'):
    cyl('Planter',(x,y,.2),.17,.4,'Porcelain',zone,r2=.22,verts=12)
    cyl('Soil',(x,y,.399),.20,.006,'Walnut',zone)
    rod('PlantStem',(x,y,.38),(x+.04,y,h),.018,'Walnut',zone)
    for i in range(7):
        t=i*2.4;z=.48+(h-.48)*i/7
        leaf=sphere('Leaf',(x+math.cos(t)*.13,y+math.sin(t)*.13,z),(.22,.07,.055),'Moss' if i%2 else 'Leaf',zone);leaf.rotation_euler=(0,.5,t)

# All dimensions below are inferred. Main forms are anchored to ZAPX's single perspective.
box('Plinth',(0,-.5,.09),(6.7,10.15,.18),'Oak','floor',.04)
box('Floor',(0,-.5,.195),(6.4,9.8,.045),'Concrete','floor')
# Left window wall: black frame, frosted lower panels. Upper glass intentionally omitted for visibility.
for y in [-4.2,-2.9,-1.6,-.3,1,2.3,3.6,4.3]:box('WindowMullion',(-2.78,y,1.58),(.065,.06,2.75),'Metal','windows')
for z in [.26,1.1,2.93]:box('WindowRail',(-2.78,.05,z),(.08,8.55,.065),'Metal','windows')
for i in range(5):box('FrostedPanel',(-2.79,-1.58+i*1.3,.65),(.024,1.24,.81),'Glass','windows')
box('WindowHeader',(-2.77,.0,3.0),(.22,8.8,.22),'Plaster','windows')
# Perimeter is selectively removed in the dollhouse view; interior presets show these walls.
box('RightWall',(3.26,-.45,1.65),(.15,9.65,2.88),'Plaster','shell')
box('BackWall',(0,4.45,1.65),(6.6,.15,2.88),'Plaster','shell')
box('FrontWall',(0,-5.45,1.65),(6.6,.15,2.88),'Plaster','shell')
box('Roof',(0,-.5,3.2),(6.65,9.9,.12),'Plaster','roof')
# White subway-tile half wall, timber bench and slim trim (reference ZAPX).
box('TileBacking',(2.76,.6,.93),(.025,5.65,1.38),'Grout','tilewall')
for row in range(7):
    for col in range(23):
        y=-2.11+col*.243+(row%2)*.1215
        if y<3.42:box('SubwayTile',(2.737,y,.34+row*.188),(.027,.232,.177),'Tile','tilewall',.002)
box('TimberCap',(2.73,.65,1.6),(.075,5.7,.055),'Oak','tilewall')
box('BenchBase',(2.48,.7,.42),(.56,5.3,.41),'Oak','bench',.01)
box('BenchTop',(2.45,.7,.645),(.64,5.35,.055),'OakLight','bench',.012)
for y in [-1.7,-.25,1.15,2.45]:
    cyl('RoundCushion',(2.46,y,.693),.20,.07,'Cushion' if y<0 else 'Red','bench',verts=16)
# Central plank table and paired chairs: foreground table in ZAPX image.
box('CommunalTop',(-.85,1.22,.98),(.95,2.65,.085),'Walnut','tables',.014)
for x in [-1.20,-.50]:
    for y in [.13,2.31]:box('CommunalLeg',(x,y,.60),(.085,.085,.74),'Walnut','tables',.008)
for i in range(6):box('BoardSeam',(-1.24+i*.155,1.22,1.025),(.006,2.58,.002),'Coffee','tables')
for y in [.26,1.18,2.05]:
    chair(-1.55,y,math.pi/2,'chairs',True)
    chair(-.15,y,-math.pi/2,'chairs',True)
chair(-.85,-.48,math.pi,'chairs');chair(-.85,2.92,0,'chairs',True)
# Window tables, metal-frame chairs, and secondary tables along right bench.
for y in [-.65,1.05,2.79]:
    pedestal(-2.87,y,.55,1.05,.98,'tables','Oak')
    chair(-2.40,y,-math.pi/2,'chairs')
for y in [1.78,2.88]:
    pedestal(2.48,y,.66,.63,.95,'tables')
    chair(1.81,y,math.pi/2,'chairs')
box('WhiteTable',(2.27,-.38,.97),(.84,1.45,.065),'Porcelain','tables',.009)
for x in [1.95,2.59]:
    for y in [-1.00,.24]:cyl('WhiteLeg',(x,y,.58),.024,.73,'Porcelain','tables')
for y in [-.82,.05]:chair(1.60,y,math.pi/2,'chairs')
# Back wall projection, white framed opening, concrete service mass. No invented back room.
box('ServiceMass',(2.09,3.89,1.66),(1.06,.88,2.88),'Concrete','projection',.01)
for x in [-2.51,.63]:box('DoorFrame',(x,4.28,1.48),(.08,.10,2.56),'Porcelain','projection')
box('DoorHeader',(-.94,4.28,2.78),(3.24,.12,.1),'Porcelain','projection')
box('DoorInset',(-.94,4.29,1.5),(3.04,.045,2.47),'Glass','projection')
box('ScreenBorder',(-.74,4.18,1.91),(2.40,.05,1.57),'Metal','projection')
box('Screen',(-.74,4.145,1.91),(2.32,.018,1.49),'Screen','projection')
rod('ScreenRoll',(-1.96,4.15,2.73),(.48,4.15,2.73),.026,'Metal','projection')
box('Projector',(-.36,1.14,2.88),(.34,.28,.13),'Metal','ceiling',.025)
rod('ProjectorMount',(-.36,1.14,2.9),(-.36,1.14,3.15),.026,'Silver','ceiling')
lens=cyl('ProjectorLens',(-.44,1.29,2.88),.046,.025,'Blue','ceiling',verts=16);lens.rotation_euler.x=math.pi/2
# Four characteristic pendants and rails.
for x in [-2.0,1.6]:box('Track',(x,.60,3.10),(.04,6.85,.045),'Porcelain','ceiling')
for y in [-1.4,.15,1.65,3.0]:
    cyl('CeilingRose',(-2.0,y,3.10),.055,.035,'Metal','ceiling')
    rod('PendantCord',(-2.0,y,3.08),(-2.0,y,2.35),.009,'Metal','ceiling')
    cyl('PendantShade',(-2.0,y,2.31),.14,.13,'Brass','ceiling',r2=.09,verts=16)
    sphere('PendantGlobe',(-2.0,y,2.24),(.135,.135,.13),'Bulb','ceiling')
for x in [-2.0,1.6]:
    for y in [-1.1,1.2,3.1]:
        rod('SpotMount',(x,y,3.07),(x,y,2.98),.014,'Silver','ceiling')
        cyl('Spot',(x,y,2.96),.035,.08,'Porcelain','ceiling')
# Historical counter, marked separate so the viewer can distinguish its evidence.
box('CounterBase',(.1,-2.92,.7),(3.82,.64,.96),'Concrete','historic',.013)
box('CounterTop',(.1,-2.92,1.21),(3.98,.76,.065),'Porcelain','historic',.009)
box('PrepCounter',(.1,-4.02,.75),(4.0,.55,1.04),'Silver','historic')
for i in range(6):
    box('MenuBlue',(-1.62+i*.61,-4.27,2.21),(.6,.05,.65),'Blue','historic')
    box('MenuBlack',(-1.62+i*.61,-4.234,2.21),(.54,.022,.59),'Metal','historic')
    for j in range(3):box('MenuMark',(-1.62+i*.61,-4.219,2.34-j*.1),(.22+(j%2)*.1,.005,.008),'Porcelain','historic')
box('EspressoMachine',(.69,-3.91,1.56),(.78,.42,.50),'Metal','historic',.035)
box('EspressoFace',(.69,-3.679,1.52),(.7,.025,.28),'Silver','historic')
for x in [.47,.87]:
    rod('Portafilter',(x,-3.66,1.52),(x,-3.52,1.52),.022,'Metal','historic')
    cup(x,-3.52,1.283,'historic')
cyl('Grinder',(1.4,-3.9,1.48),.11,.34,'Metal','historic')
cyl('Hopper',(1.4,-3.9,1.76),.07,.21,'Glass','historic',r2=.16)
for i in range(4):
    cyl('TeaJar',(-.72+i*.25,-2.88,1.38),.055,.27,'OakLight','historic')
    cyl('TeaLid',(-.72+i*.25,-2.88,1.52),.06,.03,'Blue','historic')
box('PastryCase',(-1.63,-2.92,1.53),(.58,.57,.55),'Blue','historic',.009)
box('PastryGlass',(-1.63,-2.625,1.52),(.49,.014,.43),'Glass','historic')
# Wooden reception cabinet visible at near-left of ZAPX; speaker is a generic silhouette.
box('WelcomeCabinet',(-1.97,-1.85,.68),(1.0,.5,.93),'Oak','main')
box('Speaker',(-1.98,-1.85,1.38),(.64,.23,.46),'Metal','main',.025)
box('SpeakerGrille',(-1.98,-1.717,1.38),(.58,.015,.36),'Brass','main')
# Small reusable details, all self-authored geometry rather than photographed textures.
for x,y in [(-1.02,1.0),(-.67,2.0),(2.48,2.87),(-2.87,.99)]:cup(x,y,1.026 if x<0 else .982,'props')
box('BookCover',(-.83,.35,1.041),(.23,.30,.022),'Red','props',.004)
box('BookPages',(-.83,.35,1.06),(.22,.28,.025),'Porcelain','props')
# Covered planted veranda from 2018 photos: explicitly historic inferred connector.
box('PatioFloor',(-3.45,0,.13),(1.25,8.85,.12),'Concrete','patio')
for y in [-4.25,-1.4,1.45,4.2]:
    box('PatioPost',(-4.02,y,1.62),(.075,.075,2.95),'Metal','patio')
    box('CanopyRib',(-3.42,y,3.11),(1.29,.07,.08),'Metal','patio')
box('CanopyRail',(-4.02,0,3.11),(.075,8.6,.08),'Metal','patio')
for y in [-3.3,-1.6,.1,1.8,3.5]:plant(-3.80,y,.92)
# Spatial revision: separate opposing chair backs, preserve an open foreground.
# These offsets are modeling assumptions, not surveyed aisle dimensions.
for o in objects:
    zone=o['zone']
    if zone in ['windows','patio']:o.location.x-=.4
    elif zone in ['bench','tilewall']:o.location.x+=.4
    elif zone=='historic':o.location.y-=.8
    elif zone=='ceiling' and abs(o.location.x)>1.5:o.location.x+=(-.4 if o.location.x<0 else .4)
    elif zone=='main' and ('WelcomeCabinet' in o.name or 'Speaker' in o.name):o.location.x-=.4
# Source images in REF collection as non-exported image empties, packed for portable master.
for i,file in enumerate(['zapx.jpg','immian-10.jpg','alina-DSCF1265.jpg']):
    path=ASSET/'ref'/file
    if path.exists():
        im=bpy.data.images.load(str(path));im.pack()
        o=bpy.data.objects.new('REF_'+path.stem,None);refcol.objects.link(o);o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=3;o.location=(8+i*4,0,2);o.hide_render=True
refcol.hide_viewport=True
# Camera plus a real editable source blend.
cam=bpy.data.objects.new('Overview',bpy.data.cameras.new('Overview'));scene.collection.objects.link(cam);scene.camera=cam
cam.location=(10,-13,12);target=Vector((-.3,.15,.75));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=15.8
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
for o in objects:
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.select_set(False)
    if o['zone'] in ['shell','roof','tilewall']:o.hide_render=True
scene['evidence_status']='Photo-informed draft. All dimensions inferred; current layout unverified.'
scene['reference']='ZAPX venue photo main hall; 2017/2018 counter and veranda.'
master=ASSET/'EN_LittleDonkey_master.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(master))
scene.render.filepath=str(ASSET/'review/overview.png')
bpy.ops.render.render(write_still=True)
# Consolidate evaluated meshes on an export copy by semantic zone + material.
bpy.ops.object.select_all(action='DESELECT')
exportcol=bpy.data.collections.new('EXPORT');scene.collection.children.link(exportcol)
buckets=defaultdict(list)
deps=bpy.context.evaluated_depsgraph_get()
for o in objects:
    mesh=bpy.data.meshes.new_from_object(o.evaluated_get(deps))
    n=bpy.data.objects.new('Baked_'+o.name,mesh);exportcol.objects.link(n);n.matrix_world=o.matrix_world.copy();n['zone']=o['zone']
    buckets[(o['zone'],o.data.materials[0].name)].append(n)
merged=[]
for (zone,material),items in buckets.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=items[0]
    o.name='EN_LittleDonkey_'+zone+'_'+material+'_LOD0'
    o['zone']=zone;o['dimensionsStatus']='inferred';o['source']='historic 2017-2018' if zone in ['historic','patio'] else 'ZAPX venue photograph'
    mod=o.modifiers.new('DeliveryTriangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
    merged.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in merged:o.select_set(True)
path=OUT/'little-donkey.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_apply=True)
triangles=sum(len(o.data.polygons) for o in merged)
manifest={'asset':'EN_LittleDonkey','status':'photo-informed-draft','sourceBlend':'models/EN_LittleDonkey/EN_LittleDonkey_master.blend','file':'cafe/assets/little-donkey.glb','blender':bpy.app.version_string,'authoringAxes':'Z-up, meters','exportAxes':'Y-up, meters','triangles':triangles,'sourceObjects':len(objects),'exportMeshes':len(merged),'materials':len(mats),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':'all inferred; not surveyed','primaryReference':'https://zapx-group.com/zapx/wp-content/uploads/2025/12/Little-Donkey-Cafe.jpg','historicalZones':['historic','patio'],'unmodeled':['toilet interior','back-of-house','unseen rooms'],'textureContract':'No image textures. Pure base colors exported as PBR, replaced by shared MeshToonMaterial at runtime. Original source photographs excluded.','budgets':{'triangles':80000,'bytes':4000000,'drawCallsWithOutlines':120}}
(ASSET/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
assert triangles<80000 and path.stat().st_size<4000000,manifest
print('CAFE_EXPORT',json.dumps(manifest))
