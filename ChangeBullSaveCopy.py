# ChangeBullSaveCopy script - Change printing parameters at a given height
# This script is the successor of the TweakAtZ plugin for legacy Cura.
# It contains code from the TweakAtZ plugin V1.0-V4.x and from the ExampleScript by Jaime van Kessel, Ultimaker B.V.
# It runs with the PostProcessingPlugin which is released under the terms of the AGPLv3 or higher.
# This script is licensed under the Creative Commons - Attribution - Share Alike (CC BY-SA) terms

#Authors of the ChangeBullSaveCopy plugin / script:
# Written by Steven Morlock, smorloc@gmail.com
# Modified by Ricardo Gomez, ricardoga@otulook.com, to add Bed Temperature and make it work with Cura_13.06.04+
# Modified by Stefan Heule, Dim3nsioneer@gmx.ch since V3.0 (see changelog below)
# Modified by Jaime van Kessel (Ultimaker), j.vankessel@ultimaker.com to make it work for 15.10 / 2.x
# Modified by Ruben Dulek (Ultimaker), r.dulek@ultimaker.com, to debug.

##history / changelog:
##V3.0.1: TweakAtZ-state default 1 (i.e. the plugin works without any TweakAtZ comment)
##V3.1:   Recognizes UltiGCode and deactivates value reset, fan speed added, alternatively layer no. to tweak at,
##        extruder three temperature disabled by "#Ex3"
##V3.1.1: Bugfix reset flow rate
##V3.1.2: Bugfix disable TweakAtZ on Cool Head Lift
##V3.2:   Flow rate for specific extruder added (only for 2 extruders), bugfix parser,
##        added speed reset at the end of the print
##V4.0:   Progress bar, tweaking over multiple layers, M605&M606 implemented, reset after one layer option,
##        extruder three code removed, tweaking print speed, save call of Publisher class,
##        uses previous value from other plugins also on UltiGCode
##V4.0.1: Bugfix for doubled G1 commands
##V4.0.2: uses Cura progress bar instead of its own
##V4.0.3: Bugfix for cool head lift (contributed by luisonoff)
##V4.9.91: First version for Cura 15.06.x and PostProcessingPlugin
##V4.9.92: Modifications for Cura 15.10
##V4.9.93: Minor bugfixes (input settings) / documentation
##V4.9.94: Bugfix Combobox-selection; remove logger
##V5.0:   Bugfix for fall back after one layer and doubled G0 commands when using print speed tweak, Initial version for Cura 2.x
##V5.0.1: Bugfix for calling unknown property 'bedTemp' of previous settings storage and unkown variable 'speed'
##V5.1:   API Changes included for use with Cura 2.2

## Uses -
## M220 S<factor in percent> - set speed factor override percentage
## M221 S<factor in percent> - set flow factor override percentage
## M221 S<factor in percent> T<0-#toolheads> - set flow factor override percentage for single extruder
## M104 S<temp> T<0-#toolheads> - set extruder <T> to target temperature <S>
## M140 S<temp> - set bed target temperature
## M106 S<PWM> - set fan speed to target speed <S>
## M605/606 to save and recall material settings on the UM2

from ..Script import Script
#from UM.Logger import Logger
import re

class ChangeBullSaveCopy(Script):
    version = "5.1.1"
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"ChangeBullSaveCopy """ + self.version + """ (Experimental)",
            "key": "ChangeBullSaveCopy",
            "metadata": {},
            "version": 2,
            "settings":
            {
			    "delay":
                {
                    "label": "Cooling delay",
                    "description": "Cooling time before push. Recommended at least 20 minutes",
                    "unit": "mm",
                    "type": "int",
                    "default_value": 20
                },
			    "parts":
                {
                    "label": "Repeat",
                    "description": "Number of builds to perform",
                    "type": "int",
                    "default_value": 5 
                }
            }
        }"""
		
    def dozerCode(imodel):
        code = """\n\n
;Bulldozer code start
G0 F2000 Z150
G0 F2000 Y210 Z150
G0 F2000 X105 Y210 Z150"""
        for m in range(delay):
            for s in range(6):
                code += "G4 P10000\nM117 Cooling down, " + str(delay-m) + ":" + str(5-s) + "0\n";
                
        code += """M117 Lo and behold!\n
G0 F2000 X105 Y210 Z5
G0 F2000 X105 Y5 Z5   ; bulldozer
M117 Starting model 
""" + str(imodel+1+1) + "/" + str(parts) + "\n\n";        # +1 for 1-based numbers for human user, +1 coz starting next model after this one
        
        return code
		
		

    def execute(self, data):
        delay = self.getSettingValueByKey("delay")
        parts = self.getSettingValueByKey("parts")

        index = 0
        
        RepeatedPart = ""
        StartCod = 0
        StopCod = 0
        g280x = 140;

        for active_layer in data:
            modified_gcode = ""
            lines = active_layer.split("\n")

            for line in lines:
                if line.startswith("G280"):
                    line = "G0 F15000 X" + str(g280x) + " Y6 Z2\nG280 ;position moved\n"
                    g280x -= 30
                
                if     line == ";End of Gcode":
                    line = ""
                    for i in range(parts-1):     
                        line += self.dozerCode(i)
                        line += RepeatedPart
                    line += self.dozerCode(parts-1)
                    line += ";End of Gcode \n"
                    StopCod=1
                    
                if (StartCod==1) and (StopCod==0):
                    RepeatedPart += line + "\n"
                    
                if     line == ";END_OF_HEADER":
                    StartCod=1
                    
                modified_gcode += line + "\n"

            data[index] = modified_gcode
            index += 1


#        lcd_text = "M117 " + name + " layer: "
#        i = 0
#        
#        g280x = 140;     # any number of G280 commands will be 
#        
 #       for layer in data:
    #        while -1 != layer.find("\nG280\n"):        
    #            layer = layer.replace("\nG280\n", "\nG0 F15000 X" + str(g280x) + " Y6 Z2\nG280 ;position moved\n", 1)
    #            g280x -= 30
                
            # the new coordinates of hirbunim - 140 and 110, to make them fall off when the part is pushed.
        
    #        i++
#            display_text = lcd_text + str(i)
#            layer_index = data.index(layer)
#            lines = layer.split("\n")
#            for line in lines:
#                if line.startswith(";LAYER:"):
#                    line_index = lines.index(line)
#                    lines.insert(line_index + 1, display_text)
#                    i += 1
#            final_lines = "\n".join(lines)
#            data[layer_index] = final_lines
            
        return data