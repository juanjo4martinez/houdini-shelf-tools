"""
AGENT BROWSER v1.0
------------------
Easy way to browse through your characters and import them as Agents
for your Crowd simulation.

HOW IT WORKS
------------
This tool looks for .FBX files in your Agent directory and displays them
as a list with the help of a UI.

You can then pick one or more Agents from the list, and the tool will
automatically set up the nodes for you (Agent, Agent Clip, Agent Layer
and Agent Prep).

Feel free to change the 'AGENT_DIR' variable with your own Agent directory.

IMPORTANT
---------
This code looks for subfolders too, so if you store your .FBX motion clips
in the same directory as your .FBX agents you may get some unexpected results.

In order to avoid that, make sure to have ONLY YOUR .FBX CHARACTERS in the
Agent Directory.

* If you are using HOUDINI 18.5, replace the 'copysourcelayer1' parameter
by 'sourcecopy' so that it can be run in the old AGENT LAYER node.
"""

# Import built-in modules.
from collections import OrderedDict
import os
import sys

# This is where your Agents are stored.
AGENT_DIR = "F:/3D/modelos"

# Dictionary to store Agent names and file paths.
agents = OrderedDict()

# Iterate the Agent Directory and get its path, subdirectories and files.
for path,subdirs,files in os.walk(AGENT_DIR):
   
    # Iterate .FBX files and store their names and paths in the dictionary.
    for file in files:
        if file.endswith(".fbx"):
            agent_name = file.split(".")
            agent_name = agent_name[0]
            filepath = os.path.join(path, file)
            agents[agent_name] = filepath
            
# Unpack names and paths from the dictionary and store them in lists.
agent_list = []
[agent_list.append(agent_name) for agent_name in agents.keys()]

file_list = []
[file_list.append(filepath) for filepath in agents.values()]

# Open a "Select from list" window and ask the user to choose one or more agents.
# NOTE: The output will be a tuple with index(es).
selected_agents = hou.ui.selectFromList(agent_list,
                                title="Agent Browser",
                                message="Select the character(s) you want to import as agent(s):",
                                column_header="Agents",
                                width=300)

# If the user doesn't select any agent, stop the program.
try:
    selected_agents[0]
except IndexError:
    sys.exit()

# Get the "agentSetup" node - we'll use this to check if it exists or not.
obj = hou.node("/obj/")
geo_node_name = "agentSetup"
agent_setup_node = hou.node(f"{obj.path()}/{geo_node_name}")

# If "agentSetup" doesn't exist, create it.
if not agent_setup_node:
    agent_setup_node = obj.createNode("geo", geo_node_name)
   
# Iterate every index in the "selected_agents" tuple.
for index in selected_agents:

    # Get the "Agent" node - we'll use this to check if it exists or not.
    agent_node = hou.node(f"{agent_setup_node.path()}/{agent_list[index]}")

    # If the Agent node doesn't exist, create it.
    if not agent_node:
        agent_node = agent_setup_node.createNode("agent", agent_list[index])
       
        # Set the Agent Name.
        agent_node.parm("agentname").set("$OS")
       
        # Set the Input as FBX and the corresponding file path.
        agent_node.parm("input").set(2)
        agent_node.parm("fbxfile").set(file_list[index])
        agent_node.parm("fbxclipname").set("tpose")
   
        # Create an Agent Clip node and connect it to the Agent node.
        agent_clip_node = agent_setup_node.createNode("agentclip", f"{agent_list[index]}_clips")
        agent_clip_node.setInput(0, agent_node)

        # Create an Agent Layer node, connect it to the Agent Clip node,
        # and activate the Source Layer checkbox so we can see the character.
        agent_layer_node = agent_setup_node.createNode("agentlayer", f"{agent_list[index]}_layer")
        agent_layer_node.setInput(0, agent_clip_node)
        agent_layer_node.parm("copysourcelayer1").set(1)

        # Create an Agent Prep node and connect it to the Agent Layer node.
        agent_prep_node = agent_setup_node.createNode("agentprep", f"{agent_list[index]}_prep")
        agent_prep_node.setInput(0, agent_layer_node)

        # Create an OUT (Null) node and connect it to the Agent Prep node.
        out_node = agent_setup_node.createNode("null", f"OUT_{agent_list[index]}")
        out_node.setInput(0, agent_prep_node)
        
        # Activate the Display/Render flags and set the color to black.
        out_node.setDisplayFlag(True)
        out_node.setRenderFlag(True)
        out_node.setColor(hou.Color((0, 0, 0)))

        # Layout nodes inside "agentSetup".
        agent_setup_node.layoutChildren()

    # If the Agent node already exists in the scene, let the user know.
    else:
        hou.ui.displayMessage(f"The agent «{agent_list[index]}» is already in your scene.")
