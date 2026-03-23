


def enumerate_serial_ports():
    """ Uses the Win32 registry to return a iterator of serial
        (COM) ports existing on this computer.
    """

    import winreg
    import itertools

    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)


    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield (str(val[1]), str(val[0]))
        except EnvironmentError:
            break

if __name__ == "__main__":
    for port in enumerate_serial_ports():
        print(port)