import React from "react";
import { Gauge } from "lucide-react";

export default function LatencyBadge({ latency }) {
  return (
    <div className="latency-badge">
      <Gauge size={16} />
      <span>Response latency</span>
      <strong>{latency == null ? "—" : `${Math.round(latency)} ms`}</strong>
    </div>
  );
}
