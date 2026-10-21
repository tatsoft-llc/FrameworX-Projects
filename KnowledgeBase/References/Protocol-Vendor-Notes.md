# Reference: protocol vendor notes (address formats and connection traps)

The per-vendor config points a builder hits the first time they wire a channel, address grammar, the fields
that decide whether the connection establishes, and the reliability knobs. These are lookup facts, not a
tutorial.

> **Digest, verify against the live product.** The **address grammar and field formats** below mirror each
> driver's in-Designer `<Hint>` text and the product docs; when connected, `list_protocols` and `search_docs`
> are authoritative and fresher, treat this page as a convenience, not the source of truth. The
> **commissioning notes** (the OPC-UA headless cert-trust loop, the duplicate-`ClientID` drop, the IEC-104
> port, the byte-order flags) are the field judgment this page adds on top of the per-field reference.

## How to read this, and where the truth is

- **Every FrameworX channel address is composed differently per protocol**: concatenated (Modbus `400001`,
  S7 `DB1.DBW0`, Genisys `I1`), colon-separated (ControlLogix `DINT:Tag:true`, Omron `DM:0`), or dot-separated
  (BACnet `AnalogInput.0.PresentValue`). There is no universal address shape.
- **The authoritative, build-specific source is the driver's own config XML**: the `<Hint>`, `<Format>`,
  and `<Examples>` text in `Protocols\T.ProtocolDriver.<Name>.config.xml`. That `<Hint>` text is *exactly*
  what the Designer shows in the cell editor for that field. When in doubt, read the field's hint on your
  install: it is the curated, per-field trap list.
- **Confirm the protocol token before you write a channel.** Call `list_protocols` once and use the returned
  `name` verbatim: family names are not what you'd guess (often the transport, e.g. TCP vs RTU, is a
  *sub-config*, not a separate family). An unknown token is rejected outright.
- **`<Multiplatform>` in the config root** tells you whether a driver runs on a non-Windows / .NET-portable
  runtime, check it before targeting a Linux or edge runtime.

Everything below was read from driver config-XML hint text. Items that are general protocol knowledge (not
from a FrameworX source) are tagged **(general protocol knowledge)**. As always: **the live product wins**,
if a hint on your build differs, the build is right.

---

## Modbus (master)

The densest source of real config traps.

- **Register base, the `Offset address` checkbox.** `false` = address 1 is the first register; `true` =
  address 0 is the first register. The single most common Modbus off-by-one.
- **Operand prefix selects the table *and* R/W semantics:** `0` = Coil (R/W bit), `1` = Discrete Input (R/O
  bit), `3` = Input Register (R/O 16-bit), `4` = Holding Register (R/W 16-bit). IEC aliases: `%Q`/`%M` = Coil,
  `%I` = Discrete Input, `%IW` = Input Register, `%MW`/`%QW` = Holding Register.
- **Address is concatenated, not separated: prefix + 5-digit zero-padded register.** `400001` = Holding
  Register 1; register `100` becomes `00100`. No separator.
- **Encoding:** RTU (binary serial), ASCII (7-bit text), RTU TCP (TCP/IP). Wrong encoding = total comms
  failure on an otherwise-correct config. FX default is `RTU TCP`.
- **Single-write vs block-write changes the function code:** single = FC05 (coil) / FC06 (register); block =
  FC15 / FC16. Some slaves accept only one form: flip this if writes are rejected.
- **Coil ON value differs by device:** `FF` = 0xFF00 (standard), `01` = 0x0001 (some devices). A coil write
  that "does nothing" on a non-standard slave is usually this.
- **`BlockSize`** caps items per request (e.g. 250 → up to 125 registers or 2000 coils per request). Lower it
  for slaves with small buffers, a throughput/reliability knob.
- **Defaults:** TCP port 502; TCP Station UnitID 0-255 (0 = broadcast); serial SlaveID 1-247. (Note the
  Station UnitID range differs from the driver's own-SlaveID range.)

## OPC UA (client)

- **Endpoint:** `opc.tcp://<host>:4840` (4840 is the conventional port), on the Station `Url` field.
- **NodeId address:** `ns=2;s=TagName` (string id) or `ns=2;i=1001` (numeric id). The namespace index
  (`ns=`) is mandatory and server-specific.
- **The fields that gate whether a connection even handshakes:** `DisableSecurity`, `WindowsAuthentication`,
  `UserName`/`Password` (empty = anonymous), `Domain`, `CertificateType` (Default / FilePath / ProjectFolder
  / Custom).
- **⚠ Cert trust on a headless runtime, plan for it before you deploy.** With `CertificateType = Default`
  the client auto-trusts the server cert on first connect and self-populates its trusted store. With a
  **Custom** cert type it does **not** auto-trust: place the server certificate in the runtime's trust store
  **out-of-band, before** starting the channel. On a headless/remote runtime there is no interactive "trust
  this cert?" prompt, so a Custom channel loops `Connecting → Disconnected` until the server cert is
  imported. If a remote OPC UA channel won't connect, check this first.
- **Subscription vs polling:** `EnableReadPolling` switches from UA subscriptions (server push, `RefreshRate`
  ms) to timer-based polling: use polling for servers with flaky subscription support. `ReadGroupMaxSize` /
  `UseSingleReadGroup` tune items-per-read-group.
- **Timestamp/cache levers:** `UseComputerTimestamp` (local instead of server timestamp); `ReadFromDevice`
  (bypass server cache). Reliability levers when server timestamps or caching misbehave.

## MQTT (client)

- **Port:** 1883 = plaintext, 8883 = TLS. Set `NetworkSecurity` (None / TLSv1.0 / v1.1 / v1.2) to match.
  a mismatched port-vs-TLS is a *silent* connect failure.
- **Topic address uses `/` as the level separator** (`plant/line1/temperature`).
- **QoS:** AtMostOnce (0) / AtLeastOnce (1, default) / ExactlyOnce (2), delivery guarantee vs throughput.
- **`RetainedMessage` (per-topic):** the broker holds the last message so a new subscriber gets the last
  value immediately; without it a freshly-started client sees nothing until the next publish.
- **`ClientID` must be unique on the broker** (`_SolutionName_-_Guid_` auto-generates one). Duplicate client
  IDs make brokers disconnect the older session. A classic "connection keeps dropping" trap.
- **`StoreAndForward`** queues messages while the broker is unreachable and sends on reconnect, the key knob
  for intermittent links.
- **`KeepAlive`** (s, default 10) and **`TimePublishRate`** (ms; values below ~50 ms are ignored).
- **Mutual TLS:** `X509Certificate` path field for client-cert auth.
- **FrameworX ships a built-in MQTT broker + client**: point builder guidance there rather than at an
  external broker.

## MQTT Sparkplug B (and the AWS / Azure cloud siblings)

- **Address is `GroupId/NodeId/DeviceId`** (3-level identity); `+` and `#` are subscribe wildcards. The AWS
  variant splits this into separate GroupID / NodeID / DeviceID fields.
- **`Type` = Publisher vs Collector** changes the whole role: Collector subscribes/ingests, Publisher emits.
  (`TimePublishRate` is not used for a Collector.)
- **`PublishDBIRTHAfterNBIRTH`** (default true): a DBIRTH is requested when an NBIRTH is. Turning it off can
  leave device metrics unannounced. **(general Sparkplug-B knowledge)** for the birth-certificate sequencing.
- **`PublishMetricNames` is independent of Store-and-Forward.** You can publish metrics *by name* (not just
  by alias) via this dedicated option **without** enabling Store-and-Forward, which matters for a third-party
  subscriber (e.g. a Historian) that joins mid-session after DBIRTH and can't resolve aliases without the
  NBIRTH.
- **`DisableRebirthRequest`** suppresses NCMD/DCMD rebirth commands, for downstream nodes that mishandle
  rebirth.
- **Interop knobs:** `PublishUDTsAsSimpleTags` flattens UDT structures into folder-structured simple tags;
  `UseParenthesesForArray` swaps `[]` for `()` in metric names: both are traps with strict consumers.
- **TLS enum is broader/legacy-named here** (None / Ssl2 / Ssl3 / Tls / Tls11 / Tls12) vs plain MQTT's
  `TLSv1.x` naming; a `WebSocket` transport toggle is also present.
- **AWS IoT Core:** endpoint `xxxxx.iot.<region>.amazonaws.com`, port 8883, Tls12, X.509 device cert (`.pem`)
  for auth, Username usually empty (cert auth). Azure is the sibling cloud connector.

## Siemens S7: the DB / non-DB format split

The DB / non-DB format split. (The legacy `Siemens` driver is Windows-only; the `SiemensPlus` driver is
Multiplatform: pick `SiemensPlus` for Linux/.NET-portable runtimes.)

- **Station:** IP; Rack; Slot; TCP Port (102 = ISO-on-TCP); S7 family. **Rack = 0** for most PLCs; **Slot = 1
  for S7-300/400, Slot = 0 for S7-1200/1500.** Family combo `300/400` vs `1200` (1200 covers 1200/1500).
  Wrong rack/slot = no connection. **(general S7 knowledge)** for the rack/slot conventions.
- **DB vs non-DB tokens must NOT be mixed.** For `Type = DB` use DB-prefixed tokens: `DBB` (Byte), `DBW`
  (Word), `DBDW` (DWord), `DBF` (Float), `DBSTR` (String), `DBST` (Short String). For `Type = M/T/C/I/Q` use
  the non-DB tokens `B/W/DW/F/ST/C/T`. Trap: `DB3.ST12.50` is **invalid**. Use `DB3.DBSTR12.50`.
- **TIA `STRING[N]` length = TOTAL bytes = N+2** (the 2-byte S7 string header). A `STRING[24]` is configured
  as length **26**, e.g. `DB1.DBSTR16.26`. Off-by-2 truncates/corrupts the string. Use the DB-area `DBSTR`/
  `DBST` tokens for DB operands, never the non-DB `ST`.
- **Composed address shape** (not semicolon-separated): `operand + (dbGroup + '.')? + format + offset + ('.'
  + bitOrLength)?`. Examples: `MB0`, `DB1.DBW0`, `DB1.DBB15.3` (byte offset 15, bit 3), `DB1.DBF8` (float at
  offset 8).

## EtherNet/IP: ControlLogix / CompactLogix (CIP)

- **Station:** IP; Port (44818 = EtherNet/IP standard); Slot = chassis slot of the CPU module (0 = leftmost).
  Wrong slot on a multi-module chassis = no connection. **(general EtherNet/IP knowledge)**.
- **The station is `IP;Port;Slot` and nothing more: no multi-hop CIP routing.** The connector reaches the CPU
  one backplane hop from the Ethernet module at that IP. A controller reachable only through a bridge (a
  second Ethernet module, ControlNet or DH+ behind the first chassis) cannot be addressed, and a route typed
  into the Station or Slot field is not a supported way around it. Give each controller an Ethernet module
  with its own IP in its own chassis (one Device Node each), or put a gateway that speaks a supported
  protocol in front of that segment. **(checked against the FrameworX 10.1.5 connector; re-verify on your
  build)**.
- **Address is the symbolic tag name, colon-composed: `Type:DeviceTagName:ForceCIPLittleEndian`.** The tag
  name is **case-sensitive and must match the controller program exactly.** Dot for structure members
  (`Motor1.Speed`), brackets for arrays (`Temps[0]`). **(general Logix knowledge)** for case-sensitivity.
- **CIP data types:** BOOL, SINT (8), INT (16), DINT (32), REAL (float), STRING, DATATYPE (UDT).
- **⚠ Byte-order trap:** `CIPLittleEndian` (default true) auto-applies CIP little-endian ordering for
  DINT/INT/REAL. When unchecked, the per-point `ByteSwap` modifier controls ordering instead. Garbled 32-bit
  values usually trace to this flag.
- **`Model` combo** (Others / 1756-L8X / Micro850) tunes the driver per controller family;
  `MaxStringItemsPerBlock` and `WaitingBetweenMsgs` (ms) are reliability knobs for slow controllers.
- **Program-scope vs controller-scope tags are addressed differently**: a program-scope tag needs its scope
  qualification, not the bare controller-tag form. *(Confirm the exact program-scope syntax on your build.)*
- **MicroLogix sibling** uses SLC/PLC-style **file-based addressing**, concatenated
  `<FileType><FileNumber>:<Address>`: `N7:0` (Integer file 7, element 0), `F8:1` (Float), `ST11:1` (String),
  `B7:0` (Binary), `O7:0`/`I7:0` (Output/Input). Port 44818. **(general Allen-Bradley knowledge)** for the
  file-type letters.

## BACnet (BACnet/IP)

- **Station:** Device ID (the BACnet Device Instance ID, **the identity, not the IP**; wrong ID silently
  targets the wrong/no device); IP; Port 47808 (`0xBAC0`, the BACnet/IP default); Connect Timeout; Retry
  Attempts (1-10).
- **Address is dot-composed: `Type.ObjectInstance.Property`**: e.g. `AnalogInput.0.PresentValue`. Object
  types: AnalogInput/Output/Value, BinaryInput/Output/Value, MultiStateInput/Output/Value.
- **The property is explicit in the address** (PresentValue, StatusFlags, Reliability, EventState…). Most
  reads target `PresentValue`; the wrong property returns valid-but-useless data.
- Port + Connect Timeout + Retry Attempts are the reliability triad for congested building networks.

## Omron FINS

- **FINS triad:** Mode (CS1 for CS1/CJ1/compat, CV for CV/CVM1/compat); Network (0-127); Node (the PLC's FINS
  node number). Wrong Mode for the CPU family = protocol-level rejection.
- **Address is colon-composed `MemoryArea:Address`** (+ optional Bank for E/EM). Areas: CIO, WR (Work), HR
  (Holding), AR (Auxiliary), DM (Data Memory), EM/E (Extended, bank 0-7), TA/CA (Timers/Counters). Word
  address 0-32767.
- **Two transports with different Station shapes:** UDP (`IP;Port;Network;Node`) and serial
  (`Network;Node;UnitID`, UnitID for the PC interface on serial only).

## IEC 60870-5-104 (master): the telecontrol set

- **Station:** IP; Port; SlaveID = the destination ASDU/common address. Single-node-per-channel.
- **⚠ Set the Station Port explicitly to `2404`**, the **IEC 60870-5-104 standard port** **(general protocol
  knowledge)**. Don't accept whatever the field is pre-filled with (`502` is the Modbus port, not this one):
  read the value back before the first connect attempt, a standards-compliant IEC-104 server answers only on
  `2404`.
- The **IEC-101 serial sibling** is the same protocol over a serial link (a free-string destination address).

## Genisys / Microlok (rail signaling)

- **Two reliability-specific Station fields beyond the usual IP/Port/SlaveID:** `Recall` (send a Recall every
  N poll cycles, 0 = disabled) and `SecurePolls` (send checksums in polls), vital-signaling reliability
  knobs.
- **Address is concatenated `TypeAddress`:** `I` = Indicator, `C` = Control (`I1`, `C1`).

---

## Cross-cutting

- **Byte / word order on 32-bit values.** FrameworX exposes per-point `ByteSwap` / `WordSwap`-style ordering
  as modifier columns (referenced by ControlLogix `CIPLittleEndian`, and applicable to Modbus 32-bit reads).
  The general rule, **a Modbus float's byte+word order must match the slave (ABCD / CDAB / BADC / DCBA)**,
  is **(general protocol knowledge)**; if a 32-bit value reads garbled, this is the usual cause.
- **MQTT-family client certificates** resolve from the channel's `X509Certificate` field; if not found there,
  the runtime falls back to `MachineSettings/Certificates/<filename>`. This is shared across MQTT-family
  Device channels and UNS TagProviders (OPC UA keeps its own `Certificates/own/{certs,private,trusted,
  issuers}/` structure). Filename collisions are the user's responsibility. Use unique names.

*(Driver config XML is the authoritative, build-specific source for every field above. Read the `<Hint>` /
`<Format>` / `<Examples>` on your install before authoring at scale: and verify any value here against your
build.)*
