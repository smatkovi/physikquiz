cmake_minimum_required(VERSION 3.21)
project(physikquiz LANGUAGES CXX)

# Qt 6 build for Android, iOS and the desktop (for testing). Same sources and
# QML as the Sailfish OS build; only the window around AppView differs.

set(PHYSIKQUIZ_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/..")

# The version lives in the RPM spec only.
file(READ "${PHYSIKQUIZ_ROOT}/rpm/harbour-physikquiz.spec" PHYSIKQUIZ_SPEC)
string(REGEX MATCH "Version:[ \t]*([0-9]+)\\.([0-9]+)\\.([0-9]+)" _ "${PHYSIKQUIZ_SPEC}")
set(PHYSIKQUIZ_VERSION "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}.${CMAKE_MATCH_3}")
math(EXPR PHYSIKQUIZ_VERSION_CODE "${CMAKE_MATCH_1} * 10000 + ${CMAKE_MATCH_2} * 100 + ${CMAKE_MATCH_3}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 6.9 REQUIRED COMPONENTS Core Gui Network Qml Quick)
qt_standard_project_setup(REQUIRES 6.9)
set(CMAKE_AUTORCC ON)

qt_add_executable(physikquiz
    ${PHYSIKQUIZ_ROOT}/src/main.cpp
    ${PHYSIKQUIZ_ROOT}/src/QuestionBank.cpp
    ${PHYSIKQUIZ_ROOT}/src/QuestionBank.h
    ${PHYSIKQUIZ_ROOT}/src/Match.cpp
    ${PHYSIKQUIZ_ROOT}/src/Match.h
    ${PHYSIKQUIZ_ROOT}/src/GameController.cpp
    ${PHYSIKQUIZ_ROOT}/src/GameController.h
    ${PHYSIKQUIZ_ROOT}/src/LanSession.cpp
    ${PHYSIKQUIZ_ROOT}/src/LanSession.h
    ${PHYSIKQUIZ_ROOT}/src/BtLink.cpp
    ${PHYSIKQUIZ_ROOT}/src/BtLink.h
    ${PHYSIKQUIZ_ROOT}/src/BtLinkAndroid.cpp
    ${PHYSIKQUIZ_ROOT}/physikquiz.qrc
)
target_include_directories(physikquiz PRIVATE ${PHYSIKQUIZ_ROOT}/src)
target_compile_definitions(physikquiz PRIVATE PHYSIKQUIZ_VERSION="${PHYSIKQUIZ_VERSION}")
target_link_libraries(physikquiz PRIVATE Qt6::Core Qt6::Gui Qt6::Network Qt6::Qml Qt6::Quick)
# Raw RFCOMM plus BlueZ over D-Bus on desktop Linux, as on Sailfish OS.
if(LINUX AND NOT ANDROID)
    find_package(Qt6 REQUIRED COMPONENTS DBus)
    target_link_libraries(physikquiz PRIVATE Qt6::DBus)
endif()

if(ANDROID)
    # The question catalogue and the pictures go into the APK's assets/data;
    # QuestionBank reads them through Qt's assets:/ file engine.
    set(PHYSIKQUIZ_PACKAGE "${CMAKE_CURRENT_BINARY_DIR}/package")
    file(REMOVE_RECURSE "${PHYSIKQUIZ_PACKAGE}")
    file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/package/" DESTINATION "${PHYSIKQUIZ_PACKAGE}")
    file(COPY "${PHYSIKQUIZ_ROOT}/data" DESTINATION "${PHYSIKQUIZ_PACKAGE}/assets")
    set_target_properties(physikquiz PROPERTIES
        QT_ANDROID_PACKAGE_SOURCE_DIR "${PHYSIKQUIZ_PACKAGE}"
        QT_ANDROID_PACKAGE_NAME "org.smatkovi.physikquiz"
        QT_ANDROID_APP_NAME "PhysikQuiz"
        QT_ANDROID_APP_ICON "@mipmap/ic_launcher"
        QT_ANDROID_MIN_SDK_VERSION 28
        QT_ANDROID_TARGET_SDK_VERSION 36
        QT_ANDROID_VERSION_CODE ${PHYSIKQUIZ_VERSION_CODE}
        QT_ANDROID_VERSION_NAME "${PHYSIKQUIZ_VERSION}"
    )
    # Broadcast discovery needs a Wi-Fi multicast lock on many devices.
    qt_add_android_permission(physikquiz NAME android.permission.ACCESS_WIFI_STATE)
    qt_add_android_permission(physikquiz NAME android.permission.ACCESS_NETWORK_STATE)
    qt_add_android_permission(physikquiz NAME android.permission.CHANGE_WIFI_MULTICAST_STATE)
    qt_add_android_permission(physikquiz NAME android.permission.WAKE_LOCK)
elseif(IOS)
    # Without NSLocalNetworkUsageDescription iOS refuses every LAN connection
    # and never asks. Broadcast discovery would need Apple's multicast
    # entitlement, so on iOS a host is joined by its address.
    set_target_properties(physikquiz PROPERTIES
        MACOSX_BUNDLE TRUE
        MACOSX_BUNDLE_INFO_PLIST "${PHYSIKQUIZ_ROOT}/ios/Info.plist.in"
        MACOSX_BUNDLE_GUI_IDENTIFIER "org.smatkovi.physikquiz"
        MACOSX_BUNDLE_BUNDLE_NAME "PhysikQuiz"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "${PHYSIKQUIZ_VERSION}"
        MACOSX_BUNDLE_BUNDLE_VERSION "${PHYSIKQUIZ_VERSION_CODE}"
        XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED "NO"
    )
    set_target_properties(physikquiz PROPERTIES OUTPUT_NAME PhysikQuiz)
    # The catalogue next to the executable inside the .app (applicationDirPath()/data),
    # and the icons as plain files (CFBundleIconFiles in Info.plist.in).
    file(GLOB PHYSIKQUIZ_IOS_ICONS "${PHYSIKQUIZ_ROOT}/ios/icons/*.png")
    add_custom_command(TARGET physikquiz POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${PHYSIKQUIZ_ROOT}/data" "$<TARGET_BUNDLE_CONTENT_DIR:physikquiz>/data"
        COMMAND ${CMAKE_COMMAND} -E copy ${PHYSIKQUIZ_IOS_ICONS} "$<TARGET_BUNDLE_CONTENT_DIR:physikquiz>/"
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${PHYSIKQUIZ_ROOT}/ios/lproj" "$<TARGET_BUNDLE_CONTENT_DIR:physikquiz>/")
elseif(APPLE)
    # macOS: PhysikQuiz.app with the catalogue in Contents/Resources/data. The
    # public build carries the sample questions; the full catalogue is put
    # in afterwards (tools/apple-fill.sh) and the bundle signed again.
    set_source_files_properties("${PHYSIKQUIZ_ROOT}/macos/physikquiz.icns" PROPERTIES MACOSX_PACKAGE_LOCATION Resources)
    target_sources(physikquiz PRIVATE "${PHYSIKQUIZ_ROOT}/macos/physikquiz.icns")
    set_target_properties(physikquiz PROPERTIES
        OUTPUT_NAME PhysikQuiz
        MACOSX_BUNDLE TRUE
        MACOSX_BUNDLE_INFO_PLIST "${PHYSIKQUIZ_ROOT}/macos/Info.plist.in"
        MACOSX_BUNDLE_GUI_IDENTIFIER "org.smatkovi.physikquiz"
        MACOSX_BUNDLE_BUNDLE_NAME "PhysikQuiz"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "${PHYSIKQUIZ_VERSION}"
        MACOSX_BUNDLE_BUNDLE_VERSION "${PHYSIKQUIZ_VERSION_CODE}"
    )
    add_custom_command(TARGET physikquiz POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${PHYSIKQUIZ_ROOT}/data" "$<TARGET_BUNDLE_CONTENT_DIR:physikquiz>/Resources/data"
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${PHYSIKQUIZ_ROOT}/ios/lproj" "$<TARGET_BUNDLE_CONTENT_DIR:physikquiz>/Resources")
elseif(WIN32)
    # One portable PhysikQuiz.exe: static Qt, and the question catalogue with its
    # pictures compiled in as a resource (read from :/data).
    set_target_properties(physikquiz PROPERTIES WIN32_EXECUTABLE TRUE OUTPUT_NAME PhysikQuiz)
    target_sources(physikquiz PRIVATE ${PHYSIKQUIZ_ROOT}/windows/physikquiz.rc)
    target_compile_definitions(physikquiz PRIVATE PHYSIKQUIZ_EMBEDDED_DATA)
    file(GLOB_RECURSE PHYSIKQUIZ_DATA_FILES "${PHYSIKQUIZ_ROOT}/data/*")
    qt_add_resources(physikquiz physikquiz_data PREFIX "/" BASE "${PHYSIKQUIZ_ROOT}"
        FILES ${PHYSIKQUIZ_DATA_FILES} BIG_RESOURCES)
else()
    # Desktop and AppImage: data/ next to the executable.
    add_custom_command(TARGET physikquiz POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E create_symlink "${PHYSIKQUIZ_ROOT}/data" "$<TARGET_FILE_DIR:physikquiz>/data")
endif()

# Static builds (Windows) link the QML plugins the shared QML imports, and
# the WebP reader for the pictures. The QML lives in ../qml, outside the
# directory the import scanner looks at by default.
set_target_properties(physikquiz PROPERTIES QT_QML_ROOT_PATH "${PHYSIKQUIZ_ROOT}/qml")
get_target_property(PHYSIKQUIZ_QTCORE_TYPE Qt6::Core TYPE)
if(PHYSIKQUIZ_QTCORE_TYPE STREQUAL "STATIC_LIBRARY")
    # The automatic import scan finds nothing for QML outside this folder,
    # so the plugins of the imports in ../qml are named here (see main.cpp).
    target_link_libraries(physikquiz PRIVATE Qt6::qtquick2plugin Qt6::qmlplugin Qt6::modelsplugin
                                          Qt6::workerscriptplugin Qt6::quickwindow)
    target_compile_definitions(physikquiz PRIVATE PHYSIKQUIZ_STATIC_QML)
    if(TARGET Qt6::QWebpPlugin)
        qt_import_plugins(physikquiz INCLUDE Qt6::QWebpPlugin)
    endif()
endif()
