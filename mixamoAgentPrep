### MIXAMO AGENTPREP 
### Use this code if you are using models from mixamo.com for your Crowd sims and need to set up their joints for Foot Planting
### Make sure to have your Agent node selected when clicking!

# Store the selected node in a variable
thisNode = hou.selectedNodes()

# Create an auxiliary Null node and append it to our Agent node
tempNode = thisNode[0]
null = tempNode.parent().createNode("null")
null.setInput(0, tempNode)

# Select the Null node so that it becomes the new "thisNode"
null.setSelected(True, clear_all_selected=True)
thisNode = hou.selectedNodes()

# Look for the joints and assign them to a variable 
import crowdstoolutils
lst = crowdstoolutils.buildTransformMenu(thisNode[0])

for string in lst:
    
    # Left leg
    if string.endswith("LeftUpLeg"):
        upperLeg_L = string 
    if string.endswith("LeftLeg"):
        knee_L = string
    if string.endswith("LeftFoot"):    
        ankle_L = string
    if string.endswith("LeftToeBase"):
        toe_L = string
    
    # Right leg    
    if string.endswith("RightUpLeg"):
        upperLeg_R = string 
    if string.endswith("RightLeg"):
        knee_R = string
    if string.endswith("RightFoot"):    
        ankle_R = string
    if string.endswith("RightToeBase"):
        toe_R = string

    # Torso  
    if string.endswith("Hips"):
        hips = string 
    if string.endswith("Spine"):
        lowerBack = string
    if string.endswith("Head"):    
        head = string
        
    # Left arm    
    if string.endswith("LeftShoulder"):
        upperArm_L = string 
    if string.endswith("LeftArm"):
        lowerArm_L = string
    if string.endswith("LeftHand"):    
        hand_L = string
            
    # Right arm    
    if string.endswith("RightShoulder"):
        upperArm_R = string 
    if string.endswith("RightArm"):
        lowerArm_R = string
    if string.endswith("RightHand"):    
        hand_R = string

# Create Agent Prep and appends it to the selected node        
thisNode = thisNode[0]
agentPrep = thisNode.parent().createNode("agentprep")
agentPrep.setInput(0, thisNode)

# Set up the Upper Limbs
agentPrep.parm("upperlimbs").set(2)

agentPrep.parm("upperarm1").set(upperArm_L)
agentPrep.parm("lowerarm1").set(lowerArm_L)
agentPrep.parm("hand1").set(hand_L)

agentPrep.parm("upperarm2").set(upperArm_R)
agentPrep.parm("lowerarm2").set(lowerArm_R)
agentPrep.parm("hand2").set(hand_R)

# Set up the Torso
agentPrep.parm("torso").set(1)

agentPrep.parm("hips1").set(hips)
agentPrep.parm("lowerback1").set(lowerBack)
agentPrep.parm("head1").set(head)

# Set up the Lower Limbs
agentPrep.parm("lowerlimbs").set(2)

agentPrep.parm("upperleg1").set(upperLeg_L)
agentPrep.parm("knee1").set(knee_L)
agentPrep.parm("ankle1").set(ankle_L)
agentPrep.parm("toe1").set(toe_L)

agentPrep.parm("upperleg2").set(upperLeg_R)
agentPrep.parm("knee2").set(knee_R)
agentPrep.parm("ankle2").set(ankle_R)
agentPrep.parm("toe2").set(toe_R)

# Set the display and render flag on the Agent Prep node
agentPrep.setDisplayFlag(True)
agentPrep.setRenderFlag(True)

# Create Foot Plant CHOP Network
agentPrep.parm("createchopnet").pressButton()

# Kill the auxiliary Null node
null.destroy()
