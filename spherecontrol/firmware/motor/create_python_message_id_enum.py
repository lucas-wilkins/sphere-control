""" Automatically build an enum to reflect LightMessages.h"""

import textwrap

with open("motor_firmware/MotorMessages.h", 'r') as fin:
    with open("motor_messages.py", 'w') as fout:
        fout.write(textwrap.dedent('''
        """ Motor Messages
        
        This is automatically generated from LightMessages.h, via create_python_message_id_enum.py
        
        DO NOT EDIT MANUALLY
        """
        
        from enum import Enum
        
        class MotorMessageType(Enum):
        '''))

        for line in fin:
            txt = line.strip()
            if txt.startswith("#define"):
                parts = [part for part in txt.split(" ") if len(part) > 0]

                name = parts[1]
                value = parts[2]

                fout.write(f"    {name} = {value}\n")

        fout.write("\n")
