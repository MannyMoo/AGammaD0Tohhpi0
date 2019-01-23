{
  TFile file0("pipipi0_1.root") ;
  TTree* tree = (TTree*)file0.Get("DalitzEventList") ;

  TH1F hTimeD0("hTimeD0", "", 100, 0., 4.1) ;
  TH1F hTimeD0bar("hTimeD0bar", "", 100, 0., 4.1) ;
  TCanvas cD0 ;
  tree->Draw("decaytime >> hTimeD0", "tag == 1") ;
  TCanvas cD0bar ;
  tree->Draw("decaytime >> hTimeD0bar", "tag == -1") ;

  // Get the mean decay time and its uncertainty.
  double meanD0 = hTimeD0.GetMean() ;
  double meanErrorD0 = hTimeD0.GetMeanError() ;
  
  double meanD0bar = hTimeD0bar.GetMean() ;
  double meanErrorD0bar = hTimeD0bar.GetMeanError() ;

  // Add the calculation here.
  double aGamma = 0. ;
  double aGammaError = 0. ;

  TH1F hAsymmetry("hAsymmetry", "", 100, 0., 4.1) ;
  for(unsigned i = 1 ; i < hTimeD0.GetNbinsX() ; ++i){
    double nD0 = hTimeD0.GetBinContent(i) ;
    double nD0Error = hTimeD0.GetBinError(i) ;
    double nD0bar = hTimeD0bar.GetBinContent(i) ;
    double nD0barError = hTimeD0bar.GetBinError(i) ;

    // Calculate the asymmetry and its error here.
    double asymmetry = 0. ;
    double asymmetryError = 0. ;

    hAsymmetry.SetBinContent(i, asymmetry) ;
    hAsymmetry.SetBinError(i, asymmetryError) ;
  }

  TCanvas cAsymmetry ;
  hAsymmetry.Draw() ;
}
