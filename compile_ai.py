# \project aoe2-savegame-parser
# \author tmb_
# \date JUN/2023
# \licence GPL3 (see COPYING.md)

import re
import regex
import time
from pandas import read_excel

# class represents a compiled rule
# same representation used by the game internally
class CompiledRule:
  def __init__(self):
    # element number of first action
    self.separator = None
    # the list of compiled facts/logics/actions
    # format: [dtype num arg1 arg2 arg3 arg4]
    # example: (true) -> [3 0 0 0 0 0]
    self.elements = []

benchark_on = True
_setup_done = False
_dtype_to_val = None
_action_to_val = None
_logic_to_val = None
_fact_to_val = None
_val_to_dtype = None
_val_to_action = None
_val_to_logic = None
_val_to_fact = None
_constfile = None
_ptime = None

# first-time initialization of some important data
def _setup():

  global _setup_done, _dtype_to_val, _action_to_val, _logic_to_val, _fact_to_val
  global _val_to_dtype, _val_to_action, _val_to_logic, _val_to_fact, _constfile

  rule_info_name = "data/rule-info.xlsx"
  const_file_name = "data/constants.per"

  df1 = read_excel(io=rule_info_name, sheet_name="dtype")
  df2 = read_excel(io=rule_info_name, sheet_name="action-numbers")
  df3 = read_excel(io=rule_info_name, sheet_name="logic-numbers")
  df4 = read_excel(io=rule_info_name, sheet_name="fact-numbers")

  _dtype_to_val = dict(zip(df1.values[:,0], df1.values[:,1]))
  _action_to_val = dict(zip(df2.values[:,0], df2.values[:,1]))
  _logic_to_val = dict(zip(df3.values[:,0], df3.values[:,1]))
  _fact_to_val = dict(zip(df4.values[:,0], df4.values[:,1]))

  _val_to_dtype = { v:k for k,v in _dtype_to_val.items() }
  _val_to_action = { v:k for k,v in _action_to_val.items() }
  _val_to_logic = { v:k for k,v in _logic_to_val.items() }
  _val_to_fact = { v:k for k,v in _fact_to_val.items() }

  _constfile = open(const_file_name, 'r').read()
  _constfile += "\n"
  _setup_done = True

# prints out duration of previous code block
def _benchmark(strr):
  global _ptime, benchark_on
  if not benchark_on:
    return
  print(strr.ljust(20), "{:.3f}".format(time.time()-_ptime), "seconds")
  _ptime = time.time()

# compiles the script with the given name
# returns (list of compiles rules, and string table dict)
def compile_ai_script(script_name):

  global _setup_done, _dtype_to_val, _action_to_val, _logic_to_val, _fact_to_val
  global _val_to_dtype, _val_to_action, _val_to_logic, _val_to_fact, _constfile, _ptime

  print("\n--- begin compile {0} ---".format(script_name))

  ### first-time setup

  _ptime = time.time()
  if not _setup_done:
    _setup()
  _benchmark("setup")

  ### load ai script; append the constants file

  s = _constfile + open(script_name, 'r').read()
  _benchmark("load-ai-script")

  ### replace: \" with something so that these don't mess things up

  s = s.replace("\\\"", "\x16")
  _benchmark("replace => with x16")

  ### delete comments without breaking quotes

  toks = s.split("\n")
  i = -1

  for i in range(len(toks)):

    # massive speedup 11. Typical python nonsence
    if not ";" in toks[i]:
      continue

    count_quote = 0
    for j in range(len(toks[i])):
      if toks[i][j] == "\"":
        count_quote += 1
      elif toks[i][j] == ";" and count_quote % 2 == 0:
        toks[i] = toks[i][:j]
        break

  s = "\n".join(toks)
  _benchmark("delete-comments")

  ### extract all strings and replace with ID

  stringtable = { }
  index = -1
  def streplace(match):
    nonlocal index
    index += 1
    stringtable[index] = match.group(1)
    return str(index)

  s = re.sub(r"\"(.*?)\"",streplace,s)
  _benchmark("create-string-table")

  ### clean up whitespace

  s = re.sub("\s+", " ", s) # convert all whitespace to single space
  s = s.replace("( ", "(") # delete spaces between brackets
  s = s.replace(") ", ")")
  s = s.replace(") (", ")(")
  s = s.replace("=>", "\x17") #replace => with custom character
  s = s.replace(" \x17", "\x17") # remove spaces around =>
  s = s.replace("\x17 ", "\x17")
  if s[0] == " ": # remove initial space
    s = s[1:]

  _benchmark("clean up spaces")

  ### deal with macros

  # ... todo

  _benchmark("deal with macros")

  ### extract default defconsts & rules

  # points to the current element in s that we are parsing
  index = 0
  # stores the defconst -> number mappings
  symboltable = {}
  # list of all (un-compiled) rules
  rules = []
  # full length of s
  len_s = len(s)

  # pre-compile our regex's for better performance
  r1 = re.compile(r"\(defconst ([^ ]+) ([^\)]+)\)")
  r2 = regex.compile(r"\(([a-z\-]+)(?: ([^ \)]+))*\)")

  while index < len(s):

    # try to extract a defconst
    if s.startswith("(defconst",index):
      mat = r1.match(s, index, min(len_s,index+200))
      index = mat.end()
      symboltable[mat.group(1)] = int(mat.group(2))
      continue

    # try to extract a rule
    if s.startswith("(defrule ",index):
      index += 9
      # start a new rule
      rule = CompiledRule()
      # the number of facts/logics/actions in current rule so far
      command_count = 0
      # the number of nested (and, (or, etc that we are currently inside
      logic_count = 0

      while True:
        
        # try to match end of rule / nested logic
        if s.startswith(")",index):
          logic_count -= 1
          index += 1
          if logic_count < 0:
            break
          continue

        # try to match the separator
        if s[index] == "\x17":
          rule.separator = command_count
          index += 1
          continue

        command_count += 1

        # try to match a condition
        names = ("(not","(and","(xor","(or","(nor","(xnor","(nand")
        if s.startswith(names,index):
          logic_count += 1
          j = s.find(" ",index)
          rule.elements.append([s[index+1:j]])
          index =j+1
          continue

        # try to match a fact/action
        mat = r2.match(s,index,min(len_s,index+2000))
        if mat:
          rule.elements.append(mat.captures(1) + mat.captures(2))
          index = mat.end()
          continue

        # if we got here then must have failed :(
        raise Exception("could not match token")

      # add parsed rule to full list
      rules.append(rule)
      continue
    
    # try to match a load
    # todo...

    # if we got here then it wasn't a defconst or defrule
    raise Exception("invalid")

  _benchmark("extract consts/rules")

  def convert_arg(v):
    nonlocal symboltable
    try:
      return int(v)
    except:
      return symboltable[v]

  ### transform the rules into compiled form

  # the compiled form of an "invalid" command; for later use
  invalid_command = [_dtype_to_val["invalid"],-1,0,0,0,0]
  rule_size = 16 # todo: add option for DE

  for r in rules:

    # the uncompiled list of commands in the rule
    commands = r.elements
    # the compiled list of commands in the rule
    commands_final = []

    # we will fill in all 16 commands (including the invalid ones)
    for i in range(rule_size):

      # the command arguments (dtype fact/act a1 a2 a3 a4)
      args = []

      # if we are beyond the origial command list then add an invalid command
      if i >= len(commands):
        args = invalid_command

      # otherwise compile the current command
      else:
        # check if we are in the action section
        if i >= r.separator:
          args.append(_dtype_to_val["action"])
          args.append(_action_to_val[commands[i][0]])
          args += [convert_arg(i) for i in commands[i][1:]]
        # otherwise it is a logic/fact; try logic first
        elif commands[i][0] in _logic_to_val:
          args.append(_dtype_to_val["logic"])
          args.append(_logic_to_val[commands[i][0]])
        # otherwise it must be a fact
        else:
          args.append(_dtype_to_val["fact"])
          args.append(_fact_to_val[commands[i][0]])
          args += [convert_arg(i) for i in commands[i][1:]]

      # ensure that the command has 4 args, with extras filled with 0
      if len(args) < 6:
        args += [0]*(6-len(args))

      # add the compiled command to final list
      commands_final.append(args)
    
    # update the command list to the compiled form
    r.elements = commands_final

  _benchmark("compile rules")

  return (rules, stringtable)
