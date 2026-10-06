from gravity_nav.assured_pnt import AssuredPNTConfig
from gravity_nav.gateway import NavigationGateway
from gravity_nav.packets import SensorPacket


def test_gateway_processes_imu():
    cfg=AssuredPNTConfig(duration_s=2,dt=.5)
    g=NavigationGateway(cfg)
    x0=g.ekf.x.copy()
    g.process(SensorPacket('imu',.5,1,{'ax_mps2':0.1,'ay_mps2':0.0,'dt_s':.5}))
    assert g.imu_packets == 1
    assert g.ekf.x[0] > x0[0]
