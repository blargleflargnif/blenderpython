blenderpython
=============

My collection of Blender Addons

installation 
============

* Download recent Blender Build from here: https://builder.blender.org/download/
* This repo is kept mostly uptodate with recent Builds.
* Currently Blender 2.75a is supported also & would represent a minimum requirement for all features.

* Download the blenderpython zip file & unpack.
* Copy the "scripts" folder or it's contents & paste over the Blender "scripts" folder on your os or to the buildbot build "scripts" folder.
* This will replace addons_utils.py in modules to activate the addons extern folder.
* It will also replace space_view3d.py from startup/bl_ui folder for my custom menu's design. If you paste contents you can miss this file/folder if it bugs out.

Addons Extern Folder
====================
* you need patched addons_utils.py to use this folder. see note.

* addons_extern is a very useful folder, once set up, you can drop any addon in there & it's recognized.
* This allows you to delete any scripts you don't need & repopulate with ones you like at any time.
* The added benifit of this is there's no need to mix in your favorite external addons into blenders addons folders, 
then have to find & replace for each new Blender version.
* 
 
* The addons_extern folder contains many working addons I've collected over the years.
* Currently the addons_extern is reasonably up to date for blender 2.75a.
* However, I cannot guarentee every addon will be up to date at any given time.
* Please check original authors site/s for updates.
* The flip side of this is there's many addons here that are not working elsewhere...

Note: 
====================
* addons_extern should be placed next to addons & addons contrib in "blender version"\2.75\scripts
* some addons in the repo are hard coded to addons_extern folder

* Update the addons_utils.py to activate addons_extern folder & paste into new blender scripts directory & your favorites are right there.
* addons_utils.py is found in the modules folder.

Note 2:
=====================

Duplicate addons may occur as the collection is very large, just delete any duplicates you don't need.

Windows Pre built version for 2.75a: http://www.graphicall.org/1155
===================

Known Issues:
===================
* Addons Factory script is huge, it may take a few seconds to load. 
It contains all the add_mesh/curve & much more in the one activate & provides nice menu structure.

* If it fails to load, let me know, I may need to split into smaller modules again.
* In the startup/bl_ui folder, is my patched version of space_view3d.py, if this file gives problems,
replace it with the original space_view3d.py for your Blender Version.

Disclaimer:
==================
* Be careful using addons, some addons may cause crashes if used in wrong context or using huge amounts of verts.

* I'm not responsible for any lost effort or broken addons. Save Often.

* Use at Own Risk!

Enjoy
=======
* All of this works very well for me & should do so also for you.


Help Wanted
===========

Feel free to drop into irc #blenderpython if you have any question about this repo & especially if you would like to help & contribute.
Thanks.