all: move_stage meas_pico_dmm

move_stage: move_stage.c
	gcc -o move_stage move_stage.c

meas_pico_dmm: meas_pico_dmm.c
	gcc -o meas_pico_dmm meas_pico_dmm.c -lpthread

clean:
	rm -rf move_stage meas_pico_dmm
