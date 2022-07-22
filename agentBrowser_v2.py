"""
AGENT BROWSER v2.0
------------------
Easy way to browse through your characters folder and import them as
Agents for your Crowd simulation.

This version includes a dedicated UI with thumbnails, a search filter
and a green marker to let the user know if the character is already
in the scene.

HOW IT WORKS
------------
When you launch the tool for the first time, it will go through your
Agent Directory and generate the thumbnails (it may take a few seconds).

Then a window will open with all your characters displayed in a grid.

Click on the character you want to add as Agent, and the tool will
automatically set up the Agent nodes for you. A green line will appear
below the character to let you know that it is already in your scene.

Feel free to change the 'AGENT_DIR' variable in the ThumbnailGenerator()
class with your own Agent Directory.

IMPORTANT
---------
This code looks for subfolders too, so if you store your .FBX motion clips
in the same directory as your .FBX agents you may get some unexpected results.
In order to avoid that, make sure to have ONLY YOUR .FBX CHARACTERS in the
Agent Directory, each in its own folder.

* If you are using HOUDINI 18.5, replace the .items() method by .iteritems()
so that it can be run in PYTHON 2.7.

* Replace also the 'copysourcelayer1' parameter by 'sourcecopy' so that it works
with the old version of the Agent Layer node.
"""

# Import built-in modules.
from collections import OrderedDict
import os
from PySide2 import QtGui, QtWidgets, QtCore
import sys


class ThumbnailGenerator():
    """
    Look for .FBX characters in your directory, import them as Agents
    and generate a thumbnail (basic OpenGL render with camera set to Front View)
    for each of them.
   
    Thumbnails are saved as .JPEG in the same folder as your .FBX characters.    
    """

    
    def check_thumbnails(self):
        """Check if all .FBX files have a thumbnail, and if not, generate them."""
        # This is where your Agents are stored.
        self.agent_dir = "F:/3D/modelos"

        # Initialize lists and a dictionary.
        fbx_files, jpeg_files = [], []
        self.need_thumbnail = {}

        # Iterate the Agent Directory and get its path, subdirectories and files.
        for path, subdirs, files in os.walk(self.agent_dir):

            # Iterate every file in the Agent Directory.
            for file in files:
               
                # If it's an .FBX, append it to the "fbx_files" list.
                if file.endswith(".fbx"):        
                    fbx_files.append(file)
       
                # If it's a .JPEG, append it to the "jpeg_files" list.
                elif file.endswith(".jpeg"):            
                    jpeg_files.append(file)

        # Iterate every .FBX file in the "fbx_files" list.
        for fbx_file in fbx_files:

            # If this .FBX file doesn't have a thumbnail,
            # store its filename and path in the dictionary.
            if fbx_file.replace("fbx","jpeg") not in jpeg_files:
                agent_name = fbx_file.split(".")
                agent_name = agent_name[0]
                fbx_path = os.path.join(self.agent_dir, agent_name, fbx_file).replace("\\","/")
                self.need_thumbnail[agent_name] = fbx_path                

        # Run SETUP_SCENE() and SETUP_NODES()
        # for those .FBX that don't have a thumbnail.
        if self.need_thumbnail:                              
            self.setup_scene()
            self.setup_nodes()


    def search_fbx(self):
        """Search for .FBX files and store them in a dictionary."""
        # Dictionary to store Agent names and file paths.
        self.fbx_dict = OrderedDict()

        # Iterate the Agent Directory and get its path, subdirectories and files.
        for path, subdirs, files in os.walk(self.agent_dir):

            # Iterate .FBX files and store their names and paths in the dictionary.
            for file in files:
                if file.endswith(".fbx"):
                    agent_name = file.split(".")
                    agent_name = agent_name[0]
                    filepath = os.path.join(path, file).replace('\\','/')
                    self.fbx_dict[agent_name] = filepath

        # Return the dictionary (we'll need it later when generating the UI).
        return self.fbx_dict
   
       
    def setup_scene(self):
        """Turn off the reference grid and set the viewport to Front view."""
        # Get the Scene Viewer.
        scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)

        # Turn off the reference grid.
        self.grid = scene_viewer.referencePlane()
        self.grid.setIsVisible(False)

        # Get the Viewport and set it to Front View.
        self.viewport = scene_viewer.curViewport()
        self.viewport.changeType(hou.geometryViewportType.Front)


    def setup_nodes(self):    
        """Generate the nodes you need to take a screenshot of the Agent."""
        # Display a status message in Houdini.
        hou.ui.setStatusMessage("Generating thumbnails. Please wait...",
                                severity=hou.severityType.ImportantMessage)
            
        # /obj context.
        obj = hou.node("/obj/")
       
        # Iterate every item in the "need_thumbnail" dictionary.
        for agent, filepath in self.need_thumbnail.items():
            # Create a Geometry node.
            geo = obj.createNode("geo",f"agent_{agent}")
           
            # Create an Agent node and point to the .FBX file.
            agent_node = geo.createNode("agent")
            agent_node.parm("input").set(2)
            agent_node.parm("fbxfile").set(filepath)
       
            # Access the geometry level and generate a bounding box.
            agent_geo = agent_node.geometry()
            bbox = agent_geo.boundingBox()

            # Frame the bounding box we just created.
            self.viewport.frameBoundingBox(bbox)

            # Create a Camera node and set it to a square resolution.
            cam_node = obj.createNode("cam",f"cam_{agent}")
            cam_node.parmTuple("res").set((720,720))
           
            # Copy the viewport frame onto the camera.
            self.viewport.saveViewToCamera(cam_node)
           
            # Reduce the Ortho Width by 65%.
            orthowidth = cam_node.parm("orthowidth").eval()
            cam_node.parm("orthowidth").set(orthowidth*0.65)

            # Create an OpenGL node in /out.
            out = hou.node("/out/")
            opengl_node = out.createNode("opengl",f"openGL_{agent}")
           
            # Set the Frame Range to just the first frame.
            frame_range = hou.playbar.playbackRange()
            opengl_node.parm("trange").set(1)
            opengl_node.parmTuple("f").set((frame_range[0],frame_range[0],1))

            # Set the output path and file format.
            opengl_node.parm("camera").set(cam_node.path())
            opengl_node.parm("picture").set(filepath.replace("fbx","jpeg"))
            opengl_node.parm("vobjects").set(geo.name())
           
            # Run the OpenGL render.
            opengl_node.parm("execute").pressButton()

            # Clean up the network.
            geo.destroy()
            cam_node.destroy()
            opengl_node.destroy()

        # Turn on the reference grid and restore viewport to Perspective view.
        self.grid.setIsVisible(True)
        self.viewport.changeType(hou.geometryViewportType.Perspective)
        self.viewport.frameAll()

        # Display a status message in Houdini.
        hou.ui.setStatusMessage("Thumbnails have been successfully generated.")


    def run(self):
        """Run the CHECK_THUMBNAILS() method.

        If any thumbnail is missing, it will trigger the rest of the program.
        """
        self.check_thumbnails()


# Create an instance of the ThumbnailGenerator class and launch it.
thumbnail_generator = ThumbnailGenerator()
thumbnail_generator.run()


class AgentBrowser(QtWidgets.QWidget):
    """
    Look for .FBX files in your Agent directory and displays them in a UI.

    Click on the character you want to add as Agent, and the tool will
    automatically set up the Agent nodes for you.
    """
    
    
    def __init__(self):
        """Initialize the UI."""
        super(AgentBrowser, self).__init__()

        # Set the title of the window.
        self.setWindowTitle("Agent Browser v2.0")

        # Set the window to be always on top.
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Set a minimum size for the window.
        self.setMinimumSize(750, 500)

        # >>> Launch the UI.
        self.initUI()


    def initUI(self):
        """Customize the UI."""
        # Apply a Grid Layout to the main window.
        self.windowLayout = QtWidgets.QGridLayout()  
        self.setLayout(self.windowLayout)

        # Run the search filter.
        self.search_filter()
       
        # Create the main scroll area.
        self.scrollMain = QtWidgets.QScrollArea()
        self.scrollMain.setWidgetResizable(True)

        # Generate a new style for the Scroll Bar.
        scrollStyle = "QScrollBar {"
        scrollStyle += "border: 1px solid grey;"
        scrollStyle += "background: #454545;"
        scrollStyle += "}"
       
        # Apply the new stylesheet to the main scroll area.
        self.scrollMain.setStyleSheet(scrollStyle)
               
        # Add a Grid Layout to the main scroll area.
        self.scrollMainLayout = QtWidgets.QGridLayout()
        self.scrollMain.setLayout(self.scrollMainLayout)        
       
        # Create the main widget where we will store everything.
        self.mainWidget = QtWidgets.QWidget()
       
        # Add a Grid Layout to the main widget.
        self.mainWidgetLayout = QtWidgets.QGridLayout()        
        self.mainWidget.setLayout(self.mainWidgetLayout)
               
        # Link the main widget to the main scroll area.
        self.scrollMain.setWidget(self.mainWidget)
       
        # Add the main scroll area to the main window layout.
        self.windowLayout.addWidget(self.scrollMain)      
                     
        # Initialize counters - this will help us know when to start a new row.
        self.across, self.down = 0, 0
       
        # Create a Button Group.
        self.buttonGroup = QtWidgets.QButtonGroup()
       
        # Run ADD_BUTTON() for each Agent in the dictionary.
        # NOTE: The dictionary is first put in alphabetical order.
        for i, (agent_in_dict, filepath_in_dict) in enumerate(sorted(thumbnail_generator.search_fbx().items())):
            self.add_button(i, agent_in_dict, filepath_in_dict)                                                                                


    def search_filter(self):
        """Add a Line Edit (text field) to use as a filter."""
   
        # Create a widget to store the label and Line Edit.
        self.searchWidget = QtWidgets.QWidget()

        # Add a Horizontal Box Layout to the widget.
        self.searchWidgetLayout = QtWidgets.QHBoxLayout()
        self.searchWidget.setLayout(self.searchWidgetLayout)

        # Create a label and add it to the widget layout.
        self.filterLabel = QtWidgets.QLabel("Filter:")
        self.searchWidgetLayout.addWidget(self.filterLabel)

        # Create a Line Edit and add it to the widget layout.
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.searchLineEdit.textChanged.connect(self.update_grid)
        self.searchWidgetLayout.addWidget(self.searchLineEdit)        

        # Add widget to the main widget layout.
        self.windowLayout.addWidget(self.searchWidget)


    def update_grid(self, text):
        """Show only the buttons whose name matches the search filter input."""

        # Iterate every button in the group.
        for button in self.buttonGroup.buttons():
            # If the search filter input matches the text on the button, show it.
            if text.lower() in button.text().lower():
                button.show()
            # If it doesn't match, hide the button.
            else:
                button.hide()


    def update_button_color(self, button, agent_in_dict):
        """
        Check if the Agent is already in your scene.        
        If so, change the button color to green.
        """
        # Store in a list the Agents that are already in your scene.
        agents_in_scene = [node.parm("agentname").eval() for node in hou.nodeType("Sop/agent").instances()]

        # If the Agent for whom we are generating the button is in the list,
        # change the style of that button.
        if agent_in_dict in agents_in_scene:
            # Generate a new style for the Tool Button.
            newStyle = "QToolButton {"
            newStyle += "border-style: hidden;"
            newStyle += "padding: 5px;"
            newStyle += "border-bottom: 5px solid green;"
            newStyle += "}"
           
            newStyle += "QToolButton:hover {"
            newStyle += "background-color: #545454;"
            newStyle += "}"

            # Apply the new stylesheet to the Tool Button.
            button.setStyleSheet(newStyle)


    def add_button(self, i, agent_in_dict, filepath_in_dict):
        """
        Create a Tool Button with the Agent's name and thumbnail,
        then add it to the Main Widget Layout.
        """
        # Create a Tool Button and add it to the button group.
        # The index of this button will be the iterator 'i'.
        self.button = QtWidgets.QToolButton()
        self.buttonGroup.addButton(self.button, i)

        # Set the button style to "Text Under Icon".
        self.button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # The text on the button will be the Agent's name.
        self.button.setText(agent_in_dict)
       
        # Create an Icon and link it to the Agent's thumbnail.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(filepath_in_dict.replace("fbx", "jpeg")))

        # Add the Icon to the Tool Button.
        self.button.setIcon(icon)
        self.button.setIconSize(QtCore.QSize(150,150))
       
        # Generate a new style for the Tool Button.
        style = "QToolButton {"
        style += "border-style: hidden;"
        style += "border-width: 5px;"
        style += "}"
       
        style += "QToolButton:hover {"
        style += "background-color: #545454;"
        style += "}"

        # Apply the new stylesheet to the Tool Button.
        self.button.setStyleSheet(style)

        # Update the button's color.
        self.update_button_color(self.button, agent_in_dict)

        # When the button is clicked, import the corresponding Agent.
        self.button.clicked.connect(lambda: self.import_agent(agent_in_dict, filepath_in_dict, i))

        # Add Tool Button to the main widget layout.
        self.mainWidgetLayout.addWidget(self.button, self.down, self.across)
        self.across += 1

        # If we already have 4 elements in our grid, start a new row.
        if self.across == 4:
            self.across = 0
            self.down += 1


    def import_agent(self, agent_in_dict, filepath_in_dict, i):
        """Create a Geometry node called 'agentSetup' to store Agent nodes."""
        # /obj context.
        obj = hou.node("/obj/")

        # Get the "agentSetup" node.
        # We'll use this to check if we should create it or update the existing one.
        geo_node_name = "agentSetup"
        agent_setup_node = hou.node(f"{obj.path()}/{geo_node_name}")
       
        # If "agentSetup" doesn't exist, create it.
        if not agent_setup_node:
            agent_setup_node = obj.createNode('geo', geo_node_name)
               
        # Get the Agent node.
        # We'll use this to check if we should create it or update the existing one.
        agent_node = hou.node(f"{agent_setup_node.path()}/{agent_in_dict}")

        # If the Agent node doesn't exist, create it.
        if not agent_node:
            agent_node = agent_setup_node.createNode("agent", agent_in_dict)

            # Set the Agent Name.
            agent_node.parm("agentname").set("$OS")

            # Set the Input as FBX and the corresponding file path.
            agent_node.parm("input").set(2)
            agent_node.parm("fbxfile").set(filepath_in_dict)
            agent_node.parm("fbxclipname").set("tpose")
                         
            # Create an Agent Clip node and connect it to the Agent node.
            agent_clip_node = agent_setup_node.createNode("agentclip", f"{agent_in_dict}_clips")
            agent_clip_node.setInput(0, agent_node)
   
            # Create an Agent Layer node, connect it to the Agent Clip node,
            # and activate the Source Layer checkbox so we can see the character.
            agent_layer_node = agent_setup_node.createNode("agentlayer", f"{agent_in_dict}_layer")
            agent_layer_node.setInput(0, agent_clip_node)
            agent_layer_node.parm("copysourcelayer1").set(1)

            # Create an Agent Prep node and connect it to the Agent Layer node.
            agent_prep_node = agent_setup_node.createNode("agentprep", f"{agent_in_dict}_prep")
            agent_prep_node.setInput(0, agent_layer_node)

            # Create an OUT (Null) node and connect it to the Agent Prep node.
            out_node = agent_setup_node.createNode("null", f"OUT_{agent_in_dict}")
            out_node.setInput(0, agent_prep_node)

            # Activate the Display/Render flags and set the color to black.
            out_node.setDisplayFlag(True)
            out_node.setRenderFlag(True)
            out_node.setColor(hou.Color((0, 0, 0)))

            # Layout nodes inside "agentSetup".
            agent_setup_node.layoutChildren()
           
            # Iterate every button in the group.
            for button in self.buttonGroup.buttons():
            # Applies the action to each button independently.
                if button is self.buttonGroup.button(i):
                    # Update the color (make it green).
                    self.update_button_color(button, agent_in_dict)

        # If the Agent node is already in the scene, let the user know.
        else:            
            self.message = QtWidgets.QMessageBox()
            self.message.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            self.message.setWindowTitle("Agent Browser")
            self.message.setText(f"The agent «{agent_in_dict}» is already in your scene.")
            self.message.show()

# Create an instance of the AgentBrowser class and display it in a new window.
agentBrowserUI = AgentBrowser()
agentBrowserUI.show()
