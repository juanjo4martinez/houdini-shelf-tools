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

# Get the joints.
joints = crowdstoolutils.buildTransformMenu(this_node[0])

# Create an Agent Prep node and connect it to the selected node.
this_node = this_node[0]
agent_prep_node = this_node.parent().createNode("agentprep")
agent_prep_node.setInput(0, this_node)

# Set the Display/Render flag on the Agent Prep node.
agent_prep_node.setDisplayFlag(True)
agent_prep_node.setRenderFlag(True)

# Activate the Upper Limbs.
agent_prep_node.parm("upperlimbs").set(2)

# Activate the Torso.
agent_prep_node.parm("torso").set(1)

# Activate the Lower Limbs.
agent_prep_node.parm("lowerlimbs").set(2)

# Iterate the joints and apply them to the corresponding parameter.
for joint in joints:

    # Left leg.
    if joint.endswith("LeftUpLeg"):
        agent_prep_node.parm("upperleg1").set(joint)
    if joint.endswith("LeftLeg"):
        agent_prep_node.parm("knee1").set(joint)
    if joint.endswith("LeftFoot"):    
        agent_prep_node.parm("ankle1").set(joint)
    if joint.endswith("LeftToeBase"):
        agent_prep_node.parm("toe1").set(joint)
    
    # Right leg.
    if joint.endswith("RightUpLeg"):
        agent_prep_node.parm("upperleg2").set(joint)
    if joint.endswith("RightLeg"):
        agent_prep_node.parm("knee2").set(joint)
    if joint.endswith("RightFoot"):    
        agent_prep_node.parm("ankle2").set(joint)
    if joint.endswith("RightToeBase"):
        agent_prep_node.parm("toe2").set(joint)

    # Torso.
    if joint.endswith("Hips"):
        agent_prep_node.parm("hips1").set(joint)
    if joint.endswith("Spine"):
        agent_prep_node.parm("lowerback1").set(joint)
    if joint.endswith("Head"):    
        agent_prep_node.parm("head1").set(joint)
        
    # Left arm.
    if joint.endswith("LeftShoulder"):
        agent_prep_node.parm("upperarm1").set(joint)
    if joint.endswith("LeftArm"):
        agent_prep_node.parm("lowerarm1").set(joint)
    if joint.endswith("LeftHand"):
        agent_prep_node.parm("hand1").set(joint)

    # Right arm.
    if joint.endswith("RightShoulder"):
        agent_prep_node.parm("upperarm2").set(joint)
    if joint.endswith("RightArm"):
        agent_prep_node.parm("lowerarm2").set(joint)
    if joint.endswith("RightHand"):
        agent_prep_node.parm("hand2").set(joint)

# Create Foot Plant CHOP Network.
agent_prep_node.parm("createchopnet").pressButton()

# Delete the auxiliary Null node.
null.destroy()
