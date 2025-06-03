#!/bin/env python3
from plotter.plot_prefit_postfit import plot_prefit_postfit
from plotter.plot_data_validation import plot_data_validation
from plotter.plot_ratio import plot_ratio
from plotter.plot_diff_nuis import plot_diff_nuis


def main() -> None:
    lumi = {
        2017: 41.5,
        2018: 59.7,
        "Run3": 62.5,
    }
    regions = ["singlemuon", "dimuon", "gjets", "singleelectron", "dielectron", "signal"]
    procs = ["zmm", "zee", "w_weights", "photon", "wen", "wmn"]
    region_pairs = [
        # Flavor integrated
        ("combined", "gjets"),
        ("combinedW", "gjets"),
        ("combined", "combinedW"),
        # Split by flavor
        ("dimuon", "singlemuon"),
        ("dielectron", "singleelectron"),
        ("singleelectron", "gjets"),
        ("singlemuon", "gjets"),
        ("dielectron", "gjets"),
        ("dimuon", "gjets"),
    ]

    # years = [2017, 2018]
    # years = [2017]
    # years = [2018]
    years = ["Run3"]

    for year in years:
        ws_filename = "./root/ws_monojet.root"
        category = f"monojet_{year}"
        outdir = f"./plots/{year}/"
        fitdiag_file = f"diagnostics/fitDiagnostics_{category}.root"
        diffnuis_file = f"diagnostics/diffnuisances_{category}.root"
        common_args = {"category": category, "outdir": outdir, "lumi": lumi[year], "year": year}

        for region in regions:
            plot_prefit_postfit(region=region, ws_filename=ws_filename, fitdiag_file=fitdiag_file, **common_args)
        for proc in procs:
            plot_ratio(process=proc, model_filename="root/combined_model_monojet.root", **common_args)

        for region1, region2 in region_pairs:
            plot_data_validation(region1=region1, region2=region2, ws_filename=ws_filename, fitdiag_filename=fitdiag_file, **common_args)

        plot_diff_nuis(diffnuis_file=diffnuis_file, outdir=outdir, category=category)


if __name__ == "__main__":
    main()

    # ### Years fit together
    # # for tag in ["","_unblind"]:
    # for tag in [""]:
    #     outdir = "plots/combined{tag}".format(tag=tag)
    #     diffnuis_file = "diagnostics/diffnuisances_monojet{tag}_combined.root".format(tag=tag)
    #     plot_nuis(diffnuis_file, outdir)

    #     for year in [2017]:
    #         ws_filename = "root/ws_monojet.root".format(year=year)
    #         fitdiag_file = "diagnostics/fitDiagnostics_monojet{tag}_combined.root".format(year=year, tag=tag)
    #         category = "monojet_{year}".format(year=year)
    #         outdir = "./plots/combined_{year}{tag}/".format(year=year, tag=tag)
    #         for region in regions:
    #             plotPreFitPostFit(region, category, ws_filename, fitdiag_file, outdir, lumi[year], year)
