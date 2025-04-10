import ROOT  # type: ignore
from counting_experiment import naming_convention
from utils.workspace.generic import safe_import

ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")


def convertToCombineWorkspace(wsin_combine, f_simple_hists, categories, cmb_categories, controlregions_def, renameVariable=""):
    # wsout_combine = ROOT.RooWorkspace("mono-x-ws","mono-x-ws")
    # wsout_combine._import = getattr(wsout_combine,"import") # workaround: import is a python keyword
    # wsin_combine = f_combined_model.Get("combinedws")
    wsin_combine.loadSnapshot("PRE_EXT_FIT_Clean")

    # Loop over all years
    for icat, cat in enumerate(categories):
        # Pick up the category folder
        fdir = f_simple_hists.Get(f"category_{cat}")
        wlocal = fdir.Get(f"wspace_{cat}")

        # pick up the number of bins FROM one of the usual guys
        # initialize samplehist with the first histogram we find in the directory, then break out of the loop
        # samplehist is only passed to initialized the shape of the RooParametricHist
        samplehistos = fdir.GetListOfKeys()
        for s in samplehistos:
            obj = s.ReadObj()
            if not type(obj) in [ROOT.TH1D, ROOT.TH1F]:
                continue
            # if obj.GetTitle() != "base": continue # Forget all of the histos which aren't the observable variable
            samplehist = obj
            break
        nbins = samplehist.GetNbinsX()
        varname = samplehist.GetXaxis().GetTitle()

        # Fetch the mjj variable, rename it to vbf_{year}_mjj
        print(wlocal, varname)
        varl = wlocal.var(varname)
        print("VAR NAME", varl.GetName(), renameVariable)

        if renameVariable != "":
            varl.SetName(renameVariable)

        else:
            # import a Renamed copy of the variable ...
            varnameext = f"{varname}_{cat}"
            varl.SetName(varnameext)

        # Keys in the fdir
        # Same thing as samplehistos actually
        keys_local = fdir.GetListOfKeys()

        # Loop other all the histograms in the input file,
        # convert them to RooDataHist (as a function of mjj) and
        # save them to the workspace
        for key in keys_local:
            obj = key.ReadObj()
            print(obj.GetName(), obj.GetTitle(), type(obj))
            if not type(obj) in [ROOT.TH1D, ROOT.TH1F]:
                continue
            title = obj.GetTitle()
            # if title != "base": continue # Forget all of the histos which aren't the observable variable
            name = obj.GetName()
            if not obj.Integral() > 0:
                # otherwise Combine will complain!
                obj.SetBinContent(1, 0.0001)
            print("Creating Data Hist for ", name)
            # RooDataHist containing distribution of obj along dimension varl
            dhist = ROOT.RooDataHist(f"{cat}_{name}", f"DataSet - {cat}, {name}", ROOT.RooArgList(varl), obj)
            # dhist.Print("v")
            safe_import(workspace=wsin_combine, obj=dhist)

        # next Add in the V-jets backgrounds MODELS
        # Loop over all models (`Category` objects) and all their "control regions" (`Channel` objects)
        # to fetch the expected number of events (parametrized by QCD Znunu in SR and nuisances) for all process
        # and store them as RooParametricHist in the workspace
        for crd, crn in enumerate(controlregions_def):
            # check the category
            x = __import__(crn)

            # Possible to save histograms in the CR def so loop over those that are booked
            # This will not execute for vbf
            try:
                len(x.convertHistograms)
                for obj in x.convertHistograms:
                    name = obj.GetName()
                    print("Creating Data Hist for ", name)
                    dhist = ROOT.RooDataHist(f"{cat}_{name}", f"DataSet - {cat}, {name}", ROOT.RooArgList(varl), obj)
                    # dhist.Print("v")
                    safe_import(workspace=wsin_combine, obj=dhist)
            except:
                print("No explicit additional convertHistograms defined")

            # This part is to extract the process that is used to parametrize all the others,
            # so for vbf, this is QCD Znunu in SR
            # First, we fetch the expected number of events in every bin, then convert them to a RooParametricHist and save it to the workspace
            expectations = ROOT.RooArgList()
            for b in range(nbins):
                # naming_convention(b, cat+'_'+x.model, "IC" if "MTR" in renameVariable else "BU")))
                expectations.add(wsin_combine.var(f"model_mu_cat_{cat}_{x.model}_bin_{b}"))

            if (not ("wjet" in x.model)) and (not ("ewk" in x.model)):
                phist = ROOT.RooParametricHist(f"{cat}_signal_{x.model}_model", f"Model Shape for {x.model} in Category {cat}", varl, expectations, samplehist)
                phist_norm = ROOT.RooAddition(f"{phist.GetName()}_norm", f"Total number of expected events in {phist.GetName()}", expectations)
                safe_import(workspace=wsin_combine, obj=phist)
                safe_import(workspace=wsin_combine, obj=phist_norm)

            # now loop through the "control regions" for this guy
            # This part is to extract all other processes parametrized by QCD Znunu in SR,
            # convert and save them to RooParametricHist in the workspace
            for cid, cn in enumerate(cmb_categories):
                print("CHECK", cn.catid, cn.cname)
                # TODO: we are already looping through every model,
                # is this loop really needed? We are continuing
                # if we don't match the imported model anyway
                if cn.catid != cat + "_" + x.model:
                    continue
                if cn.cname != crn:
                    continue
                # Loop over all process in the category
                for cr in cn.ret_control_regions():
                    chid = cr.chid
                    cr_expectations = ROOT.RooArgList()
                    # Fetch the expected number of events for the process for every bin, paramertized by QCD Znunu in SR and nuisances
                    for b in range(nbins):
                        if "MTR" in renameVariable:
                            cr_expectations.add(wsin_combine.function(f"pmu_cat_{cat}_{x.model}_ch_{cr.chid}_bin{b + 1}"))
                        else:
                            cr_expectations.add(wsin_combine.function(f"pmu_cat_{cat}_{x.model}_ch_{cr.chid}_bin_{b}"))

                    print(f"{cat}_{cr.crname}_{x.model}_model")
                    cr_expectations.Print()
                    # Convert the distribution to RooParametricHist, save to the workspace
                    p_phist = ROOT.RooParametricHist(
                        f"{cat}_{cr.crname}_{x.model}_model",
                        f"Expected Shape for {cr.crname} in control region in Category {cat}",
                        varl,
                        cr_expectations,
                        samplehist,
                    )
                    p_phist_norm = ROOT.RooAddition(f"{p_phist.GetName()}_norm", f"Total number of expected events in {p_phist.GetName()}", cr_expectations)
                    safe_import(workspace=wsin_combine, obj=p_phist)
                    safe_import(workspace=wsin_combine, obj=p_phist_norm)

    # This is the part that prints what parameters should added at the end of the datacard (e.g. the statistical uncertainty for each bin of each process)
    allparams = ROOT.RooArgList(wsin_combine.allVars())
    for pi in range(allparams.getSize()):
        # for par in allparams:
        par = allparams.at(pi)
        if not par.getAttribute("NuisanceParameter_EXTERNAL"):
            continue
        if par.getAttribute("BACKGROUND_NUISANCE"):
            continue  # these aren't in fact used for combine
        print(par.GetName(), "param", par.getVal(), "1")
    # print "Done -- Combine Ready Workspace inside ",fout.GetName()
