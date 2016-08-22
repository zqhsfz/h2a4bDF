Reco_tf.py \
--inputAODFile /afs/cern.ch/user/q/qzeng/eos/atlas/user/q/qzeng/h2a4b/mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.merge.AOD.e3698_s2608_s2183_r7725_r7676/AOD.07915933._001821.pool.root.1 \
--outputDAODFile ttbar_calo_b_v2.pool.root \
--preExec 'rec.doApplyAODFix.set_Value_and_Lock(True);from BTagging.BTaggingFlags import BTaggingFlags;BTaggingFlags.CalibrationTag = "BTagCalibRUN12-08-18"' \
--maxEvents 50 \
--reductionConf SJET1
