[app]

title = Mi Tienda POS
package.name = mitiendapos
package.domain = org.tienda

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,otf,xlsx,db

source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git, __pycache__, venv, .venv
source.exclude_patterns = license,readme,*.pyc,*.pyo,*.spec

version = 1.0.0

requirements = python3,kivy==2.2.1,kivymd==1.1.1,openpyxl==3.1.2

orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.2.1

fullscreen = 0

android.api = 31
android.minapi = 24
android.sdk = 33
android.ndk = 23b
android.enable_androidx = True
android.accept_sdk_license = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK
android.archs = arm64-v8a
android.wakelock = True

icon.filename = assets/icon.png
presplash.filename = assets/icon.png

[buildozer]

log_level = 1
log_filename = buildozer.log
