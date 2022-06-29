# me - this DAT
# 
# comp - the replicator component which is cooking
# allOps - a list of all replicants, created or existing
# newOps - the subset that were just created
# template - table DAT specifying the replicator attributes
# master - the master operator
#

def onRemoveReplicant(comp, replicant):

	replicant.destroy()
	return

def onReplicate(comp, allOps, newOps, template, master):

	for i, c in enumerate(allOps):
		c.par.display = 1
		c.par.Name = template[i+1, 'name']
		c.par.Thumbfile = template[i+1, 'thumbFile']
		c.par.Toxfile = template[i+1, 'tox']

