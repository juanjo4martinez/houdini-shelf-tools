"""
MIXAMO AGENTPREP
----------------
Use this code if you are using models from mixamo.com for your Crowd sims
and need to set up their joints for Foot Planting.

Make sure to have your Agent node selected when clicking!
"""

# Import third-party modules.
import crowdstoolutils

# Get the selected node.
this_node = hou.selectedNodes()

# Create an auxiliary Null node and connect it to our Agent node.
aux_node = this_node[0]
null = aux_node.parent().createNode("null")
null.setInput(0, aux_node)

# Select the Null node so that it becomes the new "this_node".
null.setSelected(True, clear_all_selected=True)
this_node = hou.selectedNodes()

# Get the joints and configure them.
joints = crowdstoolutils.buildTransformMenu(this_node[0])

for joint in joints:    
    # Left leg.
    if joint.endswith("LeftUpLeg"):
        upperLeg_L = joint 
    if joint.endswith("LeftLeg"):
        knee_L = joint
    if joint.endswith("LeftFoot"):    
        ankle_L = joint
    if joint.endswith("LeftToeBase"):
        toe_L = joint
    
    # Right leg.
    if joint.endswith("RightUpLeg"):
        upperLeg_R = joint 
    if joint.endswith("RightLeg"):
        knee_R = joint
    if joint.endswith("RightFoot"):    
        ankle_R = joint
    if joint.endswith("RightToeBase"):
        toe_R = joint

    # Torso.
    if joint.endswith("Hips"):
        hips = joint 
    if joint.endswith("Spine"):
        lowerBack = joint
    if joint.endswith("Head"):    
        head = joint

    # Left arm.
    if joint.endswith("LeftShoulder"):
        upperArm_L = joint
    if joint.endswith("LeftArm"):
        lowerArm_L = joint
    if joint.endswith("LeftHand"):
        hand_L = joint

    # Right arm.
    if joint.endswith("RightShoulder"):
        upperArm_R = joint
    if joint.endswith("RightArm"):
        lowerArm_R = joint
    if joint.endswith("RightHand"):
        hand_R = joint

# Create an Agent Prep node and connect it to the selected node.
this_node = this_node[0]
agent_prep_node = this_node.parent().createNode("agentprep")
agent_prep_node.setInput(0, this_node)

# Set the Upper Limbs.
agent_prep_node.parm("upperlimbs").set(2)

agent_prep_node.parm("upperarm1").set(upperArm_L)
agent_prep_node.parm("lowerarm1").set(lowerArm_L)
agent_prep_node.parm("hand1").set(hand_L)

agent_prep_node.parm("upperarm2").set(upperArm_R)
agent_prep_node.parm("lowerarm2").set(lowerArm_R)
agent_prep_node.parm("hand2").set(hand_R)

# Set the Torso.
agent_prep_node.parm("torso").set(1)

agent_prep_node.parm("hips1").set(hips)
agent_prep_node.parm("lowerback1").set(lowerBack)
agent_prep_node.parm("head1").set(head)

# Set the Lower Limbs.
agent_prep_node.parm("lowerlimbs").set(2)

agent_prep_node.parm("upperleg1").set(upperLeg_L)
agent_prep_node.parm("knee1").set(knee_L)
agent_prep_node.parm("ankle1").set(ankle_L)
agent_prep_node.parm("toe1").set(toe_L)

agent_prep_node.parm("upperleg2").set(upperLeg_R)
agent_prep_node.parm("knee2").set(knee_R)
agent_prep_node.parm("ankle2").set(ankle_R)
agent_prep_node.parm("toe2").set(toe_R)

# Set the Display/Render flag on the Agent Prep node.
agent_prep_node.setDisplayFlag(True)
agent_prep_node.setRenderFlag(True)

# Create Foot Plant CHOP Network.
agent_prep_node.parm("createchopnet").pressButton()

# Delete the auxiliary Null node.
null.destroy()
