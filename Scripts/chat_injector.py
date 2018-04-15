import services
import injector
import sims
MP_Chat_sa_instance_ids = (15046892415517235728, )
    
@injector.inject_to(sims.sim.Sim, 'on_add')
def MP_Chat_add_super_affordances(original, self):
    original(self)
    sa_list = []
    affordance_manager = services.affordance_manager()
    for sa_id in MP_Chat_sa_instance_ids:
        tuning_class = affordance_manager.get(sa_id)
        if not tuning_class is None:
            sa_list.append(tuning_class)
    self._super_affordances = self._super_affordances + tuple(sa_list)