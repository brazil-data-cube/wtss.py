from wtss import wtss

service = wtss('http://www.esensing.dpi.inpe.br')

print(service)
print(str(service))
print(repr(service))
print(service._repr_html_())


print(service.MOD13Q1)
print(str(service.MOD13Q1))
print(repr(service.MOD13Q1))
print(service.MOD13Q1._repr_html_())
