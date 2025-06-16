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
            "lumi_13TeV_XY": 1.02,
            "lumi_13TeV_LS": 1.002,
            "lumi_13TeV_BBD": 1.0,
            "lumi_13TeV_DB": 1.0,
            "lumi_13TeV_BCC": 1.02,
            "lumi_13TeV_GS": 1.00,
            "lumi_13TeV_XY": 1.015,
        },
    }[year]


def get_lepton_efficiency_uncertainties(year: str) -> dict[str, Any]:
    return {
        "Run3": {
            "CMS_eff$ERA_b": 1.03,
            "CMS_fake$ERA_b": 1.01,
            "CMS_eff$ERA_e": {
                "dielec": 1.06,
                "singleel": 1.03,
            },
            "CMS_reco$ERA_e": {
                "dielec": 1.02,
                "singleel": 1.01,
            },
            "CMS_eff$ERA_m": {
                "dimuon": 1.01,
                "singlemu": 1.005,
            },
            "CMS_eff$ERA_g": 1.05,
        },
    }[year]


def get_trigger_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "CMS_trigger$ERA_g": 1.01,
            "CMS_trigger$ERA_e": 1.01,
            "CMS_trigger$ERA_met_stat": {
                "signal": 1.02,
                "dimuon": 1.02,
                "singlemu": 1.02,
            },
            "CMS_trigger_met_sys": {
                "signal": 1.01,
                "dimuon": 0.99,
            },
        },
    }[year]


def get_qcd_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "QCDscale_VV": 1.15,
            "QCDscale_VV_ACCEPT": 1.15,
            "QCDscale_tt": 1.1,
            "QCDscale_tt_ACCEPT": 1.1,
            "QCDscale_ggH2in": 1.4,
            "QCDscale_qqH_ACCEPT": 1.02,
        },
    }[year]


def get_pdf_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "pdf_Higgs_gg": 1.032,
            "pdf_Higgs_qq": 1.021,
            "pdf_Higgs_qq_ACCEPT": 1.01,
            # TODO: check are these are handled
            # "qqH_QCDscale": "0.997/1.004",
            # "ggH_QCDscale": "0.933/1.046",
        },
    }[year]


def get_misc_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "Top_Reweight13TeV": 1.1,
            "UEPS": 1.168,
            "ZJets_Norm13TeV": 1.2,
        },
    }[year]
