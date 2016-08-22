# checkout packages
echo " "
echo "checking out packages ..."
echo " "
pkgco.py JetCalibTools-00-04-67
pkgco.py JetTagTools-01-00-96
pkgco.py BTagging-00-07-64
pkgco.py DerivationFrameworkFlavourTag-00-01-55
pkgco.py DerivationFrameworkTop-00-03-03
pkgco.py DerivationFrameworkCore
pkgco.py AODFix

# apply patches
echo " "
echo "applying patches ..."
echo " "
cp patches/DerivationFrameworkProdFlags.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkCore/python/DerivationFrameworkProdFlags.py
cp patches/TOPQCommonSelection.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/python/TOPQCommonSelection.py
cp patches/AODFix_r207.py Reconstruction/AODFix/python
cp patches/SJET1.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/share
cp patches/ExKtbb*.cxx PhysicsAnalysis/JetTagging/JetTagTools/src/
cp patches/ExKtbb*.h PhysicsAnalysis/JetTagging/JetTagTools/JetTagTools/
