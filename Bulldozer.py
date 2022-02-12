# Cura PostProcessingPlugin
# Author:   Pavel Radzivilovsky
# Date:     February 2, 2019

## Description:  !!! Use at your own risk !!!
##               This plugin creates gcode that can seriously damage your printer.
##               Inserts code to push the print out of the printer, and restart the print of a new object.
##               Can be used to automate production process of multiple objects. Never use unattended!
##               The model must be centered horizontally and placed in the front 2/3 of the build plate.
##               Tested with Ultimaker 3. And seriously, use at your own risk, this can break your printer. 

from ..Script import Script

class Bulldozer(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Bulldozer - Kick the model out of the printer",
            "key": "Bulldozer",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "delay":
                {
                    "label": "Cooling delay",
                    "description": "Cooling time before push. Recommended at least 20 minutes",
                    "unit": "min",
                    "type": "int",
                    "default_value": 20
                },
                "parts":
                {
                    "label": "Repeat",
                    "description": "Number of builds to perform",
                    "unit": "prints",
                    "type": "int",
                    "default_value": 5                    
                },
                "zheight":
                {
                    "label": "Noozle height",
                    "description": "The height of the noozle when performing the bulldozer",
                    "unit": "mm",
                    "type": "int",
                    "default_value": 5
                }
            }
        }"""
    
    def dozerCode(self, imodel, bedtemp):
        delay = self.getSettingValueByKey("delay")
        parts = self.getSettingValueByKey("parts")
        zheight = self.getSettingValueByKey("zheight")
        
        code = """
;Bulldozer code start
G0 F2000 Z150
G0 F2000 Y210 Z150
G0 F2000 X105 Y210 Z150\n\n"""

        for m in range(delay):
            for s in range(6):
                code += "G4 P10000\nM117 Cooling down, " + str(delay-m-1) + ":" + str(5-s) + "0\n"
                
        code += """M117 Behold!\n
G0 F2000 X105 Y210 Z"""
        code +=str(zheight)
        code +="""
G0 F2000 X105 Y5 Z"""
        code +=str(zheight)
        code +="""; bulldozer
G4 P10000\n\n"""

        if imodel+1 < parts :
            code += "M117 Printing model " + str(imodel+1+1) + "/" + str(parts) + "\nM190 S" + str(bedtemp) + "\n\n"       # +1 for 1-based numbers for human user, +1 coz starting next model after this one

        return code
    
    def execute(self, data):
        parts = self.getSettingValueByKey("parts")
        index = 0
        RepeatedPart = ""
        StartCod = 0
        StopCod = 0
        g280x = 110;
        initialBedTemperature_C = 0;

        for active_layer in data:
            modified_gcode = ""
            lines = active_layer.split("\n")

            for line in lines:
                if line.startswith(";BUILD_PLATE.INITIAL_TEMPERATURE:"):
                    initialBedTemperature_C = int(line[-2:])
                    
                if line.startswith("G280") and not line.startswith("G280 S1"):
                    line = "G0 F15000 X" + str(g280x) + " Y6 Z2\nG280 ;position moved\n"
                    g280x += 15
                
                if line == ";End of Gcode":
                    line = ""
                    for i in range(parts-1):   
                        line += self.dozerCode(i, initialBedTemperature_C)
                        line += RepeatedPart
                    line += self.dozerCode(parts-1, initialBedTemperature_C)
                    line += ";End of Gcode \n"
                    StopCod=1
                    
                if (StartCod==1) and (StopCod==0):
                    RepeatedPart += line + "\n"
                    
                if     line == ";END_OF_HEADER":
                    StartCod=1
                    
                modified_gcode += line + "\n"

            data[index] = modified_gcode
            index += 1            
        return data
