import React from "react";
import { Activity, Github, Radio } from "lucide-react";
import { motion } from "framer-motion";

export default function Navbar({ backendOnline }) {
  return (
    <header className="nav-wrap">
      <nav className="navbar container">
        <a className="brand" href="#top" aria-label="BRAHMA home">
          <span className="brand-mark"><Radio size={18} /></span>
          <span>
            <strong>BRAHMA</strong>
            <small>VOICE RAG</small>
          </span>
        </a>

        <div className="nav-links">
          <a href="#console">Console</a>
          <a href="#pipeline">Pipeline</a>
          <a href="#about">About</a>
        </div>

        <div className="nav-status">
          <motion.span
            className={`status-dot ${backendOnline ? "online" : "offline"}`}
            animate={backendOnline ? { scale: [1, 1.35, 1] } : {}}
            transition={{ repeat: Infinity, duration: 2 }}
          />
          <span>{backendOnline ? "Backend online" : "Backend offline"}</span>
          <Activity size={15} />
          <a href="#github" aria-label="Project link"><Github size={17} /></a>
        </div>
      </nav>
    </header>
  );
}
