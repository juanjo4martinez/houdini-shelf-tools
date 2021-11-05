'''
AGENT BROWSER v2.0
Easy way to browse through your characters folder and import them as
Agents for your Crowd simulation.

This version includes a dedicated UI with thumbnails, a search filter
and a green marker to let the user know if the character is already
in the scene.

HOW IT WORKS:
When you launch the tool for the first time, it will go through your
Agent Directory and generate the thumbnails (it may take a few seconds).

Then a window will open with all your characters displayed in a grid.

Click on the character you want to add as Agent, and the tool will
automatically set up the Agent nodes for you. A green line will appear
below the character to let you know that it is already in your scene.

Feel free to change the "agentDir" variable in the ThumbnailGenerator()
class with your own Agent Directory.

IMPORTANT:
This code looks for subfolders too, so if you store your .FBX motion clips
in the same directory as your .FBX agents you may get some unexpected results.
In order to avoid that, make sure to have ONLY YOUR .FBX CHARACTERS in the
Agent Directory, each in its own folder.
'''

import os
import sys

from collections import OrderedDict
from PySide2 import QtGui, QtWidgets, QtCore


class ThumbnailGenerator():

    '''
    THUMBNAIL GENERATOR:
   
    This tool looks for .FBX characters in your directory, imports them as Agents
    and generates a thumbnail (basic OpenGL render with camera set to Front View)
    for each of them.
   
    Thumbnails are saved as .JPEG in the same folder as your .FBX characters.    
    '''

    def check_thumbnails(self):
        ''' Check if all the .FBX files have a thumbnail, and if not, launch
            the program to generate them '''
       
        # AGENT DIRECTORY: This is where your Agents are stored
        self.agentDir = 'C:/Users/14385/3D Objects/characters'
       
        # Initialize lists and a dictionary        
        fbxFiles, jpegFiles = [], []
        self.needThumbnail = {}
       
        # Iterate through the Agent Directory and look at its path, subdirectories and files
        for path,subdirs,files in os.walk(self.agentDir):
                     
            # Iterate through every file in the Agent Directory
            for file in files:
               
                # If it's an .FBX, append it to the "fbxFiles" list
                if file.endswith('.fbx'):        
                    fbxFiles.append(file)
       
                # If it's a .JPEG, append it to the "jpegFiles" list            
                elif file.endswith('.jpeg'):            
                    jpegFiles.append(file)
                     
               
        # Iterate through every .FBX file in the "fbxFiles" list                
        for fbxFile in fbxFiles:
       
            # If this .FBX file doesn't have a thumbnail, store its
            # file name and path in the dictionary
            if fbxFile.replace('fbx','jpeg') not in jpegFiles:        
               
                agentName = fbxFile.split('.')
                agentName = agentName[0]    
               
                fbxPath = os.path.join(self.agentDir, agentName, fbxFile).replace('\\','/')
               
                self.needThumbnail[agentName] = fbxPath                
               
   
        # Run SETUP_SCENE() and SETUP_NODES()
        # for those .FBX that don't have a thumbnail            
        if self.needThumbnail:                              
            self.setup_scene()
            self.setup_nodes()
   
   
    def search_fbx(self):
        ''' Search for .FBX files in your directory
            and store them in a dictionary '''
       
        # Initialize a dictionary to store Agent names and file paths
        self.dict = OrderedDict()
       
        # Iterate through the Agent Directory and look at its path, subdirectories and files
        for path,subdirs,files in os.walk(self.agentDir):        
         
            # Iterate through the .FBX files and store their names and paths in the dictionary
            for file in files:
         
                if file.endswith('.fbx'):  
             
                    agentName = file.split(".")
                    agentName = agentName[0]                  
                   
                    filePath = os.path.join(path, file).replace('\\','/')
                   
                    self.dict[agentName] = filePath                    
                       
        # Return the dictionary (we'll need it later when generating the UI)
        return self.dict
   
       
    def setup_scene(self):
        ''' Turn off the reference grid and set the viewport
            to Front view '''
   
        # Store the Scene Viewer in a variable
        sceneViewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
       
        # Turn off the reference grid
        self.grid = sceneViewer.referencePlane()
        self.grid.setIsVisible(False)
       
        # Store the Viewport in a variable and set it to Front View
        self.viewport = sceneViewer.curViewport()
        self.viewport.changeType(hou.geometryViewportType.Front)
       
   
    def setup_nodes(self):    
        ''' Generate the nodes you need to take a
            screenshot of the Agent '''
   
        # Display a status message in Houdini
        hou.ui.setStatusMessage('Generating thumbnails. Please wait...',
                                severity=hou.severityType.ImportantMessage)
            
        # /obj/ context
        obj = hou.node('/obj/')
       
        # Iterate through every item in the "needThumbnail" dictionary
        for agent, filePath in self.needThumbnail.iteritems():
       
            # Create a Geometry node
            geo = obj.createNode('geo','agent_{}'.format(agent))
           
            # Create an Agent node and point to the .FBX file
            agentNode = geo.createNode('agent')
            agentNode.parm('input').set(2)
            agentNode.parm('fbxfile').set(filePath)
       
            # Access the geometry level and generate a bounding box
            agentGeo = agentNode.geometry()
            bbox = agentGeo.boundingBox()
           
           
            # Frame the bounding box we just created
            self.viewport.frameBoundingBox(bbox)
           
           
            # Create a Camera node and set it to a square resolution
            camNode = obj.createNode('cam','cam_{}'.format(agent))
            camNode.parmTuple('res').set((720,720))
           
            # Copy the viewport frame onto the camera
            self.viewport.saveViewToCamera(camNode)
           
            # Reduce the Ortho Width by 50%
            orthowidth = camNode.parm('orthowidth').eval()
            camNode.parm('orthowidth').set(orthowidth*0.65)
       
           
            # Create an OpenGL node in /out/
            out = hou.node('/out/')
            openglNode = out.createNode('opengl','openGL_{}'.format(agent))
           
            # Set the Frame Range to just the first frame
            frameRange = hou.playbar.playbackRange()
            openglNode.parm('trange').set(1)
            openglNode.parmTuple('f').set((frameRange[0],frameRange[0],1))
           
            # Set the output path and file format
            openglNode.parm('camera').set(camNode.path())
            openglNode.parm('picture').set(filePath.replace('fbx','jpeg'))
            openglNode.parm('vobjects').set(geo.name())
           
            # Run the OpenGL render
            openglNode.parm('execute').pressButton()
           
           
            # Delete nodes
            geo.destroy()
            camNode.destroy()
            openglNode.destroy()                
           
            
        # Turn on the reference grid and restore viewport to Perspective view
        self.grid.setIsVisible(True)
        self.viewport.changeType(hou.geometryViewportType.Perspective)
        self.viewport.frameAll()
            
        # Display a status message in Houdini
        hou.ui.setStatusMessage('Thumbnails have been successfully generated.')


    def run(self):
        ''' Run the CHECK_THUMBNAILS() method.
            If any thumbnail is missing, it will
            trigger the rest of the program '''

        # Run CHECK_THUMBNAILS()            
        self.check_thumbnails()
       
               
# Create an instance of the ThumbnailGenerator() class
thumbGen = ThumbnailGenerator()

# Launch the RUN() method
thumbGen.run()



class AgentBrowser(QtWidgets.QWidget):

    '''
    AGENT BROWSER:
    Easy way to browse through your characters and import them as Agents
    for your Crowd simulation.
   
    This tool looks for .FBX files in your Agent directory and displays them
    as a grid in a UI.
   
    Click on the character you want to add as Agent, and the tool will
    automatically set up the Agent nodes for you.
    '''

    def __init__(self):
        ''' Initialize the UI '''
       
        super(AgentBrowser, self).__init__()

        # Set the title of the window
        self.setWindowTitle('Agent Browser v2.0')

        # Set the window to be always on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        # Set a minimum size for the window
        self.setMinimumSize(750, 500)
     
        # >>> Launch the UI
        self.initUI()

     
    def initUI(self):
        ''' Customize the UI '''
   
        # Apply a Grid Layout to the main window
        self.windowLayout = QtWidgets.QGridLayout()  
        self.setLayout(self.windowLayout)
             
        # Run SEARCH_FILTER()          
        self.search_filter()
       
        # Create the main scroll area
        self.scrollMain = QtWidgets.QScrollArea()
        self.scrollMain.setWidgetResizable(True)
       
        # Generate a new style for the Scroll Bar
        scrollStyle = 'QScrollBar {'
        scrollStyle += 'border: 1px solid grey;'
        scrollStyle += 'background: #454545;'
        scrollStyle += '}'
       
        # Apply the new stylesheet to the main scroll area
        self.scrollMain.setStyleSheet(scrollStyle)
               
        # Add a Grid Layout to the main scroll area
        self.scrollMainLayout = QtWidgets.QGridLayout()
        self.scrollMain.setLayout(self.scrollMainLayout)        
       
        # Create the main widget where we will store everything
        self.mainWidget = QtWidgets.QWidget()
       
        # Add a Grid Layout to the main widget
        self.mainWidgetLayout = QtWidgets.QGridLayout()        
        self.mainWidget.setLayout(self.mainWidgetLayout)
               
        # Link the main widget to the main scroll area
        self.scrollMain.setWidget(self.mainWidget)
       
        # Add the main scroll area to the main window layout
        self.windowLayout.addWidget(self.scrollMain)      
                     
        # Initialize grid counters
        # This will help us know when to start a new row
        self.across, self.down = 0, 0
       
        # Create a Button Group
        self.buttonGroup = QtWidgets.QButtonGroup()
       
        # Run ADD_BUTTON() for each Agent in the dictionary
        # Note: The dictionary is first put in alphabetical order
        for i, (agent_in_dict, filePath_in_dict) in enumerate(sorted(thumbGen.search_fbx().iteritems())):
            self.add_button(i, agent_in_dict, filePath_in_dict)                                                                                
       
       
    def search_filter(self):
        ''' Add a Line Edit (text field) to use as a filter '''        
   
        # Create a widget to store the label and Line Edit
        self.searchWidget = QtWidgets.QWidget()
       
        # Add a Horizontal Box Layout to the widget
        self.searchWidgetLayout = QtWidgets.QHBoxLayout()
        self.searchWidget.setLayout(self.searchWidgetLayout)  
       
        # Create a label and add it to the widget layout
        self.filterLabel = QtWidgets.QLabel('Filter:')
        self.searchWidgetLayout.addWidget(self.filterLabel)
       
        # Create a Line Edit and add it to the widget layout
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.searchLineEdit.textChanged.connect(self.update_grid)
        self.searchWidgetLayout.addWidget(self.searchLineEdit)        
     
        # Add widget to the main widget layout
        self.windowLayout.addWidget(self.searchWidget)


    def update_grid(self, text):
        ''' Show only the buttons whose name matches
            the text in search_filter() '''
           
        # Iterate through every button in the group
        for button in self.buttonGroup.buttons():
       
            # If the text in the search filter matches
            # the text on the button, show it
            if text.lower() in button.text().lower():
                button.show()
           
            # If it doesn't match, hide the button
            else:
                button.hide()
       
               
    def update_button_color(self, button, agent_in_dict):
        ''' Determine if the Agent is already in your scene,
            and if so, change the button color to green '''
           
        # Store in a list the Agents that are already in your scene
        agents_in_scene = [node.parm('agentname').eval() for node in hou.nodeType('Sop/agent').instances()]
       
        # If the Agent for whom we are generating the button
        # is in the list, change the style of that button
        if agent_in_dict in agents_in_scene:
       
            # Generate a new style for the Tool Button
            newStyle = 'QToolButton {'
            newStyle += 'border-style: hidden;'    
            newStyle += 'padding: 5px;'
            newStyle += 'border-bottom: 5px solid green;'
            newStyle += '}'
           
            newStyle += 'QToolButton:hover {'
            newStyle += 'background-color: #545454;'
            newStyle += '}'
       
            # Apply the new stylesheet to the Tool Button
            button.setStyleSheet(newStyle)              
       
             
    def add_button(self, i, agent_in_dict, filePath_in_dict):
        """ Create a Tool Button with the Agent's name and thumbnail
            and add it to the Main Widget Layout """
       
        # Create a Tool Button and add it to the button group
        # The index of this button will be the iterator 'i'
        self.button = QtWidgets.QToolButton()
        self.buttonGroup.addButton(self.button, i)

        # Set the button style to "Text Under Icon"
        self.button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # The text on the button will be the Agent's name
        self.button.setText(agent_in_dict)
       
        # Create an Icon and link it to the Agent's thumbnail
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(filePath_in_dict.replace('fbx', 'jpeg')))

        # Add the Icon to the Tool Button
        self.button.setIcon(icon)
        self.button.setIconSize(QtCore.QSize(150,150))
       
        # Generate a new style for the Tool Button
        style = 'QToolButton {'
        style += 'border-style: hidden;'        
        style += 'border-width: 5px;'
        style += '}'
       
        style += 'QToolButton:hover {'
        style += 'background-color: #545454;'
        style += '}'

        # Apply the new stylesheet to the Tool Button
        self.button.setStyleSheet(style)
       
        # Run UPDATE_BUTTON_COLOR()
        # This will determine if the button should be grey or green
        self.update_button_color(self.button, agent_in_dict)        
       
        # When the button is clicked, run IMPORT_AGENT()
        self.button.clicked.connect(lambda: self.import_agent(agent_in_dict, filePath_in_dict, i))                    

        # Add Tool Button to the main widget layout
        self.mainWidgetLayout.addWidget(self.button, self.down, self.across)
        self.across += 1
       
        # If we already have 4 elements in our grid, start a new row
        if self.across == 4:
            self.across = 0
            self.down += 1
           

    def import_agent(self, agent_in_dict, filePath_in_dict, i):
        ''' Create a Geometry node called "agentSetup" where we will
            add our Agent nodes '''

        # /obj/ context
        obj = hou.node('/obj/')
       
        # "agentSetup" node:
        # This will help us determine if we should create the node
        # or update the existing one
        geoNodeName = 'agentSetup'
        agentSetupNode = hou.node('{}/{}'.format(obj.path(), geoNodeName))
       
        # If "agentSetup" doesn't exist, create it
        if not agentSetupNode:
            agentSetupNode = obj.createNode('geo', geoNodeName)
               
        # Agent node:
        # This will help us determine if we should create the node or not
        agentNode = hou.node('{}/{}'.format(agentSetupNode.path(), agent_in_dict))

        # If the Agent node doesn't exist...
        if not agentNode:
           
            # Create an Agent node inside "agentSetup"
            agentNode = agentSetupNode.createNode('agent', agent_in_dict)
           
            # Set the Agent Name
            agentNode.parm('agentname').set('$OS')
           
            # Set Input as FBX and the file path
            agentNode.parm('input').set(2)
            agentNode.parm('fbxfile').set(filePath_in_dict)
            agentNode.parm('fbxclipname').set('tpose')
                         
            # Create an Agent Clip node and connect it to the Agent node
            agentClipNode = agentSetupNode.createNode('agentclip::2.0', '{}_clips'.format(agent_in_dict))
            agentClipNode.setInput(0, agentNode)
   
            # Create an Agent Layer node, connect it to the Agent Clip node
            # and activate the Source Layer checkbox so we can see the character
            agentLayerNode = agentSetupNode.createNode('agentlayer', '{}_layer'.format(agent_in_dict))
            agentLayerNode.setInput(0, agentClipNode)
            agentLayerNode.parm('sourcecopy').set(1)
   
            # Create an Agent Prep node and connect it to the Agent Layer node
            agentPrepNode = agentSetupNode.createNode('agentprep::3.0', '{}_prep'.format(agent_in_dict))
            agentPrepNode.setInput(0, agentLayerNode)
   
            # Create an OUT (Null) node and connect it to the Agent Prep node
            outNode = agentSetupNode.createNode('null', 'OUT_{}'.format(agent_in_dict))
            outNode.setInput(0, agentPrepNode)
           
            # Activate the Display/Render flags and set the color to black
            outNode.setDisplayFlag(True)
            outNode.setRenderFlag(True)
            outNode.setColor(hou.Color((0, 0, 0)))                        
           
            # Layout nodes inside "agentSetup"
            agentSetupNode.layoutChildren()

           
            # Iterate through every button in the group
            for button in self.buttonGroup.buttons():
               
            # Applies the action to each button independently
                if button is self.buttonGroup.button(i):
                   
                    # Run UPDATE_BUTTON_COLOR() to make it green
                    self.update_button_color(button, agent_in_dict)
                   
           
        # If the Agent node already exists in the scene,
        # display a Message Box to the user
        else:            
            self.message = QtWidgets.QMessageBox()
            self.message.setWindowTitle('Agent Browser')
            self.message.setText('The agent «{}» is already in your scene.'.format(agent_in_dict))
            self.message.show()

                   
# Create an instance of the AgentBrowser() class
agentBrowserUI = AgentBrowser()

# Display the UI in a new window
agentBrowserUI.show()
