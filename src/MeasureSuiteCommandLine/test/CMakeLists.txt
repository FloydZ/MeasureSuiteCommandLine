include(GoogleTest)

file(GLOB TEST_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/*.c)
foreach(testfile ${TEST_SOURCES})
    file(RELATIVE_PATH filename ${CMAKE_CURRENT_SOURCE_DIR} ${testfile})
    string(REPLACE ".c" "" file ${filename})
    add_executable(${file} ${testfile})
    #target_compile_options(${file} PUBLIC ${COMPILE_TEST_FLAGS})
    target_link_libraries(${file} measuresuite.a assemblyline.a)
	add_test(_${file} ${file})
endforeach(testfile ${TEST_SOURCES})
