from wtss import *

service = wtss('http://www.esensing.dpi.inpe.br')

print(service.coverages)

coverage = service['MOD13Q1']

print(coverage)

ts = coverage.ts(attributes=('red', 'nir'),
                 latitude=-12.0, longitude=-54.0,
                 start_date='2001-01-01', end_date='2001-12-31')

print(ts.red)

print(ts.nir)

print(ts.timeline)

ts.plot()