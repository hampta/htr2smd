@echo off
python -m nuitka --onefile --standalone --output-dir=build --enable-console^
    --output-filename=htr2smd --quiet --assume-yes-for-downloads --enable-plugin=upx^
    --follow-imports --no-pyi-file ./htr2smd.py
pause