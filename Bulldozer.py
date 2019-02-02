# Cura PostProcessingPlugin
# Author:   Pavel Radzivilovsky
# Date:     Frbryary 2, 2019

# Description:  !!! Use at your own risk !!!
#				This plugin creates gcode that can seriously damage your printer.
#               Inserts code to push the print out of the printer, and restart the print of a new object.
#               Can be used to automate production process of multiple objects. Never use unattended!
#				The model must be centered horizontally and placed in the front 2/3 of the build plate.
#				Tested with Ultimaker 3. And seriously, use at your own risk, this can break your printer. 

from ..Script import Script
from UM.Application import Application

class Bulldozer(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Use print head to kick the model out of the printer",
            "key": "Bulldozer",
            "metadata": {},
            "version": 1,
            "settings":
            {
                "delay":
                {
                    "label": "Cooling delay",
                    "description": "Cooling time before push. Recommended at least 20 minutes",
                    "unit": "mm",
                    "type": "int",
                    "default_value": 20
                }
				"parts"
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
""" + str(imodel+1+1) + "/" + str(parts) + "\n\n";		# +1 for 1-based numbers for human user, +1 coz starting next model after this one
		
		return code
		
    
    def execute(self, data):
		delay = self.getSettingValueByKey("delay")
		parts = self.getSettingValueByKey("parts")

#        lcd_text = "M117 " + name + " layer: "
        i = 0
        for layer in data:
			
			i++
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
