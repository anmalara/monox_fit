from typing import Any


def get_processes(analysis: str) -> dict[str, dict[str, list[str]]]:
    # TODO: might vary depending on the analysis
    return {
        "vbf": {
            "signal": {
                "signals": ["zh", "wh", "vbf", "ggh"],
                "models": ["qcd_zjets", "qcd_wjets", "ewk_zjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "dimuon": {
                "signals": [],
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "diboson"],
            },
            "dielec": {
                "signals": [],
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "diboson"],
            },
            "singlemu": {
                "signals": [],
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "singleel": {
                "signals": [],
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "photon": {
                "signals": [],
                "models": ["qcd_gjets", "ewk_gjets"],
                "backgrounds": [],
            },
        },
        "monojet": {
            # TODO: port propper processes for monojet
            "signal": {
                "signals": ["zh", "wh", "vbf", "ggh"],
                "models": ["qcd_zjets", "ewk_zjets", "qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "dimuon": {
                "signals": [],
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "diboson"],
            },
            "dielec": {
                "signals": [],
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "diboson"],
            },
            "singlemu": {
                "signals": [],
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "singleel": {
                "signals": [],
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "diboson"],
            },
            "photon": {
                "signals": [],
                "models": ["qcd_gjets", "ewk_gjets"],
                "backgrounds": [],
            },
        },
    }[analysis]


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


def get_lumi_uncertainties(year: str) -> dict[str, str]:
    # All processes (signal + backgrounds), except models
    proc_list = ["zh", "wh", "vbf", "ggh", "diboson", "top", "qcdzll", "ewkzll"]

    return {
        "2017": {
            "lumi_13TeV_XY": 1.008,
            "lumi_13TeV_LS": 1.003,
            "lumi_13TeV_BBD": 1.004,
            "lumi_13TeV_DB": 1.005,
            "lumi_13TeV_BCC": 1.003,
            "lumi_13TeV_GS": 1.001,
            "lumi_13TeV_$ERA": 1.020,
        },
        "2018": {
            "lumi_13TeV_XY": 1.02,
            "lumi_13TeV_LS": 1.002,
            "lumi_13TeV_BBD": 1.0,
            "lumi_13TeV_DB": 1.0,
            "lumi_13TeV_BCC": 1.02,
            "lumi_13TeV_GS": 1.00,
            "lumi_13TeV_$ERA": 1.015,
        },
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


def get_lepton_efficiency_uncertainties(year: str) -> dict[str, Any]:
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


def get_trigger_uncertainties(year: str) -> dict[str, str]:
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
            "CMS_trigger$ERA_g": {"photon": {"value": 1.01, "processes": proc_list}},
            "CMS_trigger$ERA_e": {"dielec": {"value": 1.01, "processes": proc_list}, "singleel": {"value": 1.01, "processes": proc_list}},
            "CMS_trigger$ERA_met_stat": {
                "signal": {"value": 1.02, "processes": proc_list},
                "dimuon": {"value": 1.02, "processes": proc_list},
                "singlemu": {"value": 1.02, "processes": proc_list},
            },
            "CMS_trigger_met_sys": {
                "signal": {"value": 1.01, "processes": proc_list},
                "dimuon": {"value": 0.99, "processes": proc_list},
            },
        },
    }[year]


def get_qcd_uncertainties(year: str) -> dict[str, str]:
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


def get_pdf_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "pdf_Higgs_gg": {"value": 1.032, "processes": ["ggh"]},
            "pdf_Higgs_qq": {"value": 1.021, "processes": ["vbf"]},
            "pdf_Higgs_qq_ACCEPT": {"value": 1.01, "processes": ["vbf"]},
            "qqH_QCDscale": {"value": (0.997, 1.004), "processes": ["vbf"]},
            "ggH_QCDscale": {"value": (0.933, 1.046), "processes": ["ggh"]},
        },
    }[year]


def get_misc_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "Top_Reweight13TeV": {"value": 1.1, "processes": ["top"]},
            "UEPS": {"value": 1.168, "processes": ["ggh"]},
            "ZJets_Norm13TeV": {"value": 1.2, "processes": ["qcdzll", "ewkzll"]},
        },
    }[year]


def get_jer_shape():

    # All processes (signal + backgrounds), except models
    proc_list = ["zh", "wh", "vbf", "ggh", "diboson", "top", "qcdzll", "ewkzll"]
    return {
        "jer_$ERA": {"value": 1.0, "processes": proc_list},
        "jesAbsolute": {"value": 1.0, "processes": proc_list},
        "jesAbsolute_$ERA": {"value": 1.0, "processes": proc_list},
        "jesBBEC1": {"value": 1.0, "processes": proc_list},
        "jesBBEC1_$ERA": {"value": 1.0, "processes": proc_list},
        "jesEC2": {"value": 1.0, "processes": proc_list},
        "jesEC2_$ERA": {"value": 1.0, "processes": proc_list},
        "jesFlavorQCD": {"value": 1.0, "processes": proc_list},
        "jesHF": {"value": 1.0, "processes": proc_list},
        "jesHF_$ERA": {"value": 1.0, "processes": proc_list},
        "jesRelativeBal": {"value": 1.0, "processes": proc_list},
        "jesRelativeSample_$ERA": {"value": 1.0, "processes": proc_list},
    }
