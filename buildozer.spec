[app]
title = Digital Expense Tracker
package.name = digitalexpensetracker
package.domain = org.rahul.digitalexpensetracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,pillow
p4a.source_dir = 

orientation = portrait
osx.kivy_version = 2.2.0

fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE

# IMPORTANT: Accept SDK license automatically
android.accept_sdk_license = True

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
