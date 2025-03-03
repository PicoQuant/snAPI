.. role:: fwLighter
    :class: fw-lighter

Installation
============

Python
------

To install the package, follow these steps:

1. Install the Microsoft Visual C++ Redistributable(x64) if missing in the system: https://aka.ms/vs/17/release/vc_redist.x64.exe.
2. First, download and install the latest version of Python 3.13 from the official Python website: https://www.python.org/downloads/
3. Once you have installed Python 3.13, open a command prompt or terminal window.

4. Right-click on "Command Prompt" and select "Run as administrator".

::

    setx PATH "%USERPROFILE%\AppData\Local\Programs\Python\Python313;%USERPROFILE%\AppData\Local\Programs\Python\Python313\Scripts;%PATH%" /M

This will add the Python 3.13 installation directory to the system path variable.

5. Close the Command Prompt and open a new one to ensure that the changes take effect.
6. Check if Python is installed correctly by typing the following command:

::

    python --version

This should output the version number of Python that you have installed.

7. Next, you will need to install the `pip` package manager. To do this, type the following command:

::

    python -m ensurepip --upgrade

This will install or upgrade `pip` to the latest version.

snAPI
-----

1. Download the latest release from `github.com/picoQuant/snAPI/releases <https://github.com/picoQuant/snapi/releases>`_ from the repository: https://github.com/picoquant/snapi

2. Finally, you can unpack the files and install your package using `pip`. Navigate to the directory where your package is located, and type the following command:

::

    pip install .\dist\snAPI-<VERSION NUMBER x.y.z>-cp313-cp313-win_amd64.whl

Dependencies
------------

1. Download and install the software for the product you need:
    - https://www.picoquant.com/dl_software/MultiHarp150/MultiHarp150_160_V3_1.zip
    - https://www.picoquant.com/dl_software/HydraHarp400/HydraHarp400_SW_and_DLL_v3_0_0_4.zip
    - https://www.picoquant.com/dl_software/TimeHarp260/TimeHarp260_SW_and_DLL_V3_2.zip
    - https://www.picoquant.com/dl_software/PicoHarp330/PicoHarp330_SW_and_DLL_v1_0.zip

2. Start the Harp Software and check if the device is working.

3. Once the installation is complete, verify that the package is installed by running the command `import snAPI` in a Python interpreter. If no error message is shown, the installation was successful.

Additional Features
-------------------

1. Colored Log is default on Windows 11 but on Windows 10 you have to enable it manually in terminal by executing the included registry key `EnableTerminalColors.reg` and restart the terminal. If it is not working in VSCode, klick on the selector next to the run button and switch to 'Run python file in dedicated Terminal'

.. image:: _static/Log.png
    :class: p-2
    
Example cutout of a colored log.

2. To get the full power of coding we suggest to use snAPI with Visual Studio Code.

.. image:: _static/VSCode.png
    :class: p-2
    
VSCode will show the documentation on mouse hover.

Getting Started
---------------

1. Open a command prompt and navigate to the demos folder.

2. Open Demo_TimeTrace.py in an editor.

3. Also change the default configuration to the matching one from the demos/config folder.

::

    sn.loadIniConfig("config\TH260N.ini")

4. edit the ini file and set the trigger levels 

5. install matplotlib

::

    pip install matplotlib

6. run the demo

::

    python .\Demo_TimeTrace.py

.. image:: _static/TimeTrace.png
    :class: p-2
    
example of a timetrace window drawn by matplotlib