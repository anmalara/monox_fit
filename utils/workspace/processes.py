from typing import Any


def get_processes(analysis: str, region: str, type: str) -> list[str]:
    """Return the list of processes for a given analysis, region, and type."""
    processes = {
        "vbf": {
            "signal": {
                "signals": ["zh", "wh", "vbf", "ggh"],
                "models": ["qcd_zjets", "qcd_wjets", "ewk_zjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "wz", "zz", "ww"],
            },
            "dimuon": {
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "wz", "zz", "ww"],
            },
            "dielec": {
                "models": ["qcd_zll", "ewk_zll"],
                "backgrounds": ["top", "wz", "zz", "ww"],
            },
            "singlemu": {
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "ewkzll", "top", "wz", "zz", "ww"],
            },
            "singleel": {
                "models": ["qcd_wjets", "ewk_wjets"],
                "backgrounds": ["qcdzll", "qcdgjets", "ewkzll", "top", "wz", "zz", "ww"],
            },
            "photon": {
                "models": ["qcd_gjets", "ewk_gjets"],
            },
        },
        "monojet": {
            "signal": {
                "signals": ["zh", "wh", "vbf", "ggh"],  # ggzh
                "models": ["qcd_zjets", "qcd_wjets"],
                "backgrounds": ["top", "wz", "zz", "ww"],
                "data_driven": ["qcd"],
            },
            "dimuon": {
                "models": ["qcd_zll"],
                "backgrounds": ["top", "wz", "zz", "ww"],
            },
            "dielec": {
                "models": ["qcd_zll"],
                "backgrounds": ["top", "wz", "zz", "ww"],
            },
            "singlemu": {
                "models": ["qcd_wjets"],
                "backgrounds": ["qcdzll", "top", "wz", "zz", "ww", "qcd"],
            },
            "singleel": {
                "models": ["qcd_wjets"],
                "backgrounds": ["qcdzll", "qcdgjets", "top", "wz", "zz", "ww", "qcd"],
            },
            "photon": {
                "models": ["qcd_gjets"],
                "backgrounds": ["wgamma", "zgamma"],
                "data_driven": ["qcd"],
            },
        },
    }

    return processes.get(analysis, {}).get(region, {}).get(type, [])


def get_all_regions() -> list[str]:
    return [region for region, _ in get_region_label_map()]


def get_region_label_map() -> list[tuple[str, str]]:
    return [
        ("dielec", "Zee"),
        ("dimuon", "Zmm"),
        ("signal", "signal"),
        ("singleel", "Wen"),
        ("singlemu", "Wmn"),
        ("photon", "gjets"),
    ]


def get_process_model_map(region: str) -> dict[str, dict[str, str]]:
    return {
        "dielec": {
            "ewk_zll": "ewk_dielectron_ewk_zjets",
            "qcd_zll": "qcd_dielectron_qcd_zjets",
        },
        "dimuon": {
            "ewk_zll": "ewk_dimuon_ewk_zjets",
            "qcd_zll": "qcd_dimuon_qcd_zjets",
        },
        "signal": {
            "ewk_wjets": "ewk_wjetssignal_ewk_zjets",
            "ewk_zjets": "ewkqcd_signal_qcd_zjets",
            "qcd_wjets": "qcd_wjetssignal_qcd_zjets",
            "qcd_zjets": "signal_qcd_zjets",
        },
        "singleel": {
            "ewk_wjets": "ewk_singleelectron_ewk_wjets",
            "qcd_wjets": "qcd_singleelectron_qcd_wjets",
        },
        "singlemu": {
            "ewk_wjets": "ewk_singlemuon_ewk_wjets",
            "qcd_wjets": "qcd_singlemuon_qcd_wjets",
        },
        "photon": {
            "ewk_gjets": "ewk_photon_ewk_zjets",
            "qcd_gjets": "qcd_photon_qcd_zjets",
        },
    }[region]


def get_processes_by_region(analysis: str, region: str, types: list[str] = ["backgrounds", "models"]) -> set[str]:
    """Return the set of all processes of the given types used in all regions of the given analysis."""
    return {proc for category in types for proc in get_processes(analysis=analysis, region=region, type=category)}
