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
