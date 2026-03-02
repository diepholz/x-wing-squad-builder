import { create } from "zustand";
import { DefinitionData, SquadPilot, EquippedUpgrade, Upgrade } from "../types";
import { buildEffectivePilot, filterUpgradesForPilot, resolveUpgradeCost } from "../lib/squadLogic";

interface BuilderState {
  definition: DefinitionData | null;
  faction: string | null;
  squad: SquadPilot[];
  squadName: string;

  setDefinition: (d: DefinitionData) => void;
  setFaction: (f: string) => void;
  setSquadName: (n: string) => void;
  addPilot: (shipName: string, pilotName: string) => void;
  removePilot: (idx: number) => void;
  equipUpgrade: (pilotIdx: number, slot: string, upgradeName: string) => void;
  unequipUpgrade: (pilotIdx: number, slot: string) => void;
  reset: () => void;
  loadSquad: (faction: string, pilots: SquadPilot[]) => void;

  // Derived helpers (call with current state inline)
  totalPoints: () => number;
  getFilteredUpgrades: (pilotIdx: number, slot: string) => Upgrade[];
  getAvailableSlots: (pilotIdx: number) => string[];
}

export const useBuilderStore = create<BuilderState>((set, get) => ({
  definition: null,
  faction: null,
  squad: [],
  squadName: "My Squad",

  setDefinition: (d) => set({ definition: d }),
  setFaction: (f) => set({ faction: f, squad: [] }),
  setSquadName: (n) => set({ squadName: n }),

  addPilot(shipName, pilotName) {
    set((s) => ({
      squad: [
        ...s.squad,
        { ship_name: shipName, pilot_name: pilotName, upgrades: [] },
      ],
    }));
  },

  removePilot(idx) {
    set((s) => ({ squad: s.squad.filter((_, i) => i !== idx) }));
  },

  equipUpgrade(pilotIdx, slot, upgradeName) {
    set((s) => {
      const squad = s.squad.map((p, i) => {
        if (i !== pilotIdx) return p;
        const upgrades = p.upgrades.filter((u) => u.slot !== slot);
        upgrades.push({ slot, upgrade_name: upgradeName });
        return { ...p, upgrades };
      });
      return { squad };
    });
  },

  unequipUpgrade(pilotIdx, slot) {
    set((s) => ({
      squad: s.squad.map((p, i) =>
        i === pilotIdx
          ? { ...p, upgrades: p.upgrades.filter((u) => u.slot !== slot) }
          : p
      ),
    }));
  },

  reset() {
    set({ faction: null, squad: [], squadName: "My Squad" });
  },

  loadSquad(faction, pilots) {
    set({ faction, squad: pilots });
  },

  totalPoints() {
    const { definition, faction, squad } = get();
    if (!definition || !faction) return 0;
    let total = 0;
    for (const sp of squad) {
      const pilot = findPilot(definition, faction, sp.ship_name, sp.pilot_name);
      if (!pilot) continue;
      total += pilot.cost;
      for (const eu of sp.upgrades) {
        const upgrade = definition.upgrades.find((u) => u.name === eu.upgrade_name);
        if (!upgrade) continue;
        const ep = buildEffectivePilot(definition, faction, sp.ship_name, sp.pilot_name);
        if (ep) total += resolveUpgradeCost(upgrade, ep);
      }
    }
    return total;
  },

  getFilteredUpgrades(pilotIdx, slot) {
    const { definition, faction, squad } = get();
    if (!definition || !faction) return [];
    const sp = squad[pilotIdx];
    if (!sp) return [];
    const ep = buildEffectivePilot(definition, faction, sp.ship_name, sp.pilot_name);
    if (!ep) return [];

    // Build a minimal squad view for solitary/unique checks
    const squadView = { squad, definition, faction };
    return filterUpgradesForPilot(definition.upgrades, ep, squadView, slot);
  },

  getAvailableSlots(pilotIdx) {
    const { definition, faction, squad } = get();
    if (!definition || !faction) return [];
    const sp = squad[pilotIdx];
    if (!sp) return [];
    const ep = buildEffectivePilot(definition, faction, sp.ship_name, sp.pilot_name);
    if (!ep) return [];

    // Start with default slots
    const slots = [...ep.defaultUpgradeSlots, ...ep.hardpoint];

    // Apply modification from equipped upgrades
    for (const eu of sp.upgrades) {
      const upgrade = definition.upgrades.find((u) => u.name === eu.upgrade_name);
      if (!upgrade?.modifications?.upgrade_slots) continue;
      const { added, removed } = upgrade.modifications.upgrade_slots;
      slots.push(...added);
      for (const r of removed) {
        const idx = slots.indexOf(r);
        if (idx >= 0) slots.splice(idx, 1);
      }
    }

    // Remove occupied slots
    for (const eu of sp.upgrades) {
      const idx = slots.indexOf(eu.slot);
      if (idx >= 0) slots.splice(idx, 1);
    }

    return slots;
  },
}));

function findPilot(def: DefinitionData, faction: string, shipName: string, pilotName: string) {
  const fa = def.factions.find((f) => f.name === faction);
  if (!fa) return null;
  const ship = fa.ships.find((s) => s.name === shipName);
  if (!ship) return null;
  return ship.pilots.find((p) => p.name === pilotName) ?? null;
}
