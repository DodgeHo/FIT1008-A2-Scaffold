from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries
from branch_decision import BranchDecision


class VirusType(ABC):

    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)

    @abstractmethod
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        raise NotImplementedError()


class TopVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the top branch
        return BranchDecision.TOP


class BottomVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the bottom branch
        return BranchDecision.BOTTOM


class LazyVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Try looking into the first computer on each branch,
        take the path of the least difficulty.
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        if top_route and bot_route:
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            if top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                return BranchDecision.TOP
            elif top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP
        # If one of them has a computer, don't take it.
        # If neither do, then take the top branch.
        if top_route:
            return BranchDecision.BOTTOM
        return BranchDecision.TOP


class RiskAverseVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus is risk averse and likes to choose the path with the lowest risk factor.
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        if top_route and bot_route:
            
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer
            both_zero_risk = False
            # If it sees any computer with a risk factor of 0.0, it should take that path.
            if top_comp.risk_factor == 0.0 and bot_comp.risk_factor != 0.0:
                return BranchDecision.TOP
            elif bot_comp.risk_factor == 0.0 and top_comp.risk_factor != 0.0:
                return BranchDecision.BOTTOM
            elif  top_comp.risk_factor == 0.0 and bot_comp.risk_factor == 0.0:
                # If there are multiple computers with a risk_factor of 0.0, it should take the path with the lowest hacking difficulty.
                if top_comp.hacking_difficulty != bot_comp.hacking_difficulty:
                    if top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                        return BranchDecision.TOP
                    else:
                        return BranchDecision.BOTTOM
                    
                both_zero_risk = True

            # If there is still a tie, continue to the next comparisons.
            # Take the highest value between the hacking_difficulty and the half of the hacked_value.

            top_coef = max(top_comp.hacking_difficulty, 0.5 * top_comp.hacked_value)
            bot_coef = max(bot_comp.hacking_difficulty, 0.5 * bot_comp.hacked_value)
            # Then, divide this by the risk factor.
            if not both_zero_risk:
                # If the risk factor is zero, skip this step.
                top_coef /= top_comp.risk_factor
                bot_coef /= bot_comp.risk_factor

            # Compare the two paths and take the path with the higher value.
            if top_coef > bot_coef:
                return BranchDecision.TOP
            elif bot_coef > top_coef:
                return BranchDecision.BOTTOM
            
            # If there is a tie, take the path with the lower risk factor.
            if top_comp.risk_factor < bot_comp.risk_factor:
                return BranchDecision.TOP
            elif top_comp.risk_factor > bot_comp.risk_factor:
                return BranchDecision.BOTTOM
            
            # If there is still a tie, then STOP.
            return BranchDecision.STOP
            
        # If only one has a RouteSeries and the other a RouteSplit, pick the RouteSplit.
        # In all other cases default to the Top path.
        if top_route:
            return BranchDecision.BOTTOM
        return BranchDecision.TOP


class FancyVirus(VirusType):
    CALC_STR = "7 3 + 8 - 2 * 2 /"

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus has a fancy-pants and likes to overcomplicate its approach.
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        if top_route and bot_route:
            
            threshold = self.calculate_threshold()
            if (top_branch.store.computer.hacked_value < threshold):
                return BranchDecision.TOP
            elif (bottom_branch.store.computer.hacked_value < threshold):
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP

        # If only one has a RouteSeries and the other a RouteSplit, pick the RouteSplit.
        # In all other cases default to the Top path.
        if top_route:
            return BranchDecision.BOTTOM
        return BranchDecision.TOP
    

    def calculate_threshold(self) -> float:
        """
        Calculates the threshold by CALC_STR with reverse polish notation
        """

        chars = self.CALC_STR.split()
        char_stack = []
        
        for char in chars:
            if char.isdigit():  
                # number push to the stack
                char_stack.append(float(char)) 
            else: 
                # there should be 2 operands
                b = char_stack.pop() 
                a = char_stack.pop() 

                if char == '+':
                    char_stack.append(a + b)
                elif char == '-':
                    char_stack.append(a - b)
                elif char == '*':
                    char_stack.append(a * b)
                elif char == '/':
                    if b == 0:
                        # If this happen, sth is wrong.
                        raise ValueError("Zero Division.")
                    char_stack.append(a / b)
                    
        
        result = char_stack.pop()
        return result
