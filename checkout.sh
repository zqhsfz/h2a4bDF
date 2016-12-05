# checkout packages
echo " "
echo "checking out packages ..."
echo " "
pkgco.py JetCalibTools-00-04-67
pkgco.py ParticleJetTools-00-03-33-08
pkgco.py DerivationFrameworkFlavourTag-00-01-84
pkgco.py DerivationFrameworkJetEtMiss-00-03-56
pkgco.py DerivationFrameworkTop
pkgco.py DerivationFrameworkCore
pkgco.py BTagging-00-07-63-05
pkgco.py JetTagTools-01-00-96-04
pkgco.py AODFix-00-03-29

# apply patches
echo " "
echo "applying patches ..."
echo " "
patch -N Reconstruction/AODFix/python/AODFix_r207.py < patches/AODFix_r207.patch
patch -N PhysicsAnalysis/DerivationFramework/DerivationFrameworkCore/python/DerivationFrameworkProdFlags.py < patches/DerivationFrameworkProdFlags.patch
patch -N PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/python/TOPQCommonSelection.py < patches/TOPQCommonSelection.patch
cp patches/SJET1.py PhysicsAnalysis/DerivationFramework/DerivationFrameworkTop/share
