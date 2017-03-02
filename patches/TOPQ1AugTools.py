#====================================================================
# Common file used for TOPQ1 augmentation
# Call with:
#     import DerivationFrameworkTop.TOPQCommonTruthTools
#     augmentationTools = DerivationFrameworkTop.TOPQCommonSelection.setup('TOPQ1', ToolSvc)
#====================================================================

#================================
# IMPORTS
#================================
from DerivationFrameworkCore.DerivationFrameworkMaster import *

def setup(ToolSvc):

  augmentationTools=[]

  from DerivationFrameworkTop.DerivationFrameworkTopConf import DerivationFramework__ExKtbbAugmentation
  TOPQ1ExKtbbAugmentation = DerivationFramework__ExKtbbAugmentation(name = "TOPQ1ExKtbbAugmentation")
  ToolSvc += TOPQ1ExKtbbAugmentation
  augmentationTools.append(TOPQ1ExKtbbAugmentation)
  #=============
  # RETURN TOOLS
  #=============   
  return augmentationTools

#==============================================================================
# SETUP TRUTH KERNEL
#==============================================================================
augmentationTools = setup(ToolSvc)
TOPQ1ExKtCommonTruthKernel = CfgMgr.DerivationFramework__CommonAugmentation("TOPQ1ExKtCommonTruthKernel", AugmentationTools = augmentationTools)
