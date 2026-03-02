import { useState } from "react";
import { SquadPilot, Upgrade } from "../../types";
import { useBuilderStore } from "../../stores/builderStore";
import { prettifyName, resolveUpgradeCost, buildEffectivePilot } from "../../lib/squadLogic";
import UpgradeSlot from "./UpgradeSlot";
import UpgradeModal from "./UpgradeModal";

interface Props {
  squadPilot: SquadPilot;
  pilotIdx: number;
}

export default function PilotCard({ squadPilot, pilotIdx }: Props) {
  const { definition, faction, removePilot, equipUpgrade, unequipUpgrade, getAvailableSlots } =
    useBuilderStore();
  const [openSlot, setOpenSlot] = useState<string | null>(null);

  if (!definition || !faction) return null;

  const ep = buildEffectivePilot(definition, faction, squadPilot.ship_name, squadPilot.pilot_name);
  if (!ep) return null;

  const availableSlots = getAvailableSlots(pilotIdx);
  // All slots = equipped + available
  const occupiedSlots = squadPilot.upgrades.map((u) => u.slot);
  const allSlots = [...new Set([...occupiedSlots, ...availableSlots])].sort();

  // Sum upgrade costs
  const upgradeCost = squadPilot.upgrades.reduce((sum, eu) => {
    const upgrade = definition.upgrades.find((u) => u.name === eu.upgrade_name);
    return sum + (upgrade ? resolveUpgradeCost(upgrade, ep) : 0);
  }, 0);

  return (
    <>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-3">
        <div className="flex items-start justify-between mb-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-gray-500 w-5 text-center bg-gray-800 rounded">
                {ep.initiative}
              </span>
              <span className={`font-medium text-sm ${ep.unique ? "text-yellow-300" : "text-white"}`}>
                {prettifyName(squadPilot.pilot_name)}
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5 ml-7">
              {prettifyName(squadPilot.ship_name)}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-brand-400">
              {ep.cost + upgradeCost} pts
            </span>
            <button
              onClick={() => removePilot(pilotIdx)}
              className="text-gray-600 hover:text-red-400 text-lg leading-none transition-colors"
              title="Remove pilot"
            >
              ×
            </button>
          </div>
        </div>

        {/* Stats row */}
        <div className="flex gap-3 text-xs text-gray-500 mb-2 ml-7">
          <span title="Attack">⚔ {ep.statistics.attacks[0]?.attack ?? 0}</span>
          <span title="Agility">↷ {ep.statistics.agility}</span>
          <span title="Hull">♥ {ep.statistics.hull}</span>
          {(ep.statistics.shield?.shield ?? 0) > 0 && (
            <span title="Shield">🛡 {ep.statistics.shield.shield}</span>
          )}
          {(ep.statistics.force?.force ?? 0) > 0 && (
            <span title="Force">✦ {ep.statistics.force.force}</span>
          )}
        </div>

        {/* Upgrade slots */}
        <div className="border-t border-gray-800 pt-2 ml-2">
          {allSlots.map((slot) => {
            const eu = squadPilot.upgrades.find((u) => u.slot === slot);
            return (
              <UpgradeSlot
                key={slot}
                slot={slot}
                equipped={eu?.upgrade_name}
                onOpen={() => setOpenSlot(slot)}
                onUnequip={() => unequipUpgrade(pilotIdx, slot)}
              />
            );
          })}
          {allSlots.length === 0 && (
            <p className="text-xs text-gray-600 italic">No upgrade slots</p>
          )}
        </div>
      </div>

      {openSlot && (
        <UpgradeModal
          pilotIdx={pilotIdx}
          slot={openSlot}
          currentUpgrade={squadPilot.upgrades.find((u) => u.slot === openSlot)?.upgrade_name}
          onSelect={(upgradeName) => {
            equipUpgrade(pilotIdx, openSlot, upgradeName);
            setOpenSlot(null);
          }}
          onClose={() => setOpenSlot(null)}
        />
      )}
    </>
  );
}
