#====================================================================
# SJET1.py
# reductionConf flag SJET1 in Reco_tf.py   
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

if DFisMC:
  from DerivationFrameworkMCTruth.MCTruthCommon import *

from JetRec.JetRecStandard import jtm
from JetRec.JetRecConf import JetAlgorithm
from JetRec.JetRecConf import PseudoJetGetter

#####################################################################
# Utils Functions
#####################################################################

# For R=0.6,0.7,0.8 jet
# R=1.0 jet should be done separately
# Track jets should be done separately
def addRscanJets(jetalg,radius,inputtype,sequence,outputlist,addinputs=[]):
  # list of modifiers for topo
  if "topo_rscan" not in jtm.modifiersMap:
    jtm.modifiersMap["topo_rscan"] = list(jtm.modifiersMap["calib_topo_ungroomed"])
    print "List of topo_rscan_mods:", jtm.modifiersMap["topo_rscan"]

  # list of modifiers for truth
  if jetFlags.useTruth() and ("truth_rscan" not in jtm.modifiersMap):
    jtm.modifiersMap["truth_rscan"] = list(jtm.modifiersMap["truth_ungroomed"])
    print "List of truth_rscan_modes", jtm.modifiersMap["truth_rscan"]

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
      # TODO: confirm the pt threshold, and calibOpt "aro"
      # addStandardJets(jetalg, radius, "LCTopo", mods="topo_rscan", ghostArea=0.01, ptmin=30000, ptminFilter=7000, calibOpt="aro", algseq=sequence, outputGroup=outputlist)
      addStandardJets(jetalg, radius, "LCTopo", mods="topo_rscan", ghostArea=0.01, ptmin=2000, ptminFilter=5000, calibOpt="aro", algseq=sequence, outputGroup=outputlist)

  return jetname

# For track jets
def addTrackJets(radius, sequence):
  jetname = "AntiKt%dPV0TrackJets" % (radius*10)
  algname = "jfind_akt%dpv0trackjet" % (radius*10)

  if not hasattr(sequence, algname):
    jfind_aktXtrackjet = jtm.addJetFinder(jetname, "AntiKt", radius, "pv0track", ghostArea=0.00, ptmin=2000, ptminFilter=5000, calibOpt="none")
    jetalg_aktXtrackjet = JetAlgorithm(algname, Tools = [jfind_aktXtrackjet])
    sequence += jetalg_aktXtrackjet

  return jetname

#####################################################################
# Configurations / Initializations
#####################################################################

# TODO: seems redundant
doRetag = True

#====================================================================
# SET UP STREAM   
#====================================================================
streamName = derivationFlags.WriteDAOD_SJET1Stream.StreamName
fileName   = buildFileName( derivationFlags.WriteDAOD_SJET1Stream )
SJET1Stream = MSMgr.NewPoolRootStream( streamName, fileName )
# Accept the most selective kernel (last one in sequence; later in derivation)
SJET1Stream.AcceptAlgs(["SJET1Kernel"])

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
TOPQ1ThinningHelper.TriggerChains =  DerivationFrameworkTop.TOPQCommonThinning.TOPQTriggerChains()
TOPQ1ThinningHelper.AppendToStream(SJET1Stream)

#====================================================================
# SKIMMING TOOLS
#====================================================================
import DerivationFrameworkTop.TOPQCommonSelection
skimmingTools_lep = DerivationFrameworkTop.TOPQCommonSelection.setup_lep('TOPQ1', ToolSvc)
skimmingTools_jet = DerivationFrameworkTop.TOPQCommonSelection.setup_jet('SJET1', ToolSvc)

#====================================================================
# THINNING TOOLS
#====================================================================
# No thinning at all
# import DerivationFrameworkTop.TOPQCommonThinning
# thinningTools = DerivationFrameworkTop.TOPQCommonThinning.setup('TOPQ1',TOPQ1ThinningHelper.ThinningSvc(), ToolSvc)
thinningTools = []

#====================================================================
# CREATE THE KERNEL(S)
#====================================================================
from DerivationFrameworkCore.DerivationFrameworkCoreConf import DerivationFramework__DerivationKernel

#=======================================
# CREATE PRIVATE SEQUENCE
#=======================================

SJET1Sequence = CfgMgr.AthSequencer("SJET1Sequence")

#====================================================================
# Build VR Track Jets
#====================================================================

VRJetList = []

# only add one nominal VR here
jfind_vr = jtm.addJetFinder("AntiKtVR30Rmax4Rmin02PV0TrackJets", "AntiKt", 0.4, "pv0track", "pv0track",
                            ghostArea = 0 , ptmin = 2000, ptminFilter = 7000,
                            variableRMinRadius = 0.02, variableRMassScale = 30000, calibOpt = "none")
jalg_vr = JetAlgorithm("jfind_AntiKtVR30Rmax4Rmin02PV0TrackJets", Tools = [jfind_vr])
SJET1Sequence += jalg_vr

jtm += PseudoJetGetter(
                        "gvr30rmax4rmin02trackget",
                        InputContainer     = jetFlags.containerNamePrefix() + "AntiKtVR30Rmax4Rmin02PV0TrackJets",
                        Label              = "GhostVR30Rmax4Rmin02PV0TrackJet",
                        OutputContainer    = "PseudoJetGhostVR30Rmax4Rmin02PV0TrackJet",
                        SkipNegativeEnergy = True,
                        GhostScale         = 1.e-20,
                      )

jtm.gettersMap["lctopo"]   += [jtm.gvr30rmax4rmin02trackget]
jtm.gettersMap["emtopo"]   += [jtm.gvr30rmax4rmin02trackget]
jtm.gettersMap["empflow"]  += [jtm.gvr30rmax4rmin02trackget]
jtm.gettersMap["emcpflow"] += [jtm.gvr30rmax4rmin02trackget]
jtm.gettersMap["track"]    += [jtm.gvr30rmax4rmin02trackget]
jtm.gettersMap["ztrack"]   += [jtm.gvr30rmax4rmin02trackget]
jtm.gettersMap["pv0track"] += [jtm.gvr30rmax4rmin02trackget]

VRJetList += ["AntiKtVR30Rmax4Rmin02PV0TrackJets"]

#====================================================================
# Jets for R-scan
#====================================================================

if jetFlags.useTruth():
  addRscanJets("AntiKt", 0.6, "Truth", SJET1Sequence, "SJET1")
  addRscanJets("AntiKt", 0.7, "Truth", SJET1Sequence, "SJET1")
  addRscanJets("AntiKt", 0.8, "Truth", SJET1Sequence, "SJET1")

addRscanJets("AntiKt", 0.6, "LCTopo", SJET1Sequence, "SJET1")
addRscanJets("AntiKt", 0.7, "LCTopo", SJET1Sequence, "SJET1")
addRscanJets("AntiKt", 0.8, "LCTopo", SJET1Sequence, "SJET1")

#====================================================================
# Build new AntiKt10 LCTopo Jets with lower threshold
#====================================================================

# TODO: check if this is good
if jetFlags.useTruth():
  jfind_largefr10_truth = jtm.addJetFinder("AntiKt10TruthLowPtJets", "AntiKt", 1.0, "truth", "truth_ungroomed", ghostArea = 0.01, ptmin = 2000, ptminFilter = 5000, calibOpt = "none")
  jetalg_largefr10_truth = JetAlgorithm("jfind_largefr10_truth", Tools = [jfind_largefr10_truth])
  SJET1Sequence += jetalg_largefr10_truth

jfind_largefr10_lctopo = jtm.addJetFinder("AntiKt10LCTopoLowPtJets", "AntiKt", 1.0, "lctopo", "calib_topo_ungroomed", ghostArea = 0.01, ptmin = 2000, ptminFilter = 5000, calibOpt = "none")
jetalg_largefr10_lctopo = JetAlgorithm("jfind_largefr10_lctopo", Tools = [jfind_largefr10_lctopo])
SJET1Sequence += jetalg_largefr10_lctopo


#====================================================================
# Build Track Jets
#====================================================================

addTrackJets(0.6, SJET1Sequence)
addTrackJets(0.7, SJET1Sequence)
addTrackJets(0.8, SJET1Sequence)
addTrackJets(1.0, SJET1Sequence)

#===================================================================
# Build ExKt and ExCoM subjet collections
#===================================================================

# Jet Copy
addCopyJet(SJET1Sequence, ToolSvc, "AntiKt6LCTopoJets", "NewAntiKt6LCTopoJets")
addCopyJet(SJET1Sequence, ToolSvc, "AntiKt7LCTopoJets", "NewAntiKt7LCTopoJets")
addCopyJet(SJET1Sequence, ToolSvc, "AntiKt8LCTopoJets", "NewAntiKt8LCTopoJets")
addCopyJet(SJET1Sequence, ToolSvc, "AntiKt10LCTopoLowPtJets", "NewAntiKt10LCTopoLowPtJets")

# ExKt configs
ExKtJetCollection__FatJetConfigs = {
                                     # calo-jet
                                     "AntiKt6LCTopoJets"         : {"doTrackSubJet": False},
                                     "NewAntiKt6LCTopoJets"      : {"doTrackSubJet": True},
                                     "AntiKt7LCTopoJets"         : {"doTrackSubJet": False},
                                     "NewAntiKt7LCTopoJets"      : {"doTrackSubJet": True},
                                     "AntiKt8LCTopoJets"         : {"doTrackSubJet": False},
                                     "NewAntiKt8LCTopoJets"      : {"doTrackSubJet": True},
                                     "AntiKt10LCTopoLowPtJets"   : {"doTrackSubJet": False},
                                     "NewAntiKt10LCTopoLowPtJets": {"doTrackSubJet": True},

                                     # track jets
                                     "AntiKt6PV0TrackJets" : {"doTrackSubJet": False},
                                     "AntiKt7PV0TrackJets" : {"doTrackSubJet": False},
                                     "AntiKt8PV0TrackJets" : {"doTrackSubJet": False},
                                     "AntiKt10PV0TrackJets": {"doTrackSubJet": False},
                                   }

# build subjets
ExKtJetCollection__FatJet = ExKtJetCollection__FatJetConfigs.keys()
ExKtJetCollection__SubJet = []
for key, config in ExKtJetCollection__FatJetConfigs.items():
  ExKtJetCollection__SubJet += addExKt(SJET1Sequence, ToolSvc, [key], **config)

#===================================================================
# Transfer the Links to minimize output jet collections
#===================================================================

jetassoctool = getJetExternalAssocTool("AntiKt6LCTopo", "NewAntiKt6LCTopo", MomentPrefix="", ListOfOldLinkNames=["ExKt2SubJets"], ListOfNewLinkNames=["ExKt2TrackSubJets"])
applyJetAugmentation('AntiKt6LCTopo', 'AugmentationAlg_LinkTransfer_AntiKt6LCTopo', SJET1Sequence, jetassoctool)

jetassoctool = getJetExternalAssocTool("AntiKt7LCTopo", "NewAntiKt7LCTopo", MomentPrefix="", ListOfOldLinkNames=["ExKt2SubJets"], ListOfNewLinkNames=["ExKt2TrackSubJets"])
applyJetAugmentation('AntiKt7LCTopo', 'AugmentationAlg_LinkTransfer_AntiKt7LCTopo', SJET1Sequence, jetassoctool)

jetassoctool = getJetExternalAssocTool("AntiKt8LCTopo", "NewAntiKt8LCTopo", MomentPrefix="", ListOfOldLinkNames=["ExKt2SubJets"], ListOfNewLinkNames=["ExKt2TrackSubJets"])
applyJetAugmentation('AntiKt8LCTopo', 'AugmentationAlg_LinkTransfer_AntiKt8LCTopo', SJET1Sequence, jetassoctool)

jetassoctool = getJetExternalAssocTool("AntiKt10LCTopoLowPt", "NewAntiKt10LCTopoLowPt", MomentPrefix="", ListOfOldLinkNames=["ExKt2SubJets"], ListOfNewLinkNames=["ExKt2TrackSubJets"])
applyJetAugmentation('AntiKt10LCTopoLowPt', 'AugmentationAlg_LinkTransfer_AntiKt10LCTopoLowPt', SJET1Sequence, jetassoctool)

#===================================================================
# Reset EL in ExKt subjets after all of them are built
#===================================================================

SJET1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg("ELReset_AfterSubjetBuild", SGKeys=[name+"Aux." for name in ExKtJetCollection__SubJet])

#===================================================================
# Run b-tagging
#===================================================================

defaultTaggers = ['IP2D', 'IP3D', 'SV0', 'MultiSVbb1', 'MultiSVbb2', 'SV1', 'BasicJetFitter', 'JetFitterTag', 'JetFitterNN', 'GbbNNTag', 'MV2c00', 'MV2c10', 'MV2c20', 'MV2c100', 'MV2m']
specialTaggers = ['ExKtbb_Hbb_MV2Only', 'ExKtbb_Hbb_MV2andJFDRSig', 'ExKtbb_Hbb_MV2andTopos']

# setup alias
from BTagging.BTaggingFlags import BTaggingFlags
BTaggingFlags.CalibrationChannelAliases += ["AntiKt10LCTopoTrimmedPtFrac5SmallR20->AntiKt4EMTopo"]  # enforced by ExKt tagger
BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in ExKtJetCollection__FatJet ]
BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in ExKtJetCollection__SubJet ]
BTaggingFlags.CalibrationChannelAliases += [ jetname[:-4].replace("PV0", "")+"->AntiKt4EMTopo" for jetname in VRJetList ]

# run b-tagging
from DerivationFrameworkFlavourTag.FlavourTagCommon import FlavorTagInit
FlavorTagInit( 
              myTaggers      = defaultTaggers, 
              JetCollections = ["AntiKt4LCTopoJets", "AntiKt4PV0TrackJets", "AntiKt2PV0TrackJets"]+VRJetList+ExKtJetCollection__SubJet,
              Sequencer      = SJET1Sequence,
             )

FlavorTagInit( 
              myTaggers      = defaultTaggers+specialTaggers,
              JetCollections = ExKtJetCollection__FatJet,
              Sequencer      = SJET1Sequence,
             )

#===================================================================
# Reset EL in ExKt subjets after b-tagging
#===================================================================

SJET1Sequence += CfgMgr.xAODMaker__ElementLinkResetAlg("ELReset_AfterBtag", SGKeys=[name+"Aux." for name in ExKtJetCollection__SubJet])

#===================================================================
# SKIMMING TOOLS
#===================================================================

# Skim on leptons
SJET1Sequence += CfgMgr.DerivationFramework__DerivationKernel("TOPQ1SkimmingKernel_lep", SkimmingTools = skimmingTools_lep)
SJET1Sequence += CfgMgr.DerivationFramework__DerivationKernel("TOPQ1SkimmingKernel_jet", SkimmingTools = skimmingTools_jet)

if DFisMC:
  from DerivationFrameworkTop.TOPQCommonTruthTools import *
  SJET1Sequence += TOPQCommonTruthKernel

SJET1Sequence += CfgMgr.DerivationFramework__DerivationKernel("SJET1Kernel", ThinningTools = thinningTools)
# JetTagNonPromptLepton decorations
import JetTagNonPromptLepton.JetTagNonPromptLeptonConfig as Config
SJET1Sequence += Config.DecoratePromptLepton("Electrons", "AntiKt4PV0TrackJets")
SJET1Sequence += Config.DecoratePromptLepton("Muons",     "AntiKt4PV0TrackJets")

#Mazin - private little aug sequence to do a few checks, fills some empty things...
#from DerivationFrameworkTop.SJET1AugTools import *
#SJET1Sequence += SJET1CommonTruthKernel
# Finally, add the private sequence to the main job
DerivationFrameworkJob += SJET1Sequence

#====================================================================
# SLIMMING
#====================================================================
import DerivationFrameworkTop.TOPQCommonSlimming
DerivationFrameworkTop.TOPQCommonSlimming.setup('SJET1', SJET1Stream)
# ====================================================================
# Add the containers to the output stream - slimming done here
# ====================================================================
from DerivationFrameworkCore.SlimmingHelper import SlimmingHelper
SJET1SlimmingHelper = SlimmingHelper("SJET1SlimmingHelper")

# declare all collections that are NOT in input files (i.e. built on-the-fly)
SJET1SlimmingHelper.AppendToDictionary = {
                                           # add something exceptional here
                                         }
for JetCollectionName in VRJetList+ExKtJetCollection__FatJet+ExKtJetCollection__SubJet:
  JetCollectionBtagName = JetCollectionName[:-4].replace("PV0", "")

  SJET1SlimmingHelper.AppendToDictionary[JetCollectionName] = "xAOD::JetContainer"
  SJET1SlimmingHelper.AppendToDictionary[JetCollectionName+"Aux"] = "xAOD::JetAuxContainer"

  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionBtagName] = "xAOD::BTaggingContainer"
  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionBtagName+"Aux"] = "xAOD::BTaggingAuxContainer"

  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionBtagName+"SecVtx"] = "xAOD::VertexContainer"
  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionBtagName+"SecVtxAux"] = "xAOD::VertexAuxContainer"

  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionBtagName+"JFVtx"] = "xAOD::BTagVertexContainer"
  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionBtagName+"JFVtxAux"] = "xAOD::BTagVertexAuxContainer"

# smart collection
SJET1SlimmingHelper.SmartCollections = [
                                        "AntiKt4EMTopoJets",
                                        "BTagging_AntiKt4EMTopo",
                                        "Electrons",
                                        "Muons",
                                        "Photons",
                                        "MET_Reference_AntiKt4EMTopo"
                                       ]

# collection that we want all variables
SJET1SlimmingHelper.AllVariables = [
                                    "TruthEvents", 
                                    "TruthParticles",
                                    "TruthVertices",

                                    "AntiKt2PV0TrackJets",
                                    "BTagging_AntiKt2Track",
                                    "BTagging_AntiKt2TrackJFVtx",
                                    "BTagging_AntiKt2TrackSecVtx",

                                    "MET_RefFinal",
                                    "InDetTrackParticles",
                                    "PrimaryVertices",
                                    "CaloCalTopoClusters",
                                   ]
for JetCollectionName in VRJetList+ExKtJetCollection__FatJet+ExKtJetCollection__SubJet:
  JetCollectionBtagName = JetCollectionName[:-4].replace("PV0", "")

  SJET1SlimmingHelper.AllVariables += [
                                        JetCollectionName,
                                        "BTagging_"+JetCollectionBtagName,
                                        "BTagging_"+JetCollectionBtagName+"JFVtx",
                                        "BTagging_"+JetCollectionBtagName+"SecVtx",
                                      ]

# Trigger content
SJET1SlimmingHelper.IncludeJetTriggerContent = True

SJET1SlimmingHelper.AppendContentToStream(SJET1Stream)
SJET1Stream.RemoveItem("xAOD::TrigNavigation#*")
SJET1Stream.RemoveItem("xAOD::TrigNavigationAuxInfo#*")
