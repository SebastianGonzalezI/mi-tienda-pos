#!/bin/bash
# Patch buildozer root check to auto-yes
BUILDOZER_FILE=$(python3 -c "import buildozer; print(buildozer.__file__)")
echo "Patching $BUILDOZER_FILE"
# Replace the interactive prompt with auto-yes
python3 -c "
import re
with open('$BUILDOZER_FILE', 'r') as f:
    content = f.read()
# Replace: cont = None   + while + input   with just cont = 'y'
old = '''            cont = None
            while cont not in ('y', 'n'):
                cont = input('Are you sure you want to continue [y/n]? ')'''
new = '''            cont = 'y'  # patched for non-interactive builds'''
content = content.replace(old, new)
with open('$BUILDOZER_FILE', 'w') as f:
    f.write(content)
echo 'Patch applied successfully'
"
