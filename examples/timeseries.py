from wtss import *

service = wtss('http://www.esensing.dpi.inpe.br')

cv = service.MOD13Q1

ts = cv.ts(latitude=-12,
           longitude=-54,
           attributes=['nir', 'red'],
           start_date='2001-01-01',
           end_date='2002-02-02')

print(ts)

print(ts.timeline)

print(ts.red)

print(ts.nir)

ts.plot()