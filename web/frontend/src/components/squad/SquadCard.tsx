import { useState } from "react";
import { ApiSquad } from "../../types";
import { prettifyName } from "../../lib/squadLogic";
import { squadsApi } from "../../api/client";

interface Props {
  squad: ApiSquad;
  onLoad: () => void;
  onDelete: () => void;
}

export default function SquadCard({ squad, onLoad, onDelete }: Props) {
  const [shareUrl, setShareUrl] = useState<string | null>(
    squad.share_token ? `/share/${squad.share_token}` : null
  );
  const [copying, setCopying] = useState(false);

  async function handleShare() {
    try {
      const { data } = await squadsApi.share(squad.id);
      setShareUrl(data.share_url);
      await navigator.clipboard.writeText(window.location.origin + `/share/${data.share_token}`);
      setCopying(true);
      setTimeout(() => setCopying(false), 2000);
    } catch {
      // ignore
    }
  }

  const pts = squad.data.pilots.reduce(
    (sum, p) => sum + 0, // server doesn't return costs; show pilot count instead
    0
  );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-white">{squad.name}</h3>
          <p className="text-xs text-gray-500 mt-0.5">{prettifyName(squad.faction)}</p>
        </div>
        <button
          onClick={onDelete}
          className="text-gray-600 hover:text-red-400 text-sm transition-colors"
          title="Delete"
        >
          ✕
        </button>
      </div>

      <div className="text-sm text-gray-400">
        {squad.data.pilots.length} pilot{squad.data.pilots.length !== 1 ? "s" : ""}:{" "}
        {squad.data.pilots
          .map((p) => prettifyName(p.pilot_name))
          .join(", ")}
      </div>

      <div className="flex gap-2 pt-1">
        <button
          onClick={onLoad}
          className="flex-1 bg-brand-700 hover:bg-brand-600 text-white text-sm py-1.5 rounded transition-colors"
        >
          Load
        </button>
        <button
          onClick={handleShare}
          className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm py-1.5 rounded transition-colors"
        >
          {copying ? "Copied!" : "Share"}
        </button>
      </div>
    </div>
  );
}
