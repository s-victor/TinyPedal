#!/bin/bash

SOURCE_PATH=$(dirname "$(readlink -f $0)")


replace() {
    PATTERN="$1"
    STRING="$2"
    while read LINE; do
        echo "${LINE/${PATTERN}/${STRING}}"
    done
}

setinstallpaths () {
    SHARE_PATH="${DESTINATION_PREFIX}/share"
    APPLICATIONS_PATH="${SHARE_PATH}/applications"
    BIN_PATH="${DESTINATION_PREFIX}/bin"
    DESTINATION_PATH="${SHARE_PATH}/TinyPedal"
}


install_to() {

    setinstallpaths

    if [ ! -w "${SHARE_PATH}" -o ! -w "${BIN_PATH}" ]; then
        setsudo=1
    fi


    ${setsudo:+'sudo'} rsync -av --progress --exclude=".git" "$SOURCE_PATH" "$SHARE_PATH"
    ${setsudo:+'sudo'} chown $USER "${DESTINATION_PATH}"

    if [ ! -d "${APPLICATIONS_PATH}" ]; then
        echo "creating applications directory"
        ${setsudo:+'sudo'} mkdir ${APPLICATIONS_PATH}
        ${setsudo:+'sudo'} chown $USER "${APPLICATIONS_PATH}"
    fi

    echo "Writing ${APPLICATIONS_PATH}/svictor-TinyPedal.desktop"
    replace "/usr/local" "${DESTINATION_PREFIX}" <"${SOURCE_PATH}/svictor-TinyPedal.desktop" | ${setsudo:+'sudo'} tee "${APPLICATIONS_PATH}/svictor-TinyPedal.desktop" > /dev/null
    ${setsudo:+'sudo'} chown $USER "${APPLICATIONS_PATH}/svictor-TinyPedal.desktop"


    echo "Writing ${BIN_PATH}/TinyPedal"
    replace "./" "${DESTINATION_PATH}/" <"${SOURCE_PATH}/TinyPedal.sh" | ${setsudo:+'sudo'} tee "${BIN_PATH}/TinyPedal" > /dev/null
    ${setsudo:+'sudo'} chown $USER "${BIN_PATH}/TinyPedal"
    ${setsudo:+'sudo'} chmod a+x "${BIN_PATH}/TinyPedal"

    echo ""
    echo "Installation finished."

    OLDINSTALL="$DESTINATION_PREFIX"
}

path_approval() {
    echo ""
    echo "Are you sure you want to install TinyPedal to '${DESTINATION_PREFIX}' prefix?"
    select yn in "yes" "go back" "exit"; do
        case $yn in
            "yes"      )   install_to;main_menu;;
            "go back"  )   main_menu;;
            "exit"     )   exit;;
        esac
    done
}

remove() {
    ${setsudo:+'sudo'} rm -r "${DESTINATION_PREFIX}/share/TinyPedal"
    ${setsudo:+'sudo'} rm "${DESTINATION_PREFIX}/share/applications/svictor-TinyPedal.desktop"
    ${setsudo:+'sudo'} rm "${DESTINATION_PREFIX}/bin/TinyPedal"
    echo "TinyPedal removed."
}


set_path() {
    echo ""
    echo "desired installation path:"
    read CUSTOMPATH
    DESTINATION_PREFIX=${CUSTOMPATH%/}
}


logo () {
    echo "                                             "
    echo " _____  _            _____         _       _ "
    echo "|_   _||_| ___  _ _ |  _  | ___  _| | ___ | |"
    echo "  | |  | ||   || | ||   __|| -_|| . || .'|| |"
    echo "  |_|  |_||_|_||_  ||__|   |___||___||__,||_|"
    echo "               |___|                         "
    echo ""

}

setvenv () {
    TEMP_FILE=$(mktemp)

    sed "s|'env|'source ${DESTINATION_PATH}/venv/bin/activate \&\& env|g" "${APPLICATIONS_PATH}/svictor-TinyPedal.desktop" > "$TEMP_FILE"
    if [[ -s "$TEMP_FILE" ]]; then
        ${setsudo:+sudo} mv "$TEMP_FILE" "${APPLICATIONS_PATH}/svictor-TinyPedal.desktop"
        echo ".desktop file updated successfully."
    else
        echo "Error: No changes made to .desktop file."
    fi

    sed "s|env|source ${DESTINATION_PATH}/venv/bin/activate \&\& env|g" "${BIN_PATH}/TinyPedal" > "$TEMP_FILE"
    if [[ -s "$TEMP_FILE" ]]; then
        ${setsudo:+sudo} mv "$TEMP_FILE" "${BIN_PATH}/TinyPedal"
        echo "/bin/TinyPedal updated successfully."
    else
        echo "Error: No changes made to /bin/TinyPedal."
    fi
}

venv () {
    setinstallpaths
    echo "creating virtual environment using Python3.8"
    python3.8 -m venv ${DESTINATION_PREFIX}/share/TinyPedal/venv/
    echo "activating virtual environment"
    source ${DESTINATION_PREFIX}/share/TinyPedal/venv/bin/activate
    echo "installing dependencies"
    pip install pyxdg psutil PySide2
    echo "exiting virtual environment"
    deactivate
    setvenv

}

getpysideversion () {
    if grep -q "from PySide2.QtCore" "${DESTINATION_PREFIX}/share/TinyPedal/tinypedal/ui/app.py"; then
        PYSIDE="2"
        OPPOSE="6"
    elif grep -q "from PySide6.QtCore" "${DESTINATION_PREFIX}/share/TinyPedal/tinypedal/ui/app.py"; then
        PYSIDE="6"
        OPPOSE="2"
    fi
}

switchto6() {
    setinstallpaths
    find "${DESTINATION_PATH}/tinypedal/" -name "*.py" -exec sh -c '
        sed -i "s/PySide2/PySide6/g" "$1";
    ' _ {} \;

    sed -i "0,/QAction/{s/QAction//}" "${DESTINATION_PATH}/tinypedal/ui/vehicle_brand_editor.py"

    find "${DESTINATION_PATH}/tinypedal/ui/" \( -name "app.py" -o -name "tray_icon.py" -o -name "menu.py" -o -name "vehicle_brand_editor.py" \) -exec sh -c '

    # Replace the first occurrence of ", QAction"
    sed -i "0,/, QAction/{s/, QAction//}" "$1"

    # Replace the first occurrence of "QAction,"
    sed -i "0,/QAction,/{s/QAction,//}" "$1"



    # Handle "QtGui import" based on parentheses
    if grep -q "QtGui import (" "$1"; then
        sed -i "0,/QtGui import (/{s/QtGui import (/QtGui import QAction,/}" "$1"
    elif grep -q "QtGui import" "$1"; then
        sed -i "0,/QtGui import/{s/QtGui import/QtGui import QAction,/}" "$1"
    fi
    ' _ {} \;


    echo "deleting virtual env starting args from files"
    TEMP_FILE=$(mktemp)
    sed "s|'source ${DESTINATION_PATH}/venv/bin/activate \&\& env|'env|g" "${APPLICATIONS_PATH}/svictor-TinyPedal.desktop" > "$TEMP_FILE"
    if [[ -s "$TEMP_FILE" ]]; then
        ${setsudo:+sudo} mv "$TEMP_FILE" "${APPLICATIONS_PATH}/svictor-TinyPedal.desktop"
        echo ".desktop file updated successfully."
    else
        echo "Error: No changes made to .desktop file."
    fi

    sed "s|source ${DESTINATION_PATH}/venv/bin/activate \&\& env|env|g" "${BIN_PATH}/TinyPedal" > "$TEMP_FILE"
    if [[ -s "$TEMP_FILE" ]]; then
        ${setsudo:+sudo} mv "$TEMP_FILE" "${BIN_PATH}/TinyPedal"
        echo "/bin/TinyPedal updated successfully."
    else
        echo "Error: No changes made to /bin/TinyPedal."
    fi

}


main_menu() {
    logo
    echo "Welcome to the TinyPedal Manager!"
    echo ""

    if [ $OLDINSTALL ];then
        getpysideversion
        setinstallpaths
        if [ $PYSIDE -eq "2" ];then
            echo "Currently TinyPedal is using PySide${PYSIDE}. To successfully run, please ensure you have python3.8 installed and create a Virtual Environment."
            echo "In case you experience graphical issues, try switching to PySide6. "
            echo "with PySide6 TinyPedal doesnt need virtual env and runs with latest Python but changes scaling of the widgets."
        fi
        if [ $PYSIDE -eq "6" ];then
            echo "Currently TinyPedal is using PySide${PYSIDE}. If you are running KDE, dependencies already should be installed and you are good to go!"
            echo "Needed dependencies: PySide6, python-psutil, python-pyxdg."
        fi
        echo""
        MENU_ITEMS=()
        if [ ! -d "${DESTINATION_PREFIX}/share/TinyPedal/venv/" -a  ${PYSIDE} -eq "2" ]; then
            MENU_ITEMS+=("setup virtual environment")
        fi
        MENU_ITEMS+=("switch to PySide${OPPOSE}" "run TinyPedal" "remove TinyPedal" "exit")


        select yn in "${MENU_ITEMS[@]}" ; do
            case $yn in
                "setup virtual environment"      )   venv;main_menu;;
                "switch to PySide${OPPOSE}"      )   if [ ${OPPOSE} -eq "6" ];then switchto6;else install_to;if [ -d "${DESTINATION_PATH}/venv/" ];then setvenv;fi;fi;main_menu;;
                "run TinyPedal"                  )   sh "${BIN_PATH}/TinyPedal";exit;;
                "remove TinyPedal"               )   remove;exit;;
                "exit"                           )   exit;;
            esac
        done
    else
        echo "Installing as single user requires \$HOME/.local/bin in \$PATH to be able to start TinyPedal/tpsetup from Commandline."
        echo ""
        select yn in "single user" "all users(with root privileges)" "exit"; do
            case $yn in
                "single user"                      )   DESTINATION_PREFIX="$HOME/.local";path_approval;;
                "all users(with root privileges)"  )   DESTINATION_PREFIX="/usr/local";path_approval;;
                "exit"                             )   exit;;
            esac
        done
    fi

}


if [ ! -e "pyRfactor2SharedMemory/__init__.py" ];
then
    logo
    echo "Error: Missing files. Please, use a Linux source release file or 'git clone --recurse-submodules'."
    echo ""
    exit 1
fi

if [ -d "/usr/local/share/TinyPedal"  ];
then
    DESTINATION_PREFIX="/usr/local"
    OLDINSTALL=1
    setsudo=1
elif [ -d "$HOME/.local/share/TinyPedal" ];
then
    OLDINSTALL=1
    DESTINATION_PREFIX="$HOME/.local"
fi


if [ -n "$1" ];then DESTINATION_PREFIX=${1%/};path_approval;else main_menu;fi



