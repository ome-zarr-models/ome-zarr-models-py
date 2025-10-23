"""
Private utilities.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import MISSING, fields, is_dataclass
from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
import pydantic_zarr.v2
import pydantic_zarr.v3
from pydantic import create_model

from ome_zarr_models.base import BaseAttrsv2, BaseAttrsv3
from ome_zarr_models.common.validation import (
    check_array_path,
    check_group_path,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    import graphviz
    import zarr
    from zarr.abc.store import Store

    from ome_zarr_models._v06.base import BaseGroupv06
    from ome_zarr_models._v06.coordinate_transforms import CoordinateSystem, Transform
    from ome_zarr_models.v04.base import BaseGroupv04
    from ome_zarr_models.v05.base import BaseGroupv05


TBaseGroupv2 = TypeVar("TBaseGroupv2", bound="BaseGroupv04[Any]")
TAttrsv2 = TypeVar("TAttrsv2", bound=BaseAttrsv2)


def _from_zarr_v2(
    group: zarr.Group,
    group_cls: type[TBaseGroupv2],
    attrs_cls: type[TAttrsv2],
) -> TBaseGroupv2:
    """
    Create a GroupSpec from a potentially unlistable Zarr group.

    This uses methods on the attribute class to get required and optional
    paths to ararys and groups, and then manually constructs the GroupSpec
    from those paths.

    Parameters
    ----------
    group :
        Zarr group to create GroupSpec from.
    group_cls :
        Class of the Group to return.
    attrs_cls :
        Attributes class.
    """
    # on unlistable storage backends, the members of this group will be {}
    group_spec_in: pydantic_zarr.v2.AnyGroupSpec
    group_spec_in = pydantic_zarr.v2.GroupSpec.from_zarr(group, depth=0)
    attributes = attrs_cls.model_validate(group_spec_in.attributes)

    members_tree_flat: dict[
        str, pydantic_zarr.v2.AnyGroupSpec | pydantic_zarr.v2.AnyArraySpec
    ] = {}

    # Required array paths
    for array_path in attrs_cls.get_array_paths(attributes):
        array_spec = check_array_path(group, array_path, expected_zarr_version=2)
        members_tree_flat["/" + array_path] = array_spec

    # Optional array paths
    for array_path in attrs_cls.get_optional_array_paths(attributes):
        try:
            array_spec = check_array_path(group, array_path, expected_zarr_version=2)
        except ValueError:
            continue
        members_tree_flat["/" + array_path] = array_spec

    # Required group paths
    required_groups = attrs_cls.get_group_paths(attributes)
    for group_path in required_groups:
        check_group_path(group, group_path, expected_zarr_version=2)
        group_flat = required_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    # Optional group paths
    optional_groups = attrs_cls.get_optional_group_paths(attributes)
    for group_path in optional_groups:
        try:
            check_group_path(group, group_path, expected_zarr_version=2)
        except FileNotFoundError:
            continue
        group_flat = optional_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    members_normalized: pydantic_zarr.v2.AnyGroupSpec = (
        pydantic_zarr.v2.GroupSpec.from_flat(members_tree_flat)
    )
    return group_cls(members=members_normalized.members, attributes=attributes)


TBaseGroupv3 = TypeVar("TBaseGroupv3", bound="BaseGroupv05[Any] | BaseGroupv06[Any]")
TAttrsv3 = TypeVar("TAttrsv3", bound=BaseAttrsv3)


def _from_zarr_v3(
    group: zarr.Group,
    group_cls: type[TBaseGroupv3],
    attrs_cls: type[TAttrsv3],
) -> TBaseGroupv3:
    """
    Create a GroupSpec from a potentially unlistable Zarr group.

    This uses methods on the attribute class to get required and optional
    paths to ararys and groups, and then manually constructs the GroupSpec
    from those paths.

    Parameters
    ----------
    group :
        Zarr group to create GroupSpec from.
    group_cls :
        Class of the Group to return.
    attrs_cls :
        Attributes class.
    """
    # on unlistable storage backends, the members of this group will be {}
    group_spec_in: pydantic_zarr.v3.AnyGroupSpec
    group_spec_in = pydantic_zarr.v3.GroupSpec.from_zarr(group, depth=0)
    ome_attributes = attrs_cls.model_validate(group.attrs.asdict()["ome"])

    members_tree_flat: dict[
        str, pydantic_zarr.v3.AnyGroupSpec | pydantic_zarr.v3.AnyArraySpec
    ] = {}

    # Required array paths
    for array_path in attrs_cls.get_array_paths(ome_attributes):
        array_spec = check_array_path(group, array_path, expected_zarr_version=3)
        members_tree_flat["/" + array_path] = array_spec

    # Optional array paths
    for array_path in attrs_cls.get_optional_array_paths(ome_attributes):
        try:
            array_spec = check_array_path(group, array_path, expected_zarr_version=3)
        except ValueError:
            continue
        members_tree_flat["/" + array_path] = array_spec

    # Required group paths
    required_groups = attrs_cls.get_group_paths(ome_attributes)
    for group_path in required_groups:
        check_group_path(group, group_path, expected_zarr_version=3)
        group_flat = required_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    # Optional group paths
    optional_groups = attrs_cls.get_optional_group_paths(ome_attributes)
    for group_path in optional_groups:
        try:
            check_group_path(group, group_path, expected_zarr_version=3)
        except FileNotFoundError:
            continue
        group_flat = optional_groups[group_path].from_zarr(group[group_path]).to_flat()  # type: ignore[arg-type]
        for path in group_flat:
            members_tree_flat["/" + group_path + path] = group_flat[path]

    members_normalized: pydantic_zarr.v3.AnyGroupSpec
    members_normalized = pydantic_zarr.v3.GroupSpec.from_flat(members_tree_flat)
    return group_cls(  # type: ignore[return-value]
        members=members_normalized.members, attributes=group_spec_in.attributes
    )


def get_store_path(store: Store) -> str:
    """
    Get a path from a zarr store
    """
    if hasattr(store, "path"):
        return store.path  # type: ignore[no-any-return]

    return ""


T = TypeVar("T")


def duplicates(values: Iterable[T]) -> dict[T, int]:
    """
    Takes a sequence of hashable elements and returns a dict where the keys are the
    elements of the input that occurred at least once, and the values are the
    frequencies of those elements.
    """
    counts = Counter(values)
    return {k: v for k, v in counts.items() if v > 1}


def dataclass_to_pydantic(dataclass_type: type) -> type[pydantic.BaseModel]:
    """Convert a dataclass to a Pydantic model.

    Parameters
    ----------
    dataclass_type : type
        The dataclass to convert to a Pydantic model.

    Returns
    -------
    type[pydantic.BaseModel] a Pydantic model class.
    """
    if not is_dataclass(dataclass_type):
        raise TypeError(f"{dataclass_type} is not a dataclass")

    field_definitions = {}
    for _field in fields(dataclass_type):
        if _field.default is not MISSING:
            # Default value is provided
            field_definitions[_field.name] = (_field.type, _field.default)
        elif _field.default_factory is not MISSING:
            # Default factory is provided
            field_definitions[_field.name] = (_field.type, _field.default_factory())
        else:
            # No default value
            field_definitions[_field.name] = (_field.type, Ellipsis)

    return create_model(dataclass_type.__name__, **field_definitions)  # type: ignore[no-any-return, call-overload]


class TransformGraph:
    """
    A graph representing coordinate transforms.
    """

    def __init__(self) -> None:
        # Mapping from input coordinate system to a dict of {output_system: transform}
        self._graph: dict[str, dict[str, Transform]] = defaultdict(dict)
        self._named_systems: dict[str, CoordinateSystem] = {}
        self._default_system = ""
        self._subgraphs: dict[str, TransformGraph] = {}

    def add_system(self, system: CoordinateSystem) -> None:
        """
        Add a named coordinate system to the graph.
        """
        self._named_systems[system.name] = system

    def add_subgraph(self, path: str, graph: TransformGraph) -> None:
        """
        Add a subgraph to this graph.
        """
        self._subgraphs[path] = graph

    def set_default_system(self, system_name: str) -> None:
        """
        Set the default coordinate system used when transforming
        out of this graph.
        """
        if system_name not in self._named_systems:
            raise ValueError(
                f"System named '{system_name}' not in list of named coordinate systems "
                f"({self._named_systems.keys()})"
            )
        self._default_system = system_name

    def add_transform(self, transform: Transform) -> None:
        """
        Add a transform to the graph.
        """
        if transform.input is None or transform.output is None:
            raise ValueError("transform must have both input and output set")
        self._graph[transform.input][transform.output] = transform

    def to_graphviz(self) -> graphviz.Digraph:
        """
        Convert to a graphviz graph.

        Notes
        -----
        Requires the `graphviz` package to be installed.
        """
        import graphviz

        graph_gv = graphviz.Digraph()
        self._add_nodes_edges(self, graph_gv)

        for graph_name in self._subgraphs:
            with graph_gv.subgraph(name=f"cluster_{graph_name}") as subgraph_gv:
                subgraph = self._subgraphs[graph_name]
                self._add_nodes_edges(subgraph, subgraph_gv, path=graph_name)
                # Add edge between default coordinate system and path name in
                # the collection
                graph_gv.edge(
                    self._node_key(graph_name, subgraph._default_system),
                    self._node_key("", graph_name),
                    arrowhead="none",
                )
                subgraph_gv.attr(label=graph_name)

        return graph_gv

    @property
    def _path_systems(self) -> set[str]:
        systems = set()
        for sys_in in self._graph:
            systems.add(sys_in)
            for sys_out in self._graph[sys_in]:
                systems.add(sys_out)

        return systems - set(self._named_systems.keys())

    @classmethod
    def _add_nodes_edges(
        cls, graph: TransformGraph, graphviz_graph: graphviz.Digraph, path: str = ""
    ) -> None:
        """
        Add nodes and edges to a graphviz graph.
        """
        global_attrs = {"fontname": "open-sans"}
        for system_name in graph._named_systems:
            graphviz_graph.node(
                cls._node_key(path, system_name),
                label=system_name,
                style="filled",
                fillcolor="#fdbb84",
                **global_attrs,
            )

        for system_name in graph._path_systems:
            graphviz_graph.node(
                cls._node_key(path, system_name),
                label=system_name,
                style="filled",
                # fillcolor="#fdbb84",
                **global_attrs,
            )

        for input_sys in graph._graph:
            for output_sys in graph._graph[input_sys]:
                graphviz_graph.edge(
                    cls._node_key(path, input_sys),
                    cls._node_key(path, output_sys),
                    label=graph._graph[input_sys][output_sys]._short_name,
                    **global_attrs,
                )

    @staticmethod
    def _node_key(path: str, system_name: str) -> str:
        """
        Unique key for nodes in graphviz graphs.
        """
        return str(hash((path, system_name)))
