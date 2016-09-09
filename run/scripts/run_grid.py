import os
from samples import *

# sampleList = _MC_Signal + _MC_ttbar
sampleList = ["mc15_13TeV.341577.PowhegPy8EG_AZNLOCTEQ6L1_WplusenuH_H125_a20a20_bbbb.merge.AOD.e4118_s2608_s2183_r7772_r7676"]  # for test only

# config
nEventsPerJob = 1000
version = "test0"

# now loop over them
for sampleName in sampleList:

	inDS = sampleName
	
	inDS_split = inDS.split(".")
	inDS_split[-2] = "DAOD_SJET1"
	outDS = "user.qzeng." + ".".join(inDS_split) + "." + version

	config = {
	  "inDS": inDS,
	  "outDS": outDS,
	  "nEventsPerJob": nEventsPerJob,
	}

	cmd = "pathena --userNewTRF --trf \"Reco_tf.py --preExec 'rec.doApplyAODFix.set_Value_and_Lock(True);from BTagging.BTaggingFlags import BTaggingFlags;BTaggingFlags.CalibrationTag = \\\"BTagCalibRUN12-08-18\\\"' --reductionConf SJET1 --maxEvents '{nEventsPerJob}' --skipEvents %SKIPEVENTS --inputAODFile=%IN --outputDAODFile %OUT.DAOD_SJET1.pool.root\" --skipScout --nEventsPerJob={nEventsPerJob} --inDS {inDS} --outDS {outDS}".format(**config)

	print cmd