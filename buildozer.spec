[app]
title = YT Downloader
package.name = ytdownloader
package.domain = org.ytdl
source.dir = .
source.include_exts = py
version = 0.1
requirements = python3,kivy==2.3.0,yt-dlp,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
