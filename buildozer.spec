[app]

# Название вашего приложения
title = MyBank

# Имя пакета (должно быть уникальным)
package.name = com.example.mybank

# Домен (обратный домен)
package.domain = org.example

# Исходный код
source.dir = .

# Главный файл приложения
source.include_exts = py,png,jpg,kv,atlas,json

# Версия приложения
version = 1.0

# Требования
requirements = python3,kivy,plyer,android,pyjnius,openssl

# Разрешения Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,VIBRATE,WAKE_LOCK

# Ориентация экрана
orientation = portrait

# Характеристики оборудования
fullscreen = 1

# Версия Android API
android.api = 33
android.minapi = 21
android.ndk = 23b
android.sdk = 33

# Иконка приложения (должна быть в вашем проекте)
icon.filename = icon.png

# Splash screen (опционально)
presplash.filename = presplash.png

# Архитектура
android.arch = arm64-v8a