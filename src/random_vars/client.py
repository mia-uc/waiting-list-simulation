import numpy as np
import random

from random_vars.base import ExponentialRandomVar
from random_vars.base import MultiModalRandomVar
from random_vars.base import ConstantRandomVar
from random_vars.base import UniformRandomVar
from random_vars.base import LogNormRandomVar
from random_vars.base import GeometricRandomVar

from entities.client import ClientType, Client


class A:
    # Random Vars of Client Arrive Event
    MorningArrival = ExponentialRandomVar(0, 1/25)
    NoonArrival = ExponentialRandomVar(0, 1/30)
    EveningArrival = ExponentialRandomVar(0, 1/27)

    # Random Vars of Client Leave Totem Event
    LeaveTotem = UniformRandomVar(12, 13)
    RequirementType = MultiModalRandomVar([0.20, 0.30, 0.50])

    # Random Vars for each RequirementType
    class RequirementType1:
        AttentionTime = ExponentialRandomVar(0, 1/10)
        Price = LogNormRandomVar(0.47, 0, np.exp(11.35))

    class RequirementType2:
        AttentionTime = ExponentialRandomVar(0, 1/16)
        Price = -1 * LogNormRandomVar(0.20, 0, np.exp(11.35))

    class RequirementType3:
        AttentionTime = ExponentialRandomVar(0, 1/15)
        Price = ConstantRandomVar(0)

    # Random Vars Leakage
    TotemWaitingListLeakage = GeometricRandomVar(0.03)
    WaitingRoomLeakage = GeometricRandomVar(0.01)
    LeakageCost = ConstantRandomVar(-100000)


class B:
    # Random Vars of Client Arrive Event
    MorningArrival = ExponentialRandomVar(0, 1/15)
    NoonArrival = ExponentialRandomVar(0, 1/20)
    EveningArrival = ExponentialRandomVar(0, 1/10)

    # Random Vars of Client Leave Totem Event
    LeaveTotem = UniformRandomVar(12, 13)
    RequirementType = MultiModalRandomVar([0.40, 0.10, 0.50])

    # Random Vars for each RequirementType
    class RequirementType1:
        AttentionTime = ExponentialRandomVar(0, 1/14)
        Price = LogNormRandomVar(0.33, 0, np.exp(11.92))

    class RequirementType2:
        AttentionTime = ExponentialRandomVar(0, 1/20)
        Price = -1 * LogNormRandomVar(0.10, 0, np.exp(11.92))

    class RequirementType3:
        AttentionTime = ExponentialRandomVar(0, 1/10)
        Price = ConstantRandomVar(0)

    # Random Vars Leakage
    TotemWaitingListLeakage = GeometricRandomVar(0.03)
    WaitingRoomLeakage = GeometricRandomVar(0.01)
    LeakageCost = ConstantRandomVar(-300000)


class C:
    # Random Vars of Client Arrive Event
    MorningArrival = ExponentialRandomVar(0, 1/8)
    NoonArrival = ExponentialRandomVar(0, 1/15)
    EveningArrival = ExponentialRandomVar(0, 1/15)

    # Random Vars of Client Leave Totem Event
    LeaveTotem = UniformRandomVar(12, 13)
    RequirementType = ConstantRandomVar(1)

    # Random Vars for each RequirementType
    class RequirementType1:
        AttentionTime = ExponentialRandomVar(0, 1/12)
        Price = LogNormRandomVar(0.20, 0, np.exp(11.51))

    # Random Vars Leakage
    TotemWaitingListLeakage = GeometricRandomVar(0.03)
    WaitingRoomLeakage = GeometricRandomVar(0.01)
    LeakageCost = ConstantRandomVar(-100000)


def get_random_var(type: ClientType):
    if type == ClientType.A:
        return A
    if type == ClientType.B:
        return B
    if type == ClientType.C:
        return C
    raise Exception("ClientRandomVar Not Found")

########################################################################
# Random Vars of Client Arrive Event
########################################################################


def next_morning_arrive(type: ClientType):
    rvar = get_random_var(type)
    return rvar.MorningArrival.generate()


def next_noon_arrive(type: ClientType):
    rvar = get_random_var(type)
    return rvar.NoonArrival.generate()


def next_evening_arrive(type: ClientType):
    rvar = get_random_var(type)
    return rvar.EveningArrival.generate()

########################################################################
# Random Vars of Client Leave Totem Event
########################################################################


def next_totem_finish(type: ClientType):
    rvar = get_random_var(type)
    return rvar.LeaveTotem.generate() / 3600


def select_requirement(type: ClientType):
    rvar = get_random_var(type)
    return rvar.RequirementType.generate()

########################################################################
# Random Vars for each RequirementType
########################################################################


def get_requirement_random_var(type: ClientType, requirement_type):
    rvar = get_random_var(type)

    if requirement_type == 1:
        return rvar.RequirementType1
    if requirement_type == 2:
        return rvar.RequirementType2
    if requirement_type == 3:
        return rvar.RequirementType3
    raise Exception("ClientRandomVar Not Found")


def get_attention(type: ClientType, requirement_type):
    rvar = get_requirement_random_var(type, requirement_type)
    return rvar.AttentionTime.generate()


def get_price(type: ClientType, requirement_type):
    rvar = get_requirement_random_var(type, requirement_type)
    return rvar.Price.generate()


########################################################################
# Random Vars Leakage
########################################################################


def leakage_from_totem_waiting_list(client: Client, clock):
    rvar = get_random_var(client.type)
    t = round((clock - client.arrive_time) * 60)

    prob = rvar.TotemWaitingListLeakage.generate(t)
    rnum = random.random()

    return rnum > prob


def leakage_from_waiting_room(client: Client, clock):
    rvar = get_random_var(client.type)
    t = round((clock - client.waiting_room_arrive_time) * 60)

    prob = rvar.WaitingRoomLeakage.generate(t)
    rnum = random.random()

    return rnum > prob


def leakage_cost(client: Client):
    rvar = get_random_var(client.type)
    return rvar.LeakageCost.generate()
