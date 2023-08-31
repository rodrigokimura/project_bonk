DEVICE_PATH := /run/media/$(USER)/CIRCUITPY

install:
	@circup install -a --auto-file ./src/code.py

update:
	@circup update

put:
	@rm $(DEVICE_PATH)/*.py -vf
	@rm $(DEVICE_PATH)/*.json -vf
	@rm $(DEVICE_PATH)/*.toml -vf
	@cp src/* $(DEVICE_PATH)/ -rv

check:
	@rshell -l

test:
	@ampy -p /dev/ttyACM1 run src/code.py

reset:
	@ampy -p /dev/ttyACM1 reset

lint:
	@pipenv run black .
	@pipenv run isort .
