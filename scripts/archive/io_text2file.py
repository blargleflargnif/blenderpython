# io_text2file.py - Copyright (C) 2011, Simon Coppard (Saeblundr)
 
 #  ***** BEGIN GPL LICENSE BLOCK *****
 #
 #  This program is free software: you can redistribute it and/or modify
 #  it under the terms of the GNU General Public License as published by
 #  the Free Software Foundation, either version 3 of the License, or
 #  (at your option) any later version.
 #
 #  This program is distributed in the hope that it will be useful,
 #  but WITHOUT ANY WARRANTY; without even the implied warranty of
 #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #  GNU General Public License for more details.
 #
 #  You should have received a copy of the GNU General Public License
 #  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 #
 #  The Original Code is Copyright (C) 2011 by Simon Coppard (Saeblundr)
 #  All rights reserved.
 #
 #  Contact:      coppards@hotmail.com	
 #  Information:  <n/a>
 #
 #  The Original Code is: all of this file.
 #
 #  Contributor(s): none yet.
 #
 #  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Export: Text'2'File",
    "author": "Simon Coppard (Saeblundr)",
    "version": (0, 0, 3),
    "blender": (2, 5, 6),
    "api": 34303,
    "location": "File > Export",
    "description": "Writes all Text files to Disk",
    "warning": "Maintainer is a self declared noob",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Text Editor"
}

'''

Intended primarily as a method for working on internal BGE scripts enmass, that need updating from 2.49 to 2.5x

TODO:
 - replace LegalName() logic with less strict rules

DONE:
v 0,0,3 - 23/01/2011
 - Boolean 'Only *.py files'
 - Boolean 'All to *.py files'
 - Boolean 'Overwrite if exist'
 - Folder selection for output
v 0,0,2 - 22/01/2011
 - Rewrite logic as export script
 - optimise PWD logic
v 0,0,1 - 30/12/2010
 - initial logic, as runtime script, as per suggested on BlenderArtists.org

'''

T2FOpts = []
T2FOpts.append(("0", "All, No Change", ""))
T2FOpts.append(("1", "All as '.py' files", ""))
T2FOpts.append(("2", "Only '.py' files", ""))

### Container for the exporter settings
class Text2FileSettings:
    def __init__(self,
                 context,
                 FilePath,
                 T2FOption=0,
                 Overwrite=False,
                 Verbose=False):
        self.context = context
        self.FilePath = FilePath
        self.T2FOption = int(T2FOption)
        self.Overwrite = Overwrite
        self.Verbose = Verbose

### Filenames are not allowed any non-alphanumeric chars, just to be safe
def LegalName(Name,Used):
    NewName = Name
    for x in range(len(NewName)):
        if not NewName[x].isalnum():
            NewName.replace(NewName[x], '_')
    while( NewName in Used ):
        NewName = "_" + NewName
    return(NewName)

### MAIN BODY ###

import bpy
from os import path as osPath
from time import time

def do_Text2File(Config):
    if Config.Verbose:
        print("----------\n")
    print("Exporting to {}".format(Config.FilePath))
    start_time = time()
    processed = []

    for text in bpy.data.texts:
        if Config.Verbose:
            print("Processing: {}".format(text.name))

        textname = LegalName(text.name, processed)
        if textname != text.name and Config.Verbose:
            print("Renamed to: {}".format(textname))

        if Config.T2FOption == 1 and osPath.splitext(textname)[1] != '.py':
            textname = textname + ".py"
            if Config.Verbose:
                print("Added '.py' extension: {}".format(textname))

        if Config.T2FOption == 2 and osPath.splitext(textname)[1] != '.py':
            if Config.Verbose:
                print("No '.py' extension: {}".format(textname))
            continue

        FullFilePath = osPath.join(Config.FilePath, textname)

        if osPath.exists(FullFilePath):
            if Config.Verbose:
                print("Already Exists: {}".format(FullFilePath))
            if not Config.Overwrite:
                print("Overwrite disabled")
                continue
            elif not osPath.isfile(FullFilePath):
                if Config.Verbose:
                    print("Cannot Overwrite, not proper file")
                continue

        if Config.Verbose:
            print("Writing {}...".format(FullFilePath))

        Config.File = open(FullFilePath, "w")
        Config.File.write( text.as_string() )
        Config.File.close()

        processed.append(textname)

    print('Finished Export in %s seconds' %((time() - start_time)))

### EXPORT OPERATOR ###

from bpy.props import *
 
class Text2File(bpy.types.Operator):
    '''Exports files in Text Editor to File.'''
    bl_idname = "export_text2file"
    bl_label = "Export Text2File (*.*)"

    filepath = StringProperty(subtype='FILE_PATH')
    T2FOption = EnumProperty(name="File Option", description="Select a method for output.", items=T2FOpts, default="2")
    Overwrite = BoolProperty(name="Overwrite Existing?", description="Write text to file, even if a file of that name already exists.", default=False)
    Verbose = BoolProperty(name="Verbose", description="Run the exporter in debug mode.  Check the console for output.", default=False)

    def execute(self, context):
        FilePath = self.filepath
        if not osPath.isdir(FilePath):
            print( "Not a Directory: {}".format(FilePath) )
            return {"CANCELLED"}

        Config = Text2FileSettings(context,
                                   FilePath,
                                   T2FOption=self.T2FOption,
                                   Overwrite=self.Overwrite,
                                   Verbose=self.Verbose)

        do_Text2File(Config)
        return {"FINISHED"}
        if Config.Verbose:
            print("Writing {}/{}...".format(Config.FilePath, text.name))
    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


### REGISTER ###

def menu_func(self, context):
    default_path = osPath.join( osPath.split(bpy.data.filepath)[0], osPath.curdir )
    self.layout.operator(Text2File.bl_idname, text="TextEditor2Files (*.py)").filepath = default_path

def register():
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()

### EOF io_text2file.py ###
#
