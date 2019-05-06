from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def levantar_configuracion():
	f = open('config.yaml', 'r')
	document = f.read()
	f.close()
	config = load(document, Loader=Loader)
	return config

def sacar_configuracion(config):
	f = open('config_actual.yaml', 'w')
	dump(config, f, Dumper=Dumper, default_flow_style=False)
	f.close()

