'''
CROWD TO SOLARIS
Import your Crowd sim into Solaris and optionally add textures with a UI.

HOW IT WORKS:
- Run the tool and select the SOP node containing your Crowd sim.
- The "Apply Textures to Crowd" window will open.
- Choose a texture file for each shape and hit "Apply Materials".

The following nodes will be created in the /stage/ context:

- SOP Import: Brings your Crowd sim into Solaris. 
- Material Library: Contains the Principled Shader materials.
- Assign Material: Assigns those materials to their corresponding shapes.

If you do not want to add any textures, click on "Skip this step"
and only the SOP Import will be created.

IMPORTANT:
This code works only in Houdini 19 (Python 3).
'''


import sys
from numpy import cumsum
from PySide2 import QtGui, QtWidgets, QtCore


#######################
## GATHER AGENT INFO ##  
#######################


# Let the user choose the SOP node containing the Crowd
selectedNode = hou.ui.selectNode(title='Select your Crowd node:', node_type_filter=hou.nodeTypeFilter.Sop)

# If the user doesn't select any node, stop the program
if selectedNode:
    crowdCacheNode = hou.node(selectedNode)
else:
    sys.exit()
    
# Initialize lists to store Agent Names and Agent Shapes
agentList = []
shapeList = []

# Access the Geometry level, pick the "Agent Name" point attribute and add it to the Agent list
geo = crowdCacheNode.geometry()
agentName = geo.pointStringAttribValues('agentname')
agentList.append(agentName)

# Access the Prim level
prims = geo.prims()

# Iterate through the Prims (i.e: the Agents)
for prim in prims:

    # Pick the "agentshapelibrary" intrinsic and add it to an auxiliary variable
    shapeLibrary = prim.intrinsicValue('agentshapelibrary')
   
    # Discard shapes from the Collision Layer (keep only the "default" and custom ones)
    shapeLibrary = tuple(x for x in shapeLibrary if not x.startswith('collision'))
           
    # Add this tuple of shapes to the Shape list
    shapeList.append(shapeLibrary)
   
 
# Calculate how many elements are stored in the Agent list and Shape list
agentCount = sum([len(agentName) for agentName in agentList])
shapeCount = sum([len(shapeName) for shapeName in shapeList])
   
   
####################
## OPTIMIZE LISTS ##    
####################
   

# Iterate through every tuple in the Agent Name list
for tuple in agentList:

    # Convert the tuple into a dictionary to remove duplicates, and then convert into a list
    agentList = list(dict.fromkeys(tuple))    
   
# Calculate how many agents are in the optimized Agent list    
agentOptCount = len(agentList)
   
# Convert the Agent Shape list into a dictionary to remove duplicates, and then convert into a list
shapeList = list(dict.fromkeys(shapeList))

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

 
################################
## APPLY TEXTURES TO CROWD UI ##
################################


# Create a Button Group
buttongroup = QtWidgets.QButtonGroup()


class ApplyTexturesToCrowdUI(QtWidgets.QWidget):
    '''
    APPLY TEXTURES TO CROWD UI:
    
    In this window, you will see a list of Agents with their corresponding Agent Shapes.
    You can then select a texture file for each Shape, and let the tool create all the
    Material nodes for you in the /stage/ context.
    
    If you do not want to add any textures to your Crowd, click on the "SKIP THIS STEP" button.
    '''
 

    def __init__(self):
        ''' Initialize the UI '''
                
        super(ApplyTexturesToCrowdUI, self).__init__()
        
        # Set the title of the window
        self.setWindowTitle('Apply textures to Crowd | Solaris')

        # Set a minimum size for the window
        self.setMinimumSize(750, 400)     

        # >>> Launch the UI
        self.initUI()

     
    def initUI(self):
        ''' Customize the UI '''
        
        # Set up the font
        self.font = QtGui.QFont()
        self.font.setBold(True)
             
        # Apply a Grid Layout to the main window
        self.windowLayout = QtWidgets.QGridLayout()  
        self.setLayout(self.windowLayout)
        
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
        
        # Initialize a list to store labels
        self.labelList = []
     
        # >>> Run ADDAGENTNAME() for each Agent Shape in the list
        for i, (agent_in_dict, shapes_in_dict) in enumerate(dict.items()):
            self.addAgentName(i, agent_in_dict, shapes_in_dict)

                                   
        # Add a spacer to the main window layout
        self.spacer = QtWidgets.QSpacerItem(0,30)
        self.windowLayout.addItem(self.spacer)
     
        # Add the "Apply Textures" button to the main window layout
        self.applyButton = QtWidgets.QPushButton('APPLY TEXTURES')
        self.applyButton.setMinimumSize(500,30)
        self.applyButton.clicked.connect(self.createMaterials)
        self.windowLayout.addWidget(self.applyButton)    
     
        # Add the "Skip this step" button to the main window layout
        self.skipButton = QtWidgets.QPushButton(' Skip this step')
        self.skipButton.setMinimumSize(500,30)        
        icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ToolBarHorizontalExtensionButton)
        self.skipButton.setIcon(icon)
        self.skipButton.setStyleSheet('background-color: #545454; border: none;')
        self.skipButton.clicked.connect(self.createMaterials)
        self.windowLayout.addWidget(self.skipButton)    
        
        
    def addAgentName(self, i, agent_in_dict, shapes_in_dict):
        ''' Create label named after the Agent '''
        
        # Create a widget to store the label
        self.labelWidget = QtWidgets.QWidget()
     
        # Add a Grid Layout to the widget
        self.labelWidgetLayout = QtWidgets.QGridLayout()
        self.labelWidget.setLayout(self.labelWidgetLayout)
     
        # Create a label named after the agent, add it to the widget layout
        self.label = QtWidgets.QLabel(agent_in_dict+f' ({lengths[i]} shapes)')
        self.label.setFont(self.font)
        self.labelWidgetLayout.addWidget(self.label)        
     
        # Add widget to the main widget layout
        self.mainWidgetLayout.addWidget(self.labelWidget)
                   
        # >>> Run ADDLABEL()
        self.addLabel(i, agent_in_dict, shapes_in_dict)
     
       
    def addLabel(self, i, agent_in_dict, shapes_in_dict):     
        ''' Create a label for each Agent Shape '''
    
        # Create a widget to store the labels (and later, the buttons)
        self.buttonWidget = QtWidgets.QWidget()
        self.buttonWidget.setAutoFillBackground(True)
        self.buttonWidget.setStyleSheet('background-color: #545454;')
     
        # Add a Grid Layout to the widget
        self.buttonWidgetLayout = QtWidgets.QGridLayout()
        self.buttonWidget.setLayout(self.buttonWidgetLayout)     
     
        # Add widget to the main widget layout
        self.mainWidgetLayout.addWidget(self.buttonWidget)
                             
        # Iterate through the current agent's list of shapes
        for j, shape in enumerate(shapes_in_dict):
     
            # Create a label named after the shape
            self.label = QtWidgets.QLabel(shape)
 
            # Add label to the widget layout
            self.buttonWidgetLayout.addWidget(self.label)
               
            # >>> Run ADDBUTTONS()
            self.addButtons(i, j, shape, shapes_in_dict)            
                   
               
    def addButtons(self, i, j, shape, shapes_in_dict):  
        ''' Create a button next to each label '''
    
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
       
        # >>> When button is clicked, run CHOOSEFILE()
        self.button.clicked.connect(lambda: self.chooseFile(shape, index))
     
        # Add button to the widget layout and place it in the 2nd column
        self.buttonWidgetLayout.addWidget(self.button, shapes_in_dict.index(shape), 1)
     
     
    def chooseFile(self, shape, index):
        ''' Let the user choose a texture file '''
       
        # Iterate through every button in the group
        for button in buttongroup.buttons():
               
            # Applies the action to each button independently
            if button is buttongroup.button(index):
             
                # Open a File Dialog, pick the name of the file and set it as the button's text
                filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a texture file')
                self.path = filename[0]
                button.setText(self.path)           

               
    def storeTextures(self):
        ''' Store the selected texture files in a list '''
 
        # Initialize a list
        self.buttonTextList = []
     
        # Pick the text on each button (i.e: file path) and add it to the list
        for button in buttongroup.buttons():

            if button.text() == 'Browse File':
                self.buttonTextList.append('')
            
            else:
                self.buttonTextList.append(button.text())     
     

    def importCrowdIntoStage(self):
        ''' Create a SOP Import node in the /stage/ context to bring the Crowd '''
        
        # Store the /stage/ context in a variable
        self.lop = hou.node('/stage')

        # Create a SOP Import node
        self.importCrowdNode = self.lop.createNode('sopimport','import_crowd')
        self.importCrowdNode.parm('soppath').set(crowdCacheNode.path())
        self.importCrowdNode.parm('pathprefix').set('/crowd')

        # Import the Agents as "Skelroots" so we can apply textures to their Shapes      
        self.importCrowdNode.parm('enable_agenthandling').set(1)
        self.importCrowdNode.parm('agenthandling').set('skelroots')

        
    def createMaterials(self):
        ''' Create a Principled Shader node linked to a texture file '''    
    
        # >>> Run IMPORTCROWDINTOSTAGE()
        self.importCrowdIntoStage()
        
        # CONDITIONAL: If the "APPLY TEXTURES" button is pressed, materials will
        # be created and applied to the Crowd. Otherwise, the tool will just switch
        # to the Solaris desktop and close the program
        clickedButton = self.sender()
        
        if clickedButton.text() == 'APPLY TEXTURES':

            # >>> Run STORETEXTURES()
            self.storeTextures()
                           
            # Create a Material Library node and connect it to the SOP Import 
            self.matLibraryNode = self.lop.createNode('materiallibrary','set_materials')
            self.matLibraryNode.setInput(0,self.importCrowdNode)
            self.matLibraryNode.parm('materials').set(shapeOptCount)
            
            # Create an Assign Material node and connect it to the Material Library
            self.assignMatNode = self.lop.createNode('assignmaterial','assign_materials')
            self.assignMatNode.setInput(0,self.matLibraryNode)
            self.assignMatNode.parm('nummaterials').set(shapeOptCount)
                        
            # Initialize an auxiliary list      
            self.auxList = []
    
            # Iterate through the dictionary and add all the Agent Shapes to the auxiliary list
            ''' The order in which they enter the list will be used as index
            (i.e: For the first shape, we pick the File Path of the first button, etc.) '''
           
            for agent_in_dict, shapes_in_dict in dict.items():
                for shape in shapes_in_dict:
                    self.auxList.append(shape)
                    
                    # Create a Principled Shader node in the Material Library
                    # This node will use as texture the one selected in the corresponding button  
                    self.matNode = self.matLibraryNode.createNode("principledshader", agent_in_dict+'_'+shape)
                    self.matNode.parm('basecolor_useTexture').set(True)
                    self.matNode.parm('basecolor_texture').set(self.buttonTextList[self.auxList.index(shape)])
    
                    # Set a counter to modify multiparms
                    parmCounter = self.auxList.index(shape)+1
                    
                    # Adjust the parameters in the Material Library node 
                    self.matLibraryNode.parm(f'matnode{parmCounter}').set(f'/stage/{self.matLibraryNode.name()}/{agent_in_dict}_{shape}')
                    self.matLibraryNode.parm(f'matpath{parmCounter}').set(shape.replace('.','_'))           
                    self.matLibraryNode.parm(f'matflag{parmCounter}').set(0)
                    self.matLibraryNode.parm(f'assign{parmCounter}').set(0)
            
                    # Adjust the parameters in the Assign Material node
                    self.assignMatNode.parm(f'primpattern{parmCounter}').set(f'/crowd/{agent_in_dict}_*/{shape.replace(".","_")}')
                    self.assignMatNode.parm(f'matspecpath{parmCounter}').set(f'/materials/{shape.replace(".","_")}')
                
                    
            # Layout nodes in the Material Library
            self.matLibraryNode.layoutChildren(horizontal_spacing=1.0, vertical_spacing=1.0)
            
            # Display the Assign Material node as set it as selected 
            self.assignMatNode.setDisplayFlag(1)
            self.assignMatNode.setSelected(1, clear_all_selected=True)
            
            
        # Layout nodes in the /stage/ context
        self.lop.layoutChildren()

        # Switch to the Solaris desktop
        solarisDesktop = hou.ui.desktop('Solaris')
        solarisDesktop.setAsCurrent()
        
        # Go to the /stage/ context in the Network View 
        networkView = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        networkView.cd('/stage/')

        # Close the program
        self.close()
            
                      
# Create an instance of the ApplyTexturesToCrowd() class
ui = ApplyTexturesToCrowdUI()

# Display the UI in a new window
ui.show()
