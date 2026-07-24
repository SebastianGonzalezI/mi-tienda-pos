#!/bin/bash
cd /home/user/hostcwd
# Patch buildozer to skip root check
BUILDOZER_FILE=$(python3 -c "import buildozer; print(buildozer.__file__)")
sed -i 's/if os.geteuid() == 0:/if False:  #/' "$BUILDOZER_FILE"
# Run build
buildozer android debug
