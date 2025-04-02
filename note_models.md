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