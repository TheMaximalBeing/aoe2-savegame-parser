# \project aoe2-savegame-parser
# \author tmb_
# \date JUN/2023
# \licence GPL3 (see COPYING.md)

import savegame
import compile_ai
import os

def ascii(t):
  return str(t).encode("ascii")

def _getstr(t):
  return t.decode("ascii")

def extract_ais_from_save(savename, outbasename):

  # make sure the dicts are initialized
  compile_ai._setup()

  # parse savegame into nested structures
  thesave = savegame.read_savegame_file(open(savename, 'rb').read())

  # make sure that the save file includes at least 1 AI
  head = thesave.header
  if head.include_ai == 0:
    raise Exception("no AI in save game")

  # convert string table to defconsts (this is for all AIs)
  defconst_strings = ""
  string_table = head.ai_info.string_table
  resource_strings = string_table.resource_strings
  defconst_strings += "; ==== begin string table === \n"
  for i,r in enumerate(resource_strings):
    tmp = b"(defconst __s" + ascii(i) + b" \"" + r.string +b"\")\n"
    defconst_strings += tmp.decode("UTF-8",errors='ignore')
  defconst_strings += "; ==== end string table === \n"

  # now get all the AI scripts
  ai_data = head.ai_info.ai_data
  for i,d in enumerate(ai_data):
    if d.ai_number != -1:

      # start the output file for current ai
      filename = outbasename+"_"+str(d.ai_number+1)+".per"
      os.makedirs(os.path.dirname(filename), exist_ok=True)
      out = open(filename, "w")
      out.write(defconst_strings)
      out.write("\n; ==== begin rules === \n")

      # write rules for current ai script
      for j,r in enumerate(d.rules):

        open_logics = []
        actions_started = False

        # begin the current rule
        out.write("; Rule #"+str(j)+"\n")
        out.write("(defrule \n")

        # add the rule commands
        for c in r.ruledata:

          # skip invalid commands
          if c.idd == -1:
            break
          if c.dtype == 1:
            # write action separator when first action found
            if not actions_started:
              out.write("  =>\n")
            actions_started = True

          argcount = None # num arguments required for current command
          idd = None # id string (aka name) for current command

          if c.dtype == 1:
            idd = compile_ai._val_to_action[c.idd]
            argcount = compile_ai._nargs_action[c.idd]
          if c.dtype == 2:
            idd = compile_ai._val_to_logic[c.idd]
            argcount = compile_ai._nargs_logic[c.idd]
          if c.dtype == 3:
            idd = compile_ai._val_to_fact[c.idd]
            argcount = compile_ai._nargs_fact[c.idd]
          idd = idd.encode("ascii")

          # get parameters as a list of strings
          params = c.params[:argcount]
          params = [ascii(p) for p in params]

          # update the number of things in the currently open logic structure
          # i.e. add 1 more command to it
          if len(open_logics) > 0:
            open_logics[-1] -= 1
            open_logics[-1] = max(0,open_logics[-1])
        
          # check if it is a logic command
          if c.dtype == 2:
            out.write(_getstr(b"  (" + idd + b" " + b"\n"))
            open_logics.append(argcount)
          # otherwise print fact/action command
          else:
            out.write(_getstr(b"  (" + idd + b" " + b" ".join(params) + b")\n"))

          # check if we are ready to add closing brackets for logic structures
          if len(open_logics) > 0 and open_logics[-1] == 0:
            out.write("  ")
            while len(open_logics) > 0 and open_logics[-1] == 0:
              out.write(")")
              open_logics.pop()
            out.write("\n")

        # finish off the current rule
        out.write(")\n")

      # finish off the current ai script
      out.write("; ==== end rules === \n")
      out.close()

