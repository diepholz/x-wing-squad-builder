// ── Definition schema (mirrors definition.json) ──────────────────────────────

export interface Attack {
  attack: number;
  arc_type: string;
}

export interface SubStat {
  [key: string]: number | null; // e.g. { shield: 2, recharge: 0 }
}

export interface ShipStatistics {
  attacks: Attack[];
  agility: number;
  hull: number;
  shield: SubStat;
  force: SubStat;
  energy: SubStat;
  charge: SubStat;
}

export interface Action {
  action: string;
  color: string;
  action_link: string | null;
  color_link: string | null;
}

export interface Pilot {
  name: string;
  unique: boolean;
  initiative: number;
  cost: number;
  keywords: string[];
  stat_overrides: Partial<ShipStatistics>;
  extra_actions: Action[];
  extra_upgrade_slots: string[];
}

export interface Ship {
  name: string;
  base: string;
  statistics: ShipStatistics;
  actions: Action[];
  upgrade_slots: string[];
  pilots: Pilot[];
  hardpoint?: string[];
}

export interface Faction {
  name: string;
  ships: Ship[];
}

export interface VariableCost {
  type: string; // "by_base" | "by_initiative" | "by_agility" | "by_attacks"
  [key: string]: number | string;
}

export type UpgradeCost = number | VariableCost;

export type RangeRestriction = { low: number | null; high: number | null };

export interface SubStatRestriction {
  [key: string]: RangeRestriction;
}

export interface UpgradeRestrictions {
  limit?: number;
  pilot_initiative?: RangeRestriction;
  pilot_limit?: RangeRestriction;
  factions?: string[];
  ships?: string[];
  base_sizes?: string[];
  attacks?: RangeRestriction;
  arc_types?: string[];
  agility?: RangeRestriction;
  hull?: RangeRestriction;
  shield?: SubStatRestriction;
  force?: SubStatRestriction;
  energy?: SubStatRestriction;
  charge?: SubStatRestriction;
  actions?: Action[];
  keywords?: string[];
  other_equipped_upgrades?: string[];
}

export interface UpgradeModifications {
  actions?: Action[];
  upgrade_slots?: { added: string[]; removed: string[] };
}

export interface Upgrade {
  name: string;
  upgrade_slot_types: string[];
  cost: UpgradeCost;
  autoinclude: boolean;
  epic: boolean;
  solitary: boolean;
  squad_include?: string[];
  restrictions?: UpgradeRestrictions;
  modifications?: UpgradeModifications;
}

export interface DefinitionData {
  factions: Faction[];
  upgrades: Upgrade[];
}

// ── Squad builder state ───────────────────────────────────────────────────────

export interface EquippedUpgrade {
  slot: string;
  upgrade_name: string;
}

export interface SquadPilot {
  ship_name: string;
  pilot_name: string;
  upgrades: EquippedUpgrade[];
}

export interface SquadData {
  pilots: SquadPilot[];
}

// ── API types ─────────────────────────────────────────────────────────────────

export interface ApiUser {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface ApiToken {
  access_token: string;
  token_type: string;
}

export interface ApiSquad {
  id: number;
  name: string;
  faction: string;
  data: SquadData;
  share_token: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface ShareResponse {
  share_token: string;
  share_url: string;
}

export interface SharedSquadResponse {
  squad: ApiSquad;
  owner: string;
}

// ── Derived pilot (ship + pilot merged) ──────────────────────────────────────

export interface EffectivePilot {
  factionName: string;
  shipName: string;
  pilotName: string;
  base: string;
  initiative: number;
  cost: number;
  unique: boolean;
  keywords: string[];
  statistics: ShipStatistics;
  actions: Action[];
  /** Base upgrade slots before equipping any upgrades */
  defaultUpgradeSlots: string[];
  hardpoint: string[];
}
