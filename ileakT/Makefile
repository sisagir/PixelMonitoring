# g++ -o ileak_layers.exe ileak_layers.C `root-config --cflags --libs`

ileak: ileak_layers.C
	g++ -o  ileak_layers ileak_layers.C \
	`root-config --cflags --libs`
	@echo 'done: ileak_layers'

temp:  ileakTemp_layers.C
	g++ -o  ileakTemp_layers ileakTemp_layers.C \
	`root-config --cflags --libs`
	@echo 'done: ileakTemp_layers'