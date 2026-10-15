cmake_minimum_required(VERSION 3.5)
project(harbour-physikquiz LANGUAGES CXX)

# Sailfish OS build (Qt 5.6 + Silica). Android and iOS build from android/.

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/rpm/harbour-physikquiz.spec" PHYSIKQUIZ_SPEC)
string(REGEX MATCH "Version:[ \t]*([0-9.]+)" _ "${PHYSIKQUIZ_SPEC}")
set(PHYSIKQUIZ_VERSION "${CMAKE_MATCH_1}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt5 REQUIRED COMPONENTS Core DBus Gui Network Qml Quick)
find_package(PkgConfig REQUIRED)
pkg_check_modules(SAILFISHAPP REQUIRED sailfishapp)

set(PHYSIKQUIZ_SOURCES
    src/main.cpp
    src/QuestionBank.cpp
    src/Match.cpp
    src/GameController.cpp
    src/LanSession.cpp
    src/BtLink.cpp
)

add_executable(harbour-physikquiz ${PHYSIKQUIZ_SOURCES} physikquiz.qrc)
target_compile_definitions(harbour-physikquiz PRIVATE SAILFISH PHYSIKQUIZ_VERSION="${PHYSIKQUIZ_VERSION}")
target_include_directories(harbour-physikquiz PRIVATE src ${SAILFISHAPP_INCLUDE_DIRS})
target_link_libraries(harbour-physikquiz Qt5::Core Qt5::DBus Qt5::Gui Qt5::Network Qt5::Qml Qt5::Quick ${SAILFISHAPP_LIBRARIES})

install(TARGETS harbour-physikquiz RUNTIME DESTINATION bin)
install(DIRECTORY data DESTINATION share/harbour-physikquiz)
install(FILES harbour-physikquiz.desktop DESTINATION share/applications)
foreach(size 86 108 128 172)
    install(FILES assets/appicon/physikquiz-${size}.png
            DESTINATION share/icons/hicolor/${size}x${size}/apps
            RENAME harbour-physikquiz.png)
endforeach()
