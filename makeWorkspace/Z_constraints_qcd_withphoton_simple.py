import ROOT
from counting_experiment import *
from utils.jes_utils import get_jes_variations, get_jes_jer_source_file_for_tf
from utils.general import read_key_for_year, get_nuisance_name
from W_constraints import do_stat_unc, add_variation
# Define how a control region(s) transfer is made by defining *cmodel*, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "qcd_zjets"

def cmodel(cid,nam,_f,_fOut, out_ws, diag, year,convention="BU"):

  # Some setup
  _fin = _f.Get("category_%s"%cid)
  _wspace = _fin.Get("wspace_%s"%cid)

  # ############################ USER DEFINED ###########################################################
  # First define the nominal transfer factors (histograms of signal/control, usually MC
  # note there are many tools available inside include/diagonalize.h for you to make
  # special datasets/histograms representing these and systematic effects
  # example below for creating shape systematic for photon which is just every bin up/down 30%

  metname    = 'particlenet_score'          # Observable variable name

  target             = _fin.Get("signal_qcdzjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_qcdzll")           # defines Zmm MC of which process will be controlled by
  controlmc_e        = _fin.Get("Zee_qcdzll")           # defines Zmm MC of which process will be controlled by
  controlmc_w        = _fin.Get("signal_qcdwjets")
  controlmc_ewk      = _fin.Get('signal_ewkzjets')
  controlmc_photon   = _fin.Get("gjets_qcdgjets")       # defines Gjets MC of which process will be controlled by

  # Create the transfer factors and save them (not here you can also create systematic variations of these
  # transfer factors (named with extention _sysname_Up/Down

  # QCD Z(vv) / Z(mm) transfer factor
  ZmmScales = target.Clone() 
  ZmmScales.SetName("qcd_zmm_weights_%s"%cid)
  ZmmScales.Divide(controlmc)
  _fOut.WriteTObject(ZmmScales)  # always write out to the directory

  # QCD Z(vv) / Z(ee) transfer factor
  ZeeScales = target.Clone() 
  ZeeScales.SetName("qcd_zee_weights_%s"%cid)
  ZeeScales.Divide(controlmc_e)
  _fOut.WriteTObject(ZeeScales)  # always write out to the directory

  # QCD Z(vv) / W(lv) transfer factor
  WZScales = target.Clone() 
  WZScales.SetName("qcd_w_weights_%s"%cid)
  WZScales.Divide(controlmc_w)
  _fOut.WriteTObject(WZScales)  # always write out to the directory

  # QCD Z(vv) / EWK Z(vv)
  EQScales = target.Clone()
  EQScales.SetName("ewkqcd_weights_%s"%cid)
  EQScales.Divide(controlmc_ewk)
  _fOut.WriteTObject(EQScales)  # always write out to the directory

  # QCD Z(vv) / Gamma+jet
  PhotonScales = target.Clone() 
  PhotonScales.SetName("qcd_photon_weights_%s"%cid)
  PhotonScales.Divide(controlmc_photon)
  _fOut.WriteTObject(PhotonScales) # always write out to the directory

  my_function(_wspace,_fin,_fOut,cid,diag, year)

  #######################################################################################################

  _bins = []  # take bins from some histogram, can choose anything but this is easy
  for b in range(target.GetNbinsX()+1):
    _bins.append(target.GetBinLowEdge(b+1))

  # Here is the important bit which "Builds" the control region, make a list of control regions which
  # are constraining this process, each "Channel" is created with ...
  #   (name,_wspace,out_ws,cid+'_'+model,TRANSFERFACTORS)
  # the second and third arguments can be left unchanged, the others instead must be set
  # TRANSFERFACTORS are what is created above, eg WScales

  CRs = [
    Channel("qcd_dimuon",_wspace,out_ws,cid+'_'+model,ZmmScales,convention=convention),
    Channel("qcd_dielectron",_wspace,out_ws,cid+'_'+model,ZeeScales,convention=convention),
    Channel("qcd_wjetssignal",_wspace,out_ws,cid+'_'+model,WZScales,convention=convention),
    Channel("qcd_photon",_wspace,out_ws,cid+'_'+model,PhotonScales,convention=convention),
    Channel("ewkqcd_signal",_wspace,out_ws,cid+'_'+model,EQScales,convention=convention),
  ]
  
  # Veto weight uncertainties on QCD Z(vv) / W(lv)
  CRs[2].add_nuisance('CMS_eff_tauveto_{YEAR}'.format(YEAR=year),     -0.01)

  CRs[2].add_nuisance('CMS_eff_e_idiso_veto_{YEAR}'.format(YEAR=year),  -0.005)
  CRs[2].add_nuisance('CMS_eff_e_reco_veto_{YEAR}'.format(YEAR=year),  -0.01)

  CRs[2].add_nuisance('CMS_eff_m_id_veto', -0.001)
  CRs[2].add_nuisance('CMS_eff_m_iso_veto', -0.002)

  # Pileup uncertainties on ratios
  for i in range(len(CRs)):
    CRs[i].add_nuisance('CMS_pileup', 0.01)
    CRs[i].add_nuisance('CMS_jesTotal', 0.01)
    CRs[i].add_nuisance('CMS_jer_{YEAR}'.format(YEAR=year), 0.01)

  # ############################ USER DEFINED ###########################################################
  # Add systematics in the following, for normalisations use name, relative size (0.01 --> 1%)
  # for shapes use add_nuisance_shape with (name,_fOut)
  # note, the code will LOOK for something called NOMINAL_name_Up and NOMINAL_name_Down, where NOMINAL=WScales.GetName()
  # these must be created and writted to the same dirctory as the nominal (fDir)

  # Bin by bin nuisances to cover statistical uncertainties ...

  # do_stat_unc(ZmmScales,    proc='qcd_zmm',      region='qcd_dimuonCR',     CR=CRs[0], cid=cid, outfile=_fOut)
  # do_stat_unc(ZeeScales,    proc='qcd_zee',      region='qcd_dielectronCR', CR=CRs[1], cid=cid, outfile=_fOut)
  # do_stat_unc(WZScales,     proc='qcd_w',        region='qcd_wzCR',         CR=CRs[2], cid=cid, outfile=_fOut)
  # do_stat_unc(PhotonScales, proc='qcd_photon',   region='qcd_photonCR',     CR=CRs[3], cid=cid, outfile=_fOut)
  # do_stat_unc(EQScales,     proc='ewkqcd',       region='ewkqcdzCR',        CR=CRs[4], cid=cid, outfile=_fOut)

  #######################################################################################################

  # Theory uncertainties on QCD Z(vv) / W(lv)
  CRs[2].add_nuisance("ZnunuWJets_QCD_pdf_vbf", 0.001)
  CRs[2].add_nuisance("ZnunuWJets_QCD_facscale_vbf", 0.03)
  CRs[2].add_nuisance("ZnunuWJets_QCD_renscale_vbf", 0.05)

  # Theory uncertainties on QCD Z(vv) / gamma+jet
  CRs[3].add_nuisance("Photon_QCD_pdf_vbf", 0.001)
  CRs[3].add_nuisance("Photon_QCD_facscale_vbf", 0.03)
  CRs[3].add_nuisance("Photon_QCD_renscale_vbf", 0.05)

  #######################################################################################################

  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,target.GetName(),CRs,diag,convention=convention)
  # Return of course
  return cat

# My Function. Just to put all of the complicated part into one function
def my_function(_wspace,_fin,_fOut,nam,diag, year):

  metname    = "mjj"   # Observable variable name

  target             = _fin.Get("signal_qcdzjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_qcdzll")           # defines Zmm MC of which process will be controlled by
  controlmc_w        = _fin.Get("signal_qcdwjets")
  controlmc_photon   = _fin.Get("gjets_qcdgjets")

  #################################################################################################################


  #################################################################################################################
  WSpectrum      = controlmc_w.Clone(); WSpectrum.SetName("qcd_w_spectrum_%s_"%nam)
  ZvvSpectrum    = target.Clone(); ZvvSpectrum.SetName("qcd_zvv_spectrum_%s_"%nam)
  PhotonSpectrum = controlmc_photon.Clone(); PhotonSpectrum.SetName("qcd_gjets_spectrum_%s_"%nam)

  _fOut.WriteTObject( WSpectrum )
  _fOut.WriteTObject( PhotonSpectrum )
  #_fOut.WriteTObject( ZvvSpectrum ) No need to rewrite