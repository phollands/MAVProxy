#!/usr/bin/env python
'''enable run-time addition and removal of UDP clients , just like --out on the cnd line'''
''' TO USE: 
    output add 10.11.12.13:14550
    output list
    output remove 3      # to remove 3rd output
'''    

from pymavlink import mavutil


from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util

class OutputModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(OutputModule, self).__init__(mpstate, "output", "output control", public=True)
        self.add_command('output', self.cmd_output, "output control",
                         ["<list|add|remove>"])

    def cmd_output(self, args):
        '''handle output commands'''
        if len(args) < 1 or args[0] == "list":
            self.cmd_output_list()
        elif args[0] == "add":
            if len(args) != 2:
                print("Usage: output add OUTPUT")
                return
            self.cmd_output_add(args[1:])
        elif args[0] == "remove":
            if len(args) != 2:
                print("Usage: output remove OUTPUT")
                return
            self.cmd_output_remove(args[1:])
        else:
            print("usage: output <list|add|remove>")

    def cmd_output_list(self):
        '''list outputs'''
        print("%u outputs" % len(self.mpstate.mav_outputs))
        for i in range(len(self.mpstate.mav_outputs)):
            conn = self.mpstate.mav_outputs[i]
            print("%u: %s" % (i, conn.address))

    def cmd_output_add(self, args):
        '''add new output'''
        device = args[0]
        print("Adding output %s" % device)
        try:
            conn = mavutil.mavlink_connection(device, input=False)
        except Exception:
            print("Failed to connect to %s" % device)
            return
        self.mpstate.mav_outputs.append(conn)
        try:
            mp_util.child_fd_list_add(conn.port.fileno())
        except Exception:
            pass

    def cmd_output_remove(self, args):
        '''remove an output'''
        device = args[0]
        for i in range(len(self.mpstate.mav_outputs)):
            conn = self.mpstate.mav_outputs[i]
            if str(i) == device or conn.address == device:
                print("Removing output %s" % conn.address)
                try:
                    mp_util.child_fd_list_add(conn.port.fileno())
                except Exception:
                    pass
                conn.close()
                self.mpstate.mav_outputs.pop(i)
                return
        
def init(mpstate):
    '''initialise module'''
    return OutputModule(mpstate)
