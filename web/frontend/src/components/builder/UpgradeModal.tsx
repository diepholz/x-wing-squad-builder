import { useState } from "react";
import { useBuilderStore } from "../../stores/builderStore";
import { prettifyName, resolveUpgradeCost, buildEffectivePilot } from "../../lib/squadLogic";
import { Upgrade } from "../../types";

interface Props {
  pilotIdx: number;
  slot: string;
  currentUpgrade: string | undefined;
  onSelect: (upgradeName: string) => void;
  onClose: () => void;
}

export default function UpgradeModal({ pilotIdx, slot, currentUpgrade, onSelect, onClose }: Props) {
  const { definition, faction, squad, getFilteredUpgrades } = useBuilderStore();
  const [search, setSearch] = useState("");

  if (!definition || !faction) return null;

  const sp = squad[pilotIdx];
  const ep = sp ? buildEffectivePilot(definition, faction, sp.ship_name, sp.pilot_name) : null;
  const upgrades = getFilteredUpgrades(pilotIdx, slot);
  const query = search.toLowerCase();
  const filtered = upgrades.filter(
    (u) => !query || u.name.includes(query) || u.upgrade_slot_types.some((s) => s.includes(query))
  );

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-md flex flex-col max-h-[80vh]">
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h3 className="font-semibold text-white capitalize">{slot} upgrades</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-white text-xl leading-none">
            ×
          </button>
        </div>

        <div className="p-3 border-b border-gray-800">
          <input
            autoFocus
            placeholder="Filter upgrades…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        <div className="overflow-y-auto flex-1 p-2">
          {filtered.length === 0 && (
            <p className="text-gray-500 text-sm text-center py-6">
              No available upgrades for this slot
            </p>
          )}
          {filtered.map((upgrade) => {
            const cost =
              ep && typeof upgrade.cost === "number"
                ? upgrade.cost
                : ep
                ? resolveUpgradeCost(upgrade, ep)
                : "?";
            const isEquipped = upgrade.name === currentUpgrade;
            return (
              <button
                key={upgrade.name}
                onClick={() => onSelect(upgrade.name)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded text-sm transition-colors text-left mb-0.5 ${
                  isEquipped
                    ? "bg-brand-800 text-white"
                    : "hover:bg-gray-800 text-gray-300 hover:text-white"
                }`}
              >
                <div>
                  <span>{prettifyName(upgrade.name)}</span>
                  {upgrade.modifications?.actions && upgrade.modifications.actions.length > 0 && (
                    <span className="ml-2 text-xs text-green-400">
                      +{upgrade.modifications.actions.map((a) => a.action).join(", ")}
                    </span>
                  )}
                </div>
                <span className="text-gray-400 text-xs shrink-0 ml-2">{cost} pts</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
