import pandapower as pp
from pandapower import control


class Storage(control.basic_controller.Controller):
    """Simple storage controller.
       - In case energy is exported, this energy is stored in the storage up until to its maximum capacity.
       - In case energy is imported, energy is taken from the storage up until the minimum is reached.
    """

    def __init__(self, net, gid, time_step_in_minutes=15, epsilon=0.001, soc_percentage=0.0, in_service=True,
                 recycle=False, order=0, level=0, **kwargs):
        super().__init__(net, in_service=in_service, recycle=recycle, order=order, level=level,
                         initial_powerflow=True, **kwargs)
        # read generator attributes from net
        self.gid = gid  # index of the controlled storage
        self.bus = net.storage.at[gid, "bus"]
        self.p_mw = net.storage.at[gid, "p_mw"]
        self.q_mvar = net.storage.at[gid, "q_mvar"]
        self.sn_mva = net.storage.at[gid, "sn_mva"]
        self.name = net.storage.at[gid, "name"]
        self.gen_type = net.storage.at[gid, "type"]
        self.in_service = net.storage.at[gid, "in_service"]
        self.applied = False
        self.applying = False

        # specific attributes
        self.max_e_mwh = net.storage.at[gid, "max_e_mwh"]
        self.min_e_mwh = net.storage.at[gid, "min_e_mwh"]
        self.soc_percent = net.storage.at[gid, "soc_percent"]

        # profile attributes
        self.time_step_in_minutes = time_step_in_minutes
        self.epsilon = epsilon
        self.soc_percent = soc_percentage

        # state of p_mw, q_mvar of current iteration, those should be reset in every iteration,
        # as these are decision variables
        self.p_mw = 0.0
        self.q_mvar = 0.0
        self.maximum_reached = False
        self.minimum_reached = False

    # We choose to represent the storage-unit as a storage element in pandapower.
    # We start with a function calculating the amout of stored energy:
    def get_stored_energy(self):
        # calculating the stored energy
        return self.max_e_mwh * self.soc_percent / 100

    def get_energy(self, p_mw):
        return p_mw * (self.time_step_in_minutes / 60.0)

    # convergence check
    # Also remember that 'is_converged()' returns the boolean value of convergence:
    def is_converged(self, net):
        # check if controller already was applied
        if self.applied:
            self.p_mw = 0.0
            self.q_mvar = 0.0
            self.applied = False
            return True
        return self.applied

    # Also a first step we want our controller to be able to write its P and Q and state of charge values back to the
    # data structure net.
    def write_to_net(self, net):
        # write p, q and soc_percent to bus within the net
        net.storage.at[self.gid, "p_mw"] = -self.p_mw
        net.storage.at[self.gid, "q_mvar"] = -self.q_mvar
        net.storage.at[self.gid, "soc_percent"] = self.soc_percent

    # In case the controller is not yet converged, the control step is executed. In the example it simply
    # adopts a new value according to the previously calculated target and writes back to the net.
    def control_step(self, net):
        # get the current grid import/export value
        p_mw = net.res_ext_grid.at[0, "p_mw"]
        q_mvar = net.res_ext_grid.at[0, "q_mvar"]

        self.p_mw += p_mw
        self.q_mvar += q_mvar

        # check the limits of energy storage capacity
        stored_energy = self.get_stored_energy()
        # negative if energy is exported into the external grid
        # positive if energy is imported from the external grid
        additional_internal_energy = self.get_energy(p_mw)
        if not self.applying and self.get_stored_energy() + -additional_internal_energy > self.max_e_mwh:
            self.maximum_reached = True  # set as convergence criterion
            remaining_energy = self.max_e_mwh - self.get_stored_energy()
            current_energy = -self.get_energy(self.p_mw)
            ratio = remaining_energy / current_energy
            self.p_mw *= ratio
            self.q_mvar *= ratio
        elif not self.applying and self.get_stored_energy() - additional_internal_energy < self.min_e_mwh:
            self.minimum_reached = True  # set as convergence criterion
            # this is not the missing_energy but the remaining energy
            # test case of empty storage not working
            remaining_energy = self.get_stored_energy() - self.min_e_mwh
            current_energy = self.get_energy(self.p_mw)
            served_ratio = remaining_energy / current_energy  # this is the ratio that we can serve from the battery

            self.p_mw *= served_ratio
            self.q_mvar *= served_ratio

        self.applying = True

        # check if we already converged, i.e., we know how much energy we could store
        if abs(p_mw) < self.epsilon or self.maximum_reached or self.minimum_reached:
            self.applied = True

        # update storage
        net.storage.at[self.gid, "p_mw"] = -self.p_mw
        net.storage.at[self.gid, "q_mvar"] = -self.q_mvar

        if self.applied:
            additional_soc_percentage = -(self.get_energy(self.p_mw) / self.max_e_mwh) * 100
            self.soc_percent = self.soc_percent + additional_soc_percentage
            net.storage.at[self.gid, "soc_percent"] = self.soc_percent


class StateException(Exception):
    pass


if __name__ == '__main__':
    # create simple network: load, generation, storage, external grid
    testnet = pp.create_empty_network()

    b1 = pp.create_bus(testnet, vn_kv=0.4, name="consumer")
    b2 = pp.create_bus(testnet, vn_kv=0.4, name="grid_connection")
    b3 = pp.create_bus(testnet, vn_kv=0.4, name="generator")
    b4 = pp.create_bus(testnet, vn_kv=0.4, name="storage")

    pp.create_ext_grid(testnet, bus=b2, vm_pu=1.0, name="grid_connection")
    pp.create_load(testnet, bus=b1, p_mw=0.0004, q_mvar=0.0, name="consumer")
    pp.create_sgen(testnet, bus=b3, p_mw=0.0004, q_mvar=0.0, name="generator")
    store_el = pp.create_storage(testnet, bus=b4, p_mw=0.0, q_mvar=0.0, max_e_mwh=0.01, min_e_mwh=0.0, name="storage")

    ctrl = Storage(net=testnet, gid=store_el, soc_percentage=1)

    pp.create_line(testnet, from_bus=b2, to_bus=b3, name="grid->generator",
                   length_km=0.001, std_type="NAYY 4x50 SE")
    pp.create_line(testnet, from_bus=b3, to_bus=b1, name="generator->consumer",
                   length_km=0.001, std_type="NAYY 4x50 SE")
    pp.create_line(testnet, from_bus=b3, to_bus=b4, name="generator->storage",
                   length_km=0.001, std_type="NAYY 4x50 SE")

    pp.runpp(testnet, run_control=True)

    # print("res_sgen", testnet.res_sgen)
    print("res_storage", testnet.res_storage)
    print("res_ext_grid", testnet.res_ext_grid)
    print("res_load", testnet.res_load)
    print("res_sgen", testnet.res_sgen)
    print("storage", testnet.storage)
    # print(testnet.storage.loc[0, 'soc_percent'])
    # print(testnet.res_ext_grid.loc[0, 'p_mw'])

    print(testnet)
