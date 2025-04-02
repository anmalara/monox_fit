import ROOT
from typing import Any
from utils.generic.logger import initialize_colorized_logger

ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
logger = initialize_colorized_logger("INFO")


def convert_to_combine_workspace(
    wsin_combine: ROOT.RooWorkspace,
    f_simple_hists: ROOT.TFile,
    category: str,
    cmb_categories: list[Any],
    controlregions_def: list[str],
    rename_variable: str = "",
) -> None:
    """Converts histograms into RooDataHists and RooParametricHist models and adds them to the RooWorkspace.

    Args:
        wsin_combine (ROOT.RooWorkspace): Target workspace to import objects into.
        f_simple_hists (ROOT.TFile): File containing category histograms and workspaces.
        categories (list[str]): List of analysis categories (e.g., ['vbf_2017']).
        cmb_categories (list[Any]): Combined categories with control region info.
        controlregions_def (list[str]): List of CR Python modules to import.
        rename_variable (str): Optional renaming of the observable variable.
    """
    wsin_combine.loadSnapshot("PRE_EXT_FIT_Clean")

    cat = category
    fdir = f_simple_hists.Get(f"category_{cat}")
    wlocal = fdir.Get(f"wspace_{cat}")

    # Identify observable variable and template histogram
    samplehist = None
    for key in fdir.GetListOfKeys():
        obj = key.ReadObj()
        if isinstance(obj, (ROOT.TH1D, ROOT.TH1F)):
            samplehist = obj
            break

    if not samplehist:
        logger.critical(f"No valid histogram found for category {cat}.", exception_cls=RuntimeError)

    nbins = samplehist.GetNbinsX()
    varname = samplehist.GetXaxis().GetTitle()

    logger.info(varname)
    varl = wlocal.var(varname)
    logger.info("VAR NAME {varl.GetName()} {rename_variable}")

    if rename_variable:
        varl.SetName(rename_variable)
    else:
        # import a Renamed copy of the variable ...
        varl.SetName(f"{varname}_{cat}")

    # Import all valid histograms in the category
    for key in fdir.GetListOfKeys():
        obj = key.ReadObj()
        logger.info(f"{obj.GetName()}, {obj.GetTitle()}, {type(obj)}")
        if not isinstance(obj, (ROOT.TH1D, ROOT.TH1F)):
            continue
        if obj.Integral() <= 0:
            obj.SetBinContent(1, 1e-4)
        name = obj.GetName()
        logger.info(f"Importing histogram {name} for category {cat}")
        dhist = ROOT.RooDataHist(f"{cat}_{name}", f"DataSet - {cat}, {name}", ROOT.RooArgList(varl), obj)
        wsin_combine._import(dhist)

    # Add in the V-jets backgrounds MODELS
    for crn in controlregions_def:
        cr_def = __import__(crn)

        # Parametric model expectations
        expectations = ROOT.RooArgList()
        for b in range(nbins):
            var = wsin_combine.var(f"model_mu_cat_{cat}_{cr_def.model}_bin_{b}")
            expectations.add(var)

        # TODO
        if (not ("wjet" in cr_def.model)) and (not ("ewk" in cr_def.model)):
            phist = ROOT.RooParametricHist(
                f"{cat}_signal_{cr_def.model}_model", f"Model Shape for {cr_def.model} in Category {cat}", varl, expectations, samplehist
            )
            norm = ROOT.RooAddition(f"{phist.GetName()}_norm", f"Total number of expected events in {phist.GetName()}", expectations)
            wsin_combine._import(phist)
            wsin_combine._import(norm)

        # Add control region models
        for cn in cmb_categories:
            logger.info(f"CHECK {cn.catid} {cn.cname}")
            if cn.catid != f"{cat}_{cr_def.model}" or cn.cname != crn:
                continue

            for cr in cn.ret_control_regions():
                cr_expectations = ROOT.RooArgList()
                for b in range(nbins):
                    binstr = f"bin{b + 1}" if "MTR" in rename_variable else f"bin_{b}"
                    func = wsin_combine.function(f"pmu_cat_{cat}_{cr_def.model}_ch_{cr.chid}_{binstr}")
                    cr_expectations.add(func)

                model_name = f"{cat}_{cr.crname}_{cr_def.model}_model"
                logger.info(f"Building CR model: {model_name}")
                cr_expectations.Print()
                print("Look here", samplehist.GetNbinsX(), cr_expectations.getSize())
                cr_phist = ROOT.RooParametricHist(
                    model_name,
                    f"Expected Shape for {cr.crname} in control region in Category {cat}",
                    varl,
                    cr_expectations,
                    samplehist,
                )
                cr_norm = ROOT.RooAddition(f"{cr_phist.GetName()}_norm", "Total number of expected events in {cr_phist.GetName()}", cr_expectations)
                wsin_combine._import(cr_phist)
                wsin_combine._import(cr_norm)

    # Log external nuisance parameters
    allparams = ROOT.RooArgList(wsin_combine.allVars())
    for i in range(allparams.getSize()):
        par = allparams.at(i)
        if not par.getAttribute("NuisanceParameter_EXTERNAL"):
            continue
        if par.getAttribute("BACKGROUND_NUISANCE"):
            continue  # these aren't in fact used for combine
        logger.info(f"External nuisance parameter: {par.GetName()} = {par.getVal():.3f}")
