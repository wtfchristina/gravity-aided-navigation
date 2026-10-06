from gravity_nav.packets import SensorPacket
from gravity_nav.replay import write_jsonl, read_jsonl, replay_packets


def test_jsonl_roundtrip_and_fast_replay(tmp_path):
    packets=[SensorPacket('imu',float(i),i,{'ax_mps2':0.0,'ay_mps2':0.0,'dt_s':1.0}) for i in range(3)]
    path=write_jsonl(tmp_path/'log.jsonl',packets)
    loaded=read_jsonl(path)
    assert loaded == packets
    seen=[]
    replay_packets(loaded,seen.append,speed=0)
    assert seen == packets
