from typing import Any


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
            "lumi_13TeV_XY": {"value": 1.015, "processes": proc_list},
        },
    }[year]


def get_lepton_efficiency_uncertainties(year: str) -> dict[str, Any]:
    return {
        "Run3": {
            "CMS_eff$ERA_b": {
                "value": 1.03,
                "processes": [],
            },
            "CMS_fake$ERA_b": {
                "value": 1.01,
                "processes": [],
            },
            "CMS_eff$ERA_e": {
                "dielec": {
                    "value": 1.06,
                    "processes": [],
                },
                "singleel": {
                    "value": 1.03,
                    "processes": [],
                },
            },
            "CMS_reco$ERA_e": {
                "dielec": {
                    "value": 1.02,
                    "processes": [],
                },
                "singleel": {
                    "value": 1.01,
                    "processes": [],
                },
            },
            "CMS_eff$ERA_m": {
                "dimuon": {
                    "value": 1.01,
                    "processes": [],
                },
                "singlemu": {
                    "value": 1.005,
                    "processes": [],
                },
            },
            "CMS_eff$ERA_g": {
                "value": 1.05,
                "processes": [],
            },
        },
    }[year]


def get_trigger_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "CMS_trigger$ERA_g": {
                "value": 1.01,
                "processes": [],
            },
            "CMS_trigger$ERA_e": {
                "value": 1.01,
                "processes": [],
            },
            "CMS_trigger$ERA_met_stat": {
                "signal": {
                    "value": 1.02,
                    "processes": [],
                },
                "dimuon": {
                    "value": 1.02,
                    "processes": [],
                },
                "singlemu": {
                    "value": 1.02,
                    "processes": [],
                },
            },
            "CMS_trigger_met_sys": {
                "signal": {
                    "value": 1.01,
                    "processes": [],
                },
                "dimuon": {
                    "value": 0.99,
                    "processes": [],
                },
            },
        },
    }[year]


def get_qcd_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "QCDscale_VV": {
                "value": 1.15,
                "processes": [],
            },
            "QCDscale_VV_ACCEPT": {
                "value": 1.15,
                "processes": [],
            },
            "QCDscale_tt": {
                "value": 1.1,
                "processes": [],
            },
            "QCDscale_tt_ACCEPT": {
                "value": 1.1,
                "processes": [],
            },
            "QCDscale_ggH2in": {
                "value": 1.4,
                "processes": [],
            },
            "QCDscale_qqH_ACCEPT": {
                "value": 1.02,
                "processes": [],
            },
        },
    }[year]


def get_pdf_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "pdf_Higgs_gg": {
                "value": 1.032,
                "processes": [],
            },
            "pdf_Higgs_qq": {
                "value": 1.021,
                "processes": [],
            },
            "pdf_Higgs_qq_ACCEPT": {
                "value": 1.01,
                "processes": [],
            },
            # TODO: check are these are handled
            # "qqH_QCDscale": {
            #     "value": "0.997/1.004",
            #     "processes": [],
            # },
            # "ggH_QCDscale": {
            #     "value": "0.933/1.046",
            #     "processes": [],
            # }
        },
    }[year]


def get_misc_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "Top_Reweight13TeV": {
                "value": 1.1,
                "processes": [],
            },
            "UEPS": {
                "value": 1.168,
                "processes": [],
            },
            "ZJets_Norm13TeV": {
                "value": 1.2,
                "processes": [],
            },
        },
    }[year]
