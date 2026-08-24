# Solution spec: <NAME>

> One file describes the whole solution. Fill in what applies. Delete the guidance notes in
> angle brackets as you go. The acceptance checks at the bottom are the contract the test harness
> answers to, so write them as statements a test can verify.

## 1. Intent

<One paragraph. What does this solution do, and for whom. The ambitious goal in one sentence,
then the simplest first version that hits it.>

## 2. Target and profile

- **Field hardware:** <real controllers and protocols, or "none, driven by simulation scripts">
- **Runtime host:** <see Hardware-Spec.md (from Hardware-Spec.template.md)>
- **Build and test profile:** Development (TServer 3201). Production is configured but not the
  build target.
- **Sandbox name for testing:** `ai-test-<slug>`

## 3. Data foundation

### 3.1 UserTypes (UDTs)

<The reusable structured types. One row per type. Members with their data type, engineering unit,
range, and whether retentive. Build these first.>

| UserType | Member | Type | Unit | Range | Retentive | Notes |
|---|---|---|---|---|---|---|
| `Tank` | `Level` | Double | % | 0..100 | no | |
| `Tank` | `Temperature` | Double | degC | 0..120 | no | |
| `Tank` | `Status` | Integer | | enum | yes | |

### 3.2 UNS and Asset Tree

<The hierarchy. Areas, units, and which UDT instances live where. Name hierarchically.>

```
Area1/
  Unit1   (UDT: Tank)
  Unit2   (UDT: Pump)
Area2/
  ...
```

- **Expected top-level UNS tag count:** <n>
- **Expected asset tree roots:** <list>

## 4. Connect

<Devices, or simulation. If real: channel, protocol, node, the points and the tags they map to.
If simulated: which tags the simulation drives and roughly how they move (so the test can assert
movement and range).>

- **Mode:** <devices | simulation>
- **Tags that must hold live, moving values in runtime:** <list of tag paths>

## 5. Monitor

### 5.1 Alarms

| Tag | Condition | Limit | Group | Area | Priority |
|---|---|---|---|---|---|
| `Area1/Unit1.Level` | HiHi | 95 | Process | Area1 | High |

- **Expected alarm item count:** <n>  **Groups:** <n>  **Areas:** <n>

### 5.2 Historian

| Tag | Table | Trigger | Retention |
|---|---|---|---|
| `Area1/Unit1.Level` | Process | on change | <period> |

- **Expected historian tag count:** <n>  **Tables:** <n>

## 6. Screens

<The displays and what each shows. Build from Symbols, one per asset type.>

| Display | Shows | Key controls |
|---|---|---|
| Overview | plant status | symbol per unit, alarm list |

- **Expected display count:** <n>

## 7. Security

- **Users / roles:** <list, or "default plus one operator role">

## 8. Acceptance checks (the contract for tests/)

<Short, verifiable statements. Each becomes an assertion in Sites/<Name>/Tests/expected.json.>

- [ ] The solution defines exactly <n> domain UserTypes: <list>.
- [ ] The UNS has <n> top-level tags and the asset tree exposes <roots>.
- [ ] <n> alarms exist across <n> groups and <n> areas.
- [ ] <n> historian tags log into <n> tables.
- [ ] <n> displays exist.
- [ ] In the running runtime, `<tag path>` holds a value with good quality, a timestamp under
      <n> seconds old, within <range>.
- [ ] Forcing `<condition>` makes alarm `<name>` go active.
