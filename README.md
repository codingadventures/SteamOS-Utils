# SteamOS Utils

A command line tool for automating customization and configuration of handhelds and PCs running SteamOS.

This set of tools was originally made for and tested on the Legion Go, but it works on all computing devices that run SteamOS.

## Requirements

- A device running SteamOS
- Python 3 (ships with SteamOS)

## Getting started

Clone the repository and make the script executable:

```
git clone https://github.com/codingadventures/SteamOS-Utils.git
cd SteamOS-Utils
chmod +x SteamOsUtils.py
```

Run it from the repository directory. You can call it either as `./SteamOsUtils.py <options>` or `python3 SteamOsUtils.py <options>`.

## Usage

| Command | What it does | Needs sudo? |
| --- | --- | --- |
| `--enable_acpi_calls` | Enable Linux DKMS ACPI call support (custom fan curves, charge limit) | Yes |
| `--check_dkms_acpi_calls_enabled` | Check whether DKMS ACPI calls are enabled | Yes |
| `--enable_lego2_brightness_slider` | Install the Legion Go 2 OLED brightness slider and color-correction fix | No |
| `--remove_lego2_brightness_slider` | Remove the Legion Go 2 brightness slider fix | No |
| `--dry_run` | Print the actions without executing them (combine with any command above) | - |

Every command also has a short alias, e.g. `-acpi`, `-check_acpi`, `-lego2brightness`, `-removelego2brightness`, `-d`. Run `./SteamOsUtils.py --help` to see them all.

Tip: add `--dry_run` to any command to preview exactly what it will do before running it for real.

## Enabling Linux Dynamic Kernel Module Support ACPI calls

In order to enable custom fan curves and setting the Legion Go charge limit we need to enable
DKMS ACPI call support for SteamOS. Note that this tool can be used to enable DKMS on any
handheld or gaming PC running SteamOS.

In order to enable the ACPI calls the following needs to happen:

- Disable SteamOS read-only mode
- Download and install the required kernel modules and kernel header packages
- Install the packages that enable the various daemons required for ACPI calls
- Re-enable SteamOS read-only mode

This script automates all of the above with a single command:

```
sudo ./SteamOsUtils.py --enable_acpi_calls
```

The command will take several minutes to run depending on your internet connection.

Once the above command is complete you should see a log like this in the console:

```
Congratulations! You now can enable custom fan curves and control charge limit!
```

We can confirm that the DKMS ACPI support is enabled by running:

```
./SteamOsUtils.py --check_dkms_acpi_calls_enabled
```

or directly with:

```
dkms status
```

If the DKMS ACPI was successfully enabled we should see an output similar to this:

```
acpi_call/1.2.2, 6.11.11-valve24-2-neptune-611-gfd0dd251480d, x86_64: installed
```

Note: this feature installs packages into the SteamOS root filesystem, so it is reverted by SteamOS system updates and must be re-run after a major update.

## Legion Go 2 brightness slider and color-correction fix

On the Legion Go 2 (Ryzen Z2) the in-game brightness slider does not change the OLED
brightness, and the panel can show color banding. This installs a gamescope display profile
that fixes both.

Install the fix:

```
./SteamOsUtils.py --enable_lego2_brightness_slider
```

Remove the fix:

```
./SteamOsUtils.py --remove_lego2_brightness_slider
```

Notes:

- This command does not require `sudo`, but it works either way. If you do run it with `sudo`,
  it detects your real user (via `SUDO_USER`) and writes to the correct home directory.
- The fix writes a single gamescope script to `~/.config/gamescope/scripts/lenovo.legiongo2.oled.lua`.
- Gamescope only loads display scripts at startup, so you must reboot (or fully restart Game
  Mode) once for the change to take effect. There is no need to reboot each time you use the
  brightness slider afterwards.
- Because the file lives in your home directory (not the read-only root filesystem), this fix
  survives SteamOS system updates.

## Note from the author

When I started this project I wanted to have it work for a small list of kernel versions that I could test locally before opening it up to all versions.

This was done by design so I wouldn't get a ton of tickets, while watching to see how well the tool will run in the wild.

Currently I am testing new features with my SteamOS powered high-performance gaming PCs.
