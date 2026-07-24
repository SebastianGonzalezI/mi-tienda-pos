[app]
title = Mi Tienda POS
package.name = mitiendapos
package.domain = org.tienda

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 1.0.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,openpyxl==3.1.2,schedule==1.2.0,pillow

orientation = landscape
fullscreen = 0
android.api = 31
android.minapi = 24
android.ndk = 23b
android.sdk = 33
android.enable_androidx = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.bootstrap = sdl2
android.gradle_dependencies =
android.use_gradle = True

icon.filename = assets/icon.png
presplash.filename = assets/splash.png
