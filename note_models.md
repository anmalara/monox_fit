- [1. Overview of what is done when running `generate_combine_model.py`:](#1-overview-of-what-is-done-when-running-generate_combine_modelpy)
  - [1.1. Addition of nuisances in `cmodel`](#11-addition-of-nuisances-in-cmodel)
    - [1.1.1. List of nuisances](#111-list-of-nuisances)
    - [1.1.2. Difference with monojet models](#112-difference-with-monojet-models)
  - [1.2. Overview of `init_channels`](#12-overview-of-init_channels)
  - [1.3. Overview of `convert_to_combine_workspace`](#13-overview-of-convert_to_combine_workspace)
- [2. In depth look into the old model construction scripts](#2-in-depth-look-into-the-old-model-construction-scripts)
  - [2.1. Looking inside `Z_constraints_qcd_withphoton.py`](#21-looking-inside-z_constraints_qcd_withphotonpy)
    - [2.1.1. inside `my_function`:](#211-inside-my_function)
    - [2.1.2. back to `cmodel`](#212-back-to-cmodel)
  - [2.2. Recap of `Z_constraints_qcd_withphoton.py`:](#22-recap-of-z_constraints_qcd_withphotonpy)
  - [2.3. Recap of `W_constraints.py`:](#23-recap-of-w_constraintspy)
  - [2.4. Recap of `Z_constraints_ewk_withphoton.py`:](#24-recap-of-z_constraints_ewk_withphotonpy)
  - [2.5. Recap of `W_constraints.py`:](#25-recap-of-w_constraintspy)
- [3. What are `Category`, `Channel` and `Bin` doing?](#3-what-are-category-channel-and-bin-doing)
  - [3.1. `Category`](#31-category)
  - [3.2. `Channel`](#32-channel)
  - [3.3. `Bin`](#33-bin)
  - [3.4. What is happening in `runModel.py` when doing `cn.init_channels()`?](#34-what-is-happening-in-runmodelpy-when-doing-cninit_channels)
  - [3.5. What is happening in `convert_to_combine_workspace`?](#35-what-is-happening-in-convert_to_combine_workspace)
- [4. What is a `RooParametricHist` ?](#4-what-is-a-rooparametrichist-)
  - [4.1. 🧠 **Core Idea**](#41--core-idea)
  - [4.2. 📦 **Key Components**](#42--key-components)
    - [4.2.1. Member Variables:](#421-member-variables)
  - [4.3. 🔨 **Constructor Behavior**](#43--constructor-behavior)
  - [4.4. ⚙️ **Main Methods**](#44-️-main-methods)
    - [4.4.1. `evaluate()`:](#441-evaluate)
    - [4.4.2. `evaluatePartial()`:](#442-evaluatepartial)
    - [4.4.3. `evaluateFull()`:](#443-evaluatefull)
    - [4.4.4. `evaluateMorphFunction(int bin)`:](#444-evaluatemorphfunctionint-bin)
  - [4.5. 📈 **Morphing Support**](#45--morphing-support)
  - [4.6. 🧮 **Integral Support**](#46--integral-support)
  - [4.7. 🧩 **Utility Methods**](#47--utility-methods)
  - [4.8. 🔍 Summary](#48--summary)
  - [4.9. ✅ `evaluatePartial()`](#49--evaluatepartial)
    - [4.9.1. 📌 What it does:](#491--what-it-does)
    - [4.9.2. 🔍 Code:](#492--code)
    - [4.9.3. 🔎 Step-by-step:](#493--step-by-step)
  - [4.10. ✅ `evaluateFull()`](#410--evaluatefull)
    - [4.10.1. 📌 What it does:](#4101--what-it-does)
    - [4.10.2. 🔍 Code:](#4102--code)
    - [4.10.3. 🔎 Step-by-step:](#4103--step-by-step)
  - [4.11. ✅ `evaluateMorphFunction(int bin_index)`](#411--evaluatemorphfunctionint-bin_index)
    - [4.11.1. 📌 What it does:](#4111--what-it-does)
    - [4.11.2. 🔍 Code:](#4112--code)
    - [4.11.3. 🔎 Step-by-step:](#4113--step-by-step)
  - [4.12. 🧠 Example Summary](#412--example-summary)

# 1. Overview of what is done when running `generate_combine_model.py`:

This script is where all processes are expressed as a product of transfer factors, nuisances, and parametrized by the same process,
$Z^{\text{QCD}}_{\text{SR}}\to \nu\nu$.

There are three main function calls:
   1. `cmodel`, The model construction scripts
      - This is run for each "model", containing a "target process" 
         (e.g. $Z^{\text{QCD}}_{\text{SR}}\to \nu\nu$ or $W^{\text{EWK}}_{\text{SR}}\to l\nu$) and a list of "control processes".
      - For each control process, it computes a transfer factors, ratio of the yield of the target process and control process.
      - It creates the parameters for the relevant nuisances for each transfer factor 
         (veto, JES/JER, theory, and statistical uncertainties) in the workspace.
   2. `init_channels`:
      - makes the modeled yield of events in each bin as a function of $(Z^{\text{QCD}}_{\text{SR}}\to \nu\nu)$:
         - $(Z^{\text{QCD}}_{\text{SR}}\to \nu\nu) \times \frac{CR}{Z^{\text{QCD}}_{\text{SR}}\to \nu\nu} \times \Pi^{nuis}_{CR}{(1+nuis)}$ 
         for channels in `qcd_zjets` model
         - $(Z^{\text{QCD}}_{\text{SR}}\to \nu\nu) \times \frac{Z^{\text{EWK}}_{\text{SR}}\to \nu\nu}{Z^{\text{QCD}}_{\text{SR}}\to \nu\nu} \times \Pi^{nuis}_{Z^{\text{EWK}}_{\text{SR}}\to \nu\nu}{(1+nuis)} \times \frac{Z^{\text{EWK}}_{\text{diMuon CR}} \to ll}{Z^{\text{EWK}}_{\text{SR}}\to \nu\nu} \times \Pi^{nuis}_{Z^{\text{EWK}}_{\text{diMuon CR}} \to ll}{(1+nuis)}$ 
         for channels in `ewk_zjets` `qcd_wjets` and `ewk_wjets` models
   3. `convert_tocombine_workspace`:
      - stores the distribution of modeled yields above in `RooParametricHist`s and saves them to the workspace

## 1.1. Addition of nuisances in `cmodel`

These are the steps performed when adding a nuisances `nuis` for a given transfer factor:
   - We check if a parameter for this nuisance already exist in the workspace. If not, we create and import the following:
      - The nuisance parameter `nuis`, with its value at 0, and a range of +- 3
      - A constraints named `const_{nuis}`, a gaussian centered at 0 with a sigma of 1
   - A nuisance can either affect all bins uniformely or each bin with a different shape.
   - Each bin of the distribution affected by the nuisance is assigned a function:
      - `sys_function_{nuis}_cat_vbf_2018_{model}_ch_{channel}_bin_{b}`
      - The effect of the function is `nuis * size` is the same for each bin of the process.
         So for a given process, the effect of the nuisance is uniform across all bins. 
      - Different processes can be affect by the same nuisance `nuis`, and with different strenght `size`.
   - Shape nuisances are similar, but need the up and down variations computed beforehand:
      - When adding the shape nuisance, we first fetch the variations called `{channel}_weights_vbf_2018_{nuis}_(Up|Down)`
      - For each bin, the effect of function is 
         $\left(1 + \frac{\Delta(\text{variation up}, \text{variation down})}{2 \times \text{nominal}}\right)^{\pm \text{nuisance}} - 1$
      - The exponant is $+nuisance$ if $\Delta(\text{variation up}, \text{variation down}) > 0$,
         $-nuisance$ if $\Delta(\text{variation up}, \text{variation down}) < 0$,

### 1.1.1. List of nuisances 

The following nuisances are created for each model (for the vbf case):
   - veto:
      - `"CMS_veto2018_e "`
      - `"CMS_veto2018_m "`
      - `"CMS_veto2018_t"`
   - JES/JER (shape):
      - `"jer_2018"`
      - `"jesAbsolute"`
      - `"jesAbsolute_2018"`
      - `"jesBBEC1"`
      - `"jesBBEC1_2018"`
      - `"jesEC2"`
      - `"jesEC2_2018"`
      - `"jesFlavorQCD"`
      - `"jesHF"`
      - `"jesHF_2018"`
      - `"jesRelativeBal"`
      - `"jesRelativeSample_2018"`
   - Theory (shape): 
      - QCD, PDF: `{qcd_label}_{var[1]}_vbf` 
         - `qcd_label` is `"(Photon|ZnunuWJets)_{QCD|EWK}"`
         - `var[1]` is in `["facscale", "pdf", "renscale"]`
         - e.g. `"Photon_EWK_facscale_vbf"`
      - EWK: `{ewk_label}_vbf_bin{b}`
         - `ewk_label` is in `["qcd_ewk", "qcd_photon_ewk", "ewk_ewk", "ewkphoton_ewk"]`
   - Stastistical (shape): `"vbf_2018_stat_error_{region}_bin{b}"`

### 1.1.2. Difference with monojet models

In the monojet script, things are a little different
   - vetos uncertainties are a shape nuisance (read from some systematics file templats)
   - there are trigger shape nuisances
   - there are electron/photon id shape nuisances
   - there are photon scale shape nuisances
   - there are prefiring shape nuisances

## 1.2. Overview of `init_channels`

Once all of theses nuisances are created for all models (qcd z, ewk z, qcd w, ewk w), `init_channels` is ran on each model:

   - We extract one (any) histogram, whose shape will be used as a reference 
      (the mjj bin edges, should be the same for all distributions)
   - We go through every `Channel` in the model
      - For each bin, we create a `Bin` object. This contains:
         - The bin edges
         - some ID to link it to other channels in other models
         - The initial yield for that mjj bin for the target process of that model
         ( so either $Z^{\text{QCD}}_{\text{SR}}\to \nu\nu$, $Z^{\text{EWK}}_{\text{SR}}\to \nu\nu$,
            $W^{\text{QCD}}_{\text{SR}}\to l\nu$ or $W^{\text{EWK}}_{\text{SR}}\to l\nu$)
         - The transfer factor $\frac{\text{control process}}{\text{target process}}$ for that process in that bin.
            - This way, the control process can be expressed as target process $\times$ transfer factor, and parametrized by the target process
            - This is stored as a constant `RooRealVar` `sfactor_cat_vbf_2018_{model}_ch_{channel_name}_bin_{b}`
         - Model the expected number of events.
            - At initialization, two cases:
               - For `qcd_zjets` model, RooRealVar `model_mu_cat_vbf_2018_{model}_bin_{b}` whose value is set to the QCD Znunu (SR) yield, in a range from 0 to 3 times the yield.
               - For other models, it fetches `pmu_cat_vbf_2018_qcd_zjets_bin_{b}`,  (see below)
            - Make the product of all nuisances:
               - Fetch each nuisance `nuis` , and create a `delta` function that has the formula `1+nuis`
               `delta_cat_vbf_2018_{model}_ch_{channel}_bin_{b}_{nuis}`
               - Only nuisances affecting the bin are added (so theory EWK and statistical uncertainties, decorrelated by bin, each contribute one nuisance; contributions for the other bins are skipped).
            - make `pure_mu`: two cases:
               - For `qcd_zjets`, product of `model_mu_cat_vbf_2018_{model}_bin_{b}`, `sfactor_cat_vbf_2018_{model}_ch_{channel_name}_bin_{b}` and all nuisances
               - For all other categories, product of `pmu_cat_vbf_2018_qcd_zjets_bin_{b}`, `sfactor_cat_vbf_2018_{model}_ch_{channel_name}_bin_{b}` and all nuisances

            - In other words, we have, for each bin, 
            $(Z^{\text{QCD}}_{\text{SR}}\to \nu\nu) \times \frac{CR}{Z^{\text{QCD}}_{\text{SR}}\to \nu\nu} \times \Pi^{nuis}_{CR}{(1+nuis)}$ 
            for each CR in the `qcd_zjets` model:
               - $Z^{\text{QCD}}_{\text{diMuon CR}} \to ll$
               - $Z^{\text{QCD}}_{\text{diElectron CR}} \to ll$
               - $W^{\text{QCD}}_{\text{SR}} \to l\nu$
               - $(\gamma + \text{jets})^{\text{QCD}}_{\text{SR}}$
               - $Z^{\text{EWK}}_{\text{SR}} \to \nu\nu$
            - For the other models, we fetch the previous expression from the channel the are linked to, and multiply to
            $\frac{CR}{target} \times \Pi^{nuis}_{CR}{(1+nuis)}$ 
            - For instance, in the `ewk_zjets` model, the target is $Z^{\text{EWK}}_{\text{SR}}\to \nu\nu$, we are linked to the corresponding CR in `qcd_zjets`. If we look for instance at the $Z^{\text{EWK}}_{\text{diMuon CR}} \to ll$ CR, this ends up with
            $(Z^{\text{QCD}}_{\text{SR}}\to \nu\nu) \times \frac{Z^{\text{EWK}}_{\text{SR}}\to \nu\nu}{Z^{\text{QCD}}_{\text{SR}}\to \nu\nu} \times \Pi^{nuis}_{Z^{\text{EWK}}_{\text{SR}}\to \nu\nu}{(1+nuis)} \times \frac{Z^{\text{EWK}}_{\text{diMuon CR}} \to ll}{Z^{\text{EWK}}_{\text{SR}}\to \nu\nu} \times \Pi^{nuis}_{Z^{\text{EWK}}_{\text{diMuon CR}} \to ll}{(1+nuis)}$ 
            - This is save as `pmu_cat_vbf_2018_{model}_bin_{b}`, and also wrapped in the `RooFormulaVar` `mu_cat_vbf_2018_{model}_bin_{b}`
            - The `"observed"` is fetched, and a Poisson PDF is constructed for `observed` using `mu_cat_vbf_2018_{model}_bin_{b}`.
               It is uncleared where `observed` comes from
         - Once this modelling is done for all bins, save all prefit distributions
         - The last step is unclear, maybe a check that all expected distribution exist.
## 1.3. Overview of `convert_to_combine_workspace`
This is where the all distribution used for combine are saved to the workspace.

   - We extract one (any) histogram, whose shape will be used as a reference (`samplehist`)
      (the mjj bin edges, should be the same for all distributions)
   - We extract `mjj`, rename to `mjj_vbf_2018`
   - Convert every histogram `hist` from the input file (`limit_vbf.root`) to a `RooDataHist` called `vbf_2018_{hist}`, as a function of `mjj_vbf_2018` and add it to the workspace
   - Loop over every `Category` (as in "model", qcd zjets, qcd wjets, ewk zjets, ewk wjets):
      - fetch `model_mu_cat_vbf_2018_{model}_bin_{b}` for every bin
      - Only for `qcd_zjets`  model, create the signal distribution:
         - Create a `RooParametricHist` with name `vbf_2018_signal_qcd_zjets_model`, holding the distribution of all
            `model_mu_cat_vbf_2018_{model}_bin_{b}` for every bin as a function of `mjj_vbf_2018` (with shape given by `samplehist`)
         - Create addition of expectations `vbf_2018_signal_qcd_zjets_model_norm` (integral of previous `RooParametricHist` over the whole `mjj` range)
         - import these in the workspace
      - Loop for every `Channel` in the model to get all backgrounds:
         - Create a `RooParametricHist` with name `vbf_2018_{channel}_{model}_model`, holding the distribution of all
            `pmu_cat_vbf_2018_ch_{model}_bin_{b}` for every bin as a function of `mjj_vbf_2018` (with shape given by `samplehist`)
         - Create addition of expectations `vbf_2018_{channel}_{model}_model_norm` (integral of previous `RooParametricHist` over the whole `mjj` range)
         - import these in the workspace
   - Get all parameters in the workspace
   - for all background nuisances: print the line to add in the datacard template, `{param.GetName()} param {param.getVal()} 1`

# 2. In depth look into the old model construction scripts

 some notes of what is being done in each model construction script for vbf:
   - Z_constraints_qcd_withphoton.py
   - W_constraints_qcd.py
   - Z_constraints_ewk_withphoton.py
   - W_constraints_ewk.py

## 2.1. Looking inside `Z_constraints_qcd_withphoton.py`

Inputs:
   - Target process, the one that is used to parametrize the control samples
     - QCD $Z \to \nu\nu$ in SR
   - Control MC samples: 
      - $Z \to \mu\mu$ in diMuon
      - $Z \to ee$ in diElectron
      - QCD $W \to l\nu$ in SR
      - EWK $Z \to \nu\nu$ in SR
      - QCD $\gamma$ + jets samples in SR


Compute all transfer factors: for each control sample, compute target divided by control

### 2.1.1. inside `my_function`:
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

### 2.1.2. back to `cmodel`

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

## 2.2. Recap of `Z_constraints_qcd_withphoton.py`:
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

## 2.3. Recap of `W_constraints.py`:
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

## 2.4. Recap of `Z_constraints_ewk_withphoton.py`:
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

## 2.5. Recap of `W_constraints.py`:
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

# 3. What are `Category`, `Channel` and `Bin` doing?

## 3.1. `Category`

## 3.2. `Channel`

A `Channel` object holds:
   - A transfer factor (ratio of yields from two different processes)
   - an input and an output `RooWorkspace` containting nuisances
   - A name, and some IDs to link to `Category` and `Bin`

And two methods are defined to add:
   - a nuisances that applies on all bins (normalization?)
   - a shape nuisance (quadratic or lognorm, I think we only use quadratic)

The model construction script run create different channels and add relevent nuisances
for veto, JES/JER, theory systematics as well as statistical uncertainties

## 3.3. `Bin`

bin content of transfer factor, edges, id of category and control region
Bin.cr holds the full `Channel` object

## 3.4. What is happening in `runModel.py` when doing `cn.init_channels()`?
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
      - `Bin.sfactor` is a RooRealVar `sfactor_cat_vbf_2018_{model}_ch_{channel_name}_bin_{b}` holding previous value (for qcd zjets, qcd dimuon, 0.104)
      - no range( +-INF), constant
      - TODO: why the use of `ROOT.RooFit.RecycleConflictNodes()`?
   - "Setup expected var", this is where dependences are handled
      - Case of no dependence:
         - initialize `model_mu`, a RooRealVar `model_mu_cat_vbf_2018_{model}_bin_{b}`
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
         - named `pmu_cat_vbf_2018_{model}_ch_{channel}_bin_{b}`
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

## 3.5. What is happening in `convert_to_combine_workspace`?

   - open the workspace, 
   - For every "category" (as in the year, here `vbf_2018`)
      - open the input directory containing the histograms
      - extract the binning and varname by fetching the first histogram it can find in the directory
         - Varname is taken from histogram.GetXaxis().GetTitle(). This is why all histograms in input file need to have title set to `"mjj"`
      - extract mjj from workspace (RooRealVar `varl`, vary from 200 to 6000, lowest and highest edges in distribution)
      - rename variable to mjj_vbf_2018 
      - Loop over all histograms in directory
         - if integral is 0, set first bin to something small to avoid errors in combine TODO is this needed?
         - Create RooDataHist `vbf_2018_{histogram.GetName()}` holding the distribution of the histogram along one dimension for mjj_vbf_2018
         - Import the RooDataHist in combine workspace
      - for every `Category` (as in "model", qcd zjets, qcd wjets, ewk zjets, ewk wjets):
         - import the model
         - initialize RooArgList of expectations
         - fetch `model_mu_cat_vbf_2018_{model}_bin_{b}` for every bin, add it to list of expectations.
         - Only for `qcd_zjets`  model:
            - **This if for the signal**
            - Create phist, [RooParametricHist](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/main/interface/RooParametricHist.h)
            (custom class inheriting from RooAbsPdf, see also in `src/HiggsAnalysis/CombineLimits`) with name `vbf_2018_signal_qcd_zjets_model`, RooRealVar `varl` (_x), RooArgList `expectations` (_pars), TH1 `samplehist` (_shape)
               - Histogram that holds the distribution of `expectations` (the expected number of events), with the binning provided by `samplehist` (only used for its shape),
                  and will evaluate the distribution based on the value of `varl` (in this case `mjj_vbf_2018`), it will look on the relevent bin of mjj, and return yield / bin width * nuisances
            - crate addition of expectations `vbf_2018_signal_qcd_zjets_model_norm`
            - import these in the workspace
         - loop again for every `Category` (TODO: is this really needed)
            - check that model name matches the one imported previously, else continue
            - for every `Channel` in the model, create the background distributions:
               - Fetch every `pmu_cat_vbf_2018_{model}_ch_{channel}_bin_{b}`
               - for every bin in the channel:
                  - add expectation of bin to list of expectation of the channel, using the "`pure_mu`" (from `Bin.setup_expect_var`)
               - We obtain list of `pure_mu` expectation for every bin in that channel
               - create p_phist, RooParametricHist with name `vbf_2018_{channel}_{model}_model`, RooRealVar `varl` (`mjj_vbf_2018`, `_x`), RooArgList `cr_expectations` (`_pars`) and `_shape` `samplehist`
               - create addition of expectations `vbf_2018_{channel}_{model}_model_norm`
               - import these in the workspace
   - We are done now out of  every loop
   - Get all parameters in the workspace
   - for all background nuisances: print the line to add in the datacard template, `{param.GetName()} param {param.getVal()} 1`




      
# 4. What is a `RooParametricHist` ?

ChatGPT's explaination of the code:

This `RooParametricHist` class is a **custom RooFit probability density function (PDF)** implemented in C++. It models a **binned histogram-like PDF**, where the bin contents are **free parameters**, and optionally supports **"morphing"** to smoothly interpolate between systematic variations. Here's a detailed breakdown of what it does and how it works:

---

## 4.1. 🧠 **Core Idea**
The class defines a PDF where:
- The shape is determined by a histogram (`TH1`) with a number of bins.
- Each bin has an associated **parameter** that represents its content (normalized).
- The PDF is evaluated based on which bin the observable `x` falls into.
- Optional: it can **morph** bin values based on nuisance parameters, used to model systematic uncertainties.

---

## 4.2. 📦 **Key Components**

### 4.2.1. Member Variables:
- `x`: The observable (like `mass`, `pt`, etc.).
- `pars`: A list of parameters, each representing the bin content (as a `RooAbsReal`).
- `bins`, `widths`: Vectors holding the bin edges and widths from the input histogram.
- `_coeffList`: Morphing coefficients (nuisance parameters).
- `_sums`, `_diffs`: Data structures for storing the shape variation due to morphing.
- `_hasMorphs`: Flag to enable morphing.
- `_cval`: Cached last value of the PDF.

---

## 4.3. 🔨 **Constructor Behavior**
```cpp
RooParametricHist::RooParametricHist(const char *name, const char *title, RooAbsReal& _x, RooArgList& _pars, const TH1 &_shape)
```
- Sets up the histogram-like structure using the shape of `TH1`.
- Validates that number of parameters matches the number of bins.
- Initializes bin edges and widths.

---

## 4.4. ⚙️ **Main Methods**

### 4.4.1. `evaluate()`:
- Main function called by RooFit to evaluate the PDF.
- Calls either:
  - `evaluateFull()` if morphing is enabled.
  - `evaluatePartial()` otherwise.
- Normalizes by bin width.
- Returns the PDF value at current `x`.

### 4.4.2. `evaluatePartial()`:
- Determines the bin `x` falls into.
- Returns the corresponding parameter value, normalized by bin width.

### 4.4.3. `evaluateFull()`:
- Same as `evaluatePartial`, but also applies **morphing factors** to the bin value.

### 4.4.4. `evaluateMorphFunction(int bin)`:
- Computes a scale factor to apply to a bin’s parameter based on current values of morph parameters (`_coeffList`).
- Uses `_diffs` and `_sums` to smoothly morph the bin content.

---

## 4.5. 📈 **Morphing Support**
```cpp
void RooParametricHist::addMorphs(RooDataHist &hpdfU, RooDataHist &hpdfD, RooRealVar &cVar, double smoothRegion)
```
- Adds one morphing parameter.
- Computes the "up" and "down" variations of each bin, relative to the nominal.
- Stores difference and sum terms for smooth interpolation.

---

## 4.6. 🧮 **Integral Support**
Implements:
```cpp
Double_t analyticalIntegral(Int_t code, const char* rangeName) const
```
- Computes analytical integrals over a range (needed for RooFit normalization).
- Sums only the relevant part of bins that fall within the specified range.

---

## 4.7. 🧩 **Utility Methods**
- `getBinVar(i)`: Returns the i-th parameter (for bin i).
- `getAllBinVars()`: Returns all bin parameters.
- `getFullSum()`: Sums up all bin values (with morphing if active).

---

## 4.8. 🔍 Summary

**RooParametricHist** is:
- A **parametric PDF** whose shape is defined by a histogram template.
- Each bin content is a **free parameter** (`pars[i]`).
- Optionally **morphable** using systematic variations (e.g., nuisance parameters).
- Useful for **template morphing**, **histogram fitting**, and **statistical interpretations** like limits or likelihood scans in High Energy Physics analyses.

---

If you'd like, I can draw a diagram of how it works or help you use it in a RooFit workspace. Let me know what you’re working on!

Further explation of the evaluation methods:

Absolutely! Let's walk through each of those functions—`evaluatePartial`, `evaluateFull`, and `evaluateMorphFunction`—in **clear, beginner-friendly C++ explanations**. These are central to how the `RooParametricHist` class computes the value of the PDF.

---

## 4.9. ✅ `evaluatePartial()`

### 4.9.1. 📌 What it does:
This function is used when **morphing is not enabled**. It finds the bin where the current observable value `x` lies, retrieves the corresponding bin parameter (from `pars`), and returns the normalized value for that bin.

### 4.9.2. 🔍 Code:
```cpp
double RooParametricHist::evaluatePartial() const
{
  auto it = std::upper_bound(std::begin(bins), std::end(bins), x);
  if ( it == std::begin(bins) ) {
    // underflow
    return 0;
  }
  else if ( it == std::end(bins) ) {
    // overflow
    return 0;
  }
  size_t bin_i = std::distance(std::begin(bins), it) - 1;
  RooAbsReal *retVar = (RooAbsReal*)pars.at(bin_i);

  double ret = retVar->getVal();
  ret /= widths[bin_i];
  return ret;
}
```

### 4.9.3. 🔎 Step-by-step:
1. **Find bin:** Uses `std::upper_bound` to find the first bin edge that is *greater than* the current value of `x`. This tells us which bin `x` falls into.
2. **Check edge cases:**
   - If `x` is less than the first bin edge → return 0 (underflow).
   - If `x` is greater than the last bin edge → return 0 (overflow).
3. **Get bin index:** Subtract 1 to get the actual bin index.
4. **Get parameter:** Get the corresponding parameter for that bin: `pars.at(bin_i)`.
5. **Normalize by bin width:** Divide by the bin width to get the probability density.
6. **Return result.**

---

## 4.10. ✅ `evaluateFull()`

### 4.10.1. 📌 What it does:
Used when **morphing is enabled**. This is similar to `evaluatePartial`, but it applies a **morphing correction factor** to the bin content.

### 4.10.2. 🔍 Code:
```cpp
double RooParametricHist::evaluateFull() const
{
  int bin_i;
  if (x < bins[0]) return 0;
  else if (x >= bins[N_bins]) return 0;

  else {
    for (bin_i=0; bin_i<N_bins; bin_i++) {
      if (x >= bins[bin_i] && x < bins[bin_i+1]) break;
    }
  }
  double mVar = evaluateMorphFunction(bin_i);
  RooAbsReal *retVar = (RooAbsReal*)pars.at(bin_i);

  double ret = retVar->getVal() * mVar;
  ret /= widths[bin_i];
  return ret;
}
```

### 4.10.3. 🔎 Step-by-step:
1. **Check range:**
   - If `x` is before the first bin → return 0.
   - If `x` is past the last bin → return 0.
2. **Find bin index:** Iterate through bins to find the one where `x` falls between `bins[bin_i]` and `bins[bin_i+1]`.
3. **Apply morphing:** Call `evaluateMorphFunction(bin_i)` to get a scale factor for this bin.
4. **Get parameter:** Get the corresponding parameter from `pars`.
5. **Multiply and normalize:** Multiply the parameter by the morph scale, then divide by bin width.
6. **Return result.**

---

## 4.11. ✅ `evaluateMorphFunction(int bin_index)`

### 4.11.1. 📌 What it does:
Computes a **morphing scale factor** for a given bin. This lets the bin content be adjusted (scaled) based on **nuisance parameters** like shape uncertainties.

### 4.11.2. 🔍 Code:
```cpp
double RooParametricHist::evaluateMorphFunction(int j) const
{
    double scale = 1.0;
    if (!_hasMorphs) return scale;

    int ndim = _coeffList.getSize();
    double f0 = static_cast<RooAbsReal*>(pars.at(j))->getVal();

    for (int i = 0; i < ndim; ++i) {
        double x = (dynamic_cast<RooRealVar*>(_coeffList.at(i)))->getVal();
        double a = 0.5 * x;
        double b = smoothStepFunc(x);  // smooth transition
        scale *= 1 + (1.0 / f0) * a * (_diffs[j][i] + b * _sums[j][i]);
    }

    return scale;
}
```

### 4.11.3. 🔎 Step-by-step:
1. **Skip if no morphing:** If morphing isn’t enabled, return scale = 1 (no effect).
2. **Loop over morphing parameters (`_coeffList`):**
   - Get the current value of each nuisance parameter `x`.
   - Compute a morphing term using `_diffs` and `_sums`, which represent up/down variations in the shape.
   - Multiply `scale` by a factor that adjusts the bin value.
3. **Return scale factor** that can be applied to the bin.

---

## 4.12. 🧠 Example Summary

Let’s say:
- You have 3 bins: `[0, 10), [10, 20), [20, 30)`
- Parameters `p0`, `p1`, `p2` correspond to those bins.
- `x = 12` → falls in bin 1
- PDF value = `p1 / bin_width`

If morphing is on:
- PDF value = `p1 * morph_scale / bin_width`

---

Let me know if you'd like a **Python translation** of this logic or a **visual diagram**!
