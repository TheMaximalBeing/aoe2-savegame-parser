# \project aoe2-savegame-parser
# \author tmb_
# \date JUN/2023
# \licence GPL3 (see COPYING.md)

import zlib
from savegame_structs import *
from utilz import *


data = None
index = 0
inMode = True

def get_helper(typee, size):

  global index, inMode, data

  start = index
  index += size

  if typee == 'int':
    return to_int(data[start:index])
  elif typee == 'raw':
    return data[start:index].hex()
  elif typee == 'float':
    return to_float(data[start:index])
  elif typee == 'string':
    return str(data[start:index])
  elif typee == 'nstring':
    end = index
    while data[end] != 0:
      end += 1
    index = end+1
    return str(data[start:end+1])

  raise Exception("invalid")

def get(typee, size, count=1):

  global index, inMode, data

  if count == 1:
    return get_helper(typee,size)
  else:
    return [get_helper(typee, size) for i in range(count)]

def io(obj, name, typee, size, count=1):

  global index, inMode, data

  if count == 0:
    return

  if inMode:
    setattr(obj, name, get(typee, size, count))
  else:
    raise Exception("unsupported")

def io_fcn(obj, field, fcn, count):

  if inMode:
    if count == 1:
      setattr(obj,field,fcn())
    else:
      setattr(obj,field,[fcn() for i in range(count)])
  else:
    raise Exception("unsupported")

# ----- parse tertiary structures -----


# (header)

def parse_resource_string():

  resource_String = Resource_String()
  io(resource_String, 'string_length', 'int', 4)
  io(resource_String, 'string', 'string', resource_String.string_length)
  return resource_String

def parse_string_table():

  string_table = String_Table()
  io(string_table, 'max_strings', 'int', 2) # 0x8813 -> 5000
  io(string_table, 'num_strings', 'int', 2) # 395
  io(string_table, 'unknown14', 'raw', 4) # 0x7813 9a18 -> ????
  io_fcn(string_table, 'resource_strings', parse_resource_string, string_table.num_strings)
  io(string_table, 'unknown15', 'raw', 6) # 0x0001 0001 0800
  return string_table

def parse_rule_data():
  
  rule_data = Rule_Data()
  io(rule_data, 'dtype', 'int', 4)
  io(rule_data, 'idd', 'int', 2)
  io(rule_data, 'unknown18', 'int', 2) # 0
  io(rule_data, 'params', 'int', 4, 4)
  return rule_data

def parse_rule():

  rule = Rule()
  io(rule, 'unknown15', 'int', 4) # 1
  io(rule, 'enabled', 'int', 4)
  io(rule, 'rule_number', 'int', 2)
  io(rule, 'unknown16', 'int', 2) # -1
  io(rule, 'num_facts', 'int', 1)
  io(rule, 'num_commands', 'int', 1)
  io(rule, 'unknown17', 'int', 2) # 0
  io_fcn(rule, 'ruledata', parse_rule_data, 16)
  return rule

def parse_ai_data():

  ai_data = AI_Data()
  io(ai_data, 'unknown13', 'raw', 4) # 01000000
  io(ai_data, 'ai_number', 'int', 4) # 0
  io(ai_data, 'max_rules', 'int', 2) # 10000
  io(ai_data, 'num_rules', 'int', 2) # 9797
  io(ai_data, 'unknown14', 'raw', 4) # 24d0b919 -> 19b9d024 ???
  io_fcn(ai_data, 'rules', parse_rule, ai_data.num_rules)
  return ai_data

def parse_timer():

  timer = Timer()
  io(timer, 'timers', 'int', 4, 10)
  return timer

def parse_ai_info():

  ai_info = AI_Info()
  io_fcn(ai_info, 'string_table', parse_string_table, 1)
  io_fcn(ai_info, 'ai_data', parse_ai_data, 8)
  io(ai_info, 'unknown11', 'raw', 104) # 64000000 90a8ff19 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000295c0f3ee17a943e0000000000000000000000000 90000000 10000000 20000000 10000000 1000000
  
  # 64000000 -> 100
  # 90a8ff19 -> 19ffa890 -> ?????
  # 295c0f3e -> 3e0f5c29 -> 0.140
  # e17a943e -> 3e947ae1 -> 0.290

  io_fcn(ai_info, 'timers', parse_timer, 8)
  io(ai_info, 'shared_goals', 'int', 4, 256)
  io(ai_info, 'unknown12', 'raw', 4096) # 0000...
  return ai_info

# (map-info)



# (start-info)




# ----- parse secondary structures -----


def parse_header():

  header = Header()
  io(header, 'version', "string", 8) # b'VER 9.F\\x00'
  io(header, 'unknown1', 'raw',4) # f6283c41
  io(header, 'include_ai', 'int', 4) # 1
  io_fcn(header, 'ai_info', parse_ai_info, header.include_ai)
  io(header, 'unknown2', 'raw', 4)
  io(header, 'game_speed1', 'int', 4)
  io(header, 'unknown3', 'raw', 4)
  io(header, 'game_speed2', 'int', 4)
  io(header, 'unknown4', 'float', 4)
  io(header, 'unknown5', 'raw', 4)
  io(header, 'game_speed3', 'float', 4)
  io(header, 'unknown6', 'raw', 17)
  io(header, 'rec_player', 'int', 2)
  io(header, 'num_players', 'int', 1)
  io(header, 'unknown7', 'raw', 4)
  io(header, 'unknown8', 'raw', 12)
  io(header, 'unknown9', 'raw', 14)
  io(header, 'unknown10', 'int', 4, 8)
  return header

def parse_map_terrain():

  map_terrain = Map_Terrain()
  io(map_terrain, 'terrain_id', 'int', 2) # spreadsheet was incorrect - it is 2 bytes, not 1
  io(map_terrain, 'elevation', 'int', 2) # to be fair, it could be a UP change
  return map_terrain

def parse_map_info():

  # AI on mainland
  # AI/RMS map terrain id

  map_info = Map_Info()
  io(map_info, 'map_size_x', 'int', 4)
  io(map_info, 'map_size_y', 'int', 4)
  io(map_info, 'num_data', 'int', 4) # 1


  def parse_unknown_struct2():
    unknown_struct2 = Unknown_Struct2()
    io(unknown_struct2, 'unknown24', 'raw', 255)
    io(unknown_struct2, 'unknown25', 'int', 4, 255)
    io(unknown_struct2, 'unknown26', 'int', 1, map_info.map_size_x*map_info.map_size_y)
    io(unknown_struct2, 'num_float', 'int', 4) # 42
    io(unknown_struct2, 'unknown27', 'float', 4, unknown_struct2.num_float)
    io(unknown_struct2, 'unknown28', 'int', 4) # 10
    return unknown_struct2
  
  io_fcn(map_info, 'unknown19', parse_unknown_struct2, map_info.num_data)
  io(map_info, 'unknown20', 'raw', 2) # 0001
  io_fcn(map_info, 'map_terrain', parse_map_terrain, map_info.map_size_x*map_info.map_size_y)
  io(map_info, 'unknown21', 'raw', 120)
  io(map_info, 'map_size_x2', 'int', 4)
  io(map_info, 'map_size_y2', 'int', 4)
  io(map_info, 'unknown22', 'int', 4, map_info.map_size_x2*map_info.map_size_y2)
  io(map_info, 'unknown23', 'int', 4, 8) # [5000, 1, 400, 0, 0, 2962, 0, 0]
  io(map_info, 'unknown24', 'raw', 9) # 000017 989e0000020b

  return map_info

# def parse_civ_header():

#   civ_header = Civ_Header()
#   io(civ_header, 'data', 'float', 4, 198)
#   return civ_header

def parse_research_stat():

  research_stat = Research_Stat()
  io(research_stat, 'status', 'int', 2) 
  io(research_stat, 'unknown_data1', 'raw', 12) 
  return research_stat

def parse_start_info(num_players):

  start_info = Start_Info()

  io(start_info, 'diplomacy', 'int', 1, num_players)
  io(start_info, 'my_diplomacy', 'int', 4, 9)
  io(start_info, 'padzero1', 'raw', 1, 5+2)
  io(start_info, 'player_name', 'nstring', 0)
  io(start_info, 'unknown_data1', 'raw', 1) # 0x16
  io(start_info, 'num_header_data', 'int', 4)
  io(start_info, 'unknown_data2', 'raw', 1) # 0x21
  io(start_info, 'data', 'float', 4, start_info.num_header_data)
  io(start_info, 'unknown_data3', 'int', 1) #0x0b -> no its 11
  io(start_info, 'init_camera_pos_x', 'float', 4) # -> correct
  io(start_info, 'init_camera_pos_y', 'float', 4) # -> correct
  io(start_info, 'unknown_length', 'int', 4) # -1 ?????
  io(start_info, 'unknown_pos', 'float', 4, 2*max(0,start_info.unknown_length))
  io(start_info, 'unknown_data4', 'raw', 5) # 3c 00 3c 00 02
  io(start_info, 'civilization', 'int', 1) # 0??
  io(start_info, 'unknown_data5', 'raw', 3) # 00 00 0b
  io(start_info, 'player_color', 'int', 1) # 13 wrong?
  io(start_info, 'unknown_data6', 'raw', 1) # 0b -> correct ??
  io(start_info, 'unknown_data7', 'raw', 4182)
  io(start_info, 'unknown_data8', 'float', 4) # 0.15 or 0.2 or 0？  -> correct?
  io(start_info, 'num_research', 'int', 4) # 100 ??
  io(start_info, 'padzero2', 'int', 2) # correct?
  # print(data[index:index+40000].hex())

  f = open('test.txt', 'w')
  f.write(str(data[:].hex()))
  f.close()
 

  start_info.research_stats = [parse_research_stat() for i in range(start_info.num_research)]



  # print(mydata[0:2000].hex())
  return start_info

def parse_achievement():
  mydata = data[index:]
  achievement = Achievement()
  return (achievement,index)

def parse_scenario_header():
  mydata = data[index:]
  scenario_header = Scenario_Header()
  return (scenario_header,index)

def parse_messages_and_cinematics():
  mydata = data[index:]
  messages_and_cinematics = Messages_and_Cinematics()
  return (messages_and_cinematics,index)

def parse_player_data():
  mydata = data[index:]
  player_data = Player_Data()
  return (player_data,index)

def parse_victory():
  mydata = data[index:]
  victory = Victory()
  return (victory,index)

def parse_unknown():
  mydata = data[index:]
  unknown = Unknown()
  return (unknown,index)

def parse_game_settings():
  mydata = data[index:]
  game_settings = Game_Settings()
  return (game_settings,index)

def parse_trigger_info():
  mydata = data[index:]
  trigger_info = Trigger_Info()
  return (trigger_info,index)

def parse_other_data():
  mydata = data[index:]
  other_data = Other_Data()
  return (other_data,index)

def parse_game_data():
  mydata = data[index:]
  game_data = Game_Data()
  return (game_data,index)


# ----- parse primary structures -----


def read_savegame_file(thefile):

  global index, inMode, data

  # the savegame file is stored as a zlib archive
  # decode without header bytes
  data = zlib.decompress(thefile,wbits=-15)

  # reset index to start of file
  index = 0
  
  # parse each secondary struct
  save_game = SaveGame()
  save_game.header = parse_header()
  save_game.map_info = parse_map_info()
  # save_game.start_info = [parse_start_info(save_game.header.num_players) for i in range(save_game.header.num_players)]
  # save_game.achievement = parse_achievement()
  # save_game.scenario_header = parse_scenario_header()
  # save_game.messages_and_cinematics = parse_messages_and_cinematics()
  # save_game.player_data = parse_player_data()
  # save_game.victory = parse_victory()
  # save_game.unknown = parse_unknown()
  # save_game.game_settings = parse_game_settings()
  # save_game.trigger_info = parse_trigger_info()
  # save_game.other_data = parse_other_data()

  return save_game

def print_savegame(save_game):

  print("save_game: ")
  h = save_game.header
  print("t\header: ")
  print("\t\tversion: ",h.version)
  print("\t\tunknown_const: ",h.unknown_const)
  print("\t\tinclude_ai: ",h.include_ai)
  print("\t\tai_info: ")
  ii = h.ai_info

  for i in ii:
    print("\t\t\tstring_table: ")
    st = i.string_table
    for n,s in enumerate(st.resource_strings):
      print("\t\t\t\t"+str(n)+":")
      print("\t\t\t\t\tstring_length: ", s.string_length)
      print("\t\t\t\t\tstr: ", s.strr)
    add = i.ai_data
    for ad in add:
      print("\t\t\tai_data: ")
      print("\t\t\t\tunknown: " + str(ad.unknown_const1))
      print("\t\t\t\tseq: " + str(ad.seq))
      print("\t\t\t\tmax_rule: " + str(ad.max_rule))
      print("\t\t\t\tnum_rule: " + str(ad.num_rule))
      print("\t\t\t\tunknown: " + str(ad.unknown_data1))
      print("\t\t\t\trules: ")

      r = ad.rules
      for n,rr in enumerate(r):
        rrr = rr.ruledata
        A = ["unknown", "enabled", "rule_number", "unknown", "num_facts", "size", "unknown"]
        C = ["dtype", "idd", "unknown" "param1", "param2", "param3", "param4"]
        B = [rr.unknown_data1, rr.enabled, rr.rule_number, rr.unknown_data3, rr.num_facts, rr.num_facts_and_actions, rr.unknown_data4]

        A = [x.ljust(14) for x in A]
        C = [x.ljust(14) for x in C]
        B = [str(x).ljust(14) for x in B]

        # print(" ".join(A))
        # print(" ".join(B))
        print(" ".join(C))

        for rrrr in rrr:
          
          D = [rrrr.dtype, rrrr.idd, rrrr.unknown] + rrrr.params
          # D = [rrrr.dtype, rrrr.idd]
          D = [str(x).ljust(14) for x in D]
          print(" ".join(D))



