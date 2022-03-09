import winreg
import time

version = '3.5'
key = 'gV9a-aS1j-mP09-1ddX'


def seconds_to_date(secs):
    d = secs // 86400
    h = (secs % 86400) // 3600
    m = ((secs % 86400) % 3600) // 60
    return d, h, m


def set_new_end_date():
    access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    end_date = int(time.time()) + 604800
    key = winreg.OpenKey(access_registry, fr"Software\Germes\{version}")
    winreg.SetValue(key, 'end_date', winreg.REG_SZ, str(end_date))
    print('::. Установили новый срок')
    return end_date


def check_date():
    access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    try:
        key = winreg.OpenKey(access_registry, fr"Software\Germes\{version}")
        end_date = winreg.QueryValue(key, 'end_date')
    except:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, fr"Software\Germes\{version}")
        end_date = set_new_end_date()

    time_left = int(end_date) - int(time.time())
    if time_left <= 0:
        return 0

    d, h, m = seconds_to_date(time_left)
    print(f'::. До конца пробного периода {d} д. {h} ч. {m} м.')
    return 1


def check_key(input_key):
    if input_key == key:
        return 1
    return 0

# access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
# key = winreg.OpenKey(access_registry, fr"Software\Germes\{version}")
# print(winreg.QueryValue(key, 'end_date'))
# winreg.SetValue(key, 'end_date', winreg.REG_SZ, str(int(time.time())))
# print(winreg.QueryValue(key, 'end_date'))



