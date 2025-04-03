# Model construction scripts

Taking some notes of what is being done in each model construction script for vbf:
   - Z_constraints_qcd_withphoton.py
   - W_constraints_qcd.py
   - Z_constraints_ewk_withphoton.py
   - W_constraints_ewk.py

## Looking inside `Z_constraints_qcd_withphoton.py`

Inputs:
   - Process to model (called target): QCD $Z \to \nu\nu$ in SR
   - Control MC samples: 
      - $Z \to \mu\mu$ in diMuon
      - $Z \to ee$ in diElectron
      - QCD $W \to l\nu$ in SR
      - EWK $Z \to \nu\nu$ in SR
      - QCD $\gamma$ + jets samples in SR


Compute all transfer factors: for each control sample, compute target divided by control

### inside `my_function`:
Getting theory uncertainties

compute ( (QCD Z->nunu) / (QCD W->lnu) ) * theory uncertainty (for each uncertainty) (yields from SR)
   (qcd, pdf)

compute ewk decorrelated among bins:
    - Create one clone of (QCD Z->nunu / QCD W->lnu) for each bin
    - each clone i get only bin i replace with bin i of (QCD Z->nunu / QCD W->lnu) * ewk uncertainty

Same computations for (QCD Z->nunu / QCD gamma+jets):
   - qcd
   - pdf
   - ewk, decorrelated among bins

### back to `cmodel`

extract binning of mjj

Create one "Channel" by transfer factor

For Znunu/Wlnu channel: add nuisances for vetos,
`RooFormulaVar` corresponding to vetoname * value:
   - `CMS_veto{YEAR}_t * -0.01`
   - `CMS_veto{YEAR}_m * -0.015`
   - `CMS_veto{YEAR}_e * -0.03`

Extract JER and JES uncertainties for transfer factors from `sys/vbf_jes_jer_tf_uncs.root`:
   - for each variation 
   - for transfer factor (except Znunu QCD / EWK):
   - Add histogram for Transfer factor  * variation uncertainty in output
      (variation uncertainty for transfer factor is a histogram with one bin,
      and the whole transfer factor distribution get Scaled according to the value in this one bin)
   - Add function (quadratic) to model systematic uncertainty on transfer factor

add variation from statistic uncertainty + quadratic model

add variation from theory uncertainties + quadratic model (qcd, pdf, ewk decorellated, both for Z/W and Z/gamma+jet)

Return everything as `Category` called `qcd_zjets`

## Recap of `Z_constraints_qcd_withphoton.py`:
   - Compute transfer factors:
      - `Zmm`: QCD $Z \to \nu\nu$ (SR) / $Z \to \mu\mu$ (diMuon)
      - `Zee`: QCD $Z \to \nu\nu$ (SR) / $Z \to ee$ (diElectron)
      - `WZ`: QCD $Z \to \nu\nu$ / QCD $W \to l\nu$ (both in SR)
      - `EQ`: QCD $Z \to \nu\nu$ / EWK $Z \to \nu\nu$ (both in SR)
      - `Photon`: QCD $Z \to \nu\nu$ / QCD $\gamma$ + jets (both in SR)
   - For `WZ` and `Photon`:
      - Extract Transfer factor  * theory uncertainties for QCD, PDF and EWK
      - Decorrelate EWK uncertainties bin by bin
      - Add (quadratic) function to model the theory uncertainties
   - For `WZ`: add nuisances for vetos (veto * value)
   - For `Zmm`, `Zee`, `WZ`, `Photon`:
      - Extract extract JER/JES (relative) uncertainties for each source
      - Add variation corresponding to Transfer factor scaled by relative uncertainty
      - Add (quadratic) function to model the systematic uncertainty
   - For all transfer factors:
      - Add variation from the statistical uncertainty
      - Add (quadratic) function to model the statistical uncertainty
   - Return everything as `Category` called `qcd_zjets`

## Recap of `W_constraints.py`:
   - Compute transfer factors:
      - `Wmu`: QCD $W \to l\nu$ (SR) / $W \to \mu\nu$ (singleMuon)
      - `We`: QCD $W \to l\nu$ (SR) / $W \to e\nu$ (singleElectron)
   - For both `Wmu` and `We`:
      - JER/JES uncertainties:
         - Extract extract JER/JES (relative) uncertainties for each source
         - Add variation corresponding to Transfer factor scaled by relative uncertainty
         - Add (quadratic) function to model the systematic uncertainty
      - Add nuisances for vetos (veto * value)
      - Statistical uncertainties:
         - Add variation from the statistical uncertainty
         - Add (quadratic) function to model the statistical uncertainty
   - Return everything as `Category` called `qcd_wjets` and specify it is dependant on `WZ` transfer factor of previous `qcd_zjets` category

## Recap of `Z_constraints_ewk_withphoton.py`:
   - Compute transfer factors:
      - `Zmm`: EWK $Z \to \nu\nu$ (SR) / $Z \to \mu\mu$ (diMuon)
      - `Zee`: EWK $Z \to \nu\nu$ (SR) / $Z \to ee$ (diElectron)
      - `WZ`: EWK $Z \to \nu\nu$ / EWK $W \to l\nu$ (both in SR)
      - `Photon`: EWK $Z \to \nu\nu$ / EWK $\gamma$ + jets (both in SR)
   
   - For `WZ` and `Photon`:
      - Extract Transfer factor  * theory uncertainties for QCD, PDF and EWK
      - Decorrelate EWK uncertainties bin by bin
      - Add (quadratic) function to model the theory uncertainties
   - For `WZ`: add nuisances for vetos (veto * value)
   - For all transfer factors:
      - JER/JES uncertainties:
         - Extract extract JER/JES (relative) uncertainties for each source
         - Add variation corresponding to Transfer factor scaled by relative uncertainty
         - Add (quadratic) function to model the systematic uncertainty
      - Statistical uncertainties:
         - Add variation from the statistical uncertainty
         - Add (quadratic) function to model the statistical uncertainty
   - Return everything as `Category` called `ewk_zjets` and specify it is dependant on `EQ` transfer factor of previous `qcd_zjets` category

## Recap of `W_constraints.py`:
   - Compute transfer factors:
      - `Wmu`: EWK $W \to l\nu$ (SR) / $W \to \mu\nu$ (singleMuon)
      - `We`: EWK $W \to l\nu$ (SR) / $W \to e\nu$ (singleElectron)
   - For both `Wmu` and `We`:
      - JER/JES uncertainties:
         - Extract extract JER/JES (relative) uncertainties for each source
         - Add variation corresponding to Transfer factor scaled by relative uncertainty
         - Add (quadratic) function to model the systematic uncertainty
      - Add nuisances for vetos (veto * value)
      - Statistical uncertainties:
         - Add variation from the statistical uncertainty
         - Add (quadratic) function to model the statistical uncertainty
   - Return everything as `Category` called `ewk_wjets` and specify it is dependant on `WZ` transfer factor of previous `ewk_zjets` category

# What are `Category`, `Channel` and `Bin` doing?

## `Category`

## `Channel`

A `Channel` object holds:
   - A transfer factor (ratio of yields from two different processes)
   - an input and an output `RooWorkspace` containting nuisances
   - A name, and some IDs to link to `Category` and `Bin`

And two methods are defined to add:
   - a nuisances that applies on all bins (normalization?)
   - a shape nuisance (quadratic or lognorm, I think we only use quadratic)

The model construction script run create different channels and add relevent nuisances
for veto, JES/JER, theory systematics as well as statistical uncertainties

## `Bin`

bin content of transfer factor, edges, id of category and control region
Bin.cr holds the full `Channel` object

## What is happening in `runModel.py` when doing `cn.init_channels()`?
Loop over categories, do `Category.init_channels()`

Loop over control regions (`Channel`s)

Loop over each bin:
   - extract the edges
   - initialize `Bin` object, link it to control region (using id)
   - set categoryname "bin_number"
   - initialize Y value of bin based on target dataset of this control region:
      ``` 
      INIT Y:  
      mjj>=200.0 && mjj<400.0
      self.rngename = rnge_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0 (a name given to the var in setRange, for later acces)
      self.wspace = Name: wspace_vbf_2018 Title: wspace_vbf_2018
      self.wspace.data(mcdataset) = Name: signal_qcdzjets Title: DataSet - vbf_2018, signal_qcdzjets
      mcdataset = signal_qcdzjets
      ```
   - In other words, value of bin is initialized to mjj yield of category (qcd z, qcd w, ewk z or ewk w)
   - Get "scale factor" (rather transfer factor) for that control region: 
      - given by 1 / cr.scalefactor
      - following exemple in qcd_zjets category, qcd_dimuon channel 
      - transfer factor is qcd Znunu (SR) / qcd Zll (dimuon CR)
      - transfer factor = 20087 / 2097 = 9.577
      - ret_scalefactor gives 1/9.577 = 0.104 (so qcd Zll (dimuon) / qcd Znunu (SR))
   - Set "scale factor":
      - `Bin.sfactor` is a RooRealVar `f"sfactor_cat_vbf_2018_{model}_ch_{channel_name}_bin_{b}"` holding previous value (for qcd zjets, qcd dimuon, 0.104)
      - no range( +-INF), constant
      - TODO: why the use of `ROOT.RooFit.RecycleConflictNodes()`?
   - "Setup expected var", this is where dependences are handled
      - Case of no dependence:
         - initialize `model_mu`, a RooRealVar `f"model_mu_cat_vbf_2018_{model}_bin_{b}"`
         - value: yield of target process (eg qcd Znunu SR)
         - range: from 0 to 3 times yield
      - Case of a dependence:
         - initialize `model_mu` as `pure_mu` from the channel it depends on (number of expected event in the channel it depends on, see bellow)
      - arglist: `model_mu` and `sfactor`
      - fetch nuisances (JES/JER, veto, theory, stat)
      - initialize empty `RooArgList` for nuisances `nuis_args`
      - for each nuisance:
         - get formula of nuisance in that bin, put it in a new `RooArgList`
         - get "`delta`", `RooFormulaVar` giving `1+nuisance`
         - add `delta` to `nuis_args`
         - write `delta` to the workspack
         - in systematic has no effect on the bin (sf up - sf down = 0), in `Channel.add_nuisance_shape`, nuisance is marked as `"temp"` and will not
            be skipped here, so not added to the `nuis_args`. This is likely the case for nuisances that are decorrelated by bins (stat and ewk theory) for bins they don't act on
         - resulting list of nuisances for qcd_dimuon channel in qcd_zjets:
         ```
         RooFormulaVar::delta_cat_vbf_2018_qchttps://root.cern.ch/doc/master/namespaceTMath.html#a9cef8a9eac06254be610bd64b03106d0d_zjets_ch_qcd_dimuon_bin_0_jesBBEC1_2018[ actualVars=(sys_function_jesBBEC1_2018_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesRelativeSample_2018[ actualVars=(sys_function_jesRelativeSample_2018_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesBBEC1[ actualVars=(sys_function_jesBBEC1_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesFlavorQCD[ actualVars=(sys_function_jesFlavorQCD_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesRelativeBal[ actualVars=(sys_function_jesRelativeBal_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jer_2018[ actualVars=(sys_function_jer_2018_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesEC2_2018[ actualVars=(sys_function_jesEC2_2018_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesHF_2018[ actualVars=(sys_function_jesHF_2018_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesAbsolute_2018[ actualVars=(sys_function_jesAbsolute_2018_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesEC2[ actualVars=(sys_function_jesEC2_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesHF[ actualVars=(sys_function_jesHF_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_jesAbsolute[ actualVars=(sys_function_jesAbsolute_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1
         RooFormulaVar::delta_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0_vbf_2018_stat_error_qcd_dimuonCR_bin0[ actualVars=(sys_function_vbf_2018_stat_error_qcd_dimuonCR_bin0_cat_vbf_2018_qcd_zjets_ch_qcd_dimuon_bin_0) formula="1+@0" ] = 1 
         ```
      - make product of deltas
      - add product to `arglist` (so now arglist is model_mu (yield of qcd znunu), sfactor (qcd znunu / qcd zmumu) and product of delta)
      - "`pure_mu`" is a formula for number of expected (signal) events in the bin, given by product of everything in arglist, so yield * transfer factor * effect of nuisances
      - "`mu`" is the same ? Number of expected events in the bin, but I don't see any difference with `pure_mu`
      -  add `mu` to the workspace (adds dependencies as well)
      - note about the dependant case: `pure_mu` will can be re-used by other channels. For instance all channels in the `Category` qcd_wjets depend on the qcd_w channel (qcd znunu in SR / qcd wlnu in SR) in qcd_zjets.
         In that case, for instance for the qcd_wmunu channel (qcd wln SR / qcd wln (singlemuon CR)) will initialize its `arglist` with the `pure_mu` of qcd_w. we and up with:
            pure_mu(qcd_w) * sfactor(qcd_wmunu) = (yield (= qcd znunu) * sfactor (= qcd wlnu / qcd znunu) * product of nuisances in qcd_w ) * sfactor (= qcd wmunu / qcd wlnu)
            that finaly can be simplified to yield of qcd wmunu * product of nuisance in qcd_w

            To this we will further add the product of nuisances in qcd_wmunu
      
      - get `observed` (not sure where this is passed)
      - build [poisson PDF](https://root.cern.ch/doc/master/namespaceTMath.html#a9cef8a9eac06254be610bd64b03106d0) from `observed` and `mu`
   - set_initE: returns 0
   - add_to_dataset: does nothing
- Save prefit distributions
- TODO: Last step is unclear, is it a check that all expected distribution exist?
