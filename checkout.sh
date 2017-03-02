# checkout packages
echo " "
echo "checking out packages ..."
echo " "
pkgco.py DerivationFrameworkFlavourTag
pkgco.py DerivationFrameworkTop
pkgco.py JetTagTools
git clone -b ghostTracks https://github.com/kratsg/JetReclustering.git

# apply patches
echo " "
echo "applying patches ..."
echo " "

cp patches/ExKtbbAugmentation.cxx PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/src
cp patches/ExKtbbAugmentation.h PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/DerivationFrameworkTop/
cp patches/DerivationFrameworkTop_entries.cxx PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/src/components/
cp patches/TOPQ1AugTools.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/python/
cp patches/TOPQ1.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/share
cp patches/HbbCommon.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkFlavourTag/python

cp patches/ExKtbbTag.h PhysicsAnalysis/JetTagging/JetTagTools/JetTagTools/
cp patches/ExKtbbTagTool.h PhysicsAnalysis/JetTagging/JetTagTools/JetTagTools/
cp patches/ExKtbbTag.cxx PhysicsAnalysis/JetTagging/JetTagTools/src/
cp patches/requirements PhysicsAnalysis/JetTagging/JetTagTools/cmt/
