import ROOT
from counting_experiment import *
from utils.jes_utils import get_jes_variations, get_jes_jer_source_file_for_tf
from utils.general import read_key_for_year, get_nuisance_name
from W_constraints import do_stat_unc, add_variation
# Define how a control region(s) transfer is made by defining *cmodel*, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "ewk_zjets"

def cmodel(cid,nam,_f,_fOut, out_ws, diag, year, variable, convention="BU"):

  # Some setup
  _fin = _f.Get("category_%s"%cid)
  _wspace = _fin.Get("wspace_%s"%cid)

  # ############################ USER DEFINED ###########################################################
  # First define the nominal transfer factors (histograms of signal/control, usually MC
  # note there are many tools available inside include/diagonalize.h for you to make
  # special datasets/histograms representing these and systematic effects
  # example below for creating shape systematic for photon which is just every bin up/down 30%

  metname    = variable           # Observable variable name

  target             = _fin.Get("signal_ewkzjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_ewkzll")           # defines Zmm MC of which process will be controlled by
  controlmc_e        = _fin.Get("Zee_ewkzll")           # defines Zmm MC of which process will be controlled by
  controlmc_w        = _fin.Get("signal_ewkwjets")
  controlmc_g        = _fin.Get("gjets_ewkgjets")

  # Create the transfer factors and save them (not here you can also create systematic variations of these
  # transfer factors (named with extention _sysname_Up/Down

  # EWK Z(vv) / Z(mm)
  ZmmScales = target.Clone() 
  ZmmScales.SetName("ewk_zmm_weights_%s"%cid)
  ZmmScales.Divide(controlmc)
  _fOut.WriteTObject(ZmmScales)  # always write out to the directory

  # EWK Z(vv) / Z(ee)
  ZeeScales = target.Clone() 
  ZeeScales.SetName("ewk_zee_weights_%s"%cid)
  ZeeScales.Divide(controlmc_e)
  _fOut.WriteTObject(ZeeScales)  # always write out to the directory

  # EWK Z(vv) / W(lv)
  WZScales = target.Clone()
  WZScales.SetName("ewk_w_weights_%s"%cid)
  WZScales.Divide(controlmc_w)
  _fOut.WriteTObject(WZScales)  # always write out to the directory

  # EWK Z(vv) / gamma+jets
  PhotonScales = target.Clone() 
  PhotonScales.SetName("ewk_photon_weights_%s"%cid)
  PhotonScales.Divide(controlmc_g)
  _fOut.WriteTObject(PhotonScales)


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
    Channel("ewk_dimuon",_wspace,out_ws,cid+'_'+model,ZmmScales,convention=convention),
    Channel("ewk_dielectron",_wspace,out_ws,cid+'_'+model,ZeeScales,convention=convention),
    Channel("ewk_wjetssignal",_wspace,out_ws,cid+'_'+model,WZScales,convention=convention),
    Channel("ewk_photon",_wspace,out_ws,cid+'_'+model,PhotonScales,convention=convention),
  ]

  # Veto weight uncertainties on Z / W
  CRs[2].add_nuisance('CMS_eff_tauveto_{YEAR}'.format(YEAR=year),     -0.01)
  
  CRs[2].add_nuisance('CMS_eff_e_idiso_veto_{YEAR}'.format(YEAR=year),  -0.005)
  CRs[2].add_nuisance('CMS_eff_e_reco_veto_{YEAR}'.format(YEAR=year),  -0.01)

  CRs[2].add_nuisance('CMS_eff_m_id_veto', -0.001)
  CRs[2].add_nuisance('CMS_eff_m_iso_veto', -0.002)

  # Pileup uncertainties on ratios
  for i in range(len(CRs)):
    CRs[i].add_nuisance('CMS_pileup', 0.01)
    CRs[i].add_nuisance('CMS_jesTotalUnc', 0.01)
    CRs[i].add_nuisance('CMS_jer_{YEAR}'.format(YEAR=year), 0.01)

  # ############################ USER DEFINED ###########################################################
  # Add systematics in the following, for normalisations use name, relative size (0.01 --> 1%)
  # for shapes use add_nuisance_shape with (name,_fOut)
  # note, the code will LOOK for something called NOMINAL_name_Up and NOMINAL_name_Down, where NOMINAL=WScales.GetName()
  # these must be created and writted to the same dirctory as the nominal (fDir)

  # Bin by bin nuisances to cover statistical uncertainties ...

  # do_stat_unc(ZmmScales,    proc='ewk_zmm',      region='ewk_dimuonCR',     CR=CRs[0], cid=cid, outfile=_fOut)
  # do_stat_unc(ZeeScales,    proc='ewk_zee',      region='ewk_dielectronCR', CR=CRs[1], cid=cid, outfile=_fOut)
  # do_stat_unc(WZScales,     proc='ewk_w',        region='ewk_wzCR',         CR=CRs[2], cid=cid, outfile=_fOut)
  # do_stat_unc(PhotonScales, proc='ewk_photon',   region='ewk_photonCR',     CR=CRs[3], cid=cid, outfile=_fOut)

  #######################################################################################################

  # Theory uncertainties on EWK Z(vv) / W(lv)
  CRs[2].add_nuisance("ZnunuWJets_EWK_pdf_vbf", 0.001)
  CRs[2].add_nuisance("ZnunuWJets_EWK_facscale_vbf", 0.03)
  CRs[2].add_nuisance("ZnunuWJets_EWK_renscale_vbf", 0.05)

  # Theory uncertainties on EWK Z(vv) / gamma+jet
  CRs[3].add_nuisance("Photon_EWK_pdf_vbf", 0.001)
  CRs[3].add_nuisance("Photon_EWK_facscale_vbf", 0.03)
  CRs[3].add_nuisance("Photon_EWK_renscale_vbf", 0.05)

  #######################################################################################################

  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,target.GetName(),CRs,diag,convention=convention)
  # cat.setDependant("qcd_zjets","ewkqcd_signal")
  # Return of course
  return cat


# My Function. Just to put all of the complicated part into one function
def my_function(_wspace,_fin,_fOut,nam,diag, year):

  metname    = "mjj"   # Observable variable name

  target             = _fin.Get("signal_ewkzjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_ewkzll")           # defines Zmm MC of which process will be controlled by

  controlmc_w        = _fin.Get("signal_ewkwjets")
  controlmc_photon   = _fin.Get("gjets_ewkgjets")

  WSpectrum = controlmc_w.Clone(); WSpectrum.SetName("ewk_w_spectrum_%s_"%nam)
  ZvvSpectrum    = target.Clone(); ZvvSpectrum.SetName("ewk_zvv_spectrum_%s_"%nam)
  PhotonSpectrum = controlmc_photon.Clone(); WSpectrum.SetName("ewk_photon_spectrum_%s_"%nam)

  _fOut.WriteTObject( WSpectrum )
  _fOut.WriteTObject( PhotonSpectrum )
  #_fOut.WriteTObject( ZvvSpectrum ) No need to rewrite