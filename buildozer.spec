[app]
# (str) Title of your application
title = Digital Expense Tracker

# (str) Package name
package.name = digitalexpensetracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.rahul.digitalexpensetracker

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# This includes numpy==1.23.5 which is compatible with Android
requirements = python3,kivy,matplotlib,kivy-garden,numpy==1.23.5

# (str) Pre-build commands - CRITICAL for Matplotlib on Android
prebuild = python -m pip install kivy-garden && python -m garden install matplotlib

# (list) Supported orientations
orientation = portrait

# (str) Kivy version to use
osx.kivy_version = 2.2.0

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = False

# (bool) Enable Android auto backup feature
android.allow_backup = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

#
# Buildozer global settings
#

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1