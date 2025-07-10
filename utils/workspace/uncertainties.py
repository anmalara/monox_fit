from typing import Any
from functools import partial
from collections.abc import Callable

from utils.workspace.processes import get_processes_by_region, get_processes_by_type, get_region_label_map


def get_all_shapes_functions() -> list[Callable[[str, str], dict[str, Any]]]:
    return [get_jec_shape, get_prefiring_shape]


def get_all_flat_systematics_functions() -> list[Callable[[str, str], dict[str, Any]]]:
    return [get_lumi_unc, get_lepton_eff_unc, get_trigger_unc, get_qcd_unc, get_Higgs_pdf_unc, get_misc_unc]


def get_veto_unc(model: str) -> dict[str, float]:
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


def get_lumi_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return luminosity lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused

    proc_list = get_processes_by_type(analysis=analysis)
    return {
        "Run3": {
            f"lumi_13p6TeV_{year}": {"value": 1.014, "processes": proc_list},
        },
    }[year]


def get_prefiring_shape(year: str, analysis: str) -> dict[str, Any]:
    """Return prefiring shape systematics for a given year and analysis."""
    proc_list = get_processes_by_type(analysis=analysis)
    return {
        "vbf": {"Run3": {}},
        "monojet": {
            "Run3": {
                f"prefiring_jet": {"value": 1.0, "processes": proc_list},
            },
        },
    }[
        analysis
    ][year]


def get_lepton_eff_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return lepton and photon efficiency lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    procs_by_region = {
        "dielec": get_processes_by_region(analysis=analysis, region="dielec"),
        "singleel": get_processes_by_region(analysis=analysis, region="singleel"),
        "dimuon": get_processes_by_region(analysis=analysis, region="dimuon"),
        "singlemu": get_processes_by_region(analysis=analysis, region="singlemu"),
        "photon": get_processes_by_region(analysis=analysis, region="photon"),
        "signal": get_processes_by_type(analysis=analysis),
    }

    # Run-dependent efficiencies
    m_id_eff = {"Run3": 0.004}[year]
    m_iso_eff = {"Run3": 0.005}[year]
    m_reco_eff = {"Run3": 0.01}[year]  # TODO update for run3
    e_id_eff = {"Run3": 0.014}[year]
    e_reco_eff = {"Run3": 0.010}[year]  # TODO update for run3
    g_id_eff = {"Run3": 0.014}[year]
    results = {
        f"CMS_eff_b_{year}": {"value": 1.03, "processes": ["top"]},
        f"CMS_fake_b_{year}": {"value": 1.02, "processes": procs_by_region["signal"] - {"top"}},
        # TODO 1% in VBF 2% in monojet
    }
    lepton_unc = {
        f"CMS_eff_e_id_{year}": {"dielec": 2 * e_id_eff, "singleel": e_id_eff},
        f"CMS_eff_e_reco_{year}": {"dielec": 2 * e_reco_eff, "singleel": e_reco_eff},
        f"CMS_eff_m_id_{year}": {"dimuon": 2 * m_id_eff, "singlemu": m_id_eff},
        f"CMS_eff_m_iso_{year}": {"dimuon": 2 * m_iso_eff, "singlemu": m_iso_eff},
        f"CMS_eff_m_reco_{year}": {"dimuon": 2 * m_reco_eff, "singlemu": m_reco_eff},
        f"CMS_eff_g_id_{year}": {"photon": g_id_eff},
    }

    for name, entries in lepton_unc.items():
        results[name] = {region: {"value": 1 + value, "processes": procs_by_region[region]} for region, value in entries.items()}

    return results


def get_trigger_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return trigger-related lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    # All processes
    proc_list = partial(get_processes_by_region, analysis=analysis, types=["signals", "backgrounds", "models"])
    return {
        "Run3": {
            f"CMS_eff_g_trigger_{year}_13p6TeV": {
                "photon": {"value": 1.01, "processes": proc_list(region="photon")},
            },
            f"CMS_eff_e_trigger_{year}_13p6TeV": {
                "dielec": {"value": 1.01, "processes": proc_list(region="dielec")},
                "singleel": {"value": 1.01, "processes": proc_list(region="singleel")},
            },
            f"CMS_eff_met_trigger_{year}_13p6TeV": {
                "signal": {"value": 1.01, "processes": proc_list(region="signal")},
                "dimuon": {"value": 1.01, "processes": proc_list(region="dimuon")},
                "singlemu": {"value": 1.01, "processes": proc_list(region="singlemu")},
            },
        },
    }[year]


def get_qcd_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return QCD scale lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "QCDscale_VV": {"value": 1.1, "processes": ["diboson"]},
            # "QCDscale_VV_ACCEPT": {"value": 1.1, "processes": ["diboson"]}, # TODO not present for monojet?
            "QCDscale_ttbar": {"value": 1.1, "processes": ["top"]},
            # "QCDscale_ttbar_ACCEPT": {"value": 1.1, "processes": ["top"]},# TODO not present for monojet?
            "QCDscale_Higgs_ggH2in": {"value": 1.039, "processes": ["ggh"]},  # TODO for vbf (0.933, 1.046)
            "QCDscale_Higgs_ggH2in_ACCEPT": {"value": 1.4, "processes": ["ggh"]},
            "QCDscale_Higgs_qqH": {"value": (1.004, 0.997), "processes": ["vbf"]},
            "QCDscale_Higgs_qqH_ACCEPT": {"value": 1.02, "processes": ["vbf"]},
            "QCDscale_Higgs_zh": {"value": (1.03, 0.969), "processes": ["zh"]},
            "QCDscale_Higgs_wh": {"value": (1.005, 0.993), "processes": ["wh"]},
        },
    }[year]


def get_Higgs_pdf_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return PDF systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "pdf_Higgs_gg": {"value": 1.032, "processes": ["ggh"]},
            "pdf_Higgs_qqH": {"value": 1.021, "processes": ["vbf"]},
            "pdf_Higgs_qqH_ACCEPT": {"value": 1.01, "processes": ["vbf"]},
            "pdf_Higgs_zh": {"value": (1.016, 0.987), "processes": ["zh"]},  # TODO was symmetric for VBF
            "pdf_Higgs_wh": {"value": 1.019, "processes": ["wh"]},
        },
    }[year]


def get_misc_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return miscellaneous lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "Top_Reweight13p6TeV": {"value": 1.1, "processes": ["top"]},
            "ZJets_Norm13p6TeV": {"value": 1.2, "processes": ["qcdzll", "ewkzll"]},
            "GJets_Norm13p6TeV": {"value": 1.2, "processes": ["qcdgjets"]},
            # "UEPS": {"value": 1.168, "processes": ["ggh"]},  # TODO only for VBF?
        },
    }[year]


def get_jec_shape(year: str, analysis: str) -> dict[str, dict[str, Any]]:
    """Return JER and JES shape systematics for a given year and analysis."""
    _ = year  # Currently unused
    _ = analysis  # Currently unused

    proc_list = get_processes_by_type(analysis=analysis)
    # TODO need to change to CMS_scale_j_Absolute
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


def get_automc_stat(year: str, analysis: str, n_bins: int) -> dict[str, dict[str, Any]]:
    """Return autoMC stat shapes for minor backgrounds for a given year and analysis."""
    _ = year  # Currently unused
    _ = analysis  # Currently unused

    automc_shape = {
        f"{region}_mergedMCBkg_{analysis}_{year}_stat_bin{idx}": {
            region: {"value": 1.0, "processes": get_processes_by_region(analysis=analysis, region=region, types=["backgrounds"])},
        }
        for region, _ in get_region_label_map()
        for idx in range(n_bins)
    }
    return automc_shape
