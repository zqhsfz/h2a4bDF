import os
import samples
# # test purpose
# sampleList = ["mc15_13TeV.341577.PowhegPy8EG_AZNLOCTEQ6L1_WplusenuH_H125_a20a20_bbbb.merge.AOD.e4118_s2608_s2183_r7772_r7676"]  # for test only
# nEventsPerJob = 1000
# version = "test0"

# signal samples
sampleList = samples._MC_Signal
nEventsPerJob = 5000
version = "00-01-01"

# ttbar samples
# sampleList = samples._MC_ttbar
# nEventsPerJob = 10000
# version = "00-01-01"

# now loop over them
for sampleName in sampleList:

	inDS = sampleName
	
	inDS_split = inDS.split(".")
	inDS_split[-2] = "DAOD_SJET1"
	inDS_split.pop(-1)
	inDS_split.pop(-2)
	outDS = "user.qzeng." + ".".join(inDS_split) + "." + version

	config = {
	  "inDS": inDS,
	  "outDS": outDS,
	  "nEventsPerJob": nEventsPerJob,
	}

	cmd = "pathena --useNewTRF --trf \"Reco_tf.py --preExec 'rec.doApplyAODFix.set_Value_and_Lock(True);from BTagging.BTaggingFlags import BTaggingFlags;BTaggingFlags.CalibrationTag = \\\"BTagCalibRUN12-08-18\\\"' --reductionConf SJET1 --maxEvents '{nEventsPerJob}' --skipEvents %SKIPEVENTS --inputAODFile=%IN --outputDAODFile %OUT.DAOD_SJET1.pool.root\" --skipScout --nEventsPerJob={nEventsPerJob} --inDS {inDS} --outDS {outDS}".format(**config)

	print "\n"
	print cmd
	print "\n"
	os.system(cmd)
