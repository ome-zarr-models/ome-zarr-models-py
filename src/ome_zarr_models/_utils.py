"""
Private utilities.
"""

from __future__ import annotations

import heapq
from collections import Counter, defaultdict
from dataclasses import MISSING, dataclass, fields, is_dataclass
from functools import total_ordering
from typing import TYPE_CHECKING, Any, Self, TypeVar

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
    from ome_zarr_models._v06.coordinate_transforms import (
        CoordinateSystem,
        CoordinateSystemIdentifier,
        Transform,
    )
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
    attrs_dict = group.attrs.asdict()
    if "ome" not in attrs_dict:
        raise ValueError("Zarr group attributes does not contain an 'ome' key")
    ome_attributes = attrs_cls.model_validate(attrs_dict["ome"])

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


GRAPHVIZ_ATTRS = {"fontname": "open-sans"}


@dataclass(frozen=True)
class TransformGraphNode:
    name: str
    path: str | None = None

    @classmethod
    def from_identifier(cls, identifier: str | CoordinateSystemIdentifier) -> Self:
        from ome_zarr_models._v06.coordinate_transforms import (
            CoordinateSystemIdentifier,
        )

        if isinstance(identifier, CoordinateSystemIdentifier):
            return cls(name=identifier.name, path=identifier.path)
        else:
            return cls(name=identifier)


class TransformGraph:
    """
    A graph representing coordinate transforms.
    """

    # This implementation is a modified version of the astropy implementation
    # See the LICENCE_ASTROPY file next to this one for a copy of the full
    # astropy licence.

    def __init__(self) -> None:
        # Mapping from input coordinate system to a dict of {output_system: transform}
        self._graph: dict[TransformGraphNode, dict[TransformGraphNode, Transform]] = (
            defaultdict(dict)
        )
        # Mapping from system name to coordinate system
        self._systems: dict[str, CoordinateSystem] = {}
        # Mapping from path to child transform graphs
        # If this graph is a child image already, this dictionary stays empty.
        self._child_graphs: dict[str, TransformGraph] = {}
        # Cache of paths between systems
        self._shortestpaths: dict[
            TransformGraphNode,
            dict[TransformGraphNode, list[TransformGraphNode] | None],
        ] = {}

    def add_system(self, system: CoordinateSystem) -> None:
        """
        Add a named coordinate system to the graph.
        """
        self._systems[system.name] = system
        self._shortestpaths = {}

    def add_subgraph(self, path: str, graph: TransformGraph) -> None:
        """
        Add a subgraph to this graph.
        """
        self._child_graphs[path] = graph
        self._shortestpaths = {}

    def add_transform(self, transform: Transform) -> None:
        """
        Add a transform to the graph.
        """
        if transform.input is None or transform.output is None:
            raise ValueError("transform must have both input and output set")
        input_ = TransformGraphNode.from_identifier(transform.input)
        output_ = TransformGraphNode.from_identifier(transform.output)
        self._graph[input_][output_] = transform
        self._shortestpaths = {}

    def find_shortest_path(
        self, from_node: TransformGraphNode, to_node: TransformGraphNode
    ) -> list[TransformGraphNode] | None:
        """
        Computes the shortest distance along the transform graph from
        one system to another.

        Parameters
        ----------
        from_node : TransformGraphNode
            The coordinate frame class to start from.
        to_node : TransformGraphNode
            The coordinate frame class to transform into.

        Returns
        -------
        path : list of class or None
            The path from `from_node` to `to_node` as an in-order sequence
            of TransformGraphNodes.  This list includes *both* ``from_node`` and
            `to_node`. Is `None` if there is no possible path.
        """
        # Copied from astropy with minor variations, under a BSD-3 licence.
        # See the LICENCE_ASTROPY file next to this one for a copy of the full licence.
        inf = float("inf")

        # special-case the 0 or 1-path
        if to_node is from_node:
            # Means there's no transform necessary to go from it to itself.
            return [to_node]

        # otherwise, need to construct the path:
        if from_node in self._shortestpaths:
            # already have a cached result
            return self._shortestpaths[from_node].get(to_node)

        # use Dijkstra's algorithm to find shortest path in all other cases

        # We store nodes as `dict` keys because differently from `list` uniqueness is
        # guaranteed and differently from `set` insertion order is preserved.
        nodes: dict[TransformGraphNode, TransformGraphNode | None] = {}
        for node, node_graph in self._graph.items():
            nodes[node] = None
            nodes |= dict.fromkeys(node_graph)

        if from_node not in nodes or to_node not in nodes:
            # from_node or to_node are isolated or not registered, so there's
            # certainly no way to get from one to the other
            return None

        edge_weights = {}
        # construct another graph that is a dict of dicts of priorities
        # (used as edge weights in Dijkstra's algorithm)
        for a, graph in self._graph.items():
            edge_weights[a] = dict.fromkeys(graph, 1.0)

        # count is needed because in py 3.x, tie-breaking fails on the nodes.
        # this way, insertion order is preserved if the weights are the same
        @total_ordering
        @dataclass(frozen=False)
        class QItem:
            distance: float
            count: int
            node: TransformGraphNode
            path: list[TransformGraphNode]

            def __lt__(self, other: QItem) -> bool:
                return (self.distance, self.count) < (other.distance, other.count)

        q = [QItem(distance=0, count=-1, node=from_node, path=[])]
        q.extend(
            QItem(distance=inf, count=i, node=n, path=[])
            for i, n in enumerate(nodes)
            if n is not from_node
        )

        # this dict will store the distance to node from from_node and the path
        result: dict[TransformGraphNode, list[TransformGraphNode] | None] = {}

        # definitely starts as a valid heap because of the insert line; from the
        # node to itself is always the shortest distance
        while q:
            qitem = heapq.heappop(q)

            if qitem.distance == inf:
                # everything left is unreachable from from_node, just copy them to
                # the results and jump out of the loop
                result[qitem.node] = None
                for qitem_ in q:
                    result[qitem_.node] = None
                break
            result[qitem.node] = qitem.path
            qitem.path.append(qitem.node)
            if qitem.node not in edge_weights:
                # Not possible to transform from this system
                continue
            for n2 in edge_weights[qitem.node]:
                if n2 not in result:  # already visited
                    # find where n2 is in the heap
                    for q_elem in q:
                        if q_elem.node == n2:
                            if (
                                newd := qitem.distance + edge_weights[qitem.node][n2]
                            ) < q_elem.distance:
                                q_elem.distance = newd
                                q_elem.path = qitem.path.copy()
                                heapq.heapify(q)
                            break
                    else:
                        raise ValueError("n2 not in heap - this should be impossible!")

        # cache for later use
        self._shortestpaths[from_node] = result
        return result[to_node]

    @property
    def _path_system_names(self) -> set[str]:
        """
        Any coordinate systems referred to in the input/output of transforms,
        but not present in the named coordinate systems list.
        """
        systems = set()
        for sys_in in self._graph:
            systems.add(sys_in)
            for sys_out in self._graph[sys_in]:
                systems.add(sys_out)

        # Filter out any systems that point to another path
        system_names = {sys.name for sys in systems if sys.path is None}
        # Filter out named coordinate systems
        return system_names - set(self._systems.keys())

    def to_graphviz(self) -> graphviz.Digraph:
        """
        Convert to a graphviz graph.

        Notes
        -----
        Requires the `graphviz` package to be installed.
        """
        import graphviz

        graph_gv = graphviz.Digraph()
        # Add main graph
        with graph_gv.subgraph(name="cluster_") as subgraph_gv:
            self._add_nodes_edges(self, subgraph_gv, path=None)
            if len(self._child_graphs) > 0:
                subgraph_gv.attr(label="Scene", **GRAPHVIZ_ATTRS)

        # Add any subgraphs
        for child_path in self._child_graphs:
            with graph_gv.subgraph(name=f"cluster_{child_path}") as subgraph_gv:
                subgraph = self._child_graphs[child_path]
                self._add_nodes_edges(subgraph, subgraph_gv, path=child_path)
                subgraph_gv.attr(label=child_path, **GRAPHVIZ_ATTRS)

        # Add transforms that go between different subgraphs
        for input_sys in self._graph:
            for output_sys in self._graph[input_sys]:
                # Don't add internal transforms
                if (input_sys.path, output_sys.path) == (None, None):
                    continue
                print(input_sys.name, output_sys.name)
                print(input_sys.path, output_sys.path)
                print()
                graph_gv.edge(
                    self._node_key(input_sys.path, input_sys.name),
                    self._node_key(output_sys.path, output_sys.name),
                    label=self._graph[input_sys][output_sys]._short_name,
                    **GRAPHVIZ_ATTRS,
                )

        return graph_gv

    @classmethod
    def _add_nodes_edges(
        cls, graph: TransformGraph, graphviz_graph: graphviz.Digraph, path: str | None
    ) -> None:
        """
        Add nodes and edges to a graphviz graph.
        """
        # Add named systems as nodes
        for system_name in graph._systems:
            graphviz_graph.node(
                cls._node_key(path, system_name),
                label=system_name,
                style="filled",
                fillcolor="#fdbb84",
                **GRAPHVIZ_ATTRS,
            )
        # Add path systems as nodes
        for system_name in graph._path_system_names:
            graphviz_graph.node(
                cls._node_key(path, system_name),
                label=system_name,
                style="filled",
                **GRAPHVIZ_ATTRS,
            )

        # Add transforms as edges
        for input_sys in graph._graph:
            for output_sys in graph._graph[input_sys]:
                # Only add transforms internal to this group
                if (input_sys.path, output_sys.path) != (None, None):
                    continue
                graphviz_graph.edge(
                    cls._node_key(path, input_sys.name),
                    cls._node_key(path, output_sys.name),
                    label=graph._graph[input_sys][output_sys]._short_name,
                    **GRAPHVIZ_ATTRS,
                )

    @staticmethod
    def _node_key(path: str | None, system_name: str) -> str:
        """
        Unique key for nodes in graphviz graphs.
        """
        return str(hash((path, system_name)))
