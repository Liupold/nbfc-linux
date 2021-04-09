nbfc_service-debug: \
	build.c \
	config.c config.h \
	ec_debug.h ec_debug.c \
	ec_dummy.h ec_dummy.c \
	ec_linux.c ec_linux.h \
	ec_sys_linux.c ec_sys_linux.h \
	error.c error.h \
	fan.c fan.h \
	fs_sensors.c fs_sensors.h \
	generated/nbfc_service.help.h \
	generated/config.generated.c \
	generated/config.generated.h \
	info.c info.h \
	lm_sensors.c lm_sensors.h \
	macros.h \
	main.c \
	memory.c memory.h \
	nbfc.h \
	nbfc_service.c nbfc_service.h \
	nxjson.c nxjson.h \
	nxjson_utils.h \
	service_config.c service_config.h \
	temperature_filter.c temperature_filter.h \
	temperature_threshold_manager.c temperature_threshold_manager.h \
	optparse/optparse.h optparse/optparse.c
	$(CC) $(CFLAGS) -Wall -Wextra -Wfatal-errors -Wpedantic -Og -g build.c -lsensors -lm -o nbfc_service-debug

nbfc_service: \
	build.c \
	config.c config.h \
	ec_debug.h ec_debug.c \
	ec_dummy.h ec_dummy.c \
	ec_linux.c ec_linux.h \
	ec_sys_linux.c ec_sys_linux.h \
	error.c error.h \
	fan.c fan.h \
	fs_sensors.c fs_sensors.h \
	generated/nbfc_service.help.h \
	generated/config.generated.c \
	generated/config.generated.h \
	info.c info.h \
	lm_sensors.c lm_sensors.h \
	macros.h \
	main.c \
	memory.c memory.h \
	nbfc.h \
	nbfc_service.c nbfc_service.h \
	nxjson.c nxjson.h \
	nxjson_utils.h \
	service_config.c service_config.h \
	temperature_filter.c temperature_filter.h \
	temperature_threshold_manager.c temperature_threshold_manager.h \
	optparse/optparse.h optparse/optparse.c
	$(CC) $(CFLAGS) -Wall -Wextra -Os -DNDEBUG -s build.c -lsensors -lm -o nbfc_service

ec_probe-debug: \
	ec_probe.c \
	ec_sys_linux.h ec_sys_linux.c \
	error.h error.c \
	generated/ec_probe.help.h \
	nbfc.h \
	memory.h memory.c \
	optparse/optparse.h optparse/optparse.c
	$(CC) $(CFLAGS) -Wall -Wextra -Wfatal-errors -Wpedantic -Og -g ec_probe.c -o ec_probe-debug

ec_probe: \
	ec_probe.c \
	ec_sys_linux.h ec_sys_linux.c \
	error.h error.c \
	generated/ec_probe.help.h \
	nbfc.h \
	memory.h memory.c \
	optparse/optparse.h optparse/optparse.c
	$(CC) $(CFLAGS) -Wall -Wextra -Os -DNDEBUG -s ec_probe.c -lm -o ec_probe

release: nbfc_service ec_probe

generated/:
	mkdir -p generated

generated/config.generated.c: generated/ ../tools/config.py ../tools/config.json
	../tools/config.py source > generated/config.generated.c

generated/config.generated.h: generated/ ../tools/config.py ../tools/config.json
	../tools/config.py header > generated/config.generated.h

generated/nbfc_service.help.h: generated/ ../tools/argany/argany.py ../tools/argany/nbfc_service.py
	../tools/argany/argany.py printf ../tools/argany/nbfc_service.py > generated/nbfc_service.help.h

generated/ec_probe.help.h: generated/ ../tools/argany/argany.py ../tools/argany/ec_probe.py
	../tools/argany/argany.py printf ../tools/argany/ec_probe.py > generated/ec_probe.help.h

clean:
	rm -f nbfc_service ec_probe nbfc_service-debug ec_probe-debug a.out
	rm -f *.o
	(cd optparse; make clean)

clean_generated: clean
	rm -rf generated

#	git clone https://github.com/thestr4ng3r/nxjson
