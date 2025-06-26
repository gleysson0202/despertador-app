[app]

# Nome do seu app (título que aparece no dispositivo)
title = DespertadorApp

# Nome do pacote - use um domínio invertido para evitar conflitos
package.name = despertadorapp
package.domain = org.gleysson

# Pasta onde está o código fonte (geralmente a raiz do projeto)
source.dir = .

version = 1.0

# Extensões de arquivo a incluir no pacote (incluindo mp4 para vídeos)
source.include_exts = py,png,jpg,kv,atlas,mp4

# Módulos Python e bibliotecas necessários
requirements = python3,kivy,plyer

# Orientação da tela: portrait (vertical) ou landscape (horizontal)
orientation = portrait

# Permite que a app rode em modo fullscreen (opcional)
fullscreen = 0

# Versão mínima da API Android que seu app suporta
android.minapi = 21

# API alvo (por padrão será a mais recente instalada)
android.api = 31

# ABI (arquiteturas) que você quer gerar
android.archs = armeabi-v7a, arm64-v8a

# Ativar logs de debug para facilitar debug no dispositivo (opcional)
android.debug = 1

# Permissões necessárias para acessar arquivos no Android
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

[buildozer]

# Diretório para armazenar o build
build_dir = ./.buildozer

# Diretório para o cache das dependências
cache_dir = ~/.buildozer/cache

# Diretório para plataforma Android
android_platform_dir = ~/.buildozer/android/platform
