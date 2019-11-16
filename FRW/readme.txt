FRW (the Fastest Rig in the West) © soup-dev LLC

introduction
------------
There are so many rigging systems for Maya already, what makes this one any different ?

Short answer:
    1. Vfx/Games production ready, yet clean and simple.
    2. Very fast. For comparison - full featured FRW rig is on par or faster than HumanIK in its most basic form.
    3. Simple and (because of that) scalable codebase. Basic MEL commands only - create/parent/rename nodes and create/set/connect attributes. No OOP, interdependencies, C++ API calls, external libraries, plug-ins.

Long answer:
    www.soup-dev.com/videos/frw.mp4
    http://soup-dev.com/videos/frw_ogl_controls.mp4

installation
------------
1. Copy all files to /home/$USER/maya/scripts/ or other location.

getting started
---------------
1. Launch Maya.
2. Open Script Editor.
3. Update the Python system path if needed: import sys; sys.path.append("/path/to/frw/")
4. Run some code:
    arm.main()
    leg.main()
    common.control()
    biped.main()
    etc.
5. Use arguments to customize result:
    arm.main(radius=2)
    common.control(normal=(1,0,0), color=6)
    biped.main(fbx=True, radius=2, scale=2)
    etc.

To launch the manager UI run:
import manager; reload(manager); manager.main()
