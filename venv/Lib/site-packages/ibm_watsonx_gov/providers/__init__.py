import os
import sys

# Dynamically add the path to `llmevalkit`
# points to `tool_calling_hallucination`
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
