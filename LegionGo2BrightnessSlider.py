'''
    MIT License

    Copyright (c) 2026 InnoVision Games

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    file: LegionGo2BrightnessSlider.py
'''

'''
This script automates the fix described in this Reddit post:
https://www.reddit.com/r/LegionGo/comments/1s4mhlu/legion_go_2_steamos_display_fixes_color_banding/?solution=d08771d00d0f821ad08771d00d0f821a&js_challenge=1&token=bbbe4bf1c9a2b5160829c4be34da586149a5733c5aa02863ee737c521f7a85ff
'''

import os
import pwd
import sys

from ShellUtils import run_command

brightness_slider_and_color_correction_script = '''\
local lenovo_go2_oled_colorimetry = {
  r = { x = 0.6835, y = 0.3154 },
  g = { x = 0.2402, y = 0.7138 },
  b = { x = 0.1396, y = 0.0439 },
  w = { x = 0.3134, y = 0.3291 },
}

gamescope.config.known_displays.lenovo_go2_oled = {
  pretty_name = "AMS881KB01-0 OLED",
  dynamic_refresh_rates = {
    60,
    144,
  },
  hdr = {
    supported = true,
    force_enabled = true,
    eotf = gamescope.eotf.gamma22,
    max_content_light_level = 1107.128,
    max_frame_average_luminance = 475.683,
    min_content_light_level = 0.001,
  },
  colorimetry = lenovo_go2_oled_colorimetry,
  dynamic_modegen = function(base_mode, refresh)
    debug("Generating mode " .. refresh .. "Hz for AMS881KB01-0 OLED")
    local mode = base_mode

    gamescope.modegen.set_resolution(mode, 1920, 1200)
    gamescope.modegen.set_h_timings(mode, 32, 8, 40)
    if refresh == 60 then
      gamescope.modegen.set_v_timings(mode, 1904, 8, 56)
    else
      gamescope.modegen.set_v_timings(mode, 56, 8, 56)
    end
    mode.clock = gamescope.modegen.calc_max_clock(mode, refresh)
    mode.vrefresh = gamescope.modegen.calc_vrefresh(mode)

    return mode
  end,
  matches = function(display)
    if display.vendor == "SDC" and display.product == 17153 then
      return 5000
    end
    return -1
  end,
}
debug("Registered AMS881KB01-0 OLED as a known display")
'''

def get_target_user():
    # Gamescope loads user scripts from the home of the user it runs as (e.g.
    # 'deck'), which lives in the home partition and survives SteamOS updates.
    # When invoked via sudo we must target the *invoking* user's home, not
    # root's, otherwise gamescope would never read the file.
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and sudo_user != 'root':
        try:
            pw = pwd.getpwnam(sudo_user)
            return pw.pw_dir, pw.pw_uid, pw.pw_gid
        except KeyError:
            pass
    return os.path.expanduser('~'), os.getuid(), os.getgid()

def get_scripts_dir():
    home, _uid, _gid = get_target_user()
    return os.path.join(home, '.config', 'gamescope', 'scripts')

def reassign_ownership(home, scripts_dir, uid, gid):
    # When running as root (via sudo) the dirs/files we just created are owned
    # by root. Hand them back to the target user so gamescope can read them and
    # the user can manage/remove them later without sudo.
    if os.geteuid() != 0:
        return
    paths = [
        os.path.join(home, '.config'),
        os.path.join(home, '.config', 'gamescope'),
        scripts_dir,
    ]
    for path in paths:
        try:
            os.chown(path, uid, gid)
        except OSError:
            pass

def print_reboot_notice():
    print('\nA reboot (or a full restart of Game Mode / gamescope) is required for this change to take effect,')
    print('because gamescope only loads display scripts at startup.')

def enable_lego2_brightness_slider(dry_run=True):
    home, uid, gid = get_target_user()
    scripts_dir = get_scripts_dir()
    gamemode_script_filename = os.path.join(scripts_dir, 'lenovo.legiongo2.oled.lua')

    if dry_run:
        print('\n[dry-run] Would create gamemode scripts directory: %s' % scripts_dir)
        print('[dry-run] Would write gamemode script to: %s' % gamemode_script_filename)
        print('[dry-run] Script contents:\n%s' % brightness_slider_and_color_correction_script)
        return True

    print('\nNow creating gamemode scripts directory: %s' % scripts_dir)
    try:
        os.makedirs(scripts_dir, exist_ok=True)
    except OSError as e:
        print(f'Unable to create Gamemode scripts directory: {scripts_dir} ({e})')
        return False

    print('Gamemode scripts directory: %s successfully created' % scripts_dir)

    try:
        with open(gamemode_script_filename, 'w', encoding='utf-8') as file:
            file.write(brightness_slider_and_color_correction_script)
        print('Successfully wrote gamemode script to: %s' % gamemode_script_filename)
    except PermissionError:
        print('Error: Permission denied. Unable to write gamemode script to: %s' % gamemode_script_filename)
        return False
    except OSError as e:
        print(f'OS error occurred: {e}')
        return False
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return False

    reassign_ownership(home, scripts_dir, uid, gid)
    try:
        if os.geteuid() == 0:
            os.chown(gamemode_script_filename, uid, gid)
    except OSError:
        pass

    print_reboot_notice()
    return True

def remove_lego2_brightness_slider(dry_run=True):
    print('\nNow removing Legion Go 2 brightness slider and color correction fix')
    scripts_dir = get_scripts_dir()
    gamemode_script_filename = os.path.join(scripts_dir, 'lenovo.legiongo2.oled.lua')
    command = ['rm', '-rf', gamemode_script_filename]
    run_command(command, dry_run)

    if not dry_run:
        print_reboot_notice()
