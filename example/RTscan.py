# perform a simple temperature scan with a Keithley2400, Keithley2182A, and LakeShore340
import etmes

I_s = etmes.Keithley2400("GPIB::24::INSTR")
V_m = etmes.Keithley2182A("GPIB::7::INSTR")
T_c = etmes.LakeShore340("ASRL3::INSTR")

exp = etmes.exp([I_s, V_m, T_c], "RTMeas")
m = etmes.meas(exp)

I_s.setSMU("I", 0.01)
I_s.setSrc(0)
I_s.setOutput(True)

V_m.setChannel(1)

T_c.setTemp(10)
T_c.setRamp(2)
exp.wait(60, [T_c], [etmes.waitFlag.positive])

m.scanTemp(
    Tstart=10,
    Tstop=300,
    Tstep=1,
    Trate=5,
    Temp=T_c,
    func=lambda:m.SMUsrc([1e-6, -1e-6], I_s)
)
