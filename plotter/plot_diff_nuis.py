#!/usr/bin/env python3
import os
import math
import ROOT as rt  # type: ignore


def get_nbins(canvas):
    nbins = 0
    for item in canvas.GetListOfPrimitives():
        try:
            print(item)
            nbins = item.GetNbinsX()
        except:
            continue
    return nbins


def plot_diff_nuis(fname, outdir):
    if not os.path.exists(fname):
        raise IOError("Input file does not exist: " + fname)
    rt.gStyle.SetOptStat(0)

    f = rt.TFile(fname)

    canvas = f.Get("nuisances")

    canvas.SetBottomMargin(0.4)
    canvas.SetRightMargin(0.02)
    canvas.SetLeftMargin(0.02)
    canvas.SetTopMargin(0.05)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    name = os.path.basename(fname).replace(".root", "").replace("diffnuisances_", "")

    # Derive the splitting
    nbins = get_nbins(canvas)  # total bins
    perplot = 30  # optimal bins per plot
    rest = nbins % perplot  # bins in the last plot
    nplots = int(math.ceil(float(nbins) / perplot))

    # If there are too few in the last plot, just
    # redistribute to the earlier plots
    if rest < 0.2 * perplot:
        nplots = nplots - 1
        perplot = perplot + int(math.ceil(float(rest)) / nplots)

    for i in range(nplots + 1):
        for item in canvas.GetListOfPrimitives():
            try:
                item.GetXaxis().SetRangeUser(i * perplot, (i + 1) * perplot)
                item.GetXaxis().SetLabelSize(0.03)
                item.LabelsOption("v")
                item.SetTitle(f"Nuisances {name} {i}")
            except:
                pass

            try:
                item.SetBBoxX1(600)
                item.SetBBoxY1(1)
                item.SetBBoxY2(75)
            except AttributeError:
                pass
        canvas.Draw()
        canvas.SetCanvasSize(1200, 600)
        # for extension in ["png", "pdf"]:
        for extension in ["pdf"]:
            canvas.SaveAs(os.path.join(outdir, f"diffnuis_{name}_{i}.{extension}"))
