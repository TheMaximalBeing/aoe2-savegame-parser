# \project aoe2-savegame-parser
# \author tmb_
# \date JUN/2023
# \licence GPL3 (see COPYING.md)

import savegame

# load the raw save file
filename = "data/test-ai-load.gaz"
rawfile = open(filename, 'rb').read()

print("\n-- parsing \"{0}\" ---".format(filename))

# parse savegame into nested structures
savegame = savegame.read_savegame_file(rawfile)

print("\n--- here's some info ---")

# print some stats
print("num players", savegame.header.num_players-1)
if savegame.header.include_ai:
  ai = savegame.header.ai_info
  print("string table size (all AIs)", len(ai.string_table.resource_strings))
  for i in range(len(ai.ai_data)):
    if ai.ai_data[i].ai_number != -1:
      print("AI",i+1,"rule count ", ai.ai_data[i].num_rules)
else:
  print("no AIs exist in save file")
print("map-size",str(savegame.map_info.map_size_x)+"x"+str(savegame.map_info.map_size_y))

