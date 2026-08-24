# Highland Municipal Water Treatment Plant: Operator Manual

Day-to-day guide for operating the Highland WTP SCADA. Screen and alarm facts are read from the live
solution (FrameworX 10.1.5.2000); response procedures must be confirmed against the plant's TCEQ-approved
SOPs. Control loops run in the plant PLC: this system **monitors and records**; it does not run the process.

## Starting & accessing the system

1. Start the FrameworX runtime for the `HighlandWTP` solution; the client opens on **MainPage**.
2. Log on from the **LogOn** screen. You start as `Guest` (read-only); log on as `User` (operator) or
   `Administrator` for full access.
3. Web/rich clients connect to the server runtime; the header is responsive (desktop / pad / mobile).

> **Access roles:** `Guest` = view only · `User` = operate (acknowledge alarms, log samples, run reports) ·
> `Administrator` = full configuration.

## Screen guide

- **MainPage (home).** Plant overview and navigation to the four area screens and the dashboard.
- **PlantDashboard.** Operations at a glance, headline finished-water quality gauges (chlorine, pH,
  turbidity), trend, the active-alarm list, KPI datagrid, and recent lab samples. Use **Log Sample** to
  capture current analyzer readings as a finished-water grab sample.
- **Area100_RawWater.** Raw water intake: pumps P101/P102, wet-well level LT101, raw flow FT101, raw
  turbidity/pH AIT101/102.
- **Area200_ChemFeed.** Chemical feed: alum/hypochlorite/fluoride metering pumps P201/202/203 and tank
  levels LT201/202/203. Watch tank levels for refill planning.
- **Area500_Filtration.** Four gravity filters: in-service/backwash status, headloss, effluent turbidity per
  filter. **Only one filter backwashes at a time** (the other three carry full flow).
- **Area600_Disinfection.** Disinfection & clearwell: free chlorine AIT601, finished pH AIT602, finished
  turbidity AIT603, clearwell level LT601, the compliance-critical finished-water parameters.

## Alarm response

Acknowledge from the dashboard alarm list or the alarm viewer. **Critical** alarms require acknowledgement
and immediate response; **Compliance** alarms are regulatory action levels (must be logged); **Warning** is
operational.

| Alarm | Priority | Condition | Operator action |
|---|---|---|---|
| Finished turbidity > 1.0 NTU | Critical | AIT603 HiHi | **SWTR violation.** > TODO: confirm SOP, reduce/clamp output, notify supervisor, log per TCEQ reporting. |
| Free chlorine < 0.1 mg/L | Critical | AIT601 LoLo | **Disinfection failure.** > TODO: confirm SOP: check hypochlorite feed (P202, LT202), hold distribution per policy. |
| Clearwell level LoLo / HiHi | Critical | LT601 <15 % / >98 % | > TODO: confirm SOP, balance production vs. distribution draw; overflow risk at HiHi. |
| Chem tank LOW-LOW (LT201/202/203) | Critical | <10 % | Refill the affected chemical tank now (alum / hypochlorite / fluoride). |
| Free chlorine 0.2 Lo / 3.5 Hi / 4.0 MRDL | Compliance | AIT601 | Action level, adjust pre-chlorine dosing (P202); log the excursion. |
| Finished pH out of 6.5-8.5 (6.0/9.0 limits) | Compliance | AIT602 | Review chemical dosing; log if out of 6.0-9.0. |
| Finished turbidity > 0.3 NTU | Compliance | AIT603 Hi | Investigate filtration; verify filter effluent turbidities. |
| Filter effluent > 0.15 / 0.5 NTU | Compliance | Filter1-4 | Individual filter limit: > TODO: confirm SOP (backwash or remove filter from service). |
| Filter headloss > 8.0 PSI | Warning | Filter1-4 | Backwash due, one filter at a time; system enforces single-filter backwash. |
| Chem tank low (LT201/202/203) | Warning | <15 % | Plan a refill. |
| Clearwell low / high | Warning | LT601 <25 % / >95 % | Balance production vs. demand. |
| Raw turbidity high / raw pH low | Warning | AIT101 >15 / AIT102 <6.0 | Source-water change, review coagulant dosing. |

## Routine tasks

- **Acknowledge** Critical alarms; **log** Compliance excursions per TCEQ reporting requirements.
- **Log finished-water grab samples** on the dashboard at the cadence your monitoring plan requires.
- **Run the shift report** (`ShiftComplianceReport`) at shift change; KPIs and compliance % roll up per shift
  automatically.
- **Monitor filter status**: backwash is PLC-driven; confirm only one filter backwashes at a time.
- **Shift handover:** review dashboard KPIs, active alarms, and the compliance % for the shift.

## Backup, recovery & support

- **Backup:** solution `.dbsln`, the `Business` SQLite file, and the historian (≥1-year regulatory
  retention). > TODO: define backup schedule, retention verification, and the responsible role.
- **Recovery:** restore the `.dbsln` + SQLite + historian from backup; re-publish and start the runtime.
  To restore live data flow, confirm `PLC_Main` is enabled and reachable at `192.168.1.10`.
- **Support contacts:** > TODO: integrator (name & phone) · plant operations lead · TCEQ reporting contact ·
  escalation. Do not leave blank before handover.
