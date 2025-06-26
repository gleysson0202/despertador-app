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
android.build_tools_version = 36.0.0

[buildozer]
log_level = 2
warn_on_root = 1
