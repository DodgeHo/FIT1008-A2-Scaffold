from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from branch_decision import BranchDecision
from computer import Computer

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from virus import VirusType


@dataclass
class RouteSplit:
    """
    A split in the route.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Route
    bottom: Route
    following: Route

    def remove_branch(self) -> RouteStore:
        """Removes the branch, should just leave the remaining following route."""
        following_route = self.following
        return following_route.store

@dataclass
class RouteSeries:
    """
    A computer, followed by the rest of the route

    --computer--following--

    """

    computer: Computer
    following: Route

    def remove_computer(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Removing the computer at the beginning of this series.
        """
        following_route = self.following
        return following_route.store

    def add_computer_before(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer in series before the current one.
        """
        return RouteSeries(computer,Route(self))

    def add_computer_after(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer after the current computer, but before the following route.
        """
        next_route = Route(RouteSeries(computer, self.following))
        return RouteSeries(self.computer, next_route)

    def add_empty_branch_before(self) -> RouteStore:
        """Returns a route store which would be the result of:
        Adding an empty branch, where the current routestore is now the following path.
        """
        return RouteSplit(Route(None),Route(None),Route(self))


    def add_empty_branch_after(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding an empty branch after the current computer, but before the following route.
        """
        next_following = RouteSplit(Route(None),Route(None), self.following)

        return RouteSeries(self.computer, Route(next_following))


RouteStore = Union[RouteSplit, RouteSeries, None]


@dataclass
class Route:

    store: RouteStore = None

    def add_computer_before(self, computer: Computer) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding a computer before everything currently in the route.
        """
        return Route(RouteSeries(computer, self))

    def add_empty_branch_before(self) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding an empty branch before everything currently in the route.
        """
        empty_branch = RouteSplit(
            Route(None),
            Route(None),
            self
        )
        return Route(empty_branch)

    def follow_path(self, virus_type: VirusType) -> None:
        """Follow a path and add computers according to a virus_type."""


        rest_store_list = deque() 
        rest_store_list.append(self.store)

        while(len(rest_store_list)):
            next_store = rest_store_list.pop()

            if isinstance(next_store, RouteSplit):
                decision = virus_type.select_branch(next_store.top, next_store.bottom)

                following_store = next_store.following.store
                rest_store_list.append(following_store)

                if (decision == BranchDecision.TOP):
                    next_store = next_store.top.store
                elif (decision == BranchDecision.BOTTOM):
                    next_store = next_store.bottom.store
                else:
                    #next_store = None
                    break

            elif isinstance(next_store, RouteSeries):
                virus_type.add_computer(next_store.computer)
                next_store = next_store.following.store

            else:
                next_store = None

            if not next_store == None:
                rest_store_list.append(next_store)


    def add_all_computers(self) -> list[Computer]:
        """Returns a list of all computers on the route."""

        computers_list = []
        searching_list = [self.store]  

        while len(searching_list) > 0:
            current = searching_list.pop(0)

            if isinstance(current, RouteSeries):
                computers_list.append(current.computer)
                if current.following.store!= None:
                    searching_list.append(current.following.store)

            elif isinstance(current, RouteSplit):
                for pointer in [current.top.store, current.bottom.store, current.following.store]:
                    if pointer != None:
                        searching_list.append(pointer)


        return computers_list