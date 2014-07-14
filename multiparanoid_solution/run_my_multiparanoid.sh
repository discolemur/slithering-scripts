#! /bin/bash

# This script does what multiparanoid does, but a gajillion times faster for large data.

# In the directory that you run this, there should be the "sqltable.*" files from inparanoid.
# Temporary working files include "combined.disco" and "map.disco"

# The final output is called "solution.disco"

# Produce key and cipher (map.disco and combined.disco)
create_special_paranoid_mappings.py
# Run cipher through my multi program and produce encrypted result (merged.disco)
improved_multiparanoid combined.disco merged.disco
# Remove cipher
rm combined.disco
# Decode the encrypted result using the key
decode_map.py merged.disco map.disco solution.disco
# Remove encrypted result
rm merged.disco
# Remove key
rm map.disco
# Decrypted result is the only thing that remains.
# Keep solution.disco
