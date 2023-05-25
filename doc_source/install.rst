.. role:: fwLighter
    :class: fw-lighter

Installation
============

Python
------

To install the package, follow these steps:

1. First, download and install the latest version of Python 3.11 from the official Python website: https://www.python.org/downloads/
2. Once you have installed Python 3.11, open a command prompt or terminal window.

3. Right-click on "Command Prompt" and select "Run as administrator".

::

    setx PATH "%USERPROFILE%\AppData\Local\Programs\Python\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts;%PATH%" /M

This will add the Python 3.11 installation directory to the system path variable.

4. Close the Command Prompt and open a new one to ensure that the changes take effect.
5. Check if Python is installed correctly by typing the following command:

::

    python --version

This should output the version number of Python that you have installed.

6. Next, you will need to install the `pip` package manager. To do this, type the following command:

::

    python -m ensurepip --upgrade

This will install or upgrade `pip` to the latest version.

snAPI
-----

7. Download the package from the source repository: https://github.com/picoquant/snapi

8. Finally, you can install your package using `pip`. Navigate to the directory where your package is located, and type the following command:

::

    pip install snAPI-x.y.z-cp311-cp311-win_amd64.whl

Dependencies
------------
This will install your package and its dependencies.


9. Download the multiharp library from the source repository: https://www.picoquant.com/dl_software/MultiHarp150/MultiHarp150_160_V3_1.zip

10. Unzip the library to a folder on your computer.

11. Open an explorer window and navigate to the folder containing the unzipped library installer.

12. Run the `setup.exe`.

13. Once the installation is complete, verify that the package is installed by running the command `import snAPI` in a Python interpreter.

14. To enable colors output in terminal execute `EnableTerminalColors.reg` and restart the terminal.
