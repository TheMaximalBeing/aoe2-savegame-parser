# \project aoe2-savegame-parser
# \author tmb_
# \date JUN/2023
# \licence GPL3 (see COPYING.md)


# below are the structures found in the AOE2 save file format (.gaz)
# this format is very similar to the recorded game format
# in fact the recorded game format just consists of the savegame data
# plus a list of "GameData" structures at the end

# the starting point is the spredsheet by bari,
# see "data/mgx_english_0.7.xls", with some updates for UserPatch 
# and additional reverse-engineering by myself


# ----- primary structs -----


# structure to represent an AOE2 save game file (.gaz)
class SaveGame:
  
  def __init__(self):
    # type: Header
    self.header = None
    # type: Map_Info
    self.map_info = None
    # type: Start_Info
    self.start_info = None
    # type: Achievement
    self.achievement = None
    # type: Scenario_Header
    self.scenario_header = None
    # type: Messages_and_Cinematics
    self.messages_and_cinematics = None
    # type: Player_Data
    self.player_data = None
    # type: Victory
    self.victory = None
    # type: Unknown_Struct1
    self.unknown_struct1 = None
    # type: Game_Settings
    self.game_settings = None
    # type: Trigger_Info
    self.trigger_info = None
    # type: Other_Data
    self.other_data = None

# structure to represent an AOE2 recorded game file (.mgz)
class Rec:

  def __init__(self):
    # type: SaveGame
    self.save_game = None
    # type: list of Game_Data
    self.game_data = []

# structure to represent an AOE2 scenario file (.scx)
class Scenario:

  def __init__(self):
    # todo...
    pass


# ----- secondary structs -----
 

class Header:

  def __init__(self):
    # type: char[8], "VER ..."
    self.version = None
    # type: int8[4], constant? F6283C41
    self.unknown1 = None
    # type: int8[1], 0 or 1
    self.include_ai = None
    # type: AI_info[include_ai]
    self.ai_info = None
    # type: int8[4]
    self.unknown2 = None
    # type: int32[1], todo: check
    self.game_speed1 = None
    # type: int8[4]
    self.unknown3 = None
    # type: int32[1], todo: check
    self.game_speed2 = None
    # type: float32[1]
    self.unknown4 = None
    # type: int8[4]
    self.unknown5 = None
    # type: float32[1]
    self.game_speed3 = None
    # type: int8[17]
    self.unknown6 = None
    # type: int16[1]
    self.rec_player = None
    # type: int16[1], includes gaia
    self.num_players = None
    # type: int8[4], ? 0,...,0
    self.unknown7 = None
    # type: int8[12], ? -1,...,-1
    self.unknown8 = None
    # type: int8[14]
    self.unknown9 = None
    # type: int32[8], ? game_speed
    self.unknown10 = None

class Map_Info:

  def __init__(self):
    # type: int32[1]
    self.map_size_x = None
    # type: int32[1]
    self.map_size_y = None
    # type: int32[1]
    self.num_data = None
    # type: Unknown_Struct2[num_data]
    self.unknown19 = None
    # type: int16[1], ?? 0001
    self.unknown20 = None
    # type: Map_Terrain[map_size_x*map_size_y]
    self.map_terrain = None
    # type: int8[120]
    self.unknown21 = None
    # type: int32[1]
    self.map_size_x2 = None
    # type: int32[1]
    self.map_size_y2 = None
    # type: int32[map_size_x*map_size_y], unparsed
    self.unknown22 = None
    # type: int32[8], ?? 0,...,0
    self.unknown23 = None
    # type: int8[9], 989E0000020B
    self.unknown24 = None

class Start_Info:
  
  def __init__(self):
    # type: int8[num_players], 0=ally/self, 3=enemy
    self.others_diplomacy = None
    # type: int32[9], -1=invalid, 0=gaia, 1=self, 2=ally, 3=neutral, 4=enemy
    self.my_diplomacy = None
    # type: int8[5], ?? 0,...,0
    self.unknown29 = None
    # type: cstring, in-game player name
    self.player_name = None
    # type: int8[1], ?? 0x16
    self.unknown30 = None
    # type: int32[1], todo check UP size
    self.num_header_data = None
    # type: int8[1], ?? 0x21
    self.unknown31 = None
    # type: float[225?] 
    self.resource_amount_table = None
    # type: int8[1], ?? 0x0b
    self.unknown32 = None
    # type: float32[1]
    self.init_camera_pos_x = None
    # type: float32[1]
    self.init_camera_pos_y = None
    # type: int32[1]
    self.unknown_length = None
    # type: float32[2*unknown_length]
    self.unknown_pos = None
    # type: int8[5]
    self.unknown33 = None
    # type: int8[1]
    self.civilization = None
    # type: int8[3]
    self.unknown34 = None
    # type: int8[1], 0=blue, 1=red, etc.
    self.player_color = None
    # type: int8[1], ?? 0x0b
    self.unknown35 = None
    # type: int8[4182?], unparsed
    self.unknown36 = None
    # type: float32[1]
    self.unknown37 = None
    # type: int32[1], todo: count
    self.num_researches = None
    # type: int16, ?? 0
    self.unknown38 = None
    # type: Research_Status[num_researches]
    self.research_statuses = None
    # type: ?????
    self.unknown39 = None
    self.ai_doctrine = None
    self.unknown_data10 = None
    self.ai_goal = None
    self.unknown_data11 = None
    self.padzero3 = None
    self.learn_len = None
    self.learn_file = None
    self.unknown_data12 = None
    self.unknown_data13 = None
    self.ai_filename_length = None
    self.ai_filename = None
    self.unknown_data14 = None
    self.strategic_number_length = None
    self.strategic_number = None
    self.unknown_data15 = None
    self.unknown_data16 = None
    self.unknown_data17 = None
    self.unknown_data18 = None
    self.unknown_data19 = None
    self.num_obj = None
    self.obj_exist_flags = None
    self.unknown_data20 = None
    self.default_objects = None
    self.map_size_x = None
    self.map_size_y = None
    self.unknown_data20 = None
    self.los = None
    self.unknown_data21 = None
    self.unknown_data22 = None
    self.num_unknowns = None
    self.unknown_array = None
    self.unknown_data23 = None
    self.unknown_data24 = None
    self.unknown_data25 = None
    self.object_array = None
    self.unknown_data26 = None
    self.unknown_data27 = None
    self.unknown_data28 = None
    self.unknown_data29 = None
    self.unknown_data30 = None

class Achievement:

  def __init__(self):
    # size = 1817 x num_players
    self.data = None

class Scenario_Header:

  def __init__(self):
    # size = 4433
    self.data = None
    # ends with .scx
    self.original_filename = None

class Messages_and_Cinematics:

  def __init__(self):
    self.instruct_string_id = None
    self.hints_string_id = None
    self.victory_string_id = None
    self.defeat_string_id = None
    self.history_string_id = None
    self.scouts_string_id = None
    self.instructions = None
    self.hints = None
    self.victory = None
    self.defeat = None
    self.history = None
    self.scouts = None
    self.pg_cinem = None
    self.vict_cinem = None
    self.loss_cinem = None
    self.background = None
    self.bitmap_included = None
    self.bitmap_x = None
    self.bitmap_y = None
    self.whocares = None
    self.bmp_info = None
    self.bitmap = None
    self.nulls = None

class Player_Data:
  
  def __init__(self):
    self.ai = None
    self.aifiles = None
    self.separator = None
    self.resources = None

class Victory:
  
  def __init__(self):
    self.seperator = None
    self.conquest = None
    self.zero1 = None
    self.relics = None
    self.zero2 = None
    self.explored = None
    self.zero3 = None
    self.alll = None
    self.mode = None
    self.score = None
    self.time = None

class Unknown_Struct1:

  def __init__(self):
    self.data = None
    self.padzero = None

class Techs:

  def __init__(self):
    self.data = None

class Game_Settings:

  def __init__(self):
    pass

class Trigger_Info:

  def __init__(self):
    pass

class Other_Data:

  def __init__(self):
    pass

# ONLY for recs, not savegames!
class Game_Data:

  def __init__(self):
    pass


# ----- tertiary structs -----

class Timer:

  def __init__(self):
    # type: int[10]
    self.timers = None

class AI_Info:

  def __init__(self):
    # type: String_Table[1]
    self.string_table = None
    # type: AI_Data[8]
    self.ai_data = None
    # type: char[104]
    self.unknown11 = None
    # type: Timer[8]
    self.timers = None
    # type: int32[256]
    self.shared_goals = None
    # type: char[1024], 0,...,0 ??
    self.unknown12 = None

class AI_Data:

  def __init__(self):
    # type: int8[4], ?? 1
    self.unknown13 = None
    # type: int32[1], ?? check, -1 if invalid
    self.ai_number = None
    # type: int16[1]
    self.max_rules = None
    # type: int16[1]
    self.num_rules = None
    # type: int8[4]
    self.unknown14 = None
    # type: Rule[num_rule]
    self.rules = None 

class Rule:

  def __init__(self):
    # type: int32[1] ??
    self.unknown15 = None
    # type: int32[1]
    self.enabled = None
    # type: int16X[1]
    self.rule_number = None
    # type: int16X[1]
    self.unknown16 = None
    # type: int8X[1]
    self.num_facts = None
    # type: int8X[1], facts + actions
    self.num_commands = None
    # type: int16X[1], ?? always 0
    self.unknown17 = None
    # type: Rule_Data
    self.ruledata = None

class Rule_Data:

  def __init__(self):
    # type: int32[1], 1: action, 2: logic-condition, 3: fact-condition
    self.dtype = None
    # type: int16[1], id of action/fact-condition/logic-condition
    self.idd = None
    # type: int16[1], ?? often all 0 or all -1
    self.unknown18 = None
    # type: int32[4], parameters 1 to 4 (extras equal to 0)
    self.params = None

class String_Table:
  
  def __init__(self):
    # type: int16[1]
    self.max_strings = None
    # type: int16[1]
    self.num_strings = None
    # type: int32[1]
    self.unknown14 = None
    # type: Resource_String[num_strings]
    self.resource_strings = None
    # type int8[6], ?? 78006400 0800
    self.unknown15 = None

class Resource_String:

  def __init__(self):
    # type: int32[1]
    self.string_length = None
    # type: char[string_length]
    self.string = None



class Unknown_Struct2:

  def __init__(self):
    # type: int8[255], -1,...,-1
    self.unknown24 = None
    # type: int32[255], 0,...,0
    self.unknown25 = None
    # type: int8[map_size_x*map_size_y]
    self.unknown26 = None
    # type: int32[1], ?? number of terrain types
    self.num_float = None
    # type: float32[num_float]
    self.unknown27 = None
    # type: int32[1]
    self.unknown28 = None

class Map_Terrain:

  def __init__(self):
    # type: int8
    self.terrain_id = None
    # type: int8
    self.elevation = None



class Research_Status:

  def __init__(self):
    # type: int16[1], 0=prereq not met, 1=not possible, 3=completed, -1=not for civ
    self.status = None
    # type: int8[12], ?? related to automatic techs
    self.unknown_data1 = None

class Unknown_Data:

  def __init__(self):
    self.unknown_data1 = None
    self.unknown_data2 = None

class Object:

  def __init__(self):
    # this looks like another union
    # will decode later

    self.object_type = None
    self.object_type_data = None

    # object_data_gaia = None
    # object_data_other = None
    # object_data_dead_unit = None
    # object_data_unit = None
    # object_data_building = None

class Object_Type10:

  def __init__(self):
    self.typee = None
    self.data = None

class Object_Type30:

  def __init__(self):
    self.typee = None
    self.data = None

class Object_Type60:

  def __init__(self):
    self.typee = None
    self.data = None

class Attacks:

  def __init__(self):
    self.typee = None
    self.value = None

class Armours:

  def __init__(self):
    self.typee = None
    self.value = None

class Object_Cost:

  def __init__(self):
    self.typee = None
    self.amount = None
    self.used = None

class Object_Type70:

  def __init__(self):
    self.typee = None
    self.HP = None
    self.LOS = None
    self.size_x = None
    self.size_y = None
    self.unknown_data1 = None
    self.unknown_data2 = None
    self.move_rate = None
    self.unknown_data3 = None
    self.search_range = None
    self.unknown_data4 = None
    self.unknown_data5 = None
    self.attacks = None
    self.armours = None
    self.rangee = None
    self.unknown_data6 = None
    self.accuracy_percent = None
    self.projectile_id = None
    self.unknown_data6 = None
    self.unknown_data7 = None
    self.padzero = None
    self.object_cost = None
    self.training_time = None
    self.unknown_data8 = None
    self.unknown_data9 = None

class Object_Type80:

  def __init__(self):
    self.typee = None
    self.data = None

class Default_Object:

  def __init__(self):
    self.object_type = None
    self.unit_id = None
    self.unknown_id = None
    self.unit_class = None
    self.unknown_data1 = None
    self.object_type_data = None
