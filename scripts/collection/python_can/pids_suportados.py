import can, time

def pids_suportados(bus, timeout=0.5):
    """Devolve {id_da_ecu: {pids}} lendo os blocos 0x00, 0x20, 0x40..."""
    por_ecu = {}
    base = 0x00
    while base <= 0xA0:
        bus.send(can.Message(arbitration_id=0x7DF,
                             data=[2, 1, base, 0, 0, 0, 0, 0],
                             is_extended_id=False))
        fim = time.time() + timeout
        proximo = False
        while time.time() < fim:
            rx = bus.recv(timeout=max(0.0, fim - time.time()))
            if rx is None:
                break
            d = rx.data
            if not (0x7E8 <= rx.arbitration_id <= 0x7EF):
                continue
            if len(d) < 7 or d[0] != 6 or d[1] != 0x41 or d[2] != base:
                continue
            mascara = int.from_bytes(d[3:7], "big")
            conj = por_ecu.setdefault(rx.arbitration_id, set())
            for i in range(32):
                if mascara & (1 << (31 - i)):
                    conj.add(base + i + 1)
            if (base + 0x20) in conj:
                proximo = True
        if not proximo:
            break
        base += 0x20
    return por_ecu

with can.Bus(channel="can0", interface="socketcan") as bus:
    for ecu, pids in sorted(pids_suportados(bus).items()):
        print(hex(ecu), sorted(hex(p) for p in pids))