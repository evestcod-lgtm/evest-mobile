[app]
title = Evest Antivirus
package.name = evest
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.2
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,VIBRATE,FOREGROUND_SERVICE
android.api = 33
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
