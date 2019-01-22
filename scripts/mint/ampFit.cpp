// author: Jonas Rademacker (Jonas.Rademacker@bristol.ac.uk)
// status:  Mon 9 Feb 2009 19:18:01 GMT
#include "Mint/FitParameter.h"
#include "Mint/NamedParameter.h"
#include "Mint/Minimiser.h"
#include "Mint/Neg2LL.h"
#include "Mint/Neg2LLSum.h"
#include "Mint/DalitzEventList.h"

#include "Mint/CLHEPPhysicalConstants.h"


#include "Mint/PdfBase.h"
#include "Mint/DalitzPdfBase.h"
#include "Mint/DalitzPdfBaseFastInteg.h"
#include "Mint/DalitzSumPdf.h"

#include "Mint/FitAmplitude.h"
#include "Mint/FitAmpSum.h"
#include "Mint/FitAmpIncoherentSum.h"

#include "Mint/DalitzEvent.h"

#include "Mint/AmpRatios.h"

#include "Mint/IEventGenerator.h"
#include "Mint/DalitzBWBoxSet.h"
#include "Mint/DalitzBoxSet.h"

#include "Mint/SignalGenerator.h"
#include "Mint/FromFileGenerator.h"

#include "Mint/LASSO.h"

#include "TGraph.h"
#include "TFile.h"
#include "TCanvas.h"

#include "TRandom2.h"
#include "TRandom3.h"
#include <ctime>

#include <iostream>

#include "Mint/DalitzPdfNormChecker.h"
#include "Mint/DalitzPdfBaseFlexiFastInteg.h"


#include "Mint/Chi2Binning.h"
#include <memory>
#include <TSpline.h>
#include <Mint/DalitzPdfSaveInteg.h>
#include <sys/stat.h>
#include <cstdlib>

using namespace std;
using namespace MINT;

// check if a file exists.
bool exists(const string& fname) {
  struct stat statinfo ;
  return stat(fname.c_str(), &statinfo) == 0 ;
}

// Class to generate random numbers according to a spline interpolator.
class SplineGenerator {
private :
  struct BinInfo {
    double xmin ;
    double xmax ;
    double integral ;
    double ymin ;
    double ymax ;
    double boxintegral ;
  } ;
  
  TRandom3* m_rndm ;
  mutable TSpline3 m_spline ; // Cause ROOT is crap at const correctness.
  double m_integral ;
  double m_boxintegral ;
  double m_mean ;
  vector<BinInfo> m_bins ;
  
public :
  SplineGenerator(TRandom3* rndm, const TSpline3& spline) :
    m_rndm(rndm),
    m_spline(spline),
    m_integral(0.),
    m_boxintegral(0.),
    m_mean(0.),
    m_bins(spline.GetNp())
  {
    BinInfo ibin ;
    double xmin(0.), a(0.), b(0.), c(0.), d(0.) ;
    int i = m_spline.GetNp() - 1 ;
    // Get info on the highest knot in the spline.
    m_spline.GetCoeff(i, xmin, a, b, c, d) ;
    ibin.xmin = xmin ;
    ibin.xmax = 1e30 ;
    ibin.integral = 0. ;
    ibin.ymin = 0. ;
    ibin.ymax = 1e30 ;
    m_bins[i] = ibin ;
    --i ;
    // Loop backwards over knots, so we can use the x value of the knot above
    // to set the range.
    for( ; i >= 0 ; --i){
      m_spline.GetCoeff(i, xmin, a, b, c, d) ;
      ibin.xmin = xmin ;
      ibin.xmax = m_bins[i+1].xmin ;
      // cout << "ibin " << i << " xmin " << ibin.xmin << " xmax " << ibin.xmax << endl ;
      // cout << "a " << a << " b " << b << " c " << c << " d " << d << endl ;
      ibin.integral = integral(i, ibin.xmin, ibin.xmax) ;
      // cout << "integral " << ibin.integral << endl ;
      m_integral += ibin.integral ;
      pair<double, double> tps = turning_points(i) ;
      // cout << "tps.first " << tps.first << " tps.second " << tps.second << endl ;
      tps.first = max(min(tps.first, ibin.xmax), ibin.xmin) ;
      tps.second = max(min(tps.second, ibin.xmax), ibin.xmin) ;
      // cout << "tps.first " << tps.first << " tps.second " << tps.second << endl ;
      ibin.ymax = max(
		      max(
			  max(m_spline.Eval(ibin.xmin),
			      m_spline.Eval(ibin.xmax)),
			  m_spline.Eval(tps.first)),
		      m_spline.Eval(tps.second)) ;
      ibin.ymin = min(
		      min(
			  min(m_spline.Eval(ibin.xmin),
			      m_spline.Eval(ibin.xmax)),
			  m_spline.Eval(tps.first)),
		      m_spline.Eval(tps.second)) ;
      if(ibin.ymin < 0.){
	cerr << "SplineGenerator ERROR: ymin < 0. (" << ibin.ymin << ") for bin " << i << endl ;
      }
      ibin.boxintegral = ibin.ymax * (ibin.xmax - ibin.xmin) ;
      // cout << "ymax " << ibin.ymax << " ymin " << ibin.ymin << " boxintegral " << ibin.boxintegral << endl ;
      m_boxintegral += ibin.boxintegral ;
      m_bins[i] = ibin ;
      m_mean += mean(i, ibin.xmin, ibin.xmax) ;
    }
    if(m_integral != 0.)
      m_mean /= m_integral ;
  }

  // Total integral between the minimum and maximum knots.
  double integral() const {
    return m_integral ;
  }

  // Mean of the PDF.
  double mean() const {
    return m_mean ;
  }
  
  // Generate a random number from the spline.
  double gen_random() const {
    while(true){
      double boxsel = m_rndm->Rndm() * m_boxintegral ;
      double boxsum(0.) ;
      vector<BinInfo>::const_iterator ibin = m_bins.begin() ;
      for(; ibin != m_bins.end() ; ++ibin){
	boxsum += ibin->boxintegral ;
	if(boxsum >= boxsel)
	  break ;
      }
      double x = m_rndm->Rndm() * (ibin->xmax - ibin->xmin) + ibin->xmin ;
      if(m_rndm->Rndm() * ibin->ymax < m_spline.Eval(x))
	return x ;
    }
  }

  // Get the integral of the spline between xmin and xmax.
  double integral(double xmin, double xmax) {
    int istart = m_spline.FindX(xmin) ;
    int iend = m_spline.FindX(xmax) ;
    double _integral = integral(istart, xmin, m_bins[istart].xmax)
      + integral(iend, m_bins[iend].xmin, xmax) ;
    for(int ibin = istart + 1 ; ibin != iend ; ++ibin)
      _integral += m_bins[ibin].integral ;
    return _integral ;
  }

  // Get the spline.
  const TSpline3& spline() const {
    return m_spline ;
  }

private :
  // Partial integral for knot i at x.
  double partial_integral(int i, double x) {
    double xmin(0.), a(0.), b(0.), c(0.), d(0.) ;
    m_spline.GetCoeff(i, xmin, a, b, c, d) ;
    x -= xmin ;
    return x * (a + x * (b/2. + x * (c/3. + x * d/4.))) ;
  }

  // Integral for knot i between xmin and xmax.
  double integral(int i, double xmin, double xmax) {
    return partial_integral(i, xmax) - partial_integral(i, xmin) ;
  }

  // Get the turning points of knot i.
  pair<double, double> turning_points(int i) const {
    // Note the reversal of coefficient labelling, as the standard
    // quadratic formula is a x^2 + b x + c while TSplinePoly
    // uses a + b x + c x^2 + d x^3.
    double xmin(0.), d(0.), c(0.), b(0.), a(0.) ;
    m_spline.GetCoeff(i, xmin, d, c, b, a) ;
    b *= 2. ;
    a *= 3. ;
    double arg = b*b - 4. * a * c ;
    if(arg < 0.)
      return pair<double, double>(xmin-1e30, xmin-1e30) ;
    return pair<double, double>(xmin + (-b - sqrt(arg))/2./a, xmin + (-b + sqrt(arg))/2./a) ;
  }

  // The partial integral of x * f(x) used for calculating the mean.
  double mean_part_integral(int i, double x) {
    double xmin(0.), a(0.), b(0.), c(0.), d(0.) ;
    m_spline.GetCoeff(i, xmin, a, b, c, d) ;
    double xshift = x - xmin ;
    return x * xshift * (a + xshift * (b/2. + xshift * (c/3. + xshift * d/4.)))
      - xshift * xshift * (a/2. + xshift * (b/6. + xshift * (c/12. + xshift * d/20.))) ;
  }

  // Get the mean between xmin and xmax for knot i.
  double mean(int i, double xmin, double xmax) {
    return mean_part_integral(i, xmax) - mean_part_integral(i, xmin) ;
  }
} ;


// Class to generate time dependent phase space events.
class TimeDependentGenerator {

public :
  // Class to hold the generator at a given time point.
  class GenTimePoint {
  public :
    GenTimePoint(const double _decaytime, FitAmpSum* _model,
		 const double _integral, SignalGenerator* _generator) :
      decaytime(_decaytime),
      integral(_integral),
      model(_model),
      generator(_generator)
    {}
    
    const double decaytime ;
    const double integral ;
    unique_ptr<FitAmpSum> model ;
    unique_ptr<SignalGenerator> generator ;
  } ;

  typedef list<GenTimePoint> GenList ;
  typedef map<int, GenList> GenMap ;
  typedef pair<complex<double>, complex<double> > AmpPair ;

  // Class to hold the tag (production flavour), decay time and
  // Dalitz event that's generated.
  struct GenTimeEvent {
    int tag ;
    double decaytime ;
    MINT::counted_ptr<IDalitzEvent> evt ;
  } ;

  // Take the CP conjugate of the head of the decay pattern.
  static DalitzEventPattern anti(DalitzEventPattern pat) {
    pat[0].antiThis() ;
    return pat ;
  }

  /* Constructor, takes:
   name : the name of the generator and the directory in which the integrators will be saved.
   overwrite : whether to overwrite the existing integrator files (if they exist).
   rndm : The random number generator to use.
   precision : The precision to which the integrals must be calculated.
   pattern : The event pattern to be used (the CP conjugate will automatically be added).
   width : the decay width in 1/ps.
   deltam : the delta-mass in 1/ps.
   deltagamma : the delta-gamma in 1/ps.
   qoverp : the magnitude of q/p.
   phi : the phase of q/p.
   tmax : the maximum decay time that'll be generated.
   ntimepoints : the number of points to sample between 0 and tmax when building the generators.
  */
  TimeDependentGenerator(const string& name, const bool overwrite, TRandom3* rndm, double precision,
			 const DalitzEventPattern& pattern, double width, double deltam,
			 double deltagamma,
			 double qoverp, double phi, double tmax, int ntimepoints) :
    m_name(name),
    m_rndm(rndm),
    m_pattern(pattern),
    m_cppattern(anti(pattern)),
    m_width(width),
    m_deltam(deltam),
    m_deltagamma(deltagamma),
    m_qoverp(qoverp),
    m_phi(phi),
    m_tmax(tmax),
    m_ntimepoints(ntimepoints),
    m_genmap(),
    m_timegenerators(),
    m_tagintegralfrac(0.),
    m_precision(precision)
  {
    // If overwrite is true and the integrators directory exists, delete it.
    if(overwrite && exists(name)){
      cout << "Deleting previous integrators in directory " << name << endl ;
      string cmd("rm -rf " + name) ;
      system(cmd.c_str()) ;
    }

    if(!exists(name)){
      string cmd("mkdir -p " + name) ;
      system(cmd.c_str()) ;
    }
    
    const DalitzEventPattern* patterns[] = {&m_cppattern, &m_pattern} ;
    double sampleinterval = m_tmax/m_ntimepoints ;
    // Loop over flavours.
    for(int tag = -1 ; tag <= 1 ; tag += 2) {
      m_genmap[tag] = GenList() ;
      const DalitzEventPattern* evtpat = patterns[(tag+1)/2] ;
      const DalitzEventPattern* antipat = patterns[((tag+1)/2 + 1) % 2] ;
      // cout << "evtpat " ;
      // evtpat->print() ;
      // cout << " antipat " ;
      // antipat->print() ;
      // cout << endl ;
      vector<double> times ;
      vector<double> integrals ;
      // Loop over decay time sample points.
      for(int i = 0 ; i <= m_ntimepoints ; ++i){
	double decaytime = i * sampleinterval ;
	AmpPair amps = amplitude_coefficients(tag, decaytime) ;
	FitAmpSum* model(new FitAmpSum(*evtpat)) ;
	*model *= amps.first ;
	if(amps.second != complex<double>(0., 0.)){
	  FitAmpSum antimodel(*antipat) ;
	  antimodel *= amps.second ;
	  model->add(antimodel) ;
	}
	SignalGenerator* generator = new SignalGenerator(*evtpat, model) ;
	//cout << "Time point " << i << endl ;
	//model->print() ;
	//auto evt = generator->newEvent() ;
	//model->printAllAmps(*evt) ;
	ostringstream fname ;
	fname << m_name << "/tag_" << tag << "_decaytime_" << decaytime ;
	double integral(0.) ;
	// Calculate the integral if necessary.
	if(!exists(fname.str())){
	  DalitzPdfSaveInteg dalitz(*evtpat, model, m_precision, fname.str(),
				    fname.str() + "_events.root", "topUp", fname.str()) ;
	  integral = dalitz.getIntegralValue() ;
	  dalitz.saveIntegrator(fname.str()) ;
	}
	// Else retrive the integral from a file.
	else {
	  auto intcalc = model->makeIntegrationCalculator() ;
	  intcalc->retrieve(fname.str()) ;
	  integral = intcalc->integral() ;
	}
	cout << "Make generator with tag " << tag << ", decay time " << decaytime
	     << ", coeffprod " << amps.first.real()
	     << " + " << amps.first.imag() << " j, "
	     << " coeffmix " << amps.second.real() << " + " << amps.second.imag()
	     << " j, integral " << integral << endl ;
	if(integral == 0.){
	  complex<double> coeff = amps.first + amps.second ;
	  integral = sqrt(coeff.real() * coeff.real() + coeff.imag() * coeff.imag()) ;
	}
	m_genmap[tag].push_back(GenTimePoint(decaytime, model, integral, generator)) ;
	times.push_back(decaytime) ;
	integrals.push_back(integral) ;
      }
      // Make a spline interpolator of the decay time distributions, to be used to generate
      // the decay times.
      ostringstream splinename ;
      splinename << "timespline_tag_" << tag ;
      string splinenamestr = splinename.str() ;
      TSpline3 timespline(splinenamestr.c_str(), &times[0], &integrals[0], times.size()) ;
      timespline.SetName(splinenamestr.c_str()) ;
      m_timegenerators.insert(make_pair(tag, SplineGenerator(rndm, timespline))) ;
    }
    // Calculate the integrated CP asymmetry.
    double integminus = m_timegenerators.find(-1)->second.integral() ;
    double integplus = m_timegenerators.find(1)->second.integral() ;
    cout << "Integrated CP asymmetry is " << (integplus - integminus)/(integplus + integminus) << endl ;
    m_tagintegralfrac = integminus/(integminus + integplus) ;
    double tauminus = m_timegenerators.find(-1)->second.mean() ;
    double tauplus = m_timegenerators.find(1)->second.mean() ;
    cout << "Tau minus: " << tauminus << endl ;
    cout << "Tau plus: " << tauplus << endl ;
    cout << "AGamma: " << (tauminus - tauplus)/(tauminus + tauplus) << endl ;
  }

  // Get the coefficients of the amplitudes for the produced flavour and the mixed flavour
  // given the tag and decay time.
  AmpPair amplitude_coefficients(const int tag, const double decaytime) {
    double coeff = exp(-decaytime * 0.5 * (m_width + 0.5 * m_deltagamma)) ;
    complex<double> expterm = exp(complex<double>(0.5 * m_deltagamma * decaytime, m_deltam * decaytime)) ;
    complex<double> plusterm = 1. + expterm ;
    complex<double> minusterm = 1. - expterm ;
    complex<double> coeffprod = coeff * plusterm ;
    complex<double> coeffmix = pow(polar(m_qoverp, m_phi), tag) * coeff * minusterm ;
    return AmpPair(coeffprod, coeffmix) ;
  }

  // Generate a flavour.
  int generate_tag() const {
    double rndm = m_rndm->Rndm() ;
    if(rndm < m_tagintegralfrac)
      return -1 ;
    return 1 ;
  }

  // Generate a decay time for the given flavour.
  double generate_decay_time(const int tag) const {
    double decaytime = m_tmax + 1. ;
    while(decaytime > m_tmax)
      decaytime = m_timegenerators.find(tag)->second.gen_random() ;
    return decaytime ;
  }

  // Generate a Dalitz event for the given flavour and decay time.
  MINT::counted_ptr<IDalitzEvent> generate_dalitz_event(const int tag, const double decaytime) const {
    const GenList& genlist = m_genmap.find(tag)->second ;
    GenList::const_iterator igen = genlist.begin() ;
    while(igen->decaytime < decaytime && igen != genlist.end())
      ++igen ;
    if(igen == genlist.end()){
      cerr << "TimeDependentGenerator::generate_dalitz_event: ERROR: Got impossible decay time: "
	   << decaytime << " (tmax = " << m_tmax << ")" << endl ;
      return MINT::counted_ptr<IDalitzEvent>(0) ;
    }
    // Unlikely, but best to check.
    if(decaytime == igen->decaytime)
      return igen->generator->newEvent() ;
    GenList::const_iterator igenprev(igen) ;
    --igen ;
    // Pick between the generators either side of the decay time according to how close they are to it.
    double gensel = m_rndm->Rndm() ;
    if(gensel < 1. - (decaytime - igenprev->decaytime)/(igen->decaytime - igenprev->decaytime))
      return igenprev->generator->newEvent() ;
    return igen->generator->newEvent() ;
  }

  // Generate a flavour, decay time and Dalitz event.
  GenTimeEvent generate_event() const {
    GenTimeEvent evt ;
    evt.tag = generate_tag() ;
    evt.decaytime = generate_decay_time(evt.tag) ;
    evt.evt = generate_dalitz_event(evt.tag, evt.decaytime) ;
    return evt ;
  }

  // Get the decay time generators.
  const map<int, SplineGenerator> time_generators() const {
    return m_timegenerators;
  }
  
private :
  const string m_name ;
  TRandom3* m_rndm ;
  const DalitzEventPattern m_pattern ;
  const DalitzEventPattern m_cppattern ;
  
  const double m_width ;
  const double m_deltam ;
  const double m_deltagamma ;
  const double m_qoverp ;
  const double m_phi ;

  const double m_tmax ;
  const int m_ntimepoints ;

  GenMap m_genmap ;

  map<int, SplineGenerator> m_timegenerators ;

  double m_tagintegralfrac ;
  double m_precision ;
} ;


// ===========
// Main method
// ===========
int ampFit(){
  time_t startTime = time(0);

  TRandom3 ranLux;
  NamedParameter<int> RandomSeed("RandomSeed", 0);
  ranLux.SetSeed((int)RandomSeed);
  gRandom = &ranLux;

  FitAmplitude::AutogenerateFitFile();

  NamedParameter<int>  Nevents("Nevents", 10000);
  NamedParameter<int>  doScan("doScan", 0);
  NamedParameter<std::string> integMethod("IntegMethod", (std::string) "efficient");
  NamedParameter<double> integPrecision("IntegPrecision", 1.e-4);

  NamedParameter<int> EventPattern("Event Pattern", 421, -321, 211, 211, -211);
  DalitzEventPattern pat(EventPattern.getVector());
  DalitzEventPattern cpPat(pat) ;
  cpPat[0].antiThis() ;

  SignalGenerator genD0(pat);
  SignalGenerator genD0bar(cpPat);

  NamedParameter<int> saveEvents("SaveEvents", 1);
  NamedParameter<int> genTimeDependent("genTimeDependent", 0);
  NamedParameter<double> lifetime("lifetime", 0.4101) ;
  double width = 1./lifetime ;
  NamedParameter<double> x("x", 0.0039) ;
  double deltam = x * width ;
  NamedParameter<double> y("y", 0.0065) ;
  double deltagamma = y * width * 2. ;
  NamedParameter<double> qoverp("qoverp", 1.) ;
  NamedParameter<double> phi("phi", 0.) ;

  NamedParameter<double> tmax("tmax", 10.) ;
  NamedParameter<double> ntimepoints("nTimePoints", 0.1) ;
  NamedParameter<int> overwrite("overwriteIntegrators", 1) ;
  NamedParameter<string> name("integratorsDirectory", string("integrators"), (char*)0) ;
  
  unique_ptr<TimeDependentGenerator> timedepgen ;
  if(genTimeDependent){
    int startinit(time(0)) ;
    timedepgen.reset(new TimeDependentGenerator(name, overwrite, &ranLux, integPrecision, pat,
						width, deltam, deltagamma, qoverp, phi, tmax, ntimepoints)) ;
    cout << "Initialise TimeDependentGenerator took " << time(0) - startinit << " s" << endl ;
  }

  cout << " got event pattern: " << pat << endl;

  DalitzEventList eventList1 ;

  cout << "Generating " << Nevents << " signal events (1)." << endl;
  list<int> tags ;
  list<double> taus ;
  int startTimeGen(time(0)) ;
  for(int i = 0 ; i < Nevents ; ++i){
    // Decide if it's a D0 or D0bar that's being generated.
    SignalGenerator* gen(&genD0) ;
    int tag = 1 ;
    if(ranLux.Rndm() > 0.5){
      gen = &genD0bar ;
      tag = -1 ;
    }
    tags.push_back(tag) ;

    // Generate the decay time of the candidate.
    double decaytime = tmax + 1. ;
    while(decaytime > tmax)
      decaytime = ranLux.Exp(lifetime) ;
    taus.push_back(decaytime) ;

    cout << "Generating candidate " << i << " (" << (time(0)-startTimeGen)/float(i) << " s per candidate)" << endl ;
    if(genTimeDependent){
      TimeDependentGenerator::GenTimeEvent evt = timedepgen->generate_event() ;
      tags.back() = evt.tag ;
      taus.back() = evt.decaytime ;
      eventList1.Add(DalitzEvent(*evt.evt)) ;
    }
    else {
      gen->FillEventList(eventList1, 1);
    }
  }
  
  if((int) saveEvents){
    // Make sure the first event in the list is a D0 so the naming scheme is consistent.
    if(eventList1.begin()->eventPattern() != pat){
      auto ievt = eventList1.begin() ;
      ++ievt ;
      for( ; ievt->eventPattern() != pat && ievt != eventList1.end() ; ++ievt)
	continue ;
      if(ievt != eventList1.end()){
	DalitzEvent evt(*ievt) ;
	int i = ievt - eventList1.begin() ;
	eventList1.erase(ievt) ;
	eventList1.theVector().insert(eventList1.begin(), evt) ;
	auto itag = tags.begin() ;
	advance(itag, i) ;
	int tag = *itag ;
	tags.erase(itag) ;
	tags.insert(tags.begin(), tag) ;
	auto itau = taus.begin() ;
	advance(itau, i) ;
	double tau = *itau ;
	taus.erase(itau) ;
	taus.insert(taus.begin(), tau) ;
      }
    }
    NamedParameter<string> outputfname("outputFileName", string("pipipi0_1.root"), (char*)0) ;
    eventList1.save(outputfname);
    string fnamestr(outputfname) ;
    TFile tuplefile(fnamestr.c_str(), "update") ;
    TNtupleD* ntuple = (TNtupleD*)tuplefile.Get("DalitzEventList") ;
    int tag(0) ;
    double tau(0.) ;
    TBranch* tagbranch = ntuple->Branch("tag", &tag, "tag/I") ;
    TBranch* taubranch = ntuple->Branch("decaytime", &tau, "decaytime/D") ;
    list<int>::const_iterator itag = tags.begin() ;
    list<double>::const_iterator itau = taus.begin() ;
    for(int i = 0 ; i < Nevents ; ++i){
      tag = *itag ;
      tau = *itau ;
      tagbranch->Fill() ;
      taubranch->Fill() ;
      ++itag ;
      ++itau ;
    }
    ntuple->Write(ntuple->GetName(), TObject::kWriteDelete) ;
    if(genTimeDependent){
      timedepgen->time_generators().find(-1)->second.spline().Write() ;
      timedepgen->time_generators().find(1)->second.spline().Write() ;
    }
    tuplefile.Close() ;
  }
  
  DalitzHistoSet datH = eventList1.histoSet();
  datH.save("plotsFromEventList.root");

  cout << " ampFit done. Took " << (time(0) - startTime)/60. 
       << " min. Returning 0." << endl;

  return 0;
}


int main(){

  return ampFit();

}
//
