# -*- coding: utf-8 -*-

"""Sources for Bioversions."""

import ftplib
import logging
from functools import lru_cache
from typing import Iterable, List, Mapping, Optional, Type

from tqdm import tqdm

from .biofacquim import BiofacquimGetter
from .biogrid import BioGRIDGetter
from .chembl import ChEMBLGetter
from .complexportal import ComplexPortalGetter
from .daily import NCBIGeneGetter
from .dgi import DGIGetter
from .disgenet import DisGeNetGetter
from .drugbank import DrugBankGetter
from .drugcentral import DrugCentralGetter
from .expasy import ExPASyGetter
from .flybase import FlybaseGetter
from .homologene import HomoloGeneGetter
from .intact import IntActGetter
from .interpro import InterProGetter
from .kegg import KEGGGetter
from .mesh import MeshGetter
from .mirbase import MirbaseGetter
from .msigdb import MSigDBGetter
from .npass import NPASSGetter
from .obo import iter_obo_getters
from .ols import extend_ols_getters
from .pathbank import PathBankGetter
from .pfam import PfamGetter
from .pombase import PombaseGetter
from .reactome import ReactomeGetter
from .rfam import RfamGetter
from .rhea import RheaGetter
from .sgd import SgdGetter
from .stringdb import StringDBGetter
from .uniprot import UniProtGetter
from .wikipathways import WikiPathwaysGetter
from .zfin import ZfinGetter
from ..utils import Bioversion, Getter, norm, refresh_daily

__all__ = [
    "resolve",
    "get_rows",
    "get_version",
]

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_getters() -> List[Type[Getter]]:
    """Get a list of getters."""
    # TODO replace with entrypoint lookup
    getters = [
        BioGRIDGetter,
        ChEMBLGetter,
        ComplexPortalGetter,
        DrugBankGetter,
        DrugCentralGetter,
        ExPASyGetter,
        IntActGetter,
        InterProGetter,
        ReactomeGetter,
        RfamGetter,
        WikiPathwaysGetter,
        MirbaseGetter,
        MSigDBGetter,
        PfamGetter,
        UniProtGetter,
        KEGGGetter,
        PathBankGetter,
        NCBIGeneGetter,
        NPASSGetter,
        BiofacquimGetter,
        RheaGetter,
        StringDBGetter,
        HomoloGeneGetter,
        DisGeNetGetter,
        MeshGetter,
        DGIGetter,
        FlybaseGetter,
        PombaseGetter,
        SgdGetter,
        ZfinGetter,
    ]
    getters.extend(iter_obo_getters())
    extend_ols_getters(getters)
    getters: List[Type[Getter]] = sorted(
        getters, key=lambda cls: (cls.bioregistry_id or "", cls.__name__.casefold())
    )
    return getters


def get_getter_dict() -> Mapping[str, Type[Getter]]:
    """Get a dict of getters."""
    rv = {}
    for getter in get_getters():
        if getter.bioregistry_id:
            rv[getter.bioregistry_id] = getter
            rv[norm(getter.bioregistry_id)] = getter
        rv[getter.name] = getter
        rv[norm(getter.name)] = getter
    return rv


def resolve(name: str, use_cache: bool = True) -> Bioversion:
    """Resolve the database name to a :class:`Bioversion` instance."""
    if use_cache:
        return _resolve_helper_cached(name)
    else:
        return _resolve_helper(name)


@refresh_daily
def _resolve_helper_cached(name: str) -> Bioversion:
    return _resolve_helper(name)


def _resolve_helper(name: str) -> Bioversion:
    norm_name = norm(name)
    getter: Type[Getter] = get_getter_dict()[norm_name]
    return getter.resolve()


def get_version(name: str) -> str:
    """Resolve a database name to its version string."""
    return resolve(name).version


def get_rows(use_tqdm: Optional[bool] = False) -> List[Bioversion]:
    """Get the rows, refreshing once per day."""
    return list(_iter_versions(use_tqdm=use_tqdm))


def _iter_versions(use_tqdm: Optional[bool] = False) -> Iterable[Bioversion]:
    it = tqdm(get_getters(), disable=not use_tqdm)

    for cls in it:
        it.set_postfix(name=cls.name)
        try:
            yv = resolve(cls.name)
        except (IOError, AttributeError, ftplib.error_perm):
            tqdm.write(f"failed to resolve {cls.name}")
            continue
        else:
            yield yv
