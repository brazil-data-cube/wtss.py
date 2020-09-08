from wtss import *

service = wtss('http://www.esensing.dpi.inpe.br')

cv = service.MOD13Q1

ts = cv.ts(latitude=-12.0, longitude=-54, attributes=['nir', 'red'])

print(ts)

print(ts.timeline)

print(ts.red)

print(ts.nir)