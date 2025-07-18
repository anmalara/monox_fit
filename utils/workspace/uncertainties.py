from typing import Any
from functools import partial
from collections.abc import Callable

from utils.workspace.processes import get_all_regions, get_processes_by_region


def get_all_shapes_functions() -> list[Callable[[str, str], dict[str, Any]]]:
    return [get_jec_shape, get_prefiring_shape, get_pu_shape]


def get_all_flat_systematics_functions() -> list[Callable[[str, str], dict[str, Any]]]:
    return [get_lumi_unc, get_objects_eff_unc, get_trigger_unc, get_qcd_unc, get_Higgs_pdf_unc, get_misc_unc]


def get_jes_variations_names(year: str) -> list[str]:
    """Get the list of JES variations."""
    jes_names = [
        f"jer_{year}",
        "jesAbsolute",
        f"jesAbsolute_{year}",
        "jesBBEC1",
        f"jesBBEC1_{year}",
        "jesEC2",
        f"jesEC2_{year}",
        "jesFlavorQCD",
        "jesHF",
        f"jesHF_{year}",
        "jesRelativeBal",
        f"jesRelativeSample_{year}",
    ]

    return jes_names


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
    systematics = {
        "Run3": {
            f"lumi_13p6TeV_{year}": {
                region: {"value": 1.014, "processes": get_processes_by_region(analysis=analysis, region=region, types=["signals", "backgrounds"])}
                for region in get_all_regions()
            }
        },
    }
    return systematics[year]


def get_objects_eff_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return lepton and photon efficiency lnN systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    regions = get_all_regions()

    # Run-dependent efficiencies
    m_id_eff = {"Run3": 0.004}[year]
    m_iso_eff = {"Run3": 0.005}[year]
    m_reco_eff = {"Run3": 0.01}[year]  # TODO update for run3
    e_id_eff = {"Run3": 0.014}[year]
    e_reco_eff = {"Run3": 0.01}[year]  # TODO update for run3
    g_id_eff = {"Run3": 0.015}[year]

    results = {
        f"CMS_eff_b_{year}": {"value": 1.03, "processes": ["top"]},
    }
    results[f"CMS_fake_b_{year}"] = {  # TODO 1% in VBF 2% in monojet
        region: {"value": 1.02, "processes": get_processes_by_region(analysis=analysis, region=region) - {"top"}} for region in regions
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
        results[name] = {
            region: {"value": 1 + value, "processes": get_processes_by_region(analysis=analysis, region=region)} for region, value in entries.items()
        }

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
            "top_Norm_13p6TeV": {"value": 1.1, "processes": ["top"]},
            "wz_Norm_13p6TeV": {"value": 1.1, "processes": ["wz"]},
            "zz_Norm_13p6TeV": {"value": 1.1, "processes": ["zz"]},
            "ww_Norm_13p6TeV": {"value": 1.1, "processes": ["ww"]},
            "wgamma_Norm_13p6TeV": {"value": 1.1, "processes": ["wgamma"]},
            "zgamma_Norm_13p6TeV": {"value": 1.1, "processes": ["zgamma"]},
            "QCDscale_VV": {"value": 1.1, "processes": ["diboson"]},
            # "QCDscale_VV_ACCEPT": {"value": 1.1, "processes": ["diboson"]}, # TODO not present for monojet?
            # "QCDscale_ttbar": {"value": 1.1, "processes": ["top"]}, # TODO not present for monojet?
            # "QCDscale_ttbar_ACCEPT": {"value": 1.1, "processes": ["top"]},# TODO not present for monojet?
            "QCDscale_Higgs_ggH2in": {"value": 1.039, "processes": ["ggh"]},  # TODO for vbf (0.933, 1.046)
            "QCDscale_Higgs_ggH2in_ACCEPT": {"value": 1.4, "processes": ["ggh"]},
            "QCDscale_Higgs_qqH": {"value": (1.004, 0.997), "processes": ["vbf"]},
            "QCDscale_Higgs_qqH_ACCEPT": {"value": 1.02, "processes": ["vbf"]},
            "QCDscale_Higgs_zh": {"value": (1.03, 0.969), "processes": ["zh"]},
            "QCDscale_Higgs_wh": {"value": (1.005, 0.993), "processes": ["wh"]},
            "QCDscale_Higgs_ggzh": {"value": (1.251, 0.811), "processes": ["ggzh"]},
        },
    }[year]


def get_Higgs_pdf_unc(year: str, analysis: str) -> dict[str, Any]:
    """Return PDF systematics for a given year and analysis."""
    _ = analysis  # Currently unused
    return {
        "Run3": {
            "pdf_Higgs_gg": {"value": 1.032, "processes": ["ggh"]},
            "pdf_Higgs_ggzh": {"value": (1.024, 0.982), "processes": ["ggzh"]},
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
            "top_Reweight_13p6TeV": {"value": 1.1, "processes": ["top"]},
            # "ZJets_Norm_13p6TeV": {"value": 1.2, "processes": ["qcdzll", "ewkzll"]}, #TODO was used for VBF
            # "GJets_Norm_13p6TeV": {"value": 1.2, "processes": ["qcdgjets"]}, #TODO was used for VBF
            # "UEPS": {"value": 1.168, "processes": ["ggh"]},  # TODO only for VBF?
        },
    }[year]


def get_generic_shape(systematics: list[str], analysis: str) -> dict[str, dict[str, Any]]:
    """Return JER and JES shape systematics for a given year and analysis."""
    results = {
        syst: {
            region: {"value": 1.0, "processes": get_processes_by_region(analysis=analysis, region=region, types=["signals", "backgrounds"])}
            for region in get_all_regions()
        }
        for syst in systematics
    }
    return results


def get_jec_shape(year: str, analysis: str) -> dict[str, dict[str, Any]]:
    """Return JER and JES shape systematics for a given year and analysis."""
    # TODO need to change to CMS_scale_j_Absolute
    jecs = get_jes_variations_names(year=year)
    return get_generic_shape(systematics=jecs, analysis=analysis)


def get_prefiring_shape(year: str, analysis: str) -> dict[str, Any]:
    """Return prefiring shape systematics for a given year and analysis."""
    systematics = {
        "vbf": {"Run3": {}},
        "monojet": {"Run3": get_generic_shape(systematics=["prefiring_jet"], analysis=analysis)},
    }
    return systematics[analysis][year]


def get_pu_shape(year: str, analysis: str) -> dict[str, Any]:
    """Return prefiring shape systematics for a given year and analysis."""
    systematics = {
        "vbf": {"Run3": {}},
        "monojet": {"Run3": get_generic_shape(systematics=["pu"], analysis=analysis)},
    }
    return systematics[analysis][year]


def get_automc_stat(year: str, analysis: str, n_bins: int) -> dict[str, dict[str, Any]]:
    """Return autoMC stat shapes for minor backgrounds for a given year and analysis."""

    automc_shape = {
        f"{region}_mergedMCBkg_{analysis}_{year}_stat_bin{idx}": {
            region: {"value": 1.0, "processes": get_processes_by_region(analysis=analysis, region=region, types=["backgrounds"])},
        }
        for region in get_all_regions()
        for idx in range(n_bins)
    }
    return automc_shape
