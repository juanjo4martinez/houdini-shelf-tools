"""
CAMERA SHAKE TOOL
-----------------
Add some movement to your camera to make it look like it's handheld.
Make sure your Camera node is selected when running this tool!
"""

# Get the selected camera.
this_node = hou.selectedNodes()
this_cam = this_node[0]

# /obj context.
obj = hou.node("/obj")

# Create CHOP Network called "cameraShake".
chopnet = obj.findOrCreateMotionEffectsNetwork()
chopnet.setName(f"cameraShake_{this_cam.name()}", unique_name=True)

# Inside the CHOPNet, create a Channel node and give it a name.
channel_node = chopnet.createNode("channel")
channel_node.setName(f"{this_cam.name()}_rotationClips", unique_name=True)

# Pick the rotation channels from the camera and use "Euler Rotation".
channel_node.parm("name0").set(f"{this_cam.name()}:r")
channel_node.parm("type0").set(1)

# Store the newly created channel's values as individual variables.
channel_value_x = channel_node.parm("value0x")
channel_value_y = channel_node.parm("value0y")
channel_value_z = channel_node.parm("value0z")

# Store the camera's rotation parameters as individual variables.
cam_rot_x = this_cam.parm("rx")
cam_rot_y = this_cam.parm("ry")
cam_rot_z = this_cam.parm("rz")

# CONDITIONAL:
# If rotation is animated, copy those keyframes into the channel's node values.
# If rotation is NOT animated, just copy the camera's rotation values.
if len(cam_rot_x.keyframes()) > 0:
    for k in cam_rot_x.keyframes():
        channel_value_x.setKeyframe(k)    
else: 
    channel_node.parm("value0x").set(this_cam.parm("rx").eval())

if len(cam_rot_y.keyframes()) > 0:
    for k in cam_rot_y.keyframes():
        channel_value_y.setKeyframe(k)
else: 
    channel_node.parm("value0y").set(this_cam.parm("ry").eval())

if len(cam_rot_z.keyframes()) > 0:
    for k in cam_rot_z.keyframes():
        channel_value_z.setKeyframe(k)    
else: 
    channel_node.parm("value0z").set(this_cam.parm("rz").eval())

# Set the channel units to Frames and the graph color to green.
channel_node.parm("units").set(0)
channel_node.parmTuple("gcolor").set((0,1,0))

# Turn off the Export flag on the Channel node.
channel_node.setExportFlag(0)

# Inside the CHOPNet, create a Math node.
math_node = channel_node.parent().createNode("math")
math_node.setName(f"{this_cam.name()}_addNoiseToRotation", unique_name=True)

# The Math node will sum (Add) the rotation channels to the noise.
math_node.parm("chopop").set(1)

# Turn on the Display and Export flags on the Math node.
math_node.setDisplayFlag(1)
math_node.setExportFlag(1)

# Inside the CHOPNet, create a Noise node.
noise_node = chopnet.createNode("noise")

# The name of the noise channels will be the same as in the Channel node (cam:rx,ry,rz).
noise_node.parm("channelname").set(f"`run('chopls {channel_node.path()}')`")

# The seed of the noise will be $C (number of channels, i.e: 3).
noise_node.parm("seed").setExpression("$C")

# Set the roughness to 0 for camera-like movements.
noise_node.parm("rough").set(0)

# Plug the Channel and Noise nodes into the Math inputs.
math_node.setInput(0, channel_node)
math_node.setInput(1, noise_node)

# Layout nodes inside the CHOPNet.
chopnet.layoutChildren()


# CONTROLLERS
# Stores the CHOPNet's parameters as a template.
group = chopnet.parmTemplateGroup()

# Create different parameters to control the effect.
stab = hou.FloatParmTemplate(
    "stab",
    "Stabilization",
    1,
    default_value=[.5],
    min=.1,
    max=1.5,
    help="How stabilized you want your camera to be (0.1 = Shaky footage, >1 = Stabilized footage)."
    )
    
amp = hou.FloatParmTemplate(
    "amp",
    "Amplitude",
    1,
    default_value=[10],
    max=20,
    help="How far the camera moves (0 = No motion, >10 = Wider range)."
    )
    
seed = hou.FloatParmTemplate(
    "seed",
    "Seed",
    1,
    default_value=[1],
    min=0,
    help="Add variation to your camera by changing this value."
    )

# Create a Tab to store the parameters we just created.
folder = hou.FolderParmTemplate(
    "cameraShake",
    "Camera Shake",
    parm_templates=[stab, amp, seed],
    )

# Add the Tab to the CHOPNet's template.
group.append(folder)

# Applies this new template to the CHOPNet.
chopnet.setParmTemplateGroup(group)

# The «Stabilization» parameter controls the noise's «Period» parameter.
noise_node.parm("period").setExpression(f"ch('{chopnet.path()}/stab')")

# The «Amp» parameter controls the noise's «Amp» parameter
noise_node.parm("amp").setExpression(f"ch('{chopnet.path()}/amp')")

# The «Seed» parameter controls the noise's Y Translate (changes the waveform and adds variation).
noise_node.parm("transy").setExpression(f"ch('{chopnet.path()}/seed')")

# Deselect everything except the CHOPNet so the user sees where to tweak the values.
chopnet.setCurrent(1, clear_all_selected=1)
