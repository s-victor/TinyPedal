#!/bin/bash
echo -e "Export TinyPedal icon, require ImageMagick v7.0+\n"

# Export as ICO
EXPORT_ICO="icon.ico"
SOURCE_ICO="src/icon.svg"
SIZE_ICO="16,24,32,48,256"

if [ -f "${SOURCE_ICO}" ];
then
    echo -e "SOURCE: $(magick identify ${SOURCE_ICO})"
    magick -define icon:auto-resize="${SIZE_ICO}" \
        -filter box -background none \
        "${SOURCE_ICO}" "${EXPORT_ICO}"
    echo -e "EXPORT: ${EXPORT_ICO} (${SIZE_ICO})\n"
fi

# Export as PNG-8
for SOURCE_SVG in src/*.svg; do
    echo "SOURCE: $(magick identify ${SOURCE_SVG})"
    EXPORT_PNG="$(basename ${SOURCE_SVG} .svg).png"
    magick -format png -depth 8 \
        -define png:compression-level=9 \
        -define png:exclude-chunk=all \
        -background none \
        "${SOURCE_SVG}" "${EXPORT_PNG}"
    echo -e "EXPORT: ${EXPORT_PNG}\n"
done