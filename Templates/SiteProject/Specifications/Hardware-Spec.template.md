# Hardware and topology spec: <NAME>

> The hardware envelope the solution targets. A solution that does not know its hardware is a
> prototype. State the controllers, the network, the protocol load, the point counts, and the
> runtime host sizing. For a simulation-only first version, say so and fill in the runtime host;
> the rest can be marked "future" until the field layer is real.

## 1. Field devices

| Device | Vendor / model | Protocol | Point count | Poll rate | Notes |
|---|---|---|---|---|---|
| <PLC-1> | <model> | <Modbus TCP / OPC UA / EtherNet-IP / ...> | <n> | <ms> | |

- **Total points:** <n>
- **Total tags:** <n>  (points plus calculated and internal)

> If this version is simulation-only: "No field devices in this version. Process values are driven
> by simulation scripts. Field layer is future work." Then complete Section 4.

## 2. Network and topology

- **Segments:** <control network, plant network, business network>
- **Where the runtime host sits:** <segment>
- **Where operators connect from:** <thin client, web, local>
- **Remote access for the AI MCP bridges:** <localhost only | trusted LAN | VPN>. See
  `KnowledgeBase/Method/mcp-setup.md` for the auth model. Do not expose a bridge to the public internet.

## 3. Protocol load and redundancy

- **Protocols in use:** <list>
- **Redundancy:** <none | redundant runtime | redundant network>
- **Expected update rate end to end:** <field to screen, ms>

## 4. Runtime host sizing

| Resource | Minimum | Recommended | Notes |
|---|---|---|---|
| CPU | <cores> | <cores> | leave headroom for the historian and any local AI model |
| RAM | <GB> | <GB> | scales with tag count and historian retention |
| Disk | <GB> | <GB> | historian growth at <points> x <rate> x <retention> |
| OS | Windows <ver> | | |

- **Historian growth estimate:** <points logged> x <samples/day> x <bytes/sample> x <retention days>
  = <GB>. Size the disk for this, not for today.
- **Local AI (optional):** if the solution uses the platform's local AI features, the host needs
  room for the model. A CPU-only default model is a few GB of RAM and disk; a larger production
  model needs more. Plan the host so the AI model does not starve the runtime.

## 5. Growth

<How this scales. More lines, more sites, more points. The architecture should grow by adding
instances of existing UserTypes and adding device channels, not by reworking the foundation. State
the next two growth steps so the foundation is sized for them.>
