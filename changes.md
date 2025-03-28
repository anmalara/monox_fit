process_vbf.sh:
   - only running the configuration of one year (2018) instead of both 2017 and 2018
   - not running configuration for IC

convert.py:
  - I cannot remember why I did this change:
  ```
  103c103
  <             if (not ("wjet" in x.model)) and (not ("ewk" in x.model)):
  ---
  >             if not ("wjet" in x.model):
  ```

makeWorkspace/counting_experiment.py: 
   - putting high limit on nuisance for model_mu_cat_vbf_2017_...

makeWorkspace/make_ws.py:
   -  `key_valid = lambda x: (tag in x) and (not "jesTotal" in x)  # , keynames`, syntax difference from `python2`?
     `filter(key_valid, keynames)` is called later anyway
   - Not attempting to get signal theory variations for vbf (not present for `makeWorkspace/sys/signal_theory_unc.root`)
   - Not attempting to get photon id variations for vbf (not present for `makeWorkspace/sys/photon_id_unc.root`)
   - Not attempting to get mistag variations for vbf (not present for `makeWorkspace/sys/mistag_sf_variations.root`)

plotter/plot_datavalidation.py:
   - `is` -> `==`, syntax difference from `python2` ?

plotter/plot_diffnuis.py:
   - number of nuisances per plots?

plotter/plot_PreFitPostFit.py
   - `is` -> `==`, syntax difference from `python2` ?

plotter/plot_ratio.py
   - CoM 13TeV -> 13.6TeV in figures

vbf/scripts/make_plots.py:
   - Lumi in plots

vbf/scripts/diagnostic.sh:
   - running only 2018
   - removed mask on SR (we are using pseudo-data)
   - plotting all nuisances (even the ones which are unchanged w.r.t. pre-fit values.)
   - not running combined 2017+2018

vbf/scripts/impacts.sh:
   - running only 2018
   - changed some options (mirroring impacts_condor script)
   - using asimov toys

vbf/scripts/limits.sh:
   - running only 2018
   - not running the "nophoton" configuration
   - saving toys
   - not running combined 2017+2018

vbf/scripts/make_cards.sh
   - running only 2018
   - changed template to use
   - not running combined 2017+2018
   - not running configuration for IC

vbf/templates/vbf_template_debug.txt:
   - copied from vbf_template_pretty_withphotons.txt
   - removed 1 process: qcd
   - qcd removed from signal region, single muon, single electron
      - removed shape uncertainties for that process
   - different number of bins