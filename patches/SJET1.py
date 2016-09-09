#====================================================================
# SJET1.py
# reductionConf flag SJET1 in Reco_tf.py   
#====================================================================

from DerivationFrameworkCore.DerivationFrameworkMaster import *
from DerivationFrameworkInDet.InDetCommon import *
from DerivationFrameworkJetEtMiss.JetCommon import *
from DerivationFrameworkJetEtMiss.ExtendedJetCommon import *
#from DerivationFrameworkJetEtMiss.METCommon import *
#from DerivationFrameworkJetEtMiss.JetCommon import *
#from DerivationFrameworkJetEtMiss.ExtendedJetCommon import * 
from DerivationFrameworkJetEtMiss.METCommon import *
from DerivationFrameworkEGamma.EGammaCommon import *
from DerivationFrameworkMuons.MuonsCommon import *
from AthenaCommon.GlobalFlags import globalflags
DFisMC = (globalflags.DataSource()=='geant4')


if DFisMC:
  from DerivationFrameworkMCTruth.MCTruthCommon import *
doRetag = True
JetCollections = [
  'AntiKt6LCTopoJets', 
  'AntiKt7LCTopoJets', 
  'AntiKt8LCTopoJets',

  'AntiKt6TrackJets',
  'AntiKt7TrackJets',
  'AntiKt8TrackJets',
  ]

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
# Jets for R-scan
#====================================================================
from JetRec.JetRecStandard import jtm
from JetRec.JetRecConf import JetAlgorithm


topo_rscan_mods = jtm.modifiersMap["calib_topo_ungroomed"]
print topo_rscan_mods
if jetFlags.useTruth():
    truth_rscan_mods = jtm.modifiersMap["truth_ungroomed"]
    print truth_rscan_mods
skipmods = ["ktdr","nsubjettiness","ktsplitter","angularity","dipolarity","planarflow","ktmassdrop","encorr","comshapes"]
for mod in skipmods:
    print "remove", mod
    #topo_rscan_mods.remove(jtm.tools[mod])
    #if jetFlags.useTruth(): truth_rscan_mods.remove(jtm.tools[mod])
jtm.modifiersMap["topo_rscan"] = topo_rscan_mods
if jetFlags.useTruth(): jtm.modifiersMap["truth_rscan"] = truth_rscan_mods

def addRscanJets(jetalg,radius,inputtype,sequence,outputlist):
    jetname = "{0}{1}{2}Jets".format(jetalg,int(radius*10),inputtype)
    algname = "jetalg"+jetname

    ######## Mazin - bumping up pt threshold on jets to avoid the 1 particle event problem from subjet finder
    if not hasattr(sequence,algname):
        if inputtype == "Truth":
            addStandardJets(jetalg, radius, "Truth", mods="truth_rscan", ptmin=5000, algseq=sequence, outputGroup=outputlist)
        if inputtype == "TruthWZ":
            addStandardJets(jetalg, radius, "TruthWZ", mods="truth_rscan", ptmin=5000, algseq=sequence, outputGroup=outputlist)
        elif inputtype == "LCTopo":
            addStandardJets(jetalg, radius, "LCTopo", mods="topo_rscan",
                            ghostArea=0.01, ptmin=30000, ptminFilter=7000, calibOpt="aro", algseq=sequence, outputGroup=outputlist)

OutputJets["SJET1"] = ["AntiKt4TruthJets","AntiKt4EMTopoJets","AntiKt4LCTopoJets"]
addDefaultTrimmedJets(SJET1Sequence,"SJET1")
#if jetFlags.useTruth:
#    replaceBuggyAntiKt4TruthWZJets(SJET1Sequence,"SJET1")
for radius in [0.6,0.7,0.8]:#[0.2, 0.3, 0.5, 0.6, 0.7, 0.8]:
    if jetFlags.useTruth:
        addRscanJets("AntiKt",radius,"Truth",SJET1Sequence,"SJET1")
        #addRscanJets("AntiKt",radius,"TruthWZ",SJET1Sequence,"SJET1")
    addRscanJets("AntiKt",radius,"LCTopo",SJET1Sequence,"SJET1")

# build track jets for b-tagging
for radius in [0.6, 0.7, 0.8]:
  jfind_aktXtrackjet = jtm.addJetFinder("AntiKt%dTrackJets" % (radius*10), "AntiKt", radius, "pv0track", ghostArea=0.00, ptmin=5000, ptminFilter=5000, calibOpt="none")
  jetalg_aktXtrackjet = JetAlgorithm("jfind_akt%dtrackjet" % (radius*10), Tools = [jfind_aktXtrackjet])

  SJET1Sequence += jetalg_aktXtrackjet


#BTaggingFlags.CalibrationTag = 'BTagCalibRUN12-08-18'

#Btag RScan Jets
from DerivationFrameworkFlavourTag.FlavourTagCommon import *
defaultTaggers = ['IP2D', 'IP3D', 'SV0', 'MultiSVbb1', 'MultiSVbb2', 'SV1', 'BasicJetFitter', 'JetFitterTag', 'GbbNNTag', 'MV2c00', 'MV2c10', 'MV2c20', 'MV2c100', 'MV2m']
specialTaggers = ['ExKtbb_Hbb_MV2Only', 'ExKtbb_Hbb_MV2andJFDRSig', 'ExKtbb_Hbb_MV2andTopos']

BTaggingFlags.writeSecondaryVertices=True

BTaggingFlags.CalibrationChannelAliases += ["AntiKt10LCTopoTrimmedPtFrac5SmallR20->AntiKt10LCTopo,AntiKt6LCTopo,AntiKt6TopoEM,AntiKt4LCTopo,AntiKt4TopoEM,AntiKt4EMTopo"]

for JetCollection in JetCollections:
  print JetCollection[:-4]+"->AntiKt4EMTopo"
  BTaggingFlags.CalibrationChannelAliases += [JetCollection[:-4]+"->AntiKt4EMTopo"]


def buildExclusiveSubjets(JetCollectionName, nsubjet, ToolSvc = ToolSvc):
    from JetSubStructureMomentTools.JetSubStructureMomentToolsConf import SubjetFinderTool
    from JetSubStructureMomentTools.JetSubStructureMomentToolsConf import SubjetRecorderTool

    ExGhostLabels = []
    if "TrackJets" in JetCollectionName:
      ExGhostLabels = ["GhostBHadronsFinal", "GhostBHadronsInitial", "GhostBQuarksFinal", "GhostCHadronsFinal", "GhostCHadronsInitial", "GhostCQuarksFinal", "GhostHBosons", "GhostPartons", "GhostTQuarksFinal", "GhostTausFinal", "GhostTruth"]
    else:
      ExGhostLabels = ["GhostBHadronsFinal", "GhostBHadronsInitial", "GhostBQuarksFinal", "GhostCHadronsFinal", "GhostCHadronsInitial", "GhostCQuarksFinal", "GhostHBosons", "GhostPartons", "GhostTQuarksFinal", "GhostTausFinal", "GhostTrack", "GhostTruth"]


    SubjetContainerName = "%sExKt%iSubJets" % (JetCollectionName.replace("Jets", ""), nsubjet)

    subjetrecorder = SubjetRecorderTool("subjetrecorder%i_%s" % (nsubjet, JetCollectionName))
    ToolSvc += subjetrecorder

    subjetlabel = "ExKt%iSubJets" % (nsubjet)

    subjetrecorder.SubjetLabel = subjetlabel
    subjetrecorder.SubjetContainerName = SubjetContainerName

    from JetTagTools.JetTagToolsConf import Analysis__ExKtbbTagTool
    ExKtbbTagToolInstance = Analysis__ExKtbbTagTool(
      name = "ExKtbbTagTool%i_%s" % (nsubjet, JetCollectionName),
      JetAlgorithm = "Kt",
      JetRadius = 10.0,
      PtMin = 0,   # considering this is low pT case, we decide to move any selection on subjets to offline level
      ExclusiveNJets = 2,
      InputJetContainerName = JetCollectionName,
      SubjetRecorder = subjetrecorder,
      SubjetLabel = subjetlabel,
      SubjetContainerName = SubjetContainerName,
      SubjetAlgorithm_BTAG = "AntiKt",
      SubjetRadius_BTAG = 0.4,
      SubjetBoostConstituent = False,
      GhostLabels = ",".join(ExGhostLabels)
    )
    ToolSvc += ExKtbbTagToolInstance

    return (ExKtbbTagToolInstance, SubjetContainerName)

# build exkt subjets here
JetCollectionExKtSubJetList = []
for JetCollectionExKt in JetCollections:
  # build ExKtbbTagTool instance
  (ExKtbbTagToolInstance, SubjetContainerName) = buildExclusiveSubjets(JetCollectionExKt, 2)
  JetCollectionExKtSubJetList += [SubjetContainerName]
  
  # build subjet collection through JetRecTool
  from JetRec.JetRecConf import JetRecTool
  jetrec = JetRecTool(
                       name = "JetRecTool_ExKtbb_%s" % (JetCollectionExKt),
                       OutputContainer = JetCollectionExKt,
                       InputContainer = JetCollectionExKt,
                       JetModifiers = [ExKtbbTagToolInstance],
                     )
  ToolSvc += jetrec
  SJET1Sequence += JetAlgorithm(
                          name = "JetAlgorithm_ExKtbb_%s" % (JetCollectionExKt),
                          Tools = [jetrec],
                        )

# BTagging ExKtSubjetcs first
for JetCollectionExKtSubJet in JetCollectionExKtSubJetList:
  print JetCollectionExKtSubJet[:-4]+"->AntiKt4EMTopo"
  BTaggingFlags.CalibrationChannelAliases += [JetCollectionExKtSubJet[:-4]+"->AntiKt4EMTopo"]

FlavorTagInit(myTaggers      = defaultTaggers,
             JetCollections = JetCollectionExKtSubJetList,
             Sequencer      = SJET1Sequence)


# and then the parent jet
FlavorTagInit(myTaggers      = defaultTaggers + specialTaggers,
             JetCollections = JetCollections,
             Sequencer      = SJET1Sequence)


if not hasattr(DerivationFrameworkJob,"ELReset"):
  DerivationFrameworkJob += CfgMgr.xAODMaker__ElementLinkResetAlg( "ELReset" )

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
SJET1SlimmingHelper.AppendToDictionary = {}
for JetCollectionName in JetCollections + JetCollectionExKtSubJetList:
  SJET1SlimmingHelper.AppendToDictionary[JetCollectionName] = "xAOD::JetContainer"
  SJET1SlimmingHelper.AppendToDictionary[JetCollectionName+"Aux"] = "xAOD::JetAuxContainer"

  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionName[:-4]] = "xAOD::BTaggingContainer"
  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionName[:-4]+"Aux"] = "xAOD::BTaggingAuxContainer"

  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionName[:-4]+"SecVtx"] = "xAOD::VertexContainer"
  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionName[:-4]+"SecVtxAux"] = "xAOD::VertexAuxContainer"

  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionName[:-4]+"JFVtx"] = "xAOD::BTagVertexContainer"
  SJET1SlimmingHelper.AppendToDictionary["BTagging_"+JetCollectionName[:-4]+"JFVtxAux"] = "xAOD::BTagVertexAuxContainer"

# smart collection
SJET1SlimmingHelper.SmartCollections = ["AntiKt4EMTopoJets","AntiKt4LCTopoJets", 
                                        "AntiKt10LCTopoTrimmedPtFrac5SmallR20Jets", 
                                        "PrimaryVertices", ]

# collection that we want all variables
SJET1SlimmingHelper.AllVariables = ["TruthEvents", "TruthVertices",
                                    #  "MuonSegments",

                                    "AntiKt2PV0TrackJets",
                                    "BTagging_AntiKt2Track",
                                    "BTagging_AntiKt2TrackJFVtx",
                                    "BTagging_AntiKt2TrackSecVtx",

                                    "AntiKt3PV0TrackJets",
                                    "BTagging_AntiKt3Track",
                                    "BTagging_AntiKt3TrackJFVtx",
                                    "BTagging_AntiKt3TrackSecVtx",

                                    "AntiKt10LCTopoJets",

                                    "AntiKt6LCTopoJets",
                                    # "AntiKt6LCTopoExKt2SubJets",
                                    "BTagging_AntiKt6LCTopo",
                                    "BTagging_AntiKt6LCTopoExKt2Sub",
                                    "BTagging_AntiKt6LCTopoJFVtx",
                                    "BTagging_AntiKt6LCTopoSecVtx",
                                    "BTagging_AntiKt6LCTopoExKt2SubJFVtx",
                                    "BTagging_AntiKt6LCTopoExKt2SubSecVtx",
                                    "AntiKt7LCTopoJets",
                                    # "AntiKt7LCTopoExKt2SubJets",
                                    "BTagging_AntiKt7LCTopo",
                                    "BTagging_AntiKt7LCTopoExKt2Sub",
                                    "BTagging_AntiKt7LCTopoJFVtx",
                                    "BTagging_AntiKt7LCTopoSecVtx",
                                    "BTagging_AntiKt7LCTopoExKt2SubJFVtx",
                                    "BTagging_AntiKt7LCTopoExKt2SubSecVtx",
                                    "AntiKt8LCTopoJets",
                                    # "AntiKt8LCTopoExKt2SubJets",
                                    "BTagging_AntiKt8LCTopo",
                                    "BTagging_AntiKt8LCTopoExKt2Sub",
                                    "BTagging_AntiKt8LCTopoJFVtx",
                                    "BTagging_AntiKt8LCTopoSecVtx",
                                    "BTagging_AntiKt8LCTopoExKt2SubJFVtx",
                                    "BTagging_AntiKt8LCTopoExKt2SubSecVtx",
                                    "AntiKt6TrackJets",
                                    # "AntiKt6TrackExKt2SubJets",
                                    "BTagging_AntiKt6Track",
                                    "BTagging_AntiKt6TrackExKt2Sub",
                                    "BTagging_AntiKt6TrackJFVtx",
                                    "BTagging_AntiKt6TrackSecVtx",
                                    "BTagging_AntiKt6TrackExKt2SubJFVtx",
                                    "BTagging_AntiKt6TrackExKt2SubSecVtx",
                                    "AntiKt7TrackJets",
                                    # "AntiKt7TrackExKt2SubJets",
                                    "BTagging_AntiKt7Track",
                                    "BTagging_AntiKt7TrackExKt2Sub",
                                    "BTagging_AntiKt7TrackJFVtx",
                                    "BTagging_AntiKt7TrackSecVtx",
                                    "BTagging_AntiKt7TrackExKt2SubJFVtx",
                                    "BTagging_AntiKt7TrackExKt2SubSecVtx",
                                    "AntiKt8TrackJets",
                                    # "AntiKt8TrackExKt2SubJets",
                                    "BTagging_AntiKt8Track",
                                    "BTagging_AntiKt8TrackExKt2Sub",
                                    "BTagging_AntiKt8TrackJFVtx",
                                    "BTagging_AntiKt8TrackSecVtx",
                                    "BTagging_AntiKt8TrackExKt2SubJFVtx",
                                    "BTagging_AntiKt8TrackExKt2SubSecVtx",

                                   # "ElectronCollection",
                                   # "PhotonCollection",
                                   # "Electrons",
                                   # "Muons",
                                    #"TauRecContainer",
                                    "MET_RefFinal",
                                    #"AntiKt4LCTopoJets",
                                    #"BTagging_AntiKt4LCTopo",
                                    "InDetTrackParticles",
                                  #  "PrimaryVertices",
                                    "CaloCalTopoClusters",
                                       ]
                
# collection that needs special handling
StaticContent = []
for JetCollectionName in JetCollectionExKtSubJetList:
  StaticContent += [
                     "xAOD::JetContainer#" + JetCollectionName,
                     "xAOD::JetAuxContainer#" + JetCollectionName + "Aux." + "-Parent",
                   ]
SJET1SlimmingHelper.StaticContent += StaticContent

# Trigger content
SJET1SlimmingHelper.IncludeJetTriggerContent = True
# Add the jet containers to the stream
addJetOutputs(SJET1SlimmingHelper,["SJET1"])
SJET1SlimmingHelper.AppendContentToStream(SJET1Stream)
SJET1Stream.RemoveItem("xAOD::TrigNavigation#*")
SJET1Stream.RemoveItem("xAOD::TrigNavigationAuxInfo#*")
