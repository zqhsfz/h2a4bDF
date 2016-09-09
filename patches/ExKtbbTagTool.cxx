#include "JetTagTools/ExKtbbTagTool.h"

#include "xAODJet/JetContainer.h"
#include "xAODJet/JetAuxContainer.h"
#include "xAODJet/JetContainerInfo.h"
#include "JetEDM/IConstituentUserInfo.h"
#include "JetEDM/FastJetUtils.h"

#include "TObjArray.h"
#include "TObjString.h"

namespace Analysis{

ExKtbbTagTool::ExKtbbTagTool(std::string myname):
  JetModifierBase(myname),
  m_JetAlgorithm(""),
  m_JetRadius(0.),
  m_PtMin(0.),
  m_ExclusiveNJets(0),
  m_InputJetContainerName(""),
  m_SubjetRecorderTool("SubjetRecorderTool"),
  m_SubjetLabel(""),
  m_SubjetContainerName(""),
  m_SubjetAlgorithm_BTAG(""),
  m_SubjetRadius_BTAG(0.),
  m_SubjetBoostConstituent(false),
  m_GhostLabels("")
{
  declareProperty("JetAlgorithm", m_JetAlgorithm);
  declareProperty("JetRadius", m_JetRadius);
  declareProperty("PtMin", m_PtMin);
  declareProperty("ExclusiveNJets", m_ExclusiveNJets);

  declareProperty("InputJetContainerName", m_InputJetContainerName);
  declareProperty("SubjetRecorder", m_SubjetRecorderTool);
  declareProperty("SubjetLabel", m_SubjetLabel);
  declareProperty("SubjetContainerName", m_SubjetContainerName);
  declareProperty("SubjetAlgorithm_BTAG", m_SubjetAlgorithm_BTAG);
  declareProperty("SubjetRadius_BTAG", m_SubjetRadius_BTAG);

  declareProperty("SubjetBoostConstituent", m_SubjetBoostConstituent);

  declareProperty("GhostLabels", m_GhostLabels);

  m_GhostLabelVector.clear();
}

StatusCode ExKtbbTagTool::initialize(){
  // Initialize subjet recorder

  if(m_SubjetRecorderTool.retrieve().isFailure()){
    ATH_MSG_ERROR("#BTAG# Unable to retrieve SubjetRecorder Tool");
    return StatusCode::FAILURE;
  }
  else{
    ATH_MSG_INFO("#BTAG# Successfully retrieve SubjetRecorder Tool");
  }

  // Convert m_GhostLabels to vector of strings

  m_GhostLabelVector.clear();
  TString m_GhostLabels_tstring(m_GhostLabels);
  TObjArray* m_GhostLabels_tokenize = m_GhostLabels_tstring.Tokenize(",");
  for(int istring = 0; istring < m_GhostLabels_tokenize->GetEntries(); istring++){
    TObjString* label_tmp = dynamic_cast<TObjString*>(m_GhostLabels_tokenize->At(istring));
    m_GhostLabelVector.push_back(label_tmp->GetString().Data());
  }
  delete m_GhostLabels_tokenize;

  return StatusCode::SUCCESS;
}

std::vector<fastjet::PseudoJet> ExKtbbTagTool::getBoostedConstituents(xAOD::Jet& jet) const {
  std::vector<fastjet::PseudoJet> vec_conboost;

  TLorentzVector tlv_jet(0, 0, 0, 0); 
  double jetMass = jet.m();
  if (jetMass < 1000. ) jetMass = 1000.; // 100. MeV...
  tlv_jet.SetPtEtaPhiM(jet.pt(), jet.eta(), jet.phi(), jetMass);
  TVector3 t3_boost = -1. * tlv_jet.BoostVector();

  xAOD::JetConstituentVector constituents_tmp = jet.getConstituents();

  if (!constituents_tmp.isValid()){
    ATH_MSG_ERROR("#BTAG# Unable to retrieve valid constituents from parent of large R jet");
    return vec_conboost;
  }   

  xAOD::JetConstituentVector::iterator it = constituents_tmp.begin();
  xAOD::JetConstituentVector::iterator itE = constituents_tmp.end();

  int index = 0;
  double minimumPt = 9e99;    // need to record down the minimum pT after boost, since it could be very small! 
  for( ; it !=itE; ++it){

    TLorentzVector tlv_con(0, 0, 0, 0); 
    tlv_con.SetPxPyPzE( it->Px(), it->Py(), it->Pz(), it->E());
    tlv_con.Boost(t3_boost);
    fastjet::PseudoJet constituent_pj = fastjet::PseudoJet( tlv_con.Px(), tlv_con.Py(), tlv_con.Pz(), tlv_con.E() );
    constituent_pj.set_user_index(index); 
    vec_conboost.push_back( constituent_pj );

    if(constituent_pj.perp() < minimumPt) minimumPt = constituent_pj.perp();

    index++;
  }   

  // now add in ghost associated particles
  for(unsigned int index_GhostLabel = 0; index_GhostLabel < m_GhostLabelVector.size(); index_GhostLabel++){
    std::string GhostLabel = m_GhostLabelVector[index_GhostLabel];

    std::vector<const xAOD::IParticle*> GhostParticles;
    if(!jet.getAssociatedObjects<xAOD::IParticle>(GhostLabel, GhostParticles)){
      ATH_MSG_WARNING("Unable to fetch ghost associated collection " << GhostLabel);
      GhostParticles.clear();
    }

    for(unsigned int index_GhostParticle = 0; index_GhostParticle < GhostParticles.size(); index_GhostParticle++){
      auto GhostParticle = GhostParticles[index_GhostParticle];

      if(GhostParticle->p4().E() <= 0.0) continue;     // yes, we always skip negative energy

      TLorentzVector tlv_con(0, 0, 0, 0);
      tlv_con.SetPxPyPzE( GhostParticle->p4().Px(), GhostParticle->p4().Py(), GhostParticle->p4().Pz(), GhostParticle->p4().E() );
      tlv_con.Boost(t3_boost);
      fastjet::PseudoJet constituent_pj = fastjet::PseudoJet( tlv_con.Px(), tlv_con.Py(), tlv_con.Pz(), tlv_con.E() );

      // determine ghost dynamically (100 times smaller than the minimum Pt), making sure that ghost is still much smaller than all real constituents (after boosting back to CoM, the constituent might be nearly static)
      double ghostScale = (minimumPt/1000.)/(constituent_pj.perp());
      if(ghostScale == 0.){
        ATH_MSG_WARNING("Ghost scale is 0. Reset to 1e-40. Minimum pT is " << minimumPt);
        ghostScale = 1e-40;
      }

      constituent_pj *= ghostScale;                         // a pretty standard ghost scale
      constituent_pj.set_user_index(-1);
      constituent_pj.set_user_info(new Analysis::SimplePseudoJetUserInfo(GhostLabel, index_GhostParticle));
      vec_conboost.push_back( constituent_pj );
    }
  }

  return vec_conboost;
}

int ExKtbbTagTool::modify(xAOD::JetContainer& jets) const{
  // always create subjet container here, so that there would be no "Check number of writes failed" ERROR when the parent jet container is empty
  // move the relevant code fragment from SubjetRecorderTool.cxx to here
  xAOD::JetContainer *subjet_container = 0;
  subjet_container = evtStore()->tryRetrieve<xAOD::JetContainer>(m_SubjetContainerName);
  if(subjet_container == 0) {
    StatusCode sc;
    subjet_container = new xAOD::JetContainer;
    subjet_container->setStore(new xAOD::JetAuxContainer);
    sc = evtStore()->record(subjet_container, m_SubjetContainerName);
    if(sc.isFailure()) {
      ATH_MSG_ERROR("Error recording subjet container (" << m_SubjetContainerName << ")");
      return 0;
    }
    sc = evtStore()->record(dynamic_cast<xAOD::JetAuxContainer*>(subjet_container->getStore()), m_SubjetContainerName + "Aux.");
    if(sc.isFailure()) {
      ATH_MSG_ERROR("Error recording subjet aux container (" << m_SubjetContainerName << "Aux.)");
      return 0;
    }
  }
  else{
    // Not failing immediately, but this is really NOT expected!
    ATH_MSG_ERROR("Is it really expected that subjet collection " << m_SubjetContainerName << " has already been created ?!");
  }

  // copy from base class JetModifierBase
  for ( xAOD::JetContainer::iterator ijet=jets.begin(); ijet!=jets.end(); ++ijet) {
    modifyJet(**ijet);
  }
  return 0;
}

int ExKtbbTagTool::modifyJet(xAOD::Jet& jet) const {

  // run subjet finding //

  xAOD::JetAlgorithmType::ID ialg = xAOD::JetAlgorithmType::algId(m_JetAlgorithm);
  fastjet::JetAlgorithm fjalg = xAOD::JetAlgorithmType::fastJetDef(ialg);

  JetSubStructureUtils::SubjetFinder subjetFinder(fjalg, m_JetRadius, m_PtMin, m_ExclusiveNJets);

  std::vector<fastjet::PseudoJet> constituents_pj;
 if (m_SubjetBoostConstituent) constituents_pj = getBoostedConstituents(jet);
 else                          constituents_pj = constituentPseudoJets(jet);

  // std::vector<fastjet::PseudoJet> constituents = jet::JetConstituentFiller::constituentPseudoJets(jet);
  fastjet::PseudoJet sum_constituents_pj = fastjet::join(constituents_pj);
  std::vector<fastjet::PseudoJet> subjets_pj = subjetFinder.result(sum_constituents_pj);

  // boost subjet for CoM
  double jetMass = jet.m();
  if (jetMass < 1000. ) jetMass = 1000.; // 1GeV
  TLorentzVector tlv_jet(0, 0, 0, 0);
  tlv_jet.SetPtEtaPhiM(jet.pt(), jet.eta(), jet.phi(), jetMass);
  TVector3 t3_boost = tlv_jet.BoostVector();

  if (m_SubjetBoostConstituent){
    for (unsigned int jsub=0; jsub<subjets_pj.size(); jsub++){
      TLorentzVector tlv_subj(0, 0, 0, 0);
      tlv_subj.SetPxPyPzE(subjets_pj.at(jsub).px(), subjets_pj.at(jsub).py(), subjets_pj.at(jsub).pz(), subjets_pj.at(jsub).e());
      tlv_subj.Boost(t3_boost);
      subjets_pj.at(jsub).reset_momentum(tlv_subj.Px(), tlv_subj.Py(), tlv_subj.Pz(), tlv_subj.E());
    }
  }

  // apply pT cut //
  // Note: in fastjet exclusive clustering mode, no pT cut is applied 

  std::vector<fastjet::PseudoJet> subjets_pj_selected;
  for(auto pj : subjets_pj){
    if(pj.perp() < m_PtMin) continue;
    subjets_pj_selected.push_back(pj);
  }
  subjets_pj = subjets_pj_selected;

  // record subjets //

  auto subjets_nonconst = m_SubjetRecorderTool->recordSubjets(subjets_pj, jet);   // since we are using customized constituent pseudo-jet, constituents information will not be stored here

  // store the subjet container name and index //

  // We do this since ElementLink to the subjet could be broken after the deep-copy in b-tagging part. This was not a problem before 20.7. The reason behind it is still unknown.
  // Assuming the subjet container order is un-changed during b-tagging deep-copy, which SHOULD be valid.

  std::vector<const xAOD::Jet*> ExKtSubJets;
  if(!jet.getAssociatedObjects<xAOD::Jet>(m_SubjetLabel.c_str(), ExKtSubJets)){
    ATH_MSG_WARNING("Unable to fetch subjet collection in ExKtbbTagTool::modifyJet : " << m_SubjetLabel.c_str());
    ATH_MSG_WARNING("Nothing to be done for this problem. But you might crash very soon.");
  }

  jet.auxdata<std::string>(m_SubjetLabel + "_ContainerName") = m_SubjetContainerName;

  std::vector<int> SubjetIndexVector;
  for(auto subjet : ExKtSubJets){
    SubjetIndexVector.push_back(subjet->index());
  }
  jet.auxdata<std::vector<int> >(m_SubjetLabel + "_IndexList") = SubjetIndexVector;

  // overwrite something / store constituents //

  for(unsigned int index_subjet = 0; index_subjet < subjets_nonconst.size(); index_subjet++){
    auto subjet_nonconst = subjets_nonconst[index_subjet];
    auto subjet_pj = subjets_pj[index_subjet];

    // jet finding 
    subjet_nonconst->setAlgorithmType(xAOD::JetAlgorithmType::algId(m_SubjetAlgorithm_BTAG));
    subjet_nonconst->setSizeParameter(m_SubjetRadius_BTAG);

    // jet input type
    subjet_nonconst->setInputType(jet.getInputType());

    // setup constituents

    // check if constituents has been filled before
    if(subjet_nonconst->numConstituents() == 0){

      std::map<std::string, std::vector<const xAOD::IParticle*> > ghostMap;
      std::map<std::string, float>                                ghostPtMap;
      std::vector<std::string>                                    ghostLabelList;

      for(auto pj_constituent : subjet_pj.constituents()){

        int index_constituent = pj_constituent.user_index();  // index in parent jet constituent vector

        if(index_constituent >= 0){ // constituents
          auto el_constituent = jet.constituentLinks()[index_constituent];

          if(!el_constituent.isValid()){
            ATH_MSG_WARNING("#BTAG# Element link to jet constituent is inValid! It will still be stored anyway ... ");
          }

          subjet_nonconst->addConstituent(el_constituent, 1.0);
        }
        else{ // ghost particles -- just build the map here
          auto pj_user_info = pj_constituent.user_info<Analysis::SimplePseudoJetUserInfo>();
          std::string pj_user_label = pj_user_info.label();
          int pj_user_index = pj_user_info.index();

          const xAOD::IParticle* GhostParticle = 0;
          try{
            GhostParticle = jet.getAssociatedObjects<xAOD::IParticle>(pj_user_label)[pj_user_index];
          }
          catch(...){
            GhostParticle = 0;
          }

          if(GhostParticle == 0){
            // would not crash the code immediately, but will eventually
            ATH_MSG_ERROR("Failure in retrieving ghost particle after clustering through label " << pj_user_label << " and index " << pj_user_index);
          }
          else{
            ghostLabelList.push_back(pj_user_label);
            ghostMap[pj_user_label].push_back( GhostParticle );
            ghostPtMap[pj_user_label] += GhostParticle->pt();
          }
        }

        // now add ghost particles in
        // for(std::string GhostLabel : ghostLabelList){
        for(std::string GhostLabel : m_GhostLabelVector){
          subjet_nonconst->setAssociatedObjects(GhostLabel, ghostMap[GhostLabel]);
          subjet_nonconst->setAttribute<int>(GhostLabel + "Count", ghostMap[GhostLabel].size());
          subjet_nonconst->setAttribute<float>(GhostLabel + "Pt", ghostPtMap[GhostLabel]);
        }
        
      }

    }
    else{
      ATH_MSG_WARNING("#BTAG# Constituent link to subjet is already built, which is NOT expected!");
    }

    // set correct constituent signal state
    subjet_nonconst->setConstituentsSignalState(jet.getConstituentsSignalState());

    // add parent jet information, in case the "parent" link is broken
    auto el_parent = subjet_nonconst->auxdata<ElementLink<xAOD::JetContainer> >("Parent");
    if(!el_parent.isValid()){
      ATH_MSG_WARNING("#BTAG# Element link from ExKtSubjet to parent jet is invalid! No backup parent link information will be stored.");
    }
    else{
      subjet_nonconst->auxdata<std::string>("Parent_ContainerName") = m_InputJetContainerName;
      subjet_nonconst->auxdata<int>("Parent_Index") = jet.index();
    }

  }

  return 0;
}

std::vector<fastjet::PseudoJet> ExKtbbTagTool::constituentPseudoJets(xAOD::Jet& jet) const{
  // code adapted from JetConstituentFiller.cxx
  // Cannot use JetConstituentFiller utils due to code crash from unknown reason
  // It seems the fastjet link is broken after a deep copy of parent jet
  // but anyway ... 

  std::vector<fastjet::PseudoJet> constituents;

  xAOD::JetConstituentVector constituents_tmp = jet.getConstituents();
  xAOD::JetConstituentVector::iterator it = constituents_tmp.begin();
  xAOD::JetConstituentVector::iterator itE = constituents_tmp.end();

  int index = 0;
  for( ; it !=itE; ++it){
    fastjet::PseudoJet constituent_pj = fastjet::PseudoJet( it->Px(), it->Py(), it->Pz(), it->E() );    // this is guaranteed to be the scale used in jet finding
    constituent_pj.set_user_index(index);        // each constituent_pj will store index in parent jet constituent ve tor
    constituents.push_back( constituent_pj );

    index++;
  }

  // now add in ghost associated ones
  for(unsigned int index_GhostLabel = 0; index_GhostLabel < m_GhostLabelVector.size(); index_GhostLabel++){
    std::string GhostLabel = m_GhostLabelVector[index_GhostLabel];

    std::vector<const xAOD::IParticle*> GhostParticles;
    if(!jet.getAssociatedObjects<xAOD::IParticle>(GhostLabel, GhostParticles)){
      ATH_MSG_WARNING("Unable to fetch ghost associated collection " << GhostLabel);
      GhostParticles.clear();
    }

    for(unsigned int index_GhostParticle = 0; index_GhostParticle < GhostParticles.size(); index_GhostParticle++){
      auto GhostParticle = GhostParticles[index_GhostParticle];

      if(GhostParticle->p4().E() <= 0.0) continue;     // yes, we always skip negative energy

      fastjet::PseudoJet constituent_pj = fastjet::PseudoJet( GhostParticle->p4().Px(), GhostParticle->p4().Py(), GhostParticle->p4().Pz(), GhostParticle->p4().E() );
      constituent_pj *= 1e-40;                         // a pretty standard ghost scale
      constituent_pj.set_user_index(-1);
      constituent_pj.set_user_info(new Analysis::SimplePseudoJetUserInfo(GhostLabel, index_GhostParticle));
      constituents.push_back( constituent_pj );
    }
  }

  return constituents;
}

}
