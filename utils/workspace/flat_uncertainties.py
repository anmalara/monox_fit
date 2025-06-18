from typing import Any


def get_processes(analysis: str, region: str, type: str) -> list[str]:
    """Return the list of processes for a given analysis, region, and type."""
    processes = {
        "vbf": {
            "signal": {
                "signals": ["zh", "wh", "vbf", "ggh"],
                "models": ["qcd_zjets", "qcd_wjets", "ewk_zjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "dimuon": {
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "diboson"],
            },
            "dielec": {
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "diboson"],
            },
            "singlemu": {
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "singleel": {
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "photon": {
                "models": ["qcd_gjets", "ewk_gjets"],
            },
        },
        # TODO: "monojet": {...}
    }

    return processes.get(analysis, {}).get(region, {}).get(type, [])


def get_region_label_map() -> list[tuple[str, str]]:
    return [
        ("dielec", "Zee"),
        ("dimuon", "Zmm"),
        ("signal", "signal"),
        ("singleel", "Wen"),
        ("singlemu", "Wmn"),
        ("photon", "gjets"),
    ]


def get_region_model_map() -> dict[str, list[tuple[str, str]]]:
    return {
        "dielec": [("ewk_zll", "ewk_dielectron_ewk_zjets"), ("qcd_zll", "qcd_dielectron_qcd_zjets")],
        "dimuon": [("ewk_zll", "ewk_dimuon_ewk_zjets"), ("qcd_zll", "qcd_dimuon_qcd_zjets")],
        "signal": [
            ("ewk_wjets", "ewk_wjetssignal_ewk_zjets"),
            ("ewk_zjets", "ewkqcd_signal_qcd_zjets"),
            ("qcd_wjets", "qcd_wjetssignal_qcd_zjets"),
            ("qcd_zjets", "signal_qcd_zjets"),
        ],
        "singleel": [("ewk_wjets", "ewk_singleelectron_ewk_wjets"), ("qcd_wjets", "qcd_singleelectron_qcd_wjets")],
        "singlemu": [("ewk_wjets", "ewk_singlemuon_ewk_wjets"), ("qcd_wjets", "qcd_singlemuon_qcd_wjets")],
        "photon": [("ewk_gjets", "ewk_photon_ewk_zjets"), ("qcd_gjets", "qcd_photon_qcd_zjets")],
    }


def get_flat_uncertainties(process: str) -> dict[str, float]:
    return {
        "zmm": {"pu": 0.01, "id": 0.01, "trigger": 0.01},
        "zee": {"pu": 0.01, "id": 0.03, "trigger": 0.005},
        "photon": {"pu": 0.01, "id": 0.015, "trigger": 0.01},
        "w": {"pu": 0.01},
        "wen": {"pu": 0.01, "id": 0.015, "trigger": 0.01},
        "wmn": {"pu": 0.01, "id": 0.005, "trigger": 0.01},
    }[process]


def get_veto_uncertainties(model: str) -> dict[str, float]:
    # TODO split or with the same name?
    return {
        # VBF
        "ewk_wjets": {"t": 0.01, "m": 0.02, "e": 0.03},
        "qcd_wjets": {"t": 0.01, "m": 0.015, "e": 0.03},
        "ewk_zjets": {"t": -0.01, "m": -0.02, "e": -0.03},
        "qcd_zjets": {"t": -0.01, "m": -0.015, "e": -0.03},
        # Mono
        "wjets": {"t": 0.01, "m": 0.015, "e": 0.03},
        "zjets": {"t": -0.01, "m": -0.015, "e": -0.03},
    }[model]


def get_stat_unc_list(year: str, analysis: str, nbins: int) -> list[str]:
    """Return a list of bin-by-bin statistical uncertainty nuisance names for a given year and analysis."""
    regions = [
        "qcd_dimuonCR",
        "qcd_dielectronCR",
        "qcd_wzCR",
        "qcd_photonCR",
        "ewkqcdzCR",
        "qcd_singlemuon",
        "qcd_singleelectron",
        "ewk_dimuonCR",
        "ewk_dielectronCR",
        "ewk_wzCR",
        "ewk_photonCR",
        "ewk_singlemuon",
        "ewk_singleelectron",
    ]
    ratio_labels = ["qcd_ewk", "qcd_photon_ewk", "ewk_ewk", "ewkphoton_ewk"]

    nuisances = [f"{analysis}_{year}_stat_error_{region}_bin{i}" for region in regions for i in range(nbins)]
    nuisances += [f"{ratio}_{analysis}_bin{i}" for ratio in ratio_labels for i in range(nbins)]
    return nuisances


def get_theory_unc_list(year: str, analysis: str) -> list[str]:
    """Return a list of theory uncertainty nuisance names for a given analysis and year."""
    _ = year  # Currently unused

    ratios = ["ZnunuWJets", "Photon"]
    modes = ["QCD", "EWK"]
    uncertainties = ["renscale", "facscale", "pdf"]

    return [f"{ratio}_{mode}_{unc}_{analysis}" for ratio in ratios for mode in modes for unc in uncertainties]


def get_lumi_uncertainties(year: str, analysis: str) -> dict[str, Any]:
    """Return luminosity lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    # All processes (signal + backgrounds), except models
    proc_list = ["zh", "wh", "vbf", "ggh", "diboson", "top", "qcdzll", "ewkzll"]
    return {
        "Run3": {
            "lumi_13TeV_XY": {"value": 1.02, "processes": proc_list},
            "lumi_13TeV_LS": {"value": 1.002, "processes": proc_list},
            "lumi_13TeV_BBD": {"value": 1.0, "processes": proc_list},
            "lumi_13TeV_DB": {"value": 1.0, "processes": proc_list},
            "lumi_13TeV_BCC": {"value": 1.02, "processes": proc_list},
            "lumi_13TeV_GS": {"value": 1.00, "processes": proc_list},
            "lumi_13TeV_$ERA": {"value": 1.015, "processes": proc_list},
        },
    }[year]


def get_lepton_veto_list(year: str, analysis: str) -> list[str]:
    """Return a list of lepton veto nuisance parameter names for a given year and analysis."""
    _ = analysis  # Currently unused
    return [f"CMS_veto{year}_{lepton}" for lepton in ["t", "m", "e"]]


def get_lepton_efficiency_uncertainties(year: str, analysis: str) -> dict[str, Any]:
    """Return lepton efficiency lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "CMS_eff$ERA_b": {"value": 1.03, "processes": ["top"]},
            "CMS_fake$ERA_b": {"value": 1.01, "processes": ["zh", "wh", "vbf", "ggh", "diboson", "qcdzll", "ewkzll"]},
            "CMS_eff$ERA_e": {
                "dielec": {"value": 1.06, "processes": ["diboson", "top", "qcd_zll", "ewk_zll"]},
                "singleel": {
                    "value": 1.03,
                    # TODO: check, qcd_wjets was not present in Run2
                    "processes": ["diboson", "top", "qcdzll", "ewkzll", "ewk_wjets"],
                },
            },
            "CMS_reco$ERA_e": {
                "dielec": {"value": 1.02, "processes": ["diboson", "top", "qcd_zll", "ewk_zll"]},
                "singleel": {"value": 1.01, "processes": ["diboson", "top", "qcdzll", "ewkzll"]},
            },
            "CMS_eff$ERA_m": {
                "dimuon": {"value": 1.01, "processes": ["diboson", "top", "qcd_zll", "ewk_zll"]},
                "singlemu": {"value": 1.005, "processes": ["diboson", "top", "qcdzll", "ewkzll", "ewk_wjets", "qcd_wjets"]},
            },
            "CMS_eff$ERA_g": {"value": 1.05, "processes": ["qcd_gjets", "ewk_gjets"]},
        },
    }[year]


def get_trigger_uncertainties(year: str, analysis: str) -> dict[str, Any]:
    """Return trigger-related lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    # All processes
    proc_list = [
        "zh",
        "wh",
        "vbf",
        "ggh",
        "diboson",
        "top",
        "qcdzll",
        "ewkzll",
        "ewk_wjets",
        "qcd_wjets",
        "ewk_zjets",
        "qcd_zjets",
        "qcd_zll",
        "ewk_zll",
        "ewk_gjets",
        "qcd_gjets",
    ]
    return {
        "Run3": {
            "CMS_trigger_$ERA_g_13p6TeV": {
                "photon": {"value": 1.01, "processes": proc_list},
            },
            "CMS_trigger_$ERA_e_13p6TeV": {
                "dielec": {"value": 1.01, "processes": proc_list},
                "singleel": {"value": 1.01, "processes": proc_list},
            },
            "CMS_trigger_$ERA_met_stat_13p6TeV": {
                "signal": {"value": 1.02, "processes": proc_list},
                "dimuon": {"value": 1.02, "processes": proc_list},
                "singlemu": {"value": 1.02, "processes": proc_list},
            },
            "CMS_trigger_$ERA_met_sys_13p6TeV": {
                "signal": {"value": 1.01, "processes": proc_list},
                "dimuon": {"value": 0.99, "processes": proc_list},
            },
        },
    }[year]


def get_qcd_uncertainties(year: str, analysis: str) -> dict[str, Any]:
    """Return QCD scale lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "QCDscale_VV": {"value": 1.15, "processes": ["diboson"]},
            "QCDscale_VV_ACCEPT": {"value": 1.15, "processes": ["diboson"]},
            "QCDscale_tt": {"value": 1.1, "processes": ["top"]},
            "QCDscale_tt_ACCEPT": {"value": 1.1, "processes": ["top"]},
            "QCDscale_ggH2in": {"value": 1.4, "processes": ["ggh"]},
            "QCDscale_qqH_ACCEPT": {"value": 1.02, "processes": ["vbf"]},
        },
    }[year]


def get_pdf_uncertainties(year: str, analysis: str) -> dict[str, Any]:
    """Return PDF and QCD scale acceptance systematics for Higgs processes."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "pdf_Higgs_gg": {"value": 1.032, "processes": ["ggh"]},
            "pdf_Higgs_qq": {"value": 1.021, "processes": ["vbf"]},
            "pdf_Higgs_qq_ACCEPT": {"value": 1.01, "processes": ["vbf"]},
            "qqH_QCDscale": {"value": (0.997, 1.004), "processes": ["vbf"]},
            "ggH_QCDscale": {"value": (0.933, 1.046), "processes": ["ggh"]},
        },
    }[year]


def get_misc_uncertainties(year: str, analysis: str) -> dict[str, Any]:
    """Return miscellaneous lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "Top_Reweight13TeV": {"value": 1.1, "processes": ["top"]},
            "UEPS": {"value": 1.168, "processes": ["ggh"]},
            "ZJets_Norm13TeV": {"value": 1.2, "processes": ["qcdzll", "ewkzll"]},
        },
    }[year]


def get_jec_shape(year: str, analysis: str) -> dict[str, dict[str, Any]]:
    """Return JER and JES shape systematics for a given year and analysis."""
    _ = year  # Currently unused
    _ = analysis  # Currently unused

    # All processes (signal + backgrounds), except models
    proc_list = ["zh", "wh", "vbf", "ggh", "diboson", "top", "qcdzll", "ewkzll"]
    return {
        f"jer_{year}": {"value": 1.0, "processes": proc_list},
        "jesAbsolute": {"value": 1.0, "processes": proc_list},
        f"jesAbsolute_{year}": {"value": 1.0, "processes": proc_list},
        "jesBBEC1": {"value": 1.0, "processes": proc_list},
        f"jesBBEC1_{year}": {"value": 1.0, "processes": proc_list},
        "jesEC2": {"value": 1.0, "processes": proc_list},
        f"jesEC2_{year}": {"value": 1.0, "processes": proc_list},
        "jesFlavorQCD": {"value": 1.0, "processes": proc_list},
        "jesHF": {"value": 1.0, "processes": proc_list},
        f"jesHF_{year}": {"value": 1.0, "processes": proc_list},
        "jesRelativeBal": {"value": 1.0, "processes": proc_list},
        f"jesRelativeSample_{year}": {"value": 1.0, "processes": proc_list},
    }
