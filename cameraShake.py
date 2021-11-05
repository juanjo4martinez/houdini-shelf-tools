### CAMERA SHAKE
### Add some movement to your camera to make it look like it's handheld
### Make sure your Camera node is selected when running this tool!

# Store the selected camera in a variable
thisNode = hou.selectedNodes()
thisCam = thisNode[0]

# Create variable for /obj path
obj = hou.node("/obj")

# Create CHOP Network called "cameraShake"
chopnet = obj.findOrCreateMotionEffectsNetwork()
chopnet.setName("cameraShake_"+thisCam.name(), unique_name=True)

# Inside the CHOPNet, create a Channel node and give it a name
channelNode = chopnet.createNode("channel")
channelNode.setName(thisCam.name()+"_rotationClips", unique_name=True)

# Pick the rotation channels from the camera and use "Euler Rotation"
channelNode.parm("name0").set(thisCam.name()+":r")
channelNode.parm("type0").set(1)

# Store the newly created channel's values as individual variables
channelValue_x = channelNode.parm("value0x")
channelValue_y = channelNode.parm("value0y")
channelValue_z = channelNode.parm("value0z")

# Store the camera's rotation parameters as individual variables
camRot_x = thisCam.parm("rx")
camRot_y = thisCam.parm("ry")
camRot_z = thisCam.parm("rz")

# CONDITIONAL
# If the camera's rotation is animated, copy those keyframes into the channel's node values
# If the camera's rotation is NOT animated, just copy the camera's rotation values

if len(camRot_x.keyframes()) > 0:
    for k in camRot_x.keyframes():
        channelValue_x.setKeyframe(k)    
else: 
    channelNode.parm("value0x").set(thisCam.parm("rx").eval())

if len(camRot_y.keyframes()) > 0:
    for k in camRot_y.keyframes():
        channelValue_y.setKeyframe(k)
else: 
    channelNode.parm("value0y").set(thisCam.parm("ry").eval())

if len(camRot_z.keyframes()) > 0:
    for k in camRot_z.keyframes():
        channelValue_z.setKeyframe(k)    
else: 
    channelNode.parm("value0z").set(thisCam.parm("rz").eval())

# Set the channel units to Frames and the graph color to green
channelNode.parm("units").set(0)
channelNode.parmTuple("gcolor").set((0,1,0))

# Turn off the Export flag on the Channel node
channelNode.setExportFlag(0)

# Inside the CHOPNet, create a Math node
mathNode = channelNode.parent().createNode("math")
mathNode.setName(thisCam.name()+"_addNoiseToRotation", unique_name=True)

# The Math node will sum (Add) the rotation channels to the noise
mathNode.parm("chopop").set(1)

# Turn on the Display and Export flags on the Math node
mathNode.setDisplayFlag(1)
mathNode.setExportFlag(1)

# Inside the CHOPNet, create a Noise node
noiseNode = chopnet.createNode("noise")

# The name of the noise channels will be the same as in the Channel node (cam:rx,ry,rz)
noiseNode.parm("channelname").set('`run("chopls '+channelNode.path()+'")`')

# The seed of the noise will be $C (number of channels i.e: 3)
noiseNode.parm("seed").setExpression("$C")

# Set the roughness to 0 for camera-like movements
noiseNode.parm("rough").set(0)

# Plug the Channel and Noise nodes into the Math inputs
mathNode.setInput(0, channelNode)
mathNode.setInput(1, noiseNode)

# Layout nodes inside the CHOPNet
chopnet.layoutChildren()


### CONTROLLERS ###


# Stores the CHOPNet's parameters as a template
group = chopnet.parmTemplateGroup()

# Create different parameters to control the effect
stab = hou.FloatParmTemplate("stab", "Stabilization", 1, default_value=[.5], min=.1, max=1.5, help="How stabilized you want your camera to be (0.1 = Shaky footage, >1 = Stabilized footage).")
amp = hou.FloatParmTemplate("amp", "Amplitude", 1, default_value=[10], max=20, help="How far the camera moves (0 = No motion, >10 = Wider range).")
seed = hou.FloatParmTemplate("seed", "Seed", 1, default_value=[1], min=0, help="Add variation to your camera by changing this value.")

# Create a Tab to store the parameters we just created
folder = hou.FolderParmTemplate(
    "cameraShake",
    "Camera Shake",
    parm_templates=[stab, amp, seed],
    )

# Add the Tab to the CHOPNet's template
group.append(folder)

# Applies this new template to the CHOPNet
chopnet.setParmTemplateGroup(group)

# The «Stabilization» parameter controls the noise's «Period» parameter
noiseNode.parm("period").setExpression('ch("'+chopnet.path()+'/stab")')

# The «Amp» parameter controls the noise's «Amp» parameter
noiseNode.parm("amp").setExpression('ch("'+chopnet.path()+'/amp")')

# The "Seed" parameter controls the noise's Y Translate (changes the waveform and adds variation)
noiseNode.parm("transy").setExpression('ch("'+chopnet.path()+'/seed")')

# Deselect everything except the CHOPNet so the user sees where to tweak the values
chopnet.setCurrent(1, clear_all_selected=1)
