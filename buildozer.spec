[app]
title = Digital Expense Tracker
package.name = digitalexpensetracker
package.domain = org.rahul.digitalexpensetracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# CRITICAL: Use specific versions that work on Android
requirements = python3,kivy,kivy-garden,pillow

# IMPORTANT: This downloads the matplotlib garden for Android
prebuild = python -m pip install kivy-garden && python -m garden install matplotlib

orientation = portrait
osx.kivy_version = 2.2.0

# Android settings
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 24
android.accept_sdk_license = True
android.allow_backup = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
