#include "DerivationFrameworkTop/ExKtbbAugmentation.h"

#include "xAODEventInfo/EventInfo.h"
#include "xAODJet/JetContainer.h"
#include "xAODJet/JetAuxContainer.h"
#include "xAODBTagging/BTagging.h"
#include "xAODBTagging/BTaggingContainer.h"
#include "xAODBTagging/BTaggingAuxContainer.h"
#include "xAODTracking/VertexContainer.h"
#include "xAODTracking/VertexAuxContainer.h"


namespace DerivationFramework {


ExKtbbAugmentation::ExKtbbAugmentation(const std::string& t, const std::string& n, const IInterface* p):
  AthAlgTool(t,n,p)
{

    declareInterface<DerivationFramework::IAugmentationTool>(this);

    declareProperty("EventInfoName",m_eventInfoName="EventInfo");


}



ExKtbbAugmentation::~ExKtbbAugmentation(){}



StatusCode ExKtbbAugmentation::initialize(){

  ATH_MSG_INFO("Initializing ExKtbbAugmentation tool... " );


  return StatusCode::SUCCESS;

}



StatusCode ExKtbbAugmentation::finalize(){

  return StatusCode::SUCCESS;

}



StatusCode ExKtbbAugmentation::addBranches() const{

  const xAOD::EventInfo* eventInfo;

  if (evtStore()->retrieve(eventInfo,m_eventInfoName).isFailure()) {
    ATH_MSG_ERROR("could not retrieve event info " <<m_eventInfoName);
    return StatusCode::FAILURE;
  }

  
  const xAOD::JetContainer* jets = evtStore()->retrieve< const xAOD::JetContainer >( "AntiKt8LCTopoJets" );

  std::string algName = "ExKtbb"; 
  static SG::AuxElement::Decorator<double> jet_maxmv2(algName+"_MaxMV2c10");
  static SG::AuxElement::Decorator<double> jet_minmv2(algName+"_MinMV2c10");
  static SG::AuxElement::Decorator<double> jet_subDR(algName+"_SubjetDR");
  static SG::AuxElement::Decorator<double> jet_ptasym(algName+"_SubjetPtAsym");

  std::string algName3 = "ExKt3bb"; 
  static SG::AuxElement::Decorator<double> jet_exkt3_maxmv2(algName3+"_MaxMV2c10");
  static SG::AuxElement::Decorator<double> jet_exkt3_minmv2(algName3+"_MinMV2c10");
  static SG::AuxElement::Decorator<double> jet_exkt3_subDR(algName3+"_SubjetDR");
  static SG::AuxElement::Decorator<double> jet_exkt3_ptasym(algName3+"_SubjetPtAsym");

 //I do not like this... there must be a better way...
   //xAOD::JetContainer* ExKtSubJets = const_cast<xAOD::JetContainer*> ( evtStore()->retrieve< const xAOD::JetContainer >( "AntiKt8LCTopoExKt2SubJets" ) );
   //xAOD::JetContainer* ExKt3SubJets = const_cast<xAOD::JetContainer*> ( evtStore()->retrieve< const xAOD::JetContainer >( "AntiKt8LCTopoExKt3SubJets" ) );

  for (int i = 0; i < jets->size() ; i++){
    
    double maxmv2 = -999;
    double minmv2 = -999;
    double subDR = -999;
    double ptasym = -999;

    double exkt3_maxmv2 = -999;
    double exkt3_minmv2 = -999;
    double exkt3_subDR = -999;
    double exkt3_ptasym = -999;

    jet_maxmv2(*(jets->at(i))) = -999;
    jet_minmv2(*(jets->at(i))) = -999;
    jet_subDR(*(jets->at(i))) = -999;
    jet_ptasym(*(jets->at(i))) = -999;
    jet_exkt3_maxmv2(*(jets->at(i))) = -999;
    jet_exkt3_minmv2(*(jets->at(i))) = -999;
    jet_exkt3_subDR(*(jets->at(i))) = -999;
    jet_exkt3_ptasym(*(jets->at(i))) = -999;

    // Bug fix in 20.7: Reset ElementLink before using it
    std::vector<const xAOD::Jet*> ExKtSubjets;
    auto v_el = jets->at(i)->auxdata<std::vector<ElementLink<xAOD::IParticleContainer> > >("ExKt2SubJets");
    for(auto el : v_el){
      if(!el.toTransient()){
        ATH_MSG_WARNING("Unable to reset element link in . You would crash soon ...");
      }

      if(!el.isValid()){
        ATH_MSG_ERROR("Invalid link to subjet through link !");
        return false;
      }
      else{
        auto subjet = dynamic_cast<const xAOD::Jet*>(*el);
        if(subjet == 0){
          ATH_MSG_ERROR("Empty ptr to subjet! You will crash soon...");
          return false;
        }
        else{
          ExKtSubjets.push_back(subjet);
        }
      }
    }
std::cout << "YOYOYOYOYO" << std::endl;

    if(ExKtSubjets.size() == 2){
      std::sort(ExKtSubjets.begin(), ExKtSubjets.end(), 
        [](const xAOD::Jet* j1, const xAOD::Jet* j2){
          return (j1->pt() > j2->pt());
        }
      );

std::cout << "WOAHWOAH" << std::endl;
      const xAOD::BTagging* bjet_LeadExKtSubJet = ExKtSubjets.at(0)->btagging();
      const xAOD::BTagging* bjet_SubLeadExKtSubJet = ExKtSubjets.at(1)->btagging();

      if( (!bjet_LeadExKtSubJet) || (!bjet_SubLeadExKtSubJet) ){
        std::cout << "Exclusive kt subjet is not well b-tagged!" << std::endl;
      }
      std::cout << "WORKZZZ" <<std::endl;
      maxmv2    = std::max(bjet_LeadExKtSubJet->auxdata<double>("MV2c10_discriminant"),bjet_SubLeadExKtSubJet->auxdata<double>("MV2c10_discriminant"));
      minmv2    = std::min(bjet_LeadExKtSubJet->auxdata<double>("MV2c10_discriminant"),bjet_SubLeadExKtSubJet->auxdata<double>("MV2c10_discriminant"));
      subDR     = ExKtSubjets.at(0)->p4().DeltaR(ExKtSubjets.at(1)->p4());
      if(ExKtSubjets.at(0)->pt()+ExKtSubjets.at(1)->pt() > 0) ptasym =  fabs(ExKtSubjets.at(0)->pt()-ExKtSubjets.at(1)->pt())/(ExKtSubjets.at(0)->pt()+ExKtSubjets.at(1)->pt());
      else ptasym = -999;

    }  

    //std::vector<const xAOD::Jet*> ExKt3SubJets;
    // if(!jets->at(i)->getAssociatedObjects<xAOD::Jet>(m_SubJet3Label.c_str(), ExKt3SubJets)){
    //   std::cout << "Unable to fetch subjet collection " << m_SubJet3Label.c_str() << std::endl;
    // }
    // Bug fix in 20.7: Reset ElementLink before using it
    std::vector<const xAOD::Jet*> ExKt3Subjets;
    auto v_el3 = jets->at(i)->auxdata<std::vector<ElementLink<xAOD::IParticleContainer> > >("ExKt3SubJets");
    for(auto el : v_el3){
      if(!el.toTransient()){
        ATH_MSG_WARNING("Unable to reset element link in. You would crash soon ...");
      }

      if(!el.isValid()){
        ATH_MSG_ERROR("Invalid link to subjet through link !");
        return false;
      }
      else{
        auto subjet = dynamic_cast<const xAOD::Jet*>(*el);
        if(subjet == 0){
          ATH_MSG_ERROR("Empty ptr to subjet! You will crash soon...");
          return false;
        }
        else{
          ExKt3Subjets.push_back(subjet);
        }
      }
    }
    if(ExKt3Subjets.size() == 3){
      std::sort(ExKt3Subjets.begin(), ExKt3Subjets.end(), 
        [](const xAOD::Jet* j1, const xAOD::Jet* j2){
          return (j1->btagging()->auxdata<double>("MV2c10_discriminant") > j2->btagging()->auxdata<double>("MV2c10_discriminant"));
        }

      );
      const xAOD::BTagging* bjet_LeadExKt3SubJet = ExKt3Subjets.at(0)->btagging();
      const xAOD::BTagging* bjet_SubLeadExKt3SubJet = ExKt3Subjets.at(1)->btagging();

      //if( (!bjet_LeadExKtSubJet) || (!bjet_SubLeadExKtSubJet) ){
      //  std::cout << "Exclusive kt subjet is not well b-tagged!" << std::endl;
      //}
      exkt3_maxmv2    = std::max(bjet_LeadExKt3SubJet->auxdata<double>("MV2c10_discriminant"),bjet_SubLeadExKt3SubJet->auxdata<double>("MV2c10_discriminant"));
      exkt3_minmv2    = std::min(bjet_LeadExKt3SubJet->auxdata<double>("MV2c10_discriminant"),bjet_SubLeadExKt3SubJet->auxdata<double>("MV2c10_discriminant"));
      exkt3_subDR     = ExKt3Subjets.at(0)->p4().DeltaR(ExKt3Subjets.at(1)->p4());
      if(ExKt3Subjets.at(0)->pt()+ExKt3Subjets.at(1)->pt() > 0) exkt3_ptasym =  fabs(ExKt3Subjets.at(0)->pt()-ExKt3Subjets.at(1)->pt())/(ExKt3Subjets.at(0)->pt()+ExKt3Subjets.at(1)->pt());
      else exkt3_ptasym = -999;

      jet_maxmv2(*(jets->at(i))) = maxmv2;
      jet_minmv2(*(jets->at(i))) = minmv2;
      jet_subDR(*(jets->at(i))) = subDR;
      jet_ptasym(*(jets->at(i))) = ptasym;
      jet_exkt3_maxmv2(*(jets->at(i))) = exkt3_maxmv2;
      jet_exkt3_minmv2(*(jets->at(i))) = exkt3_minmv2;
      jet_exkt3_subDR(*(jets->at(i))) = exkt3_subDR;
      jet_exkt3_ptasym(*(jets->at(i))) = exkt3_ptasym;


    }  


  }
 return StatusCode::SUCCESS;

}



} /// namespace
