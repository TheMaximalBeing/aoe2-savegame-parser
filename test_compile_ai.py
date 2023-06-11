# \project aoe2-savegame-parser
# \author tmb_
# \date JUN/2023
# \licence GPL3 (see COPYING.md)

import compile_ai

script_name = "data/testai.per"

(rules, stringtable) = compile_ai.compile_ai_script(script_name)

print("\n--- finished compiling ai ---")
print("rule-count", len(rules))
print("string-count", len(stringtable))
