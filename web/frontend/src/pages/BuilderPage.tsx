import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useBuilderStore } from "../stores/builderStore";
import { useAuthStore } from "../stores/authStore";
import { dataApi, squadsApi } from "../api/client";
import { DefinitionData } from "../types";
import FactionPicker from "../components/builder/FactionPicker";
import PilotPool from "../components/builder/PilotPool";
import ActiveSquad from "../components/builder/ActiveSquad";

export default function BuilderPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { definition, faction, squad, squadName, setDefinition, setFaction, reset } =
    useBuilderStore();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Load definition data
  const { data: defData } = useQuery({
    queryKey: ["definition"],
    queryFn: () => dataApi.definition().then((r) => r.data as DefinitionData),
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (defData) setDefinition(defData);
  }, [defData, setDefinition]);

  // Pick faction from URL query param on mount
  useEffect(() => {
    const urlFaction = searchParams.get("faction");
    if (urlFaction && !faction) {
      setFaction(urlFaction);
    }
  }, [searchParams, faction, setFaction]);

  function handleFactionChange(f: string) {
    setFaction(f);
    navigate(`/build?faction=${encodeURIComponent(f)}`, { replace: true });
  }

  async function handleSave() {
    if (!user || !faction || squad.length === 0) return;
    setSaving(true);
    try {
      await squadsApi.create({ name: squadName, faction, data: { pilots: squad } });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  if (!defData) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading game data…
      </div>
    );
  }

  if (!faction) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-500 mb-4">
          Choose a faction
        </h2>
        <FactionPicker onSelect={handleFactionChange} />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-3 px-4 py-2 border-b border-gray-800 bg-gray-950">
        <button
          onClick={() => { reset(); navigate("/build"); }}
          className="text-xs text-gray-500 hover:text-white transition-colors"
        >
          ← Change faction
        </button>
        <span className="text-xs text-gray-600">|</span>
        <span className="text-xs text-gray-400 capitalize">{faction}</span>
        <div className="ml-auto flex gap-2">
          {user && (
            <button
              onClick={handleSave}
              disabled={saving || squad.length === 0}
              className="text-xs bg-brand-700 hover:bg-brand-600 disabled:opacity-40 text-white px-3 py-1.5 rounded transition-colors"
            >
              {saved ? "Saved!" : saving ? "Saving…" : "Save Squad"}
            </button>
          )}
        </div>
      </div>

      {/* Three-panel builder */}
      <div className="flex flex-1 overflow-hidden">
        {/* Pilot pool */}
        <div className="w-72 shrink-0 border-r border-gray-800 overflow-y-auto p-3">
          <PilotPool />
        </div>

        {/* Active squad */}
        <div className="flex-1 overflow-y-auto p-4">
          <ActiveSquad />
        </div>
      </div>
    </div>
  );
}
