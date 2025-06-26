[app]
title = AlarmVideoApp
package.name = alarmvideo
package.domain = org.gleysson
source.dir = .
source.include_exts = py,mp4
version = 1.0
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 1
android.permissions = WAKE_LOCK, INTERNET

# Configurações Android específicas
android.api = 31
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
