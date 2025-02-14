# -*- coding: utf-8 -*-

"""Getters for OBO ontologies."""

from typing import Iterable, Type

from bioversions.utils import Getter, OboGetter, VersionType

__all__ = [
    "iter_obo_getters",
    "ChebiGetter",
    "GoGetter",
    "DoidGetter",
    "PrGetter",
]


class ChebiGetter(OboGetter):
    """A getter for ChEBI."""

    name = "ChEBI"
    bioregistry_id = "chebi"
    version_type = VersionType.sequential
    homepage_fmt = "ftp://ftp.ebi.ac.uk/pub/databases/chebi/archive/rel{version}/"


class GoGetter(OboGetter):
    """A getter for the Gene Ontology (GO)."""

    name = "Gene Ontology"
    bioregistry_id = "go"
    version_type = VersionType.date
    strip_version_prefix = True
    date_version_fmt = "%Y-%m-%d"
    homepage_fmt = "http://archive.geneontology.org/full/{version}/"


class DoidGetter(OboGetter):
    """A getter for the Disease Ontology (DO)."""

    name = "Disease Ontology"
    homepage_fmt = "https://github.com/DiseaseOntology/HumanDiseaseOntology/tree/main/src/ontology/releases/{version}"
    bioregistry_id = "doid"
    version_type = VersionType.date
    strip_version_prefix = True
    strip_file_suffix = True
    date_version_fmt = "%Y-%m-%d"


class PrGetter(OboGetter):
    """A getter for the Protein Ontology (PR)."""

    name = "Protein Ontology"
    bioregistry_id = "pr"
    version_type = VersionType.semver_minor
    homepage_fmt = "https://proconsortium.org/download/release_{version}/"


def iter_obo_getters() -> Iterable[Type[Getter]]:
    """Iterate over OBO getters."""
    yield from OboGetter.__subclasses__()


def _main():
    for getter in iter_obo_getters():
        getter.print()


if __name__ == "__main__":
    _main()
