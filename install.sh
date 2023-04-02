#!/bin/sh

SOURCE_PATH=$(dirname $(readlink -f $0))
DESTINATION_PREFIX="/usr/local"
SHARE_PATH="${DESTINATION_PREFIX}/share"
APPLICATIONS_PATH="${SHARE_PATH}/applications"
BIN_PATH="${DESTINATION_PREFIX}/bin"
DESTINATION_PATH="${SHARE_PATH}/TinyPedal"

if [ ! -f "pyRfactor2SharedMemory/__init__.py" ];
then
    echo "Missing files. Please, use a Linux source release file or 'git clone --recurse-submodules'."
    exit 1
fi

if [ ! -w "${SHARE_PATH}" -o ! -w "${BIN_PATH}" -o ! -w "${APPLICATIONS_PATH}" ];
then
    echo "Insufficient privileges to install in the prefix directory: ${DESTINATION_PREFIX}"
    exit 1
fi

if [ -d "${DESTINATION_PATH}" ];
then
    if [ -w "${DESTINATION_PATH}" ];
    then
        rm -r "${DESTINATION_PATH}"
    else
        echo "Insufficient privileges to update existing install."
        exit 1
    fi
fi

echo "Writing ${DESTINATION_PATH}"
cp -r "${SOURCE_PATH}" "${DESTINATION_PATH}"

echo "Writing ${APPLICATIONS_PATH}/svictor.TinyPedal.desktop"
cp "${SOURCE_PATH}/svictor-TinyPedal.desktop" "${APPLICATIONS_PATH}"

echo "Writing ${BIN_PATH}/TinyPedal"
ln -fs "${DESTINATION_PATH}/run.py" "${BIN_PATH}/TinyPedal"

echo "Installation finished."
