def onValueChange(par, prev):
	o = parent()
	if o.par.Enable and o.par.Outputtype == 'monitor':
		o.par.Openwindow.pulse()
	else:
		o.par.Closewindow.pulse()

