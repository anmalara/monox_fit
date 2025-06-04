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
    return {
        "ewk_wjets": {"t": 0.01, "m": 0.02, "e": 0.03},
        "qcd_wjets": {"t": 0.01, "m": 0.015, "e": 0.03},
        "ewk_zjets": {"t": -0.01, "m": -0.02, "e": -0.03},
        "qcd_zjets": {"t": -0.01, "m": -0.015, "e": -0.03},
    }[model]


def get_lumi_uncertainties(year: str) -> dict[str, str]:
    return {
        "2017": {
            "@LUMIXY": "1.008",
            "@LUMILS": "1.003",
            "@LUMIBBD": "1.004",
            "@LUMIDB": "1.005",
            "@LUMIBCC": "1.003",
            "@LUMIGS": "1.001",
            "@LUMI": "1.020",
        },
        "2018": {
            "@LUMIXY": "1.02",
            "@LUMILS": "1.002",
            "@LUMIBBD": "1.0",
            "@LUMIDB": "1.0",
            "@LUMIBCC": "1.02",
            "@LUMIGS": "1.00",
            "@LUMI": "1.015",
        },
        "Run3": {
            "@LUMIXY": "1.02",
            "@LUMILS": "1.002",
            "@LUMIBBD": "1.0",
            "@LUMIDB": "1.0",
            "@LUMIBCC": "1.02",
            "@LUMIGS": "1.00",
            "@LUMI": "1.015",
        },
    }[year]


def get_lepton_efficiency_uncertainties(year: str) -> dict[str, str]:
    return {
        "2017": {
            "@b_efficiency": "1.03",
            "@b_fake": "1.01",
            "@e_efficiency": {
                "signal": "-",
                "dimuon": "-",
                "dielec": "1.06",
                "singlemu": "-",
                "singleel": "1.03",
                "photon": "-",
            },
            "@e_reco": {
                "signal": "-",
                "dimuon": "-",
                "dielec": "1.02",
                "singlemu": "-",
                "singleel": "1.01",
                "photon": "-",
            },
            "@mu_efficiency": {
                "signal": "-",
                "dimuon": "1.01",
                "dielec": "-",
                "singlemu": "1.005",
                "singleel": "-",
                "photon": "-",
            },
            "@gamma_efficiency": "1.03",
        },
        "2018": {
            "@b_efficiency": "1.03",
            "@b_fake": "1.01",
            "@e_efficiency": {
                "signal": "-",
                "dimuon": "-",
                "dielec": "1.06",
                "singlemu": "-",
                "singleel": "1.03",
                "photon": "-",
            },
            "@e_reco": {
                "signal": "-",
                "dimuon": "-",
                "dielec": "1.02",
                "singlemu": "-",
                "singleel": "1.01",
                "photon": "-",
            },
            "@mu_efficiency": {
                "signal": "-",
                "dimuon": "1.01",
                "dielec": "-",
                "singlemu": "1.005",
                "singleel": "-",
                "photon": "-",
            },
            "@gamma_efficiency": "1.03",
        },
        "Run3": {
            "@b_efficiency": "1.03",
            "@b_fake": "1.01",
            "@e_efficiency": {
                "signal": "-",
                "dimuon": "-",
                "dielec": "1.06",
                "singlemu": "-",
                "singleel": "1.03",
                "photon": "-",
            },
            "@e_reco": {
                "signal": "-",
                "dimuon": "-",
                "dielec": "1.02",
                "singlemu": "-",
                "singleel": "1.01",
                "photon": "-",
            },
            "@mu_efficiency": {
                "signal": "-",
                "dimuon": "1.01",
                "dielec": "-",
                "singlemu": "1.005",
                "singleel": "-",
                "photon": "-",
            },
            "@gamma_efficiency": "1.03",
        },
    }[year]


def get_trigger_uncertainties(year: str) -> dict[str, str]:
    return {
        "2017": {
            "@photon_trigger": "1.01",
            "@egamma_trigger": "1.01",
            "@met_trigger_stat": {
                "signal": "1.02",
                "dimuon": "1.02",
                "dielec": "-",
                "singlemu": "1.02",
                "singleel": "-",
                "photon": "-",
            },
            "@met_trigger_sys": {
                "signal": "1.01",
                "dimuon": "0.99",
                "dielec": "-",
                "singlemu": "-",
                "singleel": "-",
                "photon": "-",
            },
        },
        "2018": {
            "@photon_trigger": "1.01",
            "@egamma_trigger": "1.01",
            "@met_trigger_stat": {
                "signal": "1.02",
                "dimuon": "1.02",
                "dielec": "-",
                "singlemu": "1.02",
                "singleel": "-",
                "photon": "-",
            },
            "@met_trigger_sys": {
                "signal": "1.01",
                "dimuon": "0.99",
                "dielec": "-",
                "singlemu": "-",
                "singleel": "-",
                "photon": "-",
            },
        },
        "Run3": {
            "@photon_trigger": "1.01",
            "@egamma_trigger": "1.01",
            "@met_trigger_stat": {
                "signal": "1.02",
                "dimuon": "1.02",
                "dielec": "-",
                "singlemu": "1.02",
                "singleel": "-",
                "photon": "-",
            },
            "@met_trigger_sys": {
                "signal": "1.01",
                "dimuon": "0.99",
                "dielec": "-",
                "singlemu": "-",
                "singleel": "-",
                "photon": "-",
            },
        },
    }[year]


def get_qcd_uncertainties(year: str) -> dict[str, str]:
    return {
        "2017": {
            "@diboson_scale": "1.15",
            "@diboson_scale_acc": "1.15",
            "@tt_scale": "1.1",
            "@tt_scale_acc": "1.1",
            "@ggH_scale": "1.4",
            "@vbf_scale_acc": "1.02",
        },
        "2018": {
            "@diboson_scale": "1.15",
            "@diboson_scale_acc": "1.15",
            "@tt_scale": "1.1",
            "@tt_scale_acc": "1.1",
            "@ggH_scale": "1.4",
            "@vbf_scale_acc": "1.02",
        },
        "Run3": {
            "@diboson_scale": "1.15",
            "@diboson_scale_acc": "1.15",
            "@tt_scale": "1.1",
            "@tt_scale_acc": "1.1",
            "@ggH_scale": "1.4",
            "@vbf_scale_acc": "1.02",
        },
    }[year]


def get_pdf_uncertainties(year: str) -> dict[str, str]:
    return {
        "2017": {
            "@ggh_pdf": "1.032",
            "@vbf_pdf": "1.021",
            "@vbf_pdf_acc": "1.01",
            "@vbf_qcd_scale": "0.997 / 1.044",
            "@ggh_qcd_scale": "0.933 / 1.046",
        },
        "2018": {
            "@ggh_pdf": "1.032",
            "@vbf_pdf": "1.021",
            "@vbf_pdf_acc": "1.01",
            "@vbf_qcd_scale": "0.997 / 1.044",
            "@ggh_qcd_scale": "0.933 / 1.046",
        },
        "Run3": {
            "@ggh_pdf": "1.032",
            "@vbf_pdf": "1.021",
            "@vbf_pdf_acc": "1.01",
            "@vbf_qcd_scale": "0.997 / 1.044",
            "@ggh_qcd_scale": "0.933 / 1.046",
        },
    }[year]


def get_misc_uncertainties(year: str) -> dict[str, str]:
    return {
        "2017": {
            "@top_reweight": "1.1",
            "@ueps": "1.168",
            "@zjets_norm": "1.2",
        },
        "2018": {
            "@top_reweight": "1.1",
            "@ueps": "1.168",
            "@zjets_norm": "1.2",
        },
        "Run3": {
            "@top_reweight": "1.1",
            "@ueps": "1.168",
            "@zjets_norm": "1.2",
        },
    }[year]
