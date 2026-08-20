import React from "react";
import { Mic, Square } from "lucide-react";
import { motion } from "framer-motion";

export default function VoiceButton({ recording, onStart, onStop, disabled }) {
  return (
    <div className="voice-button-wrap">
      {recording && (
        <>
          <motion.span
            className="pulse-ring ring-one"
            animate={{ scale: [1, 1.35], opacity: [0.55, 0] }}
            transition={{ repeat: Infinity, duration: 1.6 }}
          />
          <motion.span
            className="pulse-ring ring-two"
            animate={{ scale: [1, 1.55], opacity: [0.35, 0] }}
            transition={{ repeat: Infinity, duration: 1.6, delay: 0.45 }}
          />
        </>
      )}
      <motion.button
        className={`voice-button ${recording ? "recording" : ""}`}
        whileHover={!disabled ? { scale: 1.04 } : {}}
        whileTap={!disabled ? { scale: 0.96 } : {}}
        onClick={recording ? onStop : onStart}
        disabled={disabled}
        aria-label={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? <Square size={28} fill="currentColor" /> : <Mic size={32} />}
      </motion.button>
    </div>
  );
}
