#! /bin/bash

# This script does what multiparanoid does, but a gajillion times faster for large data.


# In the directory that you run this, there should be the "sqltable.*" files from inparanoid.
# Temporary working files include "combined.disco" and "map.disco"

create_special_paranoid_mappings.py
improved_multiparanoid combined.disco merged.disco
decode_map.py merged.disco map.disco solution.disco
