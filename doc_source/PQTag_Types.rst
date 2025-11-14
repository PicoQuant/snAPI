PQ Tag Types
------------

.. note::
    
    - Tag region of files have always lengths divisible by 8
    - In files, tags start always on positions divisible by 8.
    - Tag_Id is case sensitive.

File Magic
""""""""""

The following table gives the file type identifying "magics" as to be found in preamble 1. 
This preamble is filled up to its full length of 8 with '\0'.

.. raw:: html
    :file: _static/tables/PQTagFileMagics.html

Tag Format Definition
"""""""""""""""""""""

The following table illustrates the format of valid tags. It is described as a structure with named fields:

.. raw:: html
    :file: _static/tables/PQTagFormatDefinition.html

Tag Type Definition
"""""""""""""""""""

The following table defines the types of valid tags with their domain and additional length if enhanced:

.. raw:: html
    :file: _static/tables/PQTagTypes.html