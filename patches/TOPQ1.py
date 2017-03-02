#====================================================================
# TOPQ1 
# SINGLE TOP SELECTION
#   >=1 electron(pT>20GeV) OR
#   >=1 muon(pT>20GeV) 
# reductionConf flag TOPQ1 in Reco_tf.py
#====================================================================

#====================================================================
# IMPORTS - Order Matters
#====================================================================
from DerivationFrameworkCore.DerivationFrameworkMaster import *
from DerivationFrameworkInDet.InDetCommon import *
from DerivationFrameworkJetEtMiss.JetCommon import *
from DerivationFrameworkJetEtMiss.ExtendedJetCommon import * 
from DerivationFrameworkJetEtMiss.METCommon import *
from DerivationFrameworkFlavourTag.HbbCommon import *
from DerivationFrameworkEGamma.EGammaCommon import *
from DerivationFrameworkMuons.MuonsCommon import *
from AthenaCommon.GlobalFlags import globalflags
DFisMC = (globalflags.DataSource()=='geant4')

# no truth info for data xAODs
if DFisMC:
  from DerivationFrameworkMCTruth.MCTruthCommon import *

from JetRec.JetRecStandard import jtm
from JetRec.JetRecConf import JetAlgorithm
from JetRec.JetRecConf import PseudoJetGetter

# For R=0.6,0.7,0.8 jet
# R=1.0 jet should be done separately
# Track jets should be done separately
def addRscanJets(jetalg,radius,inputtype,sequence,outputlist,addinputs=[]):
  # list of modifiers for topo
  if "topo_rscan" not in jtm.modifiersMap:
    jtm.modifiersMap["topo_rscan"] = list(jtm.modifiersMap["calib_topo_ungroomed"])
    print "List of topo_rscan_mods:", jtm.modifiersMap["topo_rscan"]

  # list of modifiers for truth
  #if jetFlags.useTruth() and ("truth_rscan" not in jtm.modifiersMap):
  #  jtm.modifiersMap["truth_rscan"] = list(jtm.modifiersMap["truth_ungroomed"])
  # print "List of truth_rscan_modes", jtm.modifiersMap["truth_rscan"]

  # naming scheme
  jetname = "{0}{1}{2}Jets".format(jetalg,int(radius*10),inputtype)
  algname = "jetalg"+jetname

  # build jets
  # Mazin - bumping up pt threshold on jets to avoid the 1 particle event problem from subjet finder
  # Qi: still keep low pT threshold for lctopo jets --> can always cut on it offline
  if not hasattr(sequence, algname):
    if inputtype == "Truth":
      addStandardJets(jetalg, radius, "Truth", mods="truth_rscan", ptmin=5000, algseq=sequence, outputGroup=outputlist)
    if inputtype == "TruthWZ":
      addStandardJets(jetalg, radius, "TruthWZ", mods="truth_rscan", ptmin=5000, algseq=sequence, outputGroup=outputlist)
    elif inputtype == "LCTopo":
      addStandardJets(jetalg, radius, "LCTopo", mods="topo_rscan", ghostArea=0.01, ptmin=2000, ptminFilter=5000, calibOpt="aro", algseq=sequence, outputGroup=outputlist)

  return jetname

#====================================================================
# SET UP STREAM   
#====================================================================
streamName = derivationFlags.WriteDAOD_TOPQ1Stream.StreamName
fileName   = buildFileName( derivationFlags.WriteDAOD_TOPQ1Stream )
TOPQ1Stream = MSMgr.NewPoolRootStream( streamName, fileName )
# Accept the most selective kernel (last one in sequence; later in derivation)
TOPQ1Stream.AcceptAlgs(["TOPQ1Kernel"])

#====================================================================
# PDF Weight Metadata  
#====================================================================
if DFisMC:
  from DerivationFrameworkCore.WeightMetadata import *

#====================================================================
# TRIGGER NAVIGATION THINNING   
#====================================================================
from DerivationFrameworkCore.ThinningHelper import ThinningHelper
import DerivationFrameworkTop.TOPQCommonThinning
TOPQ1ThinningHelper = ThinningHelper("TOPQ1ThinningHelper")
TOPQ1ThinningHelper.TriggerChains =  DerivationFrameworkTop.TOPQCommonThinning.TOPQTriggerChains('leptonicTriggers' if globalflags.DataSource()!='geant4' else 'allTriggers')
TOPQ1ThinningHelper.AppendToStream(TOPQ1Stream)

#====================================================================
# SKIMMING TOOLS
#====================================================================
import DerivationFrameworkTop.TOPQCommonSelection
skimmingTools_lep = DerivationFrameworkTop.TOPQCommonSelection.setup_lep('TOPQ1', ToolSvc)
skimmingTools_jet = DerivationFrameworkTop.TOPQCommonSelection.setup_jet('TOPQ1', ToolSvc)

#====================================================================
# THINNING TOOLS
#====================================================================
import DerivationFrameworkTop.TOPQCommonThinning
thinningTools = DerivationFrameworkTop.TOPQCommonThinning.setup('TOPQ1',TOPQ1ThinningHelper.ThinningSvc(), ToolSvc)

#====================================================================
# CREATE THE KERNEL(S) 
#====================================================================
from DerivationFrameworkCore.DerivationFrameworkCoreConf import DerivationFramework__DerivationKernel

# Create the private sequence
TOPQ1Sequence = CfgMgr.AthSequencer("TOPQ1Sequence")

#====================================================================
# Jets for R-scan
#====================================================================
#addRscanJets("AntiKt", 0.8, "LCTopo", TOPQ1Sequence, "TOPQ1")

# ExKt configs
# ExKtJetCollection__FatJetConfigs = {
#                                      "AntiKt8LCTopoJets"         : {"doTrackSubJet": True},#False},
#                                    }

# # build subjets
# ExKtJetCollection__FatJet = ExKtJetCollection__FatJetConfigs.keys()
# ExKtJetCollection__SubJet = []

# for key, config in ExKtJetCollection__FatJetConfigs.items():
#   # N=2 subjets
#   ExKtJetCollection__SubJet += addExKt(TOPQ1Sequence, ToolSvc, [key], nSubJet=2, **config)

#   # N=3 subjets
#   if "RNNCone" not in key:
#     ExKtJetCollection__SubJet += addExKt(TOPQ1Sequence, ToolSvc, [key], nSubJet=3, **config)




# #===================================================================
# # Reset EL in ExKt subjets after all of them are built
# #===================================================================

# TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg("ELReset_AfterSubjetBuild", SGKeys=[name+"Aux." for name in ExKtJetCollection__SubJet])

# #===================================================================
# # Run b-tagging
# #===================================================================

defaultTaggers = ['IP2D', 'IP3D', 'SV0', 'MultiSVbb1', 'MultiSVbb2', 'SV1', 'BasicJetFitter', 'JetFitterTag', 'JetFitterNN', 'GbbNNTag', 'MV2c00', 'MV2c10', 'MV2c20', 'MV2c100', 'MV2m']
specialTaggers = ['ExKtbb_Hbb_MV2Only', 'ExKtbb_Hbb_MV2andJFDRSig', 'ExKtbb_Hbb_MV2andTopos']

# # Retagging to get BTagging_AntiKt4EMPFlow Collection (not present in primary AOD)
from DerivationFrameworkFlavourTag.FlavourTagCommon import *
BTaggingFlags.CalibrationChannelAliases += [ "AntiKt4EMPFlow->AntiKt4EMTopo" ]
BTaggingFlags.CalibrationChannelAliases += ["AntiKt10LCTopoTrimmedPtFrac5SmallR20->AntiKt4EMTopo"]  # enforced by ExKt tagger
# BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in ExKtJetCollection__FatJet ]
# BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in ExKtJetCollection__SubJet ]

# ReTag(['IP2D', 'IP3D', 'SV0',  'MultiSVbb1',  'MultiSVbb2', 'SV1', 'JetFitterNN', 'MV2c00', 'MV2c10', 'MV2c20', 'MV2c100', 'MV2m'],['AntiKt4EMPFlowJets'], TOPQ1Sequence)


# # run b-tagging
# FlavorTagInit( 
#               myTaggers      = defaultTaggers, 
#               JetCollections = ["AntiKt4LCTopoJets", "AntiKt4PV0TrackJets", "AntiKt2PV0TrackJets"]+ExKtJetCollection__SubJet,
#               Sequencer      = TOPQ1Sequence,
#              )

# FlavorTagInit( 
#               myTaggers      = defaultTaggers,
#               JetCollections = ExKtJetCollection__FatJet,
#               Sequencer      = TOPQ1Sequence,
#              )
# #ReTag(defaultTaggers,ExKtJetCollection__SubJet+ExKtJetCollection__FatJet,TOPQ1Sequence)#DerivationFrameworkJob)
# #===================================================================
# # Reset EL in ExKt subjets after b-tagging
# #===================================================================

# TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg("ELReset_AfterBtag", SGKeys=[name+"Aux." for name in ExKtJetCollection__SubJet])

# if not hasattr(TOPQ1Sequence,"ELReset"):
#   TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg( "ELReset" )

# First skim on leptons
TOPQ1Sequence += CfgMgr.DerivationFramework__DerivationKernel("TOPQ1SkimmingKernel_lep", SkimmingTools = skimmingTools_lep)

# Then build fat/trimmed jets
import DerivationFrameworkTop.TOPQCommonJets
addDefaultTrimmedJets(TOPQ1Sequence,'TOPQ1')

#Then apply jet calibration
DerivationFrameworkTop.TOPQCommonJets.applyTOPQJetCalibration("AntiKt4EMTopo",DerivationFrameworkJob)
DerivationFrameworkTop.TOPQCommonJets.applyTOPQJetCalibration("AntiKt10LCTopoTrimmedPtFrac5SmallR20",TOPQ1Sequence)

# Then skim on the newly created fat jets and calibrated jets
TOPQ1Sequence += CfgMgr.DerivationFramework__DerivationKernel("TOPQ1SkimmingKernel_jet", SkimmingTools = skimmingTools_jet)

# Then apply the TruthWZ fix
if DFisMC:
  replaceBuggyAntiKt4TruthWZJets(TOPQ1Sequence,'TOPQ1')

# Then apply truth tools in the form of aumentation
if DFisMC:
  from DerivationFrameworkTop.TOPQCommonTruthTools import *
  TOPQ1Sequence += TOPQCommonTruthKernel

DerivationFrameworkTop.TOPQCommonJets.addMSVVariables("AntiKt4EMTopoJets", TOPQ1Sequence, ToolSvc)

ToolSvc += CfgMgr.JetReclusteringTool("TOPQ1ReclusteringTool",InputJetContainer="AntiKt4EMTopoJets", OutputJetContainer="AntiKt8LCTopoJets")
ToolSvc.TOPQ1ReclusteringTool.ReclusterRadius = 0.8
ToolSvc.TOPQ1ReclusteringTool.InputJetPtMin = -1
ToolSvc.TOPQ1ReclusteringTool.RCJetPtMin = -1
ToolSvc.TOPQ1ReclusteringTool.RCJetPtFrac = -1
ToolSvc.TOPQ1ReclusteringTool.DoArea = True
ToolSvc.TOPQ1ReclusteringTool.GhostTracksInputContainer = "InDetTrackParticles"
TOPQ1Sequence += CfgMgr.AthJetReclusteringAlgo("JetRecAlgo", JetReclusteringTool = ToolSvc.TOPQ1ReclusteringTool)
if "recluster" not in jtm.modifiersMap:
    jtm.modifiersMap["recluster"] = list(jtm.modifiersMap["emtopo"])
    #jtm.modifiersMap["recluster"].remove('calib')
    #jtm.modifiersMap["recluster"].remove('jetfilter')
    print "List of recluster_mods:", jtm.modifiersMap["recluster"]

# JetReclusterer = jtm.addJetReclusterer("AntiKt8LCTopoJets", "AntiKt", 0.8, "AntiKt4EMTopoJets",[], consumers =None, ivtx =None, ghostArea=0.01)
# ToolSvc += JetReclusterer
# TOPQ1Sequence += JetAlgorithm( name = "JetAlgorithm_RC", Tools = [JetReclusterer])

ExKtJetCollection__FatJetConfigs = {
                                     "AntiKt8LCTopoJets"         : {"doTrackSubJet": True},#False},
                                   }

# build subjets
ExKtJetCollection__FatJet = ExKtJetCollection__FatJetConfigs.keys()
ExKtJetCollection__SubJet = []

for key, config in ExKtJetCollection__FatJetConfigs.items():
  # N=2 subjets
  ExKtJetCollection__SubJet += addExKt(TOPQ1Sequence, ToolSvc, [key], nSubJet=2, **config)

  # N=3 subjets
  if "RNNCone" not in key:
    ExKtJetCollection__SubJet += addExKt(TOPQ1Sequence, ToolSvc, [key], nSubJet=3, **config)




#===================================================================
# Reset EL in ExKt subjets after all of them are built
#===================================================================

TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg("ELReset_AfterSubjetBuild", SGKeys=[name+"Aux." for name in ExKtJetCollection__SubJet])

#===================================================================
# Run b-tagging
#===================================================================

#defaultTaggers = ['IP2D', 'IP3D', 'SV0', 'MultiSVbb1', 'MultiSVbb2', 'SV1', 'BasicJetFitter', 'JetFitterTag', 'JetFitterNN', 'GbbNNTag', 'MV2c00', 'MV2c10', 'MV2c20', 'MV2c100', 'MV2m']
#specialTaggers = ['ExKtbb_Hbb_MV2Only', 'ExKtbb_Hbb_MV2andJFDRSig', 'ExKtbb_Hbb_MV2andTopos']

# Retagging to get BTagging_AntiKt4EMPFlow Collection (not present in primary AOD)
#from DerivationFrameworkFlavourTag.FlavourTagCommon import *
#BTaggingFlags.CalibrationChannelAliases += [ "AntiKt4EMPFlow->AntiKt4EMTopo" ]
#BTaggingFlags.CalibrationChannelAliases += ["AntiKt10LCTopoTrimmedPtFrac5SmallR20->AntiKt4EMTopo"]  # enforced by ExKt tagger
BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in ExKtJetCollection__FatJet ]
BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in ExKtJetCollection__SubJet ]

ReTag(['IP2D', 'IP3D', 'SV0',  'MultiSVbb1',  'MultiSVbb2', 'SV1', 'JetFitterNN', 'MV2c00', 'MV2c10', 'MV2c20', 'MV2c100', 'MV2m'],['AntiKt4EMPFlowJets'], TOPQ1Sequence)

#if not hasattr(TOPQ1Sequence,"ELReset"):
#  TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg( "ELReset" )

# run b-tagging
FlavorTagInit( 
              myTaggers      = defaultTaggers, 
              JetCollections = ["AntiKt4LCTopoJets", "AntiKt4PV0TrackJets", "AntiKt2PV0TrackJets"]+ExKtJetCollection__SubJet,
              Sequencer      = TOPQ1Sequence,
             )

FlavorTagInit( 
              myTaggers      = defaultTaggers,
              JetCollections = ExKtJetCollection__FatJet,
              Sequencer      = TOPQ1Sequence,
             )
#ReTag(defaultTaggers,ExKtJetCollection__SubJet+ExKtJetCollection__FatJet,TOPQ1Sequence)#DerivationFrameworkJob)
#===================================================================
# Reset EL in ExKt subjets after b-tagging
#===================================================================

TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg("ELReset_AfterBtag", SGKeys=[name+"Aux." for name in ExKtJetCollection__SubJet])

if not hasattr(TOPQ1Sequence,"ELReset"):
  TOPQ1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg( "ELReset" )

from DerivationFrameworkTop.TOPQ1AugTools import *
TOPQ1Sequence += TOPQ1ExKtCommonTruthKernel

# Then apply thinning
TOPQ1Sequence += CfgMgr.DerivationFramework__DerivationKernel("TOPQ1Kernel", ThinningTools = thinningTools)

# JetTagNonPromptLepton decorations
import JetTagNonPromptLepton.JetTagNonPromptLeptonConfig as Config
TOPQ1Sequence += Config.GetDecoratePromptLeptonAlgs()

# from DerivationFrameworkTop.TOPQ1AugTools import *
# TOPQ1Sequence += TOPQ1ExKtCommonTruthKernel

# Finally, add the private sequence to the main job
DerivationFrameworkJob += TOPQ1Sequence

#====================================================================
# SLIMMING
#====================================================================
import DerivationFrameworkTop.TOPQCommonSlimming
DerivationFrameworkTop.TOPQCommonSlimming.setup('TOPQ1', TOPQ1Stream)

# ====================================================================
# Add the containers to the output stream - slimming done here
# ====================================================================
from DerivationFrameworkCore.SlimmingHelper import SlimmingHelper
TOPQ1SlimmingHelper = SlimmingHelper("TOPQ1SlimmingHelper")


TOPQ1SlimmingHelper.AppendToDictionary["AntiKt8LCTopoJets"] = "xAOD::JetContainer"
TOPQ1SlimmingHelper.AppendToDictionary["AntiKt8LCTopoJets"+"Aux"] = "xAOD::JetAuxContainer"
#TOPQ1SlimmingHelper.AppendToDictionary["ReclusteredAntiKt8LCTopoJets"] = "xAOD::JetContainer"
#TOPQ1SlimmingHelper.AppendToDictionary["ReclusteredAntiKt8LCTopoJets"+"Aux"] = "xAOD::JetAuxContainer"
#TOPQ1SlimmingHelper.AppendToDictionary["BTagging_AntiKt8LCTopoExKt2Sub"] = "xAOD::BTaggingContainer"
#TOPQ1SlimmingHelper.AppendToDictionary["BTagging_AntiKt8LCTopoExKt2SubAux"] = "xAOD::BTaggingAuxContainer"
TOPQ1SlimmingHelper.ExtraVariables = ["AntiKt8LCTopoJets.pt.eta.phi.m.ExKtbb_MaxMV2c10.ExKtbb_MinMV2c10.ExKtbb_SubjetDR.ExKtbb_SubjetPtAsym.ExKt3bb_MaxMV2c10.ExKt3bb_MinMV2c10.ExKt3bb_SubjetDR.ExKt3bb_SubjetPtAsym.GhostBHadronsFinalCount.JetEMScaleMomentum_pt.JetEMScaleMomentum_eta.JetEMScaleMomentum_phi.JetEMScaleMomentum_m.JetConstitScaleMomentum_pt.JetConstitScaleMomentum_eta.JetConstitScaleMomentum_phi.JetConstitScaleMomentum_m.InputType.SizeParameter.AlgorithmType.IsoDelta3SumPt.IsoDelta2SumPt.JetGhostArea.ActiveArea4.ActiveArea4vec_pt.ActiveArea4vec_eta.ActiveArea4vec_phi.ActiveArea4vec_m.JetOriginConstitScaleMomentum_pt.JetOriginConstitScaleMomentum_eta.JetOriginConstitScaleMomentum_phi.JetOriginConstitScaleMomentum_m.ECF1.ECF2.ECF3.Width.Split12.Split23.Split34.KtDr.Aplanarity.Sphericity.Dip12.Dip13.Dip23.DipExcl12.Tau1.Tau2.Tau3.Tau1_wta.Tau2_wta.Tau3_wta.C2.D2"]

#TOPQ1SlimmingHelper.AllVariables = ["BTagging_AntiKt8LCTopoExKt2Sub","BTagging_AntiKt8LCTopoExKt2SubAux"]
#TOPQ1SlimmingHelper.AllVariables = ["ReclusteredAntiKt8LCTopoJets","ReclusteredAntiKt8LCTopoJetsAux"]
TOPQ1SlimmingHelper.AppendContentToStream(TOPQ1Stream)

