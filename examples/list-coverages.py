from wtss import *

service = wtss('http://www.esensing.dpi.inpe.br')

print(service)

print(repr(service))

print(service.coverages)