'''
MATERIAL STYLESHEETS FOR CROWD [GUI]
Add textures to your Crowd sim with the help of a graphic interface.

HOW IT WORKS:
- Select the Geometry node where your Crowd cache is stored and run the tool.
- Click the button next to each shape and choose a texture file.
- When you are done, click on "Generate Stylesheet".
- A Principled Shader will be created for every Shape, whether you chose a texture file or not.
- You can check the Material Stylesheet by creating a New Pane Tab Type > Inspectors > Data Tree.

IMPORTANT:
Running this tool more than once will generate duplicate values and unexpected results.
If you ever need to re-generate the Stylesheet, make sure to delete the previous one and also
the Principled Shaders in the /mat/ context.

NOTE:
This tool looks at File Cache nodes. Feel free to change the nodeType variable with the type
of node you want to use (e.g: If you want to look at a Crowd Source instead of a File Cache,
change the variable to "crowdsource::3.0")

*** If you are using HOUDINI 18.5, replace the .items() method by .iteritems(),
and the zip() function by itertools.izip() so that it can be run in PYTHON 2.7 ***
'''


import sys
import json
import itertools
from collections import OrderedDict
from numpy import cumsum
from PySide2 import QtGui, QtWidgets, QtCore



#################################
## SEARCH FOR FILE CACHE NODES ##
#################################



# Set the type of node we are looking at
nodeType = 'filecache'

# Store the selected nodes in a variable and pick the first one
selectedNodes = hou.selectedNodes()

# If the user doesn't select any node, throw a message and stop the program
try:
    geoNode = selectedNodes[0]
except IndexError:
    hou.ui.displayMessage('Select the Geometry node where your Crowd cache is stored and try again')
    sys.exit()


# Initialize list to store File Cache nodes
cacheNodes = []

# Iterate through the GEO Node's children, and if there is any File Cache in it, add it to the list
for node in geoNode.children():
    if node.type().name() == nodeType:
        cacheNodes.append(node)        
   
cacheCount = len(cacheNodes)
       

# CONDITIONAL: If no "File Cache" node is found (i.e: if the list is empty), throw a message        
if cacheCount == 0:
    hou.ui.displayMessage('No "File Cache" found in the selected node')
    sys.exit()
   
# If there's more than one "File Cache" node, open a Node Tree View and ask the user to pick just one
elif cacheCount > 1:
    hou.ui.displayMessage('{} FILE CACHES FOUND: Please select only one.'.format(cacheCount))
    selectedNodePath = hou.ui.selectNode(initial_node=cacheNodes[0], title='Select a File Cache node:')
   
    # CONDITIONAL: If the user doesn't select any node, stop the program
    if selectedNodePath == None:
        sys.exit()
           
    else:
        cacheNodes = [hou.node(selectedNodePath)]
       
        # If the user selects the wrong type of node, throw a message and stop the program
        if cacheNodes[0].type().name() != nodeType:
            hou.ui.displayMessage('This is not a valid FILE CACHE node')
            sys.exit()

   

#######################
## GATHER AGENT INFO ##  
#######################



# Initialize lists to store Agent Names and Agent Shapes
agentList = []
shapeList = []

# Iterate through the File Cache nodes
for node in cacheNodes:

    # Access the Geometry level, pick the "Agent Name" point attribute and add it to the Agent list
    geo = node.geometry()
    agentName = geo.pointStringAttribValues('agentname')
    agentList.append(agentName)
   
    # Access the Prim level
    prims = geo.prims()

    # Iterate through the Prims
    for prim in prims:
   
        # Pick the "agentshapelibrary" intrinsic and add it to an auxiliary variable
        shapeLibrary = prim.intrinsicValue('agentshapelibrary')
       
        # Keep only shapes starting by "default" and ending by "GEO" (i.e: the ones we really need)
        shapeLibrary = tuple(x for x in shapeLibrary if not x.startswith('collision'))
               
        # Add this tuple of shapes to the Shape list
        shapeList.append(shapeLibrary)
       
     
    # Calculate how many elements are in both the Agent list and Shape list
    agentCount = sum([len(agentName) for agentName in agentList])
    shapeCount = sum([len(shapeName) for shapeName in shapeList])
   
   
   
####################
## OPTIMIZE LISTS ##    
####################
   


# Iterate through every tuple in the Agent Name list
### BACKUP: for index, tuple in enumerate(agentList) ###
for tuple in agentList:

    # Convert the tuple into an ordered dictionary to remove duplicates, and then convert into a list
    agentList = list(OrderedDict.fromkeys(tuple))
   
   
# Calculate how many agents are in the optimized Agent list    
agentOptCount = len(agentList)
   
# Convert the Agent Shape list into an ordered dictionary to remove duplicates, and then convert into a list
shapeList = list(OrderedDict.fromkeys(shapeList))

# Calculate how many shapes are in the optimized Shape list
shapeOptCount = sum([len(shapeName) for shapeName in shapeList])



################################################
## GENERATE A DICTIONARY OF AGENTS AND SHAPES ##
################################################



# Initialize a dictionary
dict = {}

# Iterate through the Agent Names and Agent Shape lists in parallel
for agent,shape in zip(agentList,shapeList):
   
    # Generate a dictionary > Keys: Agent Names, Values: Agent Shapes
    dict[agent] = shape

    

########################################
## STORE LENGTH OF AGENT SHAPES LISTS ##
########################################



# Initialize a list
lengths = []

# Iterate through every list of Agent Shapes in the dictionary and add its length to the list
for list_of_shapes in dict.values():
    lengths.append(len(list_of_shapes))
    
 
# Generate a cumulative sum of the lengths - this will act as a counter for buttons later
counter = list(cumsum(lengths))

 

####################
## STYLESHEET GUI ##
####################



# Create a Button Group
buttongroup = QtWidgets.QButtonGroup()


# Define the "STYLESHEET GUI" Class    
class StylesheetGUI(QtWidgets.QWidget):


    # INITIALIZE THE UI
 
    def __init__(self):
        super(StylesheetGUI, self).__init__()
        self.setWindowTitle('Material Stylesheets for Crowd GUI')

        # Set size policies to prevent the window from "shrinking" the widgets
        self.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.Minimum)
        self.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Minimum)
     
        # >>>> Launch the UI
        self.initUI()

     
    # CUSTOMIZE THE UI
 
    def initUI(self):
 
        # Set up the font
        self.font = QtGui.QFont()
        self.font.setBold(True)
             
        # Apply a Grid Layout to the main window
        self.windowLayout = QtWidgets.QGridLayout()  
        self.setLayout(self.windowLayout)
        
        # Create the main Scroll Area
        self.scrollMain = QtWidgets.QScrollArea()
        self.scrollMain.setWidgetResizable(True)

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
        
        
        # Initialize a list to store labels
        self.labelList = []
     
        # >>>> Run "addAgentName" method for each Agent Shape in the list
        for i, (agent_in_dict, shapes_in_dict) in enumerate(dict.items()):
            self.addAgentName(i, agent_in_dict, shapes_in_dict)

                                   
        # Add a spacer to the main window layout
        self.spacer = QtWidgets.QSpacerItem(0,30)
        self.windowLayout.addItem(self.spacer)
     
        # Add the "Generate Stylesheet" button to the main window layout
        self.applyButton = QtWidgets.QPushButton('GENERATE STYLESHEET')
        self.applyButton.setMinimumSize(500,30)
        self.applyButton.clicked.connect(self.generateButton)
        self.windowLayout.addWidget(self.applyButton)    
     
     
    # CREATE LABEL NAMED AFTER THE AGENT
 
    def addAgentName(self, i, agent_in_dict, shapes_in_dict):
 
        # Create a widget to store the label
        self.labelWidget = QtWidgets.QWidget()
     
        # Add a Grid Layout to the widget
        self.labelWidgetLayout = QtWidgets.QGridLayout()
        self.labelWidget.setLayout(self.labelWidgetLayout)
     
        # Create a label named after the agent, add it to the widget layout
        self.label = QtWidgets.QLabel(agent_in_dict+' ({} shapes found)'.format(lengths[i]))
        self.label.setFont(self.font)
        self.labelWidgetLayout.addWidget(self.label)        
     
        # Add widget to the main widget layout
        self.mainWidgetLayout.addWidget(self.labelWidget)
                   
        # >>>> Run "addShapes" method
        self.addLabel(i, agent_in_dict, shapes_in_dict)
     
       
    # CREATE A LABEL FOR EACH AGENT SHAPE  
 
    def addLabel(self, i, agent_in_dict, shapes_in_dict):     
        
        # Create a widget to store the labels
        self.buttonWidget = QtWidgets.QWidget()
        self.buttonWidget.setAutoFillBackground(True)
        self.buttonWidget.setStyleSheet('background-color: #545454;')
     
        # Add a Grid Layout to the widget
        self.buttonWidgetLayout = QtWidgets.QGridLayout()
        self.buttonWidget.setLayout(self.buttonWidgetLayout)     
     
        # Add scroll area to the main widget layout
        self.mainWidgetLayout.addWidget(self.buttonWidget)
                             
        # Iterate through the current agent's list of shapes
        for j, shape in enumerate(shapes_in_dict):
     
            # Create a label named after the shape
            self.label = QtWidgets.QLabel(shape)
 
            # Add label to the widget layout
            self.buttonWidgetLayout.addWidget(self.label)
               
            # >>>> Run the "addButtons" method
            self.addButtons(i, j, shape, shapes_in_dict)            
                   
               
    # CREATE A BUTTON NEXT TO EACH LABEL
 
    def addButtons(self, i, j, shape, shapes_in_dict):  
   
        # Create a button
        self.button = QtWidgets.QPushButton('Browse File')
       
        # CONDITIONAL: The first agent of the dictionary will have as "index" the index of the shape
        # (i.e: Buttons will be indexed 0, 1, 2...)
        if i == 0:
            index = j
           
        # The rest of agents will have as "index" the index of the shape PLUS the length of the previous shape list
        # (i.e: If the previous agent's buttons ended with index 2, this agent will start with index 3, 4, 5...)
        else:
            index = j + counter[i-1]
     
        # Add button to the group and tag it with an index    
        buttongroup.addButton(self.button, index)
       
        # >>>> When button is clicked, run "chooseFile" method
        self.button.clicked.connect(lambda: self.chooseFile(shape, index))
     
        # Add button to the widget layout and place it in the 2nd column
        self.buttonWidgetLayout.addWidget(self.button, shapes_in_dict.index(shape), 1)
     
     
    # BUTTON ACTION: LET THE USER CHOOSE A TEXTURE FILE
 
    def chooseFile(self, shape, index):

       
        # Iterate through every button in the group
        for button in buttongroup.buttons():
               
            # Applies the action to each button independently
            if button is buttongroup.button(index):
             
                # Open a File Dialog, pick the name of the file and use it as the button's text
                filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a texture file')
                self.path = filename[0]
                button.setText(self.path)           

               
    # GENERATE BUTTON ACTION: STORE THE SELECTED FILES IN A LIST
 
    def generateButton(self):
 
        # Initialize a list
        self.buttonTextList = []
     
        # Pick the text on each button (i.e: file path) and add it to the list
        for button in buttongroup.buttons():

            if button.text() == 'Browse File':
                self.buttonTextList.append('')
            
            else:
                self.buttonTextList.append(button.text())     

     
        # >>>> Run the "createMaterials" and "createStylesheet" methods
        self.createMaterials()
        self.createStylesheet()                  
     

    # CREATE A PRINCIPLED SHADER NODE LINKED TO A TEXTURE FILE
   
    def createMaterials(self):

        # Store the /mat/ context in a variable
        self.mat = hou.node('/mat')
               
        # Initialize an auxiliary list      
        auxList = []
       
        # Iterate through the dictionary and add all the Agent Shapes to the auxiliary list
        """ The order in which they enter the list will be used as index
        (i.e: For the first shape, we'll pick the File Path of the first button, etc.) """
       
        for agent_in_dict, shapes_in_dict in dict.items():
            for shape in shapes_in_dict:
                auxList.append(shape)

                # Create a Principled Shader node pointing to the selected texture file
                self.matNode = self.mat.createNode("principledshader", agent_in_dict+'_'+shape)
                self.matNode.parm('basecolor_useTexture').set(True)
                self.matNode.parm('basecolor_texture').set(self.buttonTextList[auxList.index(shape)])
                 
        # Layout nodes in the /mat/ context
        self.mat.layoutChildren(horizontal_spacing=1.0, vertical_spacing=1.0)
     
                     
    # GENERATE A STYLESHEET AND OVERRIDE MATERIALS
   
    def createStylesheet(self):
     
        # Initialize a list where we will store the dictionaries
        self.styleList = []              

        # Create a dictionary (i.e: style) for each Agent Shape
        for agent_in_dict, shapes_in_dict in dict.items():
            for shape in shapes_in_dict:
           
                # Target geometry
                self.subTargetDict = OrderedDict()
                self.subTargetDict["label"] = "Sub-target"
                self.subTargetDict["shape"] = shape
             
                self.targetDict = OrderedDict()
                self.targetDict["label"] = "Target"
                self.targetDict["subTarget"] = self.subTargetDict
                         
                # Override materials
                self.nameDict = OrderedDict()
                self.nameDict["type"] = "string"
                self.nameDict["value"] = "/mat/{}_{}".format(agent_in_dict,shape)
             
                self.materialDict = OrderedDict()
                self.materialDict["name"] = self.nameDict
             
                self.overridesDict = OrderedDict()
                self.overridesDict["material"] = self.materialDict
             
                self.stylesDict = OrderedDict()
                self.stylesDict["label"] = agent_in_dict+'_'+shape
                self.stylesDict["target"] = self.targetDict
                self.stylesDict["overrides"] = self.overridesDict
             
                # Add this dictionary to the Style list
                self.styleList.append(self.stylesDict)
         
     
        # Create the main dictionary and put inside the Style list
        self.mainDict = OrderedDict()
        self.mainDict["styles"] = self.styleList
     
        # Convert the dictionary into JSON format
        self.json = json.dumps(self.mainDict,indent = 4)
     
        # Generate a Stylesheet using the JSON dictionary we just created
        hou.styles.addStyle(geoNode.name()+'_stylesheet','',self.json)
        
        # Throw a confirmation message and close the program
        hou.ui.displayMessage('Material Stylesheet has been succesfully generated!')
        self.close()
        
                      

# >>>> RUN THE "STYLESHEETGUI" CLASS
win = StylesheetGUI()
win.show()
