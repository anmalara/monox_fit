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


def get_lepton_efficiency_uncertainties(year: str) -> dict[str, Any]:
    return {
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
            "@gamma_efficiency": "1.05",
        },
    }[year]


def get_trigger_uncertainties(year: str) -> dict[str, str]:
    return {
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
        "Run3": {
            "@scale_diboson": "1.15",
            "@scale_acc_diboson": "1.15",
            "@scale_tt": "1.1",
            "@scale_acc_tt": "1.1",
            "@scale_ggH": "1.4",
            "@scale_acc_vbf": "1.02",
        },
    }[year]


def get_pdf_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "@pdf_ggh": "1.032",
            "@pdf_vbf": "1.021",
            "@pdf_acc_vbf": "1.01",
            "@scale_vbf_qcd": "0.997/1.004",
            "@scale_ggh_qcd": "0.933/1.046",
        },
    }[year]


def get_misc_uncertainties(year: str) -> dict[str, str]:
    return {
        "Run3": {
            "@top_reweight": "1.1",
            "@ueps": "1.168",
            "@zjets_norm": "1.2",
        },
    }[year]
