import React from "react";
import { Mic, RefreshCw } from "lucide-react";

export default function MicSelector({
  devices,
  selectedDeviceId,
  setSelectedDeviceId,
  refreshDevices,
}) {
  return (
    <div className="mic-selector">
      <div className="mic-icon"><Mic size={17} /></div>
      <div className="mic-select-wrap">
        <label htmlFor="mic-select">INPUT DEVICE</label>
        <select
          id="mic-select"
          value={selectedDeviceId}
          onChange={(e) => setSelectedDeviceId(e.target.value)}
        >
          {devices.length === 0 && <option value="">Default microphone</option>}
          {devices.map((device, index) => (
            <option key={device.deviceId} value={device.deviceId}>
              {device.label || `Microphone ${index + 1}`}
            </option>
          ))}
        </select>
      </div>
      <button className="icon-button" onClick={refreshDevices} title="Refresh microphones">
        <RefreshCw size={16} />
      </button>
    </div>
  );
}
